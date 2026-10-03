import os
import csv
import requests

class CRMExport:
    def __init__(self, csv_path="data/leads.csv"):
        self.csv_path = csv_path
        self.webhook_url = os.getenv("CRM_WEBHOOK_URL")
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
    def export_to_csv(self, leads):
        """
        Exports leads to a CSV file. Overwrites or appends depending on setup, 
        here we overwrite with the latest run's leads for simplicity.
        """
        if not leads:
            return
            
        print(f"[*] Exporting {len(leads)} leads to CSV at {self.csv_path}...")
        
        keys = ["id", "lead_score", "title", "url", "author", "ai_confidence", "ai_reason", "matched_keywords"]
        
        file_exists = os.path.isfile(self.csv_path)
        
        with open(self.csv_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for lead in leads:
                ai_data = lead.get("ai_classification", {})
                writer.writerow({
                    "id": lead.get("id"),
                    "lead_score": lead.get("lead_score"),
                    "title": lead.get("title"),
                    "url": lead.get("url"),
                    "author": lead.get("author"),
                    "ai_confidence": ai_data.get("confidence"),
                    "ai_reason": ai_data.get("reason"),
                    "matched_keywords": ", ".join(lead.get("matched_keywords", []))
                })
                
    def push_to_webhook(self, leads):
        """
        Pushes new leads to a CRM webhook (e.g., Zapier, Make).
        """
        if not self.webhook_url:
            print("[-] No CRM_WEBHOOK_URL configured. Skipping webhook push.")
            return
            
        if not leads:
            return
            
        print(f"[*] Pushing {len(leads)} leads to CRM webhook...")
        
        for lead in leads:
            try:
                response = requests.post(self.webhook_url, json=lead)
                if response.status_code not in (200, 201):
                    print(f"[!] Webhook error for lead {lead.get('id')}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"[!] Exception pushing to webhook: {e}")
                
    def export_all(self, leads):
        self.export_to_csv(leads)
        self.push_to_webhook(leads)
