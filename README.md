# Executive Email Scraper

A Python tool to find executive contact information from company websites for non-profit sponsorship outreach. Uses the Hunter.io API to discover publicly available email addresses.

## Features

- Finds executive emails (CEO, CFO, CTO, etc.) from company domains
- Exports results to Excel with two sheets: successful finds and no-results tracking
- Filters for executive-level positions automatically
- Includes confidence scores for each email
- Tracks team member assignments
- Timestamps each scraping session
- Automatic duplicate detection and append mode
- Easy to use - just add company URLs to `companies.txt`

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for package management. Install uv if needed: <https://docs.astral.sh/uv/getting-started/installation/>.

### 1. Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment (uses Python from .python-version)
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. (Optional) Using pip instead of uv

If you prefer pip:

```bash
python3 -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Get Hunter.io API Key

1. Sign up for a free account at [Hunter.io](https://hunter.io/)
2. Free tier: 25 searches per month
3. Go to [API settings](https://hunter.io/api_keys) to get your API key

### 4. Configure API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your API key(s). You can list multiple keys for automatic rotation when rate limited:

```
# Primary key (active)
HUNTER_API_KEY=your_primary_key_here

# Backup keys (used automatically when rate limited - no need to manually switch)
# HUNTER_API_KEY=backup_key_1
# HUNTER_API_KEY=backup_key_2
```

When the primary key hits Hunter.io's rate limit, the scraper automatically switches to the next key and continues. No manual editing required.

## Usage

### Add Companies to Scrape

Edit `companies.txt` and add company URLs or domains, organized by team member:

```
## Wesley
https://dangfoods.com/

## Clarisse
https://www.michelesgranola.com/
```

Lines starting with `##` indicate team member names. The scraper automatically extracts clean domains from URLs.

### Run the Scraper

```bash
python scraper.py
# or with uv (no need to activate .venv):
uv run scraper.py
```

Progress is saved to a **checkpoint file** (`scraper_checkpoint.json`) every 10 companies. If you hit the Hunter.io rate limit:

- **Multiple keys in `.env`**: The scraper automatically switches to the next key and continues. No action needed.
- **Single key or all keys exhausted**: Run the script again after adding more keys or waiting. It will **skip** domains already scraped and continue with the rest.
- When **all** domains have been scraped, the script writes `executive_emails.xlsx` once from the checkpoint.

Optional env vars: `CHECKPOINT_FILE` (default `scraper_checkpoint.json`), `CHECKPOINT_SAVE_EVERY` (default `10`).

### Output

When scraping is complete, results are written to `executive_emails.xlsx` with two sheets:

**Sheet 1: "Executive Emails"**
- Domain, Company, Email, First Name, Last Name
- Position, Department, Confidence Score
- BP Member, Parse Date

**Sheet 2: "No Results"**
- Domain, Company, BP Member
- Reason (why no emails were found)
- Parse Date

Features:
- Styled headers with blue background
- Auto-sized columns
- Checkpoint/resume: progress in JSON; re-run to skip done domains and continue
- Excel generated only when all companies are scraped
- Smart filtering (companies with results won't appear in "No Results" sheet)

### Example Output

```
Executive Email Scraper for Non-Profit Sponsorship
==================================================
Loaded 44 entries, extracted 43 unique domains
Searching 43 companies...

Searching dangfoods.com...
  Found 3 executive email(s)
Searching justins.com...
  No executive emails found

✓ 15 emails added, 5 no-result companies added to executive_emails.xlsx (0 duplicates skipped)
```

## Advanced Usage

You can use the `EmailScraper` class programmatically:

```python
from scraper import EmailScraper

scraper = EmailScraper(api_keys=['your_key'])  # or multiple: api_keys=['key1', 'key2']

# Find a specific person
result = scraper.find_email('stripe.com', 'Patrick', 'Collison')

# Search for a specific role
result = scraper.search_domain('stripe.com', role='ceo')

# Include all employees (not just executives)
results = scraper.scrape_companies(domains, executives_only=False)
```

## Hunter.io Free Tier Limits

- 25 domain searches per month
- 50 email verifications per month
- Each domain search = 1 request

Be selective with target companies to stay within limits.

## Troubleshooting

**"HUNTER_API_KEY not found"**
- Ensure you created a `.env` file with your API key
- Check the `.env` file is in the project root directory

**"No results found"**
- The company may not be in Hunter.io's database
- Try the main domain (e.g., `company.com` not `www.company.com`)

**Rate limit errors**
- Add multiple API keys to `.env` (commented or uncommented) for automatic rotation when one key is exhausted
- You've exceeded the free tier limit (25/month per key)
- Wait until next month or upgrade your Hunter.io plan

**Virtual environment issues**
- Make sure to activate the virtual environment before running the script
- Run `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)

## Legal & Ethical Use

This tool is designed for legitimate non-profit sponsorship outreach:

Do:
- Use for legitimate business outreach
- Respect opt-out requests
- Follow CAN-SPAM Act and GDPR guidelines
- Only contact publicly listed emails
- Include unsubscribe options in your emails

Don't:
- Send unsolicited spam
- Sell or share the collected data
- Ignore opt-out requests
- Scrape aggressively (respect rate limits)

## License

For non-profit sponsorship outreach use.
