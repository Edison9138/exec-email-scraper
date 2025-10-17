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

### 1. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
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

Edit `.env` and add your API key:

```
HUNTER_API_KEY=your_actual_api_key_here
```

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
```

### Output

Results are saved to `executive_emails.xlsx` with two sheets:

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
- Automatic duplicate detection
- Append mode (new data added without overwriting)
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

scraper = EmailScraper(api_key='your_key')

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
- You've exceeded the free tier limit (25/month)
- Wait until next month or upgrade your Hunter.io plan

**Virtual environment issues**
- Make sure to activate the virtual environment before running the script
- Run `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)

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
