"""
app.py
======
Market Intelligence Pro - Interactive Streamlit Dashboard
AI-Powered Competitor Analysis & Market Gap Detection

Deliverables (as per project requirements):
- Dynamic App Discovery from Google Play
- Multi-App Selection (2-4 apps) with targeted scraping
- SQLite database storage (competitor_intelligence.db)
- Multi-sheet Excel report (competitor_report.xlsx)
- AI-powered market gap analysis via Gemini API
- Interactive Plotly charts
- Bilingual support (Arabic/English)

Author: Nawal Massa
Date: October 2026
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. استيراد المحركات (كما هو مطلوب في المشروع)
# ==========================================
try:
    from market_engine import MarketEngine
    from market_ai import MarketAI
    ENGINES_LOADED = True
except ImportError as e:
    st.error(f"❌ Error importing modules: {e}")
    st.error("Please ensure market_engine.py and market_ai.py are in the same folder.")
    st.stop()

# ==========================================
# 2. نظام الترجمة (Bilingual Support AR/EN)
# ==========================================
TRANSLATIONS = {
    'en': {
        'title': "🚀 Market Intelligence Pro",
        'subtitle': "AI-Powered Competitor Analysis & Market Gap Detection",
        'welcome': " Welcome to Market Intelligence Pro",
        'welcome_desc': "Your intelligent tool to analyze competitors and discover market gaps.",
        'how_to_start': " How to Start:",
        'step1': "1. (Optional) Enter your **Gemini API Key** in the sidebar",
        'step2': '2. Search for apps using a keyword (e.g., "fitness", "food delivery")',
        'step3': "3. Select 2-4 competing apps to compare",
        'step4': "4. Click **⚡ Analyze & Report**",
        'step5': "5. View charts, AI insights, and download reports",
        'tip': "💡 **Tip:** Start by searching for apps in the sidebar!",
        'sidebar_title': "📝 Project Setup",
        'api_key': "🔑 Gemini API Key",
        'api_placeholder': "Enter your API key (optional)",
        'api_help': "Get your free key from https://aistudio.google.com/app/apikey",
        'ai_enabled': "✅ AI Analysis enabled!",
        'statistical_mode': "ℹ️ Using Statistical Analysis (AI optional)",
        'search_step': "🔍 Step 1: Search for Apps",
        'search_keyword': "Search Keyword",
        'search_placeholder': "e.g., fitness, food delivery, banking, travel",
        'num_results': "Number of Results",
        'search_btn': "🔎 Search Apps",
        'found_apps': "✅ Found {} apps",
        'no_apps': "⚠️ No apps found. Try another keyword.",
        'enter_keyword': "⚠️ Please enter a keyword",
        'select_step': "✅ Step 2: Select 2-4 Apps",
        'apps_selected': "✅ {} apps selected!",
        'max_apps': "⛔ Max 4 apps allowed",
        'need_apps': "️ Selected: {} (need 2-4)",
        'analyze_btn': "⚡ Analyze & Report",
        'processing': "⚙️ Processing data...",
        'scraping': "Scraping {}...",
        'running_analysis': "🤖 Running Analysis...",
        'analysis_complete': "✅ Analysis Complete!",
        'total_reviews': "Total Reviews",
        'apps_analyzed': "Apps Analyzed",
        'positive_sentiment': "Positive Sentiment",
        'avg_rating': "Average Rating",
        'tab_charts': "📊 Charts",
        'tab_insights': " Insights",
        'tab_raw': " Raw Data",
        'tab_download': " Download",
        'sentiment_analysis': " Sentiment Analysis",
        'market_insights': "🤖 Market Insights",
        'raw_data': "📋 Raw Data",
        'download_reports': "💾 Download Reports",
        'excel_report': "📥 Excel Report",
        'database': "📥 Database",
        'footer': "🚀 **Market Intelligence Pro** | Built with Streamlit, Python & Gemini AI",
        'footer_date': "📅 October 2026 | Nawal Massa",
        'language': "🌐 Language / اللغة",
        'searching': "🔎 Searching Google Play...",
        'no_analysis': "No analysis available yet.",
        'quick_stats': "📊 Quick Statistics",
        'positive_count': "Positive Reviews",
        'negative_count': "Negative Reviews",
        'neutral_count': "Neutral Reviews",
    },
    'ar': {
        'title': "🚀 محلل ذكاء السوق",
        'subtitle': "تحليل المنافسين واكتشاف فجوات السوق بالذكاء الاصطناعي",
        'welcome': " مرحباً بك في محلل ذكاء السوق",
        'welcome_desc': "أداتك الذكية لتحليل المنافسين واكتشاف فجوات السوق قبل تطوير المنتج.",
        'how_to_start': "🚀 كيفية البدء:",
        'step1': "1. (اختياري) أدخل **مفتاح Gemini API** في الشريط الجانبي",
        'step2': '2. ابحث عن التطبيقات باستخدام كلمة مفتاحية (مثل "لياقة"، "توصيل طعام")',
        'step3': "3. اختر 2-4 تطبيقات منافسة للمقارنة",
        'step4': "4. اضغط **⚡ تحليل وتقارير**",
        'step5': "5. اعرض الرسوم البيانية والرؤى وحمّل التقارير",
        'tip': "💡 **نصيحة:** ابدأ بالبحث عن التطبيقات في الشريط الجانبي!",
        'sidebar_title': "📝 إعدادات المشروع",
        'api_key': "🔑 مفتاح Gemini API",
        'api_placeholder': "أدخل مفتاح API (اختياري)",
        'api_help': "احصل على مفتاحك المجاني من https://aistudio.google.com/app/apikey",
        'ai_enabled': "✅ تم تفعيل تحليل الذكاء الاصطناعي!",
        'statistical_mode': "ℹ️ استخدام التحليل الإحصائي (الذكاء الاصطناعي اختياري)",
        'search_step': "🔍 الخطوة 1: البحث عن التطبيقات",
        'search_keyword': "كلمة البحث",
        'search_placeholder': "مثال: لياقة، توصيل طعام، بنوك، سفر، ملابس",
        'num_results': "عدد النتائج",
        'search_btn': "🔎 بحث عن التطبيقات",
        'found_apps': "✅ تم العثور على {} تطبيق",
        'no_apps': "⚠️ لم يتم العثور على تطبيقات. جرب كلمة أخرى.",
        'enter_keyword': "⚠️ يرجى إدخال كلمة بحث",
        'select_step': "✅ الخطوة 2: اختر 2-4 تطبيقات",
        'apps_selected': "✅ تم اختيار {} تطبيق!",
        'max_apps': "⛔ الحد الأقصى 4 تطبيقات",
        'need_apps': "ℹ️ تم اختيار: {} (تحتاج 2-4)",
        'analyze_btn': " تحليل وتقارير",
        'processing': "️ معالجة البيانات...",
        'scraping': "جاري سحب {}...",
        'running_analysis': "🤖 جاري التحليل...",
        'analysis_complete': "✅ اكتمل التحليل!",
        'total_reviews': "إجمالي التقييمات",
        'apps_analyzed': "التطبيقات المحللة",
        'positive_sentiment': "المشاعر الإيجابية",
        'avg_rating': "متوسط التقييم",
        'tab_charts': "📊 الرسوم البيانية",
        'tab_insights': "🤖 الرؤى",
        'tab_raw': "📋 البيانات الخام",
        'tab_download': "💾 تحميل",
        'sentiment_analysis': "📊 تحليل المشاعر",
        'market_insights': "🤖 رؤى السوق",
        'raw_data': "📋 البيانات الخام",
        'download_reports': "💾 تحميل التقارير",
        'excel_report': "📥 تقرير Excel",
        'database': "📥 قاعدة البيانات",
        'footer': "🚀 **محلل ذكاء السوق** | مبني بـ Streamlit و Python و Gemini AI",
        'footer_date': "📅 أكتوبر 2026 | نوال مسة",
        'language': " Language / اللغة",
        'searching': "🔎 جاري البحث في Google Play...",
        'no_analysis': "لا يوجد تحليل متاح حالياً.",
        'quick_stats': "📊 إحصائيات سريعة",
        'positive_count': "التقييمات الإيجابية",
        'negative_count': "التقييمات السلبية",
        'neutral_count': "التقييمات المحايدة",
    }
}

def get_lang():
    """الحصول على اللغة المختارة"""
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    return st.session_state.language

def t(key):
    """ترجمة النص"""
    lang = get_lang()
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))

# ==========================================
# 3. إعداد الصفحة
# ==========================================
st.set_page_config(
    page_title="Market Intelligence Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 4. التصميم (CSS احترافي)
# ==========================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 { margin: 0; font-size: 2.8rem; font-weight: 800; }
    .main-header p { margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.95; }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid #667eea;
        transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-5px); }
    .stat-card h3 { color: #667eea; font-size: 2rem; margin: 0; font-weight: 700; }
    .stat-card p { color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem; }
    .footer {
        text-align: center;
        color: #6c757d;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid #e2e8f0;
    }
    .stButton > button { transition: all 0.3s; }
    .stButton > button:hover { transform: scale(1.02); }
    /* RTL support for Arabic */
    .rtl-mode .stMarkdown, .rtl-mode .stExpander { direction: rtl; text-align: right; }
</style>
""", unsafe_allow_html=True)

