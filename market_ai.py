import os

try:
    import google.generativeai as genai
    HAS_AI = True
except:
    HAS_AI = False


class MarketAI:
    def __init__(self, api_key=None, language='en'):
        self.language = language
        self.available = False
        self.model = None
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                self.api_key = self.api_key or st.secrets['GEMINI_API_KEY']
        except:
            pass
        if self.api_key and HAS_AI:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-pro")
                self.available = True
            except:
                pass

    def analyze(self, neg_text, category, language=None):
        if language:
            self.language = language
        if not neg_text or not neg_text.strip():
            return "لا توجد تقييمات." if self.language == 'ar' else "No reviews."
        if self.available:
            return self._ai(neg_text, category)
        return self._stat(neg_text, category)

    def _ai(self, neg_text, category):
        if self.language == 'ar':
            prompt = f"""أنت محلل سوق. حلل هذه التقييمات السلبية لتطبيقات '{category}':
{neg_text}
أجب بالعربية فقط: أهم 3 مشاكل، أهم 3 ميزات ناقصة، توصيات."""
        else:
            prompt = f"""Analyze negative reviews for '{category}' apps:
{neg_text}
Provide in English: Top 3 bugs, Top 3 missing features, Recommendations."""
        try:
            return self.model.generate_content(prompt).text
        except:
            return self._stat(neg_text, category)

    def _stat(self, neg_text, category):
        neg_count = neg_text.count('\n') + 1 if neg_text else 0
        text = neg_text.lower()

        if self.language == 'ar':
            kw = {
                'مشاكل الأداء': ['slow','crash','freeze','lag','bug','error','loading','broken','بطيء','يتوقف'],
                'مشاكل الواجهة': ['confusing','hard','difficult','ugly','navigation','معقد','صعب'],
                'ميزات ناقصة': ['missing','need','want','should','wish','add','ناقص','أتمنى'],
                'دعم العملاء': ['support','help','service','response','ignored','دعم','مساعدة'],
                'الأسعار': ['expensive','price','cost','subscription','غالي','سعر','اشتراك']
            }
            counts = {c: sum(text.count(k) for k in ks) for c, ks in kw.items()}
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            report = f"##  التحليل الإحصائي لفئة '{category}'\n\n"
            report += f"**عدد التقييمات السلبية:** {neg_count}\n\n"
            report += "### 🐞 أكثر الشكاوى شيوعاً:\n"
            for i, (cat, count) in enumerate(top, 1):
                if count > 0:
                    report += f"{i}. **{cat}**: ذُكرت {count} مرة\n"
            report += "\n### 💡 التوصيات الاستراتيجية:\n"
            report += "1. **تحسين الأداء**: تطبيق سريع ومستقر\n"
            report += "2. **تبسيط الواجهة**: واجهة بديهية\n"
            report += "3. **إضافة الميزات المطلوبة**: بناءً على ملاحظات المستخدمين\n"
            report += "4. **تحسين الدعم**: خدمة عملاء سريعة\n"
            report += "5. **تسعير عادل**: نموذج شفاف\n\n"
            report += "### 📊 فرصة السوق:\n"
            score = 'عالية' if neg_count > 50 else 'متوسطة' if neg_count > 20 else 'منخفضة'
            report += f"- **درجة الفرصة**: {score}\n"
            report += f"- **المستخدمون غير الراضين**: {neg_count}\n"
            return report
        else:
            kw = {
                'Performance Issues': ['slow','crash','freeze','lag','bug','error','loading','broken'],
                'UI/UX Problems': ['confusing','hard','difficult','ugly','navigation','interface'],
                'Missing Features': ['missing','need','want','should','wish','add','lack'],
                'Customer Support': ['support','help','service','response','ignored','no reply'],
                'Pricing Concerns': ['expensive','price','cost','subscription','money','paid']
            }
            counts = {c: sum(text.count(k) for k in ks) for c, ks in kw.items()}
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            report = f"## 📊 Statistical Analysis for '{category}'\n\n"
            report += f"**Negative Reviews:** {neg_count}\n\n"
            report += "### 🐞 Top Complaints:\n"
            for i, (cat, count) in enumerate(top, 1):
                if count > 0:
                    report += f"{i}. **{cat}**: {count} mentions\n"
            report += "\n### 💡 Strategic Recommendations:\n"
            report += "1. **Optimize Performance**: Fast and stable app\n"
            report += "2. **Simplify UI**: Clean interface\n"
            report += "3. **Add Requested Features**: Based on feedback\n"
            report += "4. **Improve Support**: 24/7 service\n"
            report += "5. **Fair Pricing**: Transparent model\n\n"
            report += "### 📊 Market Opportunity:\n"
            score = 'High' if neg_count > 50 else 'Medium' if neg_count > 20 else 'Low'
            report += f"- **Opportunity Score**: {score}\n"
            report += f"- **Dissatisfied Users**: {neg_count}\n"
            return report

    def analyze_multiple_apps(self, apps_dict, category, language=None):
        if language:
            self.language = language
        results = {}
        for name, text in apps_dict.items():
            results[name] = {
                'status': 'success',
                'analysis': self.analyze(text, category, language)
            }
        return results
