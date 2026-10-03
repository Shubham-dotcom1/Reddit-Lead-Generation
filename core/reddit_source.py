import os
import praw
from datetime import datetime, timezone, timedelta
from config import config

class RedditSource:
    def __init__(self):
        client_id = os.getenv("REDDIT_CLIENT_ID")
        self.use_mock = False
        if not client_id or client_id == "your_client_id_here":
            self.use_mock = True
        else:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT", "python:redditleadgen:v1.0")
            )
        self.target_subreddits = config.TARGET_SUBREDDITS
        self.keywords = config.INTENT_KEYWORDS
        self.days_back = config.DAYS_BACK

    def fetch_recent_posts(self):
        """
        Fetches recent posts from target subreddits that match any intent keyword.
        """
        if self.use_mock:
            print("[!] No Reddit API Key provided. Using MOCK Reddit data for testing.")
            return self._get_mock_data()
            
        print(f"[*] Fetching posts from subreddits: {', '.join(self.target_subreddits)}")
        posts_data = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.days_back)
        
        # Combine subreddits into one query string (e.g. SaaS+Entrepreneur)
        subreddits_str = "+".join(self.target_subreddits)
        
        try:
            subreddit = self.reddit.subreddit(subreddits_str)
            
            # For simplicity, we fetch 'new' posts and check if they match keywords
            # and are within our time window.
            for submission in subreddit.new(limit=200):
                post_time = datetime.fromtimestamp(submission.created_utc, timezone.utc)
                if post_time < cutoff_date:
                    continue  # Too old
                
                text = (submission.title + " " + submission.selftext).lower()
                
                # Check for keywords
                matched_keywords = [kw for kw in self.keywords if kw.lower() in text]
                
                if matched_keywords:
                    posts_data.append({
                        "id": submission.id,
                        "title": submission.title,
                        "text": submission.selftext,
                        "url": submission.url,
                        "author": str(submission.author) if submission.author else "deleted",
                        "created_utc": submission.created_utc,
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "matched_keywords": matched_keywords
                    })
            
            print(f"[*] Found {len(posts_data)} potential leads from Reddit.")
            return posts_data
            
        except Exception as e:
            print(f"[!] Error fetching from Reddit: {e}")
            return []

    def _get_mock_data(self):
        """Returns mock Reddit posts for testing without an API key."""
        now = datetime.now(timezone.utc).timestamp()
        return [
            {
                "id": "mock1",
                "title": "I need a CRM for my small business, any recommendations?",
                "text": "We are growing and looking for a good CRM tool that is easy to use.",
                "url": "https://reddit.com/r/SaaS/mock1",
                "author": "mock_user1",
                "created_utc": now - 3600,
                "score": 15,
                "num_comments": 8,
                "matched_keywords": ["need a", "recommendations", "what CRM"]
            },
            {
                "id": "mock2",
                "title": "What is the best way to learn React?",
                "text": "I want to become a web developer.",
                "url": "https://reddit.com/r/webdev/mock2",
                "author": "mock_user2",
                "created_utc": now - 7200,
                "score": 5,
                "num_comments": 2,
                "matched_keywords": []
            },
            {
                "id": "mock3",
                "title": "Seeking a web developer for a startup project",
                "text": "We are hiring! Looking for someone who knows Python and React.",
                "url": "https://reddit.com/r/startups/mock3",
                "author": "mock_user3",
                "created_utc": now - 86400,
                "score": 45,
                "num_comments": 12,
                "matched_keywords": ["seeking", "hiring", "looking for"]
            }
        ]
