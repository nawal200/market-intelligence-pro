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
                self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
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

         def _statistical_analysis(self, neg_text, category):
        """تحليل إحصائي ثنائي اللغة"""
        neg_count = neg_text.count('\n') + 1 if neg_text else 0

        if self.language == 'ar':
            # قاموس عربي
            kw = {
                'مشاكل في الأداء': ['slow','crash','freeze','lag','bug','error','loading','broken','بطيء','يتوقف','خطأ'],
                'مشاكل في الواجهة': ['confusing','hard','difficult','complicated','ugly','navigation','interface','معقد','صعب'],
                'ميزات ناقصة': ['missing','need','want','should','wish','add','lack','absent','ناقص','أتمنى'],
                'دعم العملاء': ['support','help','service','response','ignored','no reply','contact','دعم','مساعدة'],
                'مخاوف الأسعار': ['expensive','price','cost','subscription','money','paid','free','غالي','سعر','اشتراك']
            }
            text = neg_text.lower()
            counts = {c: sum(text.count(k) for k in ks) for c, ks in kw.items()}
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            report = f"""## 📊 التحليل الإحصائي لفئة '{category}'

**عدد التقييمات السلبية المحللة:** {neg_count}

### 🐞 أكثر الشكاوى شيوعاً:
"""
            for i, (cat, count) in enumerate(top, 1):
                if count > 0:
                    report += f"{i}. **{cat}**: ذُكرت {count} مرة\n"
            
            if not any(c > 0 for _, c in top):
                report += "لم يتم اكتشاف أنماط محددة.\n"
            
            report += f"""
### 💡 التوصيات الاستراتيجية:
1. **تحسين الأداء**: ضمان تطبيق سريع ومستقر بوقت تحميل أقل من ثانيتين
2. **تبسيط الواجهة**: واجهة نظيفة وبديهية مع أقل عدد من النقرات
3. **إضافة الميزات المطلوبة**: بناءً على تحليل ملاحظات المستخدمين
4. **تحسين الدعم**: خدمة عملاء على مدار الساعة مع استجابة خلال ساعة
5. **تسعير عادل**: نموذج تسعير شفاف وتنافسي

### 📊 مؤشرات فرصة السوق:
- **التقييمات السلبية**: {neg_count} مستخدم يعبر عن عدم الرضا
- **درجة الفرصة**: {'عالية' if neg_count > 50 else 'متوسطة' if neg_count > 20 else 'منخفضة'}
- **مستوى المخاطرة**: متوسط

---
*ملاحظة: فعّلي مفتاح Gemini API للحصول على تحليل أعمق بالذكاء الاصطناعي*"""
            return report
        
        else:
            # English version
            kw = {
                'Performance Issues': ['slow','crash','freeze','lag','bug','error','loading','broken'],
                'UI/UX Problems': ['confusing','hard','difficult','complicated','ugly','navigation','interface'],
                'Missing Features': ['missing','need','want','should','wish','add','lack','absent'],
                'Customer Support': ['support','help','service','response','ignored','no reply','contact'],
                'Pricing Concerns': ['expensive','price','cost','subscription','money','paid','free']
            }
            text = neg_text.lower()
            counts = {c: sum(text.count(k) for k in ks) for c, ks in kw.items()}
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            report = f"""## 📊 Statistical Analysis for '{category}'

**Negative Reviews Analyzed:** {neg_count}

### 🐞 Top Complaint Categories:
"""
            for i, (cat, count) in enumerate(top, 1):
                if count > 0:
                    report += f"{i}. **{cat}**: {count} mentions\n"
            
            if not any(c > 0 for _, c in top):
                report += "No specific patterns detected.\n"
            
            report += f"""
### 💡 Strategic Recommendations:
1. **Optimize Performance**: Ensure fast, stable app with <2s load time
2. **Simplify UI**: Clean, intuitive interface with minimal clicks
3. **Add Requested Features**: Based on user feedback analysis
4. **Improve Support**: 24/7 customer service with <1h response
5. **Fair Pricing**: Transparent, competitive pricing model

### 📊 Market Opportunity:
- **Negative Reviews**: {neg_count} users expressing dissatisfaction
- **Opportunity Score**: {'High' if neg_count > 50 else 'Medium' if neg_count > 20 else 'Low'}
- **Risk Level**: Medium

---
*Note: Configure GEMINI_API_KEY for detailed AI-powered analysis*"""
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
