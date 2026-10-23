import sqlite3
import pandas as pd
import time
from google_play_scraper import search, reviews, Sort
from typing import List, Dict
from datetime import datetime


class MarketEngine:
    def __init__(self, db_name: str = 'competitor_intelligence.db'):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS apps (app_id TEXT PRIMARY KEY, title TEXT NOT NULL, developer TEXT, rating REAL, icon TEXT, scraped_at TIMESTAMP)')
        cur.execute('CREATE TABLE IF NOT EXISTS reviews (review_id TEXT PRIMARY KEY, app_id TEXT, text TEXT, score INTEGER, sentiment TEXT, review_date TIMESTAMP, thumbs_up INTEGER, FOREIGN KEY(app_id) REFERENCES apps(app_id))')
        conn.commit()
        conn.close()

    def search_apps(self, keyword: str, n_results: int = 15) -> List[Dict]:
        try:
            is_arabic = any(chr(0x0600) <= c <= chr(0x06FF) for c in keyword)
            lang = 'ar' if is_arabic else 'en'
            country = 'sa' if is_arabic else 'us'
            results = search(keyword, n_hits=n_results, lang=lang, country=country)
            apps = []
            for app in results:
                apps.append({
                    'app_id': app.get('appId'),
                    'title': app.get('title'),
                    'developer': app.get('developer'),
                    'rating': app.get('score'),
                    'icon': app.get('icon'),
                    'summary': (app.get('summary') or '')[:150]
                })
            return apps
        except Exception as e:
            print(f'Search error: {e}')
            return []

    def scrape_reviews(self, app_id: str, count: int = 200) -> pd.DataFrame:
        all_reviews = []
        continuation_token = None
        try:
            while len(all_reviews) < count:
                result, continuation_token = reviews(app_id, lang='en', country='us', sort=Sort.NEWEST, count=min(50, count - len(all_reviews)), continuation_token=continuation_token)
                if not result:
                    break
                for r in result:
                    all_reviews.append({
                        'review_id': r.get('reviewId'),
                        'app_id': app_id,
                        'text': r.get('content', '').strip(),
                        'score': r.get('score'),
                        'review_date': r.get('at'),
                        'thumbs_up': r.get('thumbsUpCount', 0)
                    })
                if continuation_token is None:
                    break
                time.sleep(1)
        except Exception as e:
            print(f'Scraping error for {app_id}: {e}')
        return pd.DataFrame(all_reviews)

    def classify_sentiment(self, score: int) -> str:
        if score >= 4:
            return 'Positive'
        elif score == 3:
            return 'Neutral'
        else:
            return 'Negative'

    def process_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df['sentiment'] = df['score'].apply(self.classify_sentiment)
        df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        df['text'] = df['text'].str.strip()
        df = df.dropna(subset=['text'])
        return df

    def save_to_database(self, apps_df: pd.DataFrame, reviews_df: pd.DataFrame):
        conn = sqlite3.connect(self.db_name)
        apps_df.to_sql('apps', conn, if_exists='replace', index=False)
        reviews_df.to_sql('reviews', conn, if_exists='replace', index=False)
        conn.close()

    def export_to_excel(self, apps_df: pd.DataFrame, reviews_df: pd.DataFrame, filename: str = 'competitor_report.xlsx'):
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            apps_df.to_excel(writer, sheet_name='Apps', index=False)
            reviews_df.to_excel(writer, sheet_name='Reviews', index=False)
            summary = reviews_df.groupby(['app_id', 'sentiment']).size().reset_index(name='count')
            summary.to_excel(writer, sheet_name='Summary', index=False)
            stats = reviews_df.groupby('app_id').agg({'score': ['mean', 'count'], 'sentiment': lambda x: (x == 'Positive').sum()}).reset_index()
            stats.columns = ['app_id', 'avg_rating', 'total_reviews', 'positive_count']
            stats.to_excel(writer, sheet_name='Statistics', index=False)

    def get_negative_reviews(self, app_id: str, max_reviews: int = 50) -> str:
        conn = sqlite3.connect(self.db_name)
        query = 'SELECT text FROM reviews WHERE app_id = ? AND score <= 2 AND text != ? LIMIT ?'
        df = pd.read_sql_query(query, conn, params=(app_id, '', max_reviews))
        conn.close()
        return '\n---\n'.join(df['text'].tolist())