# تطبيق RTL للعربية
if get_lang() == 'ar':
    st.markdown("""
    <style>
        .main .block-container { direction: rtl; }
        .stExpander { direction: rtl; }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 5. تهيئة الحالة
# ==========================================
if "apps_found" not in st.session_state:
    st.session_state.apps_found = []
if "selected_apps" not in st.session_state:
    st.session_state.selected_apps = []
if "reviews_data" not in st.session_state:
    st.session_state.reviews_data = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "keyword" not in st.session_state:
    st.session_state.keyword = ""
if "language" not in st.session_state:
    st.session_state.language = 'en'

# ==========================================
# 6. زر تبديل اللغة في الأعلى
# ==========================================
lang_col1, lang_col2, lang_col3 = st.columns([1, 2, 1])
with lang_col2:
    lang_option = st.radio(
        t('language'),
        ['English', 'العربية'],
        horizontal=True,
        label_visibility="collapsed",
        index=0 if get_lang() == 'en' else 1
    )
    if lang_option == 'العربية' and get_lang() != 'ar':
        st.session_state.language = 'ar'
        st.rerun()
    elif lang_option == 'English' and get_lang() != 'en':
        st.session_state.language = 'en'
        st.rerun()

# ==========================================
# 7. الهيدر الرئيسي
# ==========================================
st.markdown(f"""
<div class="main-header">
    <h1>{t('title')}</h1>
    <p>{t('subtitle')}</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 8. الشريط الجانبي
# ==========================================
with st.sidebar:
    st.header(t('sidebar_title'))

    # مفتاح API (اختياري)
    st.subheader(t('api_key'))
    api_key = None
    
    # محاولة الحصول من Streamlit Secrets (للنشر على Cloud)
    try:
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            api_key = st.secrets['GEMINI_API_KEY']
            st.success("✅ API Key loaded from secrets!")
    except:
        pass
    
    if not api_key:
        api_key = st.text_input(
            "",
            type="password",
            placeholder=t('api_placeholder'),
            label_visibility="collapsed",
            help=t('api_help')
        )

    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        st.success(t('ai_enabled'))
    else:
        st.info(t('statistical_mode'))

    st.markdown("---")

    # البحث عن التطبيقات
    st.subheader(t('search_step'))
    keyword = st.text_input(
        t('search_keyword'),
        placeholder=t('search_placeholder')
    )

    num_results = st.slider(t('num_results'), 5, 20, 10)

    if st.button(t('search_btn'), use_container_width=True, type="primary"):
        if keyword:
            with st.spinner(t('searching')):
                engine = MarketEngine()
                apps = engine.search_apps(keyword, n_results=num_results)
                st.session_state.apps_found = apps
                st.session_state.keyword = keyword

                if apps:
                    st.success(t('found_apps').format(len(apps)))
                else:
                    st.warning(t('no_apps'))
        else:
            st.warning(t('enter_keyword'))

    # اختيار التطبيقات
    if st.session_state.apps_found:
        st.markdown("---")
        st.subheader(t('select_step'))

        selected = []
        for app in st.session_state.apps_found:
            col1, col2 = st.columns([1, 4])
            with col1:
                if app.get('icon'):
                    try:
                        st.image(app['icon'], width=40)
                    except:
                        pass
            with col2:
                checked = st.checkbox(
                    app['title'],
                    key=app['app_id'],
                    help=f"⭐ {app['rating']} | {app['developer']}"
                )
                if checked:
                    selected.append(app)

        if 2 <= len(selected) <= 4:
            st.session_state.selected_apps = selected
            st.success(t('apps_selected').format(len(selected)))
        elif len(selected) > 4:
            st.error(t('max_apps'))
        else:
            st.info(t('need_apps').format(len(selected)))

    # زر التحليل
    if st.session_state.selected_apps:
        st.markdown("---")
        if st.button(t('analyze_btn'), use_container_width=True, type="primary"):
            with st.spinner(t('processing')):
                engine = MarketEngine()
                ai_engine = MarketAI(api_key=api_key)
                all_reviews, apps_data = [], []

                # سحب متوازي للسرعة
                def scrape_one(app):
                    df = engine.scrape_reviews(app['app_id'], count=150)
                    if not df.empty:
                        df = engine.process_reviews(df)
                        return app, df
                    return None, None

                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = {executor.submit(scrape_one, app): app 
                              for app in st.session_state.selected_apps}
                    for future in as_completed(futures):
                        try:
                            app, df = future.result()
                            if df is not None:
                                all_reviews.append(df)
                                apps_data.append(app)
                        except Exception as e:
                            print(f"Error: {e}")

                if all_reviews:
                    combined = pd.concat(all_reviews, ignore_index=True)
                    st.session_state.reviews_data = combined

                    # حفظ في قاعدة البيانات
                    engine.save_to_database(pd.DataFrame(apps_data), combined)
                    
                    # تصدير Excel
                    engine.export_to_excel(pd.DataFrame(apps_data), combined, 
                                          "competitor_report.xlsx")

                    # تحليل AI / إحصائي
                    neg_dict = {}
                    for app in apps_data:
                        neg = engine.get_negative_reviews(app['app_id'], max_reviews=50)
                        if neg:
                            neg_dict[app['title']] = neg

                    if neg_dict:
                        with st.spinner(t('running_analysis')):
                            st.session_state.analysis_results = ai_engine.analyze_multiple_apps(
                                neg_dict, st.session_state.keyword
                            )

                    st.balloons()
                    st.success(t('analysis_complete'))

# ==========================================
# 9. الواجهة الرئيسية
# ==========================================
if st.session_state.reviews_data is None:
    # صفحة الترحيب
    st.header(t('welcome'))
    st.markdown(t('welcome_desc'))

    st.markdown("---")

    st.subheader(t('how_to_start'))
    st.markdown(f"""
    {t('step1')}
    {t('step2')}
    {t('step3')}
    {t('step4')}
    {t('step5')}
    """)

    st.info(t('tip'))

else:
    # عرض النتائج
    df = st.session_state.reviews_data
    
    # دمج أسماء التطبيقات للعرض
    apps_df = pd.DataFrame(st.session_state.selected_apps)
    if 'title' in apps_df.columns:
        df = df.merge(apps_df[["app_id", "title"]], on="app_id", how="left")

    # بطاقات الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h3>{len(df):,}</h3>
            <p>{t('total_reviews')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h3>{df["app_id"].nunique()}</h3>
            <p>{t('apps_analyzed')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        pos_pct = (df['sentiment'] == 'Positive').sum() / len(df) * 100
        st.markdown(f"""
        <div class="stat-card" style="border-top-color: #2ecc71;">
            <h3 style="color: #2ecc71;">{pos_pct:.1f}%</h3>
            <p>{t('positive_sentiment')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        avg = df['score'].mean()
        st.markdown(f"""
        <div class="stat-card" style="border-top-color: #f39c12;">
            <h3 style="color: #f39c12;">{avg:.2f}⭐</h3>
            <p>{t('avg_rating')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # التبويبات
    tab1, tab2, tab3, tab4 = st.tabs([
        t('tab_charts'), t('tab_insights'), t('tab_raw'), t('tab_download')
    ])

    # ===== تبويب الرسوم البيانية =====
    with tab1:
        st.subheader(t('sentiment_analysis'))
        col1, col2 = st.columns(2)
        with col1:
            counts = df['sentiment'].value_counts().reset_index()
            counts.columns = ['Sentiment', 'Count']
            fig = px.pie(
                counts, values='Count', names='Sentiment', color='Sentiment',
                color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'},
                hole=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            by_app = df.groupby(['app_id', 'sentiment']).size().reset_index(name='count')
            fig2 = px.bar(
                by_app, x='app_id', y='count', color='sentiment',
                color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # توزيع التقييمات
        st.subheader("⭐ Rating Distribution")
        fig3 = px.histogram(
            df, x='score', color='title' if 'title' in df.columns else 'app_id',
            title="Rating Distribution Across Apps",
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ===== تبويب الرؤى =====
    with tab2:
        if get_lang() == 'ar':
            st.subheader("🤖 رؤى السوق والذكاء الاصطناعي")
        else:
            st.subheader(t('market_insights'))
        
        if st.session_state.analysis_results:
            for app_name, result in st.session_state.analysis_results.items():
                with st.expander(f"📱 {app_name}", expanded=True):
                    if result['status'] == 'success':
                        st.markdown(result['analysis'])
                    else:
                        st.error(result['analysis'])
        else:
            st.info(t('no_analysis'))

    # ===== تبويب البيانات الخام (بالعربي) =====
    with tab3:
        if get_lang() == 'ar':
            st.subheader("📋 البيانات الخام")
            
            # إنشاء نسخة مترجمة للعرض
            df_display = df.copy()
            
            # ترجمة قيم المشاعر
            sentiment_translation = {
                'Positive': 'إيجابي 😊',
                'Neutral': 'محايد 😐',
                'Negative': 'سلبي 😞'
            }
            df_display['sentiment'] = df_display['sentiment'].map(
                lambda x: sentiment_translation.get(x, x)
            )
            
            # إعادة تسمية الأعمدة
            column_translation = {
                'review_id': 'معرف التقييم',
                'app_id': 'معرف التطبيق',
                'title': 'اسم التطبيق',
                'text': 'نص التقييم',
                'score': 'التقييم (نجوم)',
                'sentiment': 'المشاعر',
                'review_date': 'تاريخ التقييم',
                'thumbs_up': 'عدد الإعجابات'
            }
            df_display = df_display.rename(columns=column_translation)
            
            # اختيار الأعمدة للعرض
            display_cols = [col for col in 
                          ['اسم التطبيق', 'نص التقييم', 'التقييم (نجوم)', 'المشاعر', 'تاريخ التقييم', 'عدد الإعجابات']
                          if col in df_display.columns]
            
            st.dataframe(df_display[display_cols], use_container_width=True, height=400)
            
            # إحصائيات سريعة
            st.markdown("---")
            st.subheader(t('quick_stats'))
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t('positive_count'), len(df[df['sentiment'].str.contains('إيجابي')]))
            with col2:
                st.metric(t('neutral_count'), len(df[df['sentiment'].str.contains('محايد')]))
            with col3:
                st.metric(t('negative_count'), len(df[df['sentiment'].str.contains('سلبي')]))
        else:
            st.subheader(t('raw_data'))
            st.dataframe(df, use_container_width=True, height=400)

    # ===== تبويب التحميل =====
    with tab4:
        st.subheader(t('download_reports'))
        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists("competitor_report.xlsx"):
                with open("competitor_report.xlsx", "rb") as f:
                    st.download_button(
                        t('excel_report'),
                        f,
                        file_name=f"competitor_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        use_container_width=True
                    )
        with col2:
            if os.path.exists("competitor_intelligence.db"):
                with open("competitor_intelligence.db", "rb") as f:
                    st.download_button(
                        t('database'),
                        f,
                        file_name=f"competitor_intelligence_{datetime.now().strftime('%Y%m%d')}.db",
                        use_container_width=True
                    )

# ==========================================
# 10. الفوتر
# ==========================================
st.markdown("---")
st.markdown(f'<div class="footer"><p>{t("footer")}</p><p>{t("footer_date")}</p></div>', unsafe_allow_html=True)