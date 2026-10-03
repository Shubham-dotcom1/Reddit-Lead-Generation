import os
import argparse
from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

from core.reddit_source import RedditSource
from core.classifier import AIClassifier
from core.lead_scorer import LeadScorer
from adapters.enrichment import EnrichmentService
from adapters.lead_db import LeadDatabase
from adapters.crm_export import CRMExport

def parse_args():
    parser = argparse.ArgumentParser(description="Reddit Lead Generation Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Collect, classify and score leads, but don't save to DB or export to CRM.")
    parser.add_argument("--top", type=int, default=10, help="Number of top leads to print in the summary.")
    return parser.parse_args()

def main():
    args = parse_args()
    
    print("=======================================")
    print("      Reddit Lead Gen Pipeline     ")
    print("=======================================")
    
    if args.dry_run:
        print("[!] DRY RUN ENABLED - No data will be written to DB or CRM")
    
    # 1. Search & Discover
    reddit = RedditSource()
    raw_posts = reddit.fetch_recent_posts()
    
    if not raw_posts:
        print("[-] No posts found matching criteria. Exiting.")
        return
        
    # 2. AI Classification
    classifier = AIClassifier()
    classified_posts = classifier.batch_classify(raw_posts)
    
    # 3. Lead Scoring
    scorer = LeadScorer()
    scored_leads = scorer.score_leads(classified_posts)
    
    if not scored_leads:
        print("[-] No leads passed the AI confidence and scoring bar. Exiting.")
        return
        
    print(f"[*] Pipeline generated {len(scored_leads)} high-quality leads.")
    
    # 4. Enrichment
    enrichment = EnrichmentService()
    enriched_leads = enrichment.enrich_batch(scored_leads)
    
    # 5. DB & CRM Export
    if not args.dry_run:
        db = LeadDatabase()
        db.save_leads(enriched_leads)
        db.close()
        
        crm = CRMExport()
        crm.export_all(enriched_leads)
    
    # Summary
    print("\n=======================================")
    print(f"      TOP {min(args.top, len(enriched_leads))} LEADS")
    print("=======================================")
    for idx, lead in enumerate(enriched_leads[:args.top], 1):
        score = lead.get("lead_score")
        title = lead.get("title")
        reason = lead.get("ai_classification", {}).get("reason", "")
        url = lead.get("url")
        print(f"{idx}. [Score: {score}] {title}")
        print(f"   Why: {reason}")
        print(f"   URL: {url}")
        print("-" * 40)
        
if __name__ == "__main__":
    main()
