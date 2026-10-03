import sqlite3
import os
import json

class LeadDatabase:
    def __init__(self, db_path="data/leads.db"):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()
        
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                title TEXT,
                url TEXT,
                author TEXT,
                lead_score REAL,
                ai_confidence REAL,
                ai_reason TEXT,
                created_utc INTEGER,
                enriched_company TEXT,
                enriched_contact TEXT,
                raw_data TEXT
            )
        ''')
        self.conn.commit()
        
    def save_leads(self, leads):
        """
        Saves a batch of leads to the database. Uses OR IGNORE to prevent duplicates.
        """
        print(f"[*] Saving {len(leads)} leads to database...")
        cursor = self.conn.cursor()
        saved_count = 0
        
        for lead in leads:
            ai_data = lead.get("ai_classification", {})
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO leads (
                        id, title, url, author, lead_score, ai_confidence, ai_reason, 
                        created_utc, enriched_company, enriched_contact, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    lead.get("id"),
                    lead.get("title"),
                    lead.get("url"),
                    lead.get("author"),
                    lead.get("lead_score"),
                    ai_data.get("confidence"),
                    ai_data.get("reason"),
                    lead.get("created_utc"),
                    lead.get("enriched_company"),
                    lead.get("enriched_contact"),
                    json.dumps(lead)
                ))
                if cursor.rowcount > 0:
                    saved_count += 1
            except Exception as e:
                print(f"[!] Error saving lead {lead.get('id')}: {e}")
                
        self.conn.commit()
        print(f"[*] Successfully added {saved_count} new leads to DB.")
        
    def get_top_leads(self, limit=25):
        """
        Fetches the top leads from the database ordered by score.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT title, url, lead_score, ai_reason FROM leads ORDER BY lead_score DESC LIMIT ?', (limit,))
        return cursor.fetchall()
        
    def close(self):
        self.conn.close()
