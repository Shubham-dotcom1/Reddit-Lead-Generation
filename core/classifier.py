import os
import json
import google.generativeai as genai

class AIClassifier:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.use_mock = False
        if not api_key or api_key == "your_gemini_api_key_here":
            self.use_mock = True
        else:
            genai.configure(api_key=api_key)
            # Using gemini-pro (Gemini 1.5 Flash or Pro) for text classification
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def classify_intent(self, post):
        """
        Uses Gemini API to classify the buying intent of a Reddit post.
        Returns a dict with 'is_lead' (boolean) and 'confidence' (float 0.0-1.0)
        and 'reason' (string).
        """
        if self.use_mock:
            return self._mock_classify_intent(post)

        title = post.get("title", "")
        text = post.get("text", "")
        
        prompt = f"""
You are an expert sales AI. Your job is to analyze a Reddit post and determine if the author is showing "buying intent".
Buying intent means they are actively looking for a product, service, tool, or solution to a problem, or asking for recommendations.

Post Title: {title}
Post Body: {text}

Analyze the post and respond strictly in valid JSON format with no markdown formatting. The JSON should have these keys:
- "is_lead": true or false
- "confidence": a number between 0.0 and 1.0 representing how confident you are
- "reason": a short 1-sentence explanation of why it is or isn't a lead

Example response:
{{
  "is_lead": true,
  "confidence": 0.85,
  "reason": "The user is explicitly asking for CRM tool recommendations for their small business."
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up markdown if the model added it
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            result = json.loads(response_text)
            
            return {
                "is_lead": result.get("is_lead", False),
                "confidence": float(result.get("confidence", 0.0)),
                "reason": result.get("reason", "No reason provided.")
            }
            
        except Exception as e:
            print(f"[!] Error classifying post {post.get('id')}: {e}")
            # Fallback safe values if API fails
            return {
                "is_lead": False,
                "confidence": 0.0,
                "reason": "API error"
            }

    def batch_classify(self, posts):
        """
        Classify multiple posts.
        """
        print(f"[*] Classifying {len(posts)} posts with Gemini AI...")
        classified_posts = []
        for post in posts:
            classification = self.classify_intent(post)
            post["ai_classification"] = classification
            classified_posts.append(post)
            
        return classified_posts

    def _mock_classify_intent(self, post):
        """Returns mock classifications based on simple keyword heuristics."""
        title = post.get("title", "").lower()
        text = post.get("text", "").lower()
        content = title + " " + text
        
        if "need a crm" in content or "recommendations" in content:
            return {
                "is_lead": True,
                "confidence": 0.90,
                "reason": "(MOCK) User is explicitly asking for CRM recommendations."
            }
        elif "seeking" in content or "hiring" in content or "looking for" in content:
            return {
                "is_lead": True,
                "confidence": 0.85,
                "reason": "(MOCK) User is seeking to hire or looking for a service."
            }
        else:
            return {
                "is_lead": False,
                "confidence": 0.20,
                "reason": "(MOCK) Just a general discussion, no buying intent."
            }
