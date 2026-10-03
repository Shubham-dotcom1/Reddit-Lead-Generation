from datetime import datetime, timezone
from config import config

class LeadScorer:
    def __init__(self):
        self.w_ai = config.WEIGHT_AI_CONFIDENCE
        self.w_eng = config.WEIGHT_ENGAGEMENT
        self.w_rec = config.WEIGHT_RECENCY
        self.w_kw = config.WEIGHT_KEYWORD_STRENGTH
        self.min_confidence = config.MIN_CONFIDENCE_TO_KEEP
        
    def score_post(self, post):
        """
        Calculates a final Lead Score (0 to 100) based on AI confidence, engagement,
        recency, and keywords matched.
        """
        ai_data = post.get("ai_classification", {})
        
        # 1. AI Confidence (0.0 to 1.0)
        confidence = ai_data.get("confidence", 0.0)
        
        # If AI doesn't think it's a lead or confidence is too low, score is 0
        if not ai_data.get("is_lead") or confidence < self.min_confidence:
            return 0
            
        # 2. Engagement score (normalize upvotes and comments)
        # Cap at 50 upvotes/comments for normalization to prevent huge numbers skewing it
        score = post.get("score", 0)
        comments = post.get("num_comments", 0)
        engagement_val = min((score + comments) / 50.0, 1.0)
        
        # 3. Recency score (newer is better)
        created_time = datetime.fromtimestamp(post.get("created_utc", 0), timezone.utc)
        age_days = (datetime.now(timezone.utc) - created_time).days
        # If 0 days old -> 1.0, if config.DAYS_BACK old -> 0.0
        recency_val = max(0.0, 1.0 - (age_days / max(config.DAYS_BACK, 1)))
        
        # 4. Keyword Strength
        matched_keywords = post.get("matched_keywords", [])
        # More keywords matched = higher score, cap at 3
        kw_val = min(len(matched_keywords) / 3.0, 1.0)
        
        # Calculate weighted sum
        total_score = (
            (confidence * self.w_ai) +
            (engagement_val * self.w_eng) +
            (recency_val * self.w_rec) +
            (kw_val * self.w_kw)
        )
        
        # Normalize to 0-100 scale based on sum of weights
        total_weights = self.w_ai + self.w_eng + self.w_rec + self.w_kw
        final_score_100 = (total_score / total_weights) * 100
        
        return round(final_score_100, 2)

    def score_leads(self, posts):
        """
        Scores a batch of classified posts and filters out non-leads.
        """
        print("[*] Scoring leads...")
        scored_leads = []
        for post in posts:
            score = self.score_post(post)
            if score > 0:
                post["lead_score"] = score
                scored_leads.append(post)
                
        # Sort leads by highest score first
        scored_leads.sort(key=lambda x: x.get("lead_score", 0), reverse=True)
        return scored_leads
