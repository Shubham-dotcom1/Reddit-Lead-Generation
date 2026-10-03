import os
from dataclasses import dataclass

@dataclass
class PipelineConfig:
    # Target subreddits to monitor
    TARGET_SUBREDDITS = [
        "SaaS",
        "Entrepreneur",
        "smallbusiness",
        "startups",
        "webdev"
    ]

    # Keywords that suggest someone is looking for a service or tool
    INTENT_KEYWORDS = [
        "looking for",
        "need a",
        "recommendation",
        "recommendations",
        "can someone recommend",
        "how do i build",
        "need help building",
        "hiring",
        "seeking",
        "which tool",
        "what CRM"
    ]

    # Lead scoring weights (must sum to 1.0 ideally, but handled relatively)
    WEIGHT_AI_CONFIDENCE = 0.50
    WEIGHT_ENGAGEMENT = 0.15
    WEIGHT_RECENCY = 0.20
    WEIGHT_KEYWORD_STRENGTH = 0.15

    # Minimum AI confidence score to consider the post a valid lead (0.0 to 1.0)
    MIN_CONFIDENCE_TO_KEEP = 0.55

    # Batch size for processing posts with AI
    CLASSIFICATION_BATCH_SIZE = 10

    # How many days back to search in Reddit
    DAYS_BACK = 7

config = PipelineConfig()
