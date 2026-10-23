"""
market_ai.py
AI-Powered Market Gap Analyzer with Statistical Fallback
"""

import os
from typing import Dict, Optional

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


class MarketAI:
    """محلل فجوات السوق بالذكاء الاصطناعي"""

    def __init__(self, api_key: Optional[str] = None):
        self.available = False
        self.model = None
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                self.api_key = self.api_key or st.secrets['GEMINI_API_KEY']
        except Exception:
            pass

        if self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.available = True
                print("Gemini AI initialized successfully")
            except Exception as e:
                print(f"AI init error: {e}")
                self.available = False

    def analyze(self, neg_text: str, category: str) -> str:
        """تحليل التقييمات السلبية"""
        if not neg_text or not neg_text.strip():
            return "No negative reviews available for analysis."
        if self.available:
            return self._ai_analysis(neg_text, category)
        else:
            return self._statistical_analysis(neg_text, category)

    def _ai_analysis(self, neg_text: str, category: str) -> str:
        """تحليل بالذكاء الاصطناعي"""
        prompt = f"""You are a Senior Product Manager and Market Analyst.

I am planning to launch a new mobile app in the **{category}** market.
Below are real 1-star and 2-star reviews from competitor apps:

=== NEGATIVE REVIEWS ===
{neg_text}
=== END OF REVIEWS ===

Provide a concise, executive-level analysis in Markdown:

## Top 3 Recurring Bugs / Complaints
- List the most frequent technical or usability issues

## Top 3 Missing Features Users Want
- List features users are asking for but competitors lack

## Strategic Recommendations for Our New App
- Provide 3-5 actionable recommendations to capture market share

Be data-driven, concise, and professional. Use bullet points."""

        try:
            import google.generativeai as genai
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1500
                )
            )
            return response.text
        except Exception as e:
            return f"AI Error: {str(e)}\n\n{self._statistical_analysis(neg_text, category)}"

    def _statistical_analysis(self, neg_text: str, category: str) -> str:
        """تحليل إحصائي بديل"""
        neg_count = neg_text.count('\n') + 1 if neg_text else 0

        complaint_keywords = {
            'Performance Issues': ['slow', 'crash', 'freeze', 'lag', 'bug', 'error', 'loading', 'broken'],
            'UI/UX Problems': ['confusing', 'hard', 'difficult', 'complicated', 'ugly', 'navigation', 'interface'],
            'Missing Features': ['missing', 'need', 'want', 'should', 'wish', 'add', 'lack', 'absent'],
            'Customer Support': ['support', 'help', 'service', 'response', 'ignored', 'no reply', 'contact'],
            'Pricing Concerns': ['expensive', 'price', 'cost', 'subscription', 'money', 'paid', 'free']
        }

        text_lower = neg_text.lower()
        keyword_counts = {}
        for cat, keywords in complaint_keywords.items():
            keyword_counts[cat] = sum(text_lower.count(kw) for kw in keywords)

        sorted_issues = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)

        report = f"""## Statistical Analysis for '{category}'

**Negative Reviews Analyzed:** {neg_count}

### Top Complaint Categories:
"""
        for i, (cat, count) in enumerate(sorted_issues[:3], 1):
            if count > 0:
                report += f"{i}. **{cat}**: {count} mentions\n"

        if not any(count > 0 for _, count in sorted_issues):
            report += "No specific complaint patterns detected.\n"

        report += f"""
### Strategic Recommendations:
1. **Optimize Performance**: Ensure fast, stable app with less than 2s load time
2. **Simplify UI**: Clean, intuitive interface with minimal clicks
3. **Add Requested Features**: Based on user feedback analysis
4. **Improve Support**: 24/7 customer service with less than 1h response
5. **Fair Pricing**: Transparent, competitive pricing model

### Market Opportunity:
- **Negative Reviews**: {neg_count} users expressing dissatisfaction
- **Opportunity Score**: {'High' if neg_count > 50 else 'Medium' if neg_count > 20 else 'Low'}
- **Risk Level**: Medium

---
*Note: Configure GEMINI_API_KEY in Streamlit Secrets for detailed AI-powered analysis*"""

        return report

    def analyze_multiple_apps(self, apps_reviews_dict: Dict[str, str], category: str) -> Dict[str, Dict]:
        """تحليل عدة تطبيقات دفعة واحدة"""
        results = {}
        for app_name, neg_text in apps_reviews_dict.items():
            results[app_name] = {
                'status': 'success',
                'analysis': self.analyze(neg_text, category)
            }
        return results
