import os
import google.generativeai as genai


class MarketAI:
    """محلل فجوات السوق بالذكاء الاصطناعي"""
    
    def __init__(self, api_key):
        """تهيئة محرك Gemini AI"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze(self, neg_text, category):
        """
        تحليل التقييمات السلبية واستخراج فجوات السوق
        
        Args:
            neg_text: نص التقييمات السلبية (1-2 نجمة)
            category: فئة السوق (مثل: fitness, food delivery)
        
        Returns:
            تقرير تحليلي بصيغة نصية
        """
        if not neg_text or not neg_text.strip():
            return "️ No negative reviews available for analysis."
        
        prompt = f"""You are a Senior Product Manager and Market Analyst.

I am planning to launch a new mobile app in the **{category}** market.
Below are real 1-star and 2-star reviews from competitor apps:

=== NEGATIVE REVIEWS ===
{neg_text}
=== END OF REVIEWS ===

Provide a concise, executive-level analysis in Markdown with these sections:

## 🐞 Top 3 Recurring Bugs / Complaints
- List the most frequent technical or usability issues

## 💡 Top 3 Missing Features Users Want
- List features users are asking for but competitors lack

##  Strategic Recommendations for Our New App
- Provide 3-5 actionable recommendations to capture market share

Be data-driven, concise, and professional. Use bullet points."""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1500
                )
            )
            return response.text
        except Exception as e:
            return f"❌ AI Analysis Error: {str(e)}\n\nPlease check your API key and try again."
    
    def analyze_multiple_apps(self, apps_reviews_dict, category):
        """
        تحليل عدة تطبيقات دفعة واحدة
        
        Args:
            apps_reviews_dict: قاموس {اسم_التطبيق: التقييمات_السلبية}
            category: فئة السوق
        
        Returns:
            قاموس يحتوي على نتائج كل تطبيق
        """
        results = {}
        
        for app_name, neg_text in apps_reviews_dict.items():
            results[app_name] = {
                'status': 'success',
                'analysis': self.analyze(neg_text, category)
            }
        
        return results