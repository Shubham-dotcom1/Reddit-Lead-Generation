# Reddit Lead Generation AI Pipeline 🚀

An automated Python pipeline that continuously monitors specific subreddits, extracts potential leads using AI-based intent classification, scores them based on engagement and recency, and exports the high-quality leads into a local SQLite database and CSV.

## Features
- **Reddit Integration:** Uses `PRAW` to fetch the latest posts from targeted subreddits based on intent keywords.
- **AI Classification:** Leverages Google's **Gemini 1.5 Flash** (via `google-generativeai`) to determine if a Reddit post shows genuine "buying intent".
- **Dynamic Lead Scoring:** Algorithmically scores leads (0-100) based on AI confidence, keyword matches, recency, and post engagement.
- **Data Persistence:** Saves deduplicated leads locally into an SQLite database (`data/leads.db`).
- **CRM Ready:** Generates an easy-to-import CSV (`data/leads.csv`) and supports Webhook integrations (Zapier/Make) for automatic CRM pushes.
- **Mock Mode:** Can run entirely on dummy data for testing purposes if API keys are not provided.

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd Reddit-automation
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup your Environment Variables:
   ```bash
   cp .env.example .env
   ```
   Fill in your `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and `GEMINI_API_KEY` in the `.env` file.

## Usage

**Run a Dry Run:**
Test the pipeline and view AI evaluations in the terminal without writing anything to the database:
```bash
python main.py --dry-run
```

**Run Production Mode:**
Execute the full pipeline to classify leads and save them to the database and CSV:
```bash
python main.py
```

## Project Structure
- `main.py` - Orchestrates the entire pipeline.
- `config.py` - Stores tunable parameters (target subreddits, keywords, weights).
- `core/` - Contains the primary logic for fetching data (`reddit_source.py`), AI classification (`classifier.py`), and scoring (`lead_scorer.py`).
- `adapters/` - Contains logic for data storage and export (`lead_db.py`, `crm_export.py`, `enrichment.py`).
