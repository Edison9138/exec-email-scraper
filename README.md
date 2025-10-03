# Executive Email Scraper

A Python tool to find executive contact information from company websites for non-profit sponsorship outreach. Uses the Hunter.io API to discover publicly available email addresses.

## Features

- 🎯 Finds executive emails (CEO, CFO, CTO, etc.) from company domains
- 📊 Exports results to CSV spreadsheet
- 🔍 Filters for executive-level positions automatically
- ✅ Includes confidence scores for each email
- 🚀 Easy to use - just add company domains

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Hunter.io API Key

1. Sign up for a free account at [Hunter.io](https://hunter.io/)
2. Free tier gives you 25 searches per month
3. Go to your [API settings](https://hunter.io/api_keys) to get your API key

### 3. Configure API Key

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
HUNTER_API_KEY=your_actual_api_key_here
```

## Usage

### Basic Usage

Edit the `domains` list in [scraper.py](scraper.py) (around line 168) with your target companies:

```python
domains = [
    'stripe.com',
    'salesforce.com',
    'microsoft.com',
    # Add your companies here
]
```

Then run:

```bash
python scraper.py
```

### Output

Results are saved to `executive_emails.csv` with the following columns:
- Domain
- Company
- Email
- First Name
- Last Name
- Position
- Department
- Confidence Score

### Example Output

```
Executive Email Scraper for Non-Profit Sponsorship
==================================================
Searching 3 companies...

Searching stripe.com...
  Found 5 executive email(s)
Searching salesforce.com...
  Found 3 executive email(s)

✓ Exported 8 emails to executive_emails.csv
```

## Advanced Usage

### Find Specific Person

```python
from scraper import EmailScraper

scraper = EmailScraper(api_key='your_key')
result = scraper.find_email('stripe.com', 'Patrick', 'Collison')
print(result)
```

### Search Specific Role

```python
scraper = EmailScraper(api_key='your_key')
result = scraper.search_domain('stripe.com', role='ceo')
```

### Include All Employees (Not Just Executives)

```python
results = scraper.scrape_companies(domains, executives_only=False)
```

## Legal & Ethical Considerations

This tool is designed for legitimate non-profit sponsorship outreach:

✅ **Do:**
- Use for legitimate business outreach
- Respect opt-out requests
- Follow CAN-SPAM Act and GDPR guidelines
- Only contact publicly listed emails
- Add unsubscribe options in your emails

❌ **Don't:**
- Send unsolicited spam
- Sell or share the collected data
- Ignore opt-out requests
- Scrape aggressively (respect rate limits)

## Hunter.io Free Tier Limits

- **25 requests per month**
- 50 email verifications per month
- Each domain search = 1 request

Tip: Be selective with your target companies to stay within limits.

## Troubleshooting

**"HUNTER_API_KEY not found"**
- Make sure you created a `.env` file with your API key

**"No results found"**
- The company may not be in Hunter.io's database
- Try the company's main domain (e.g., 'company.com' not 'www.company.com')

**Rate limit errors**
- You've exceeded the free tier limit (25/month)
- Wait until next month or upgrade your Hunter.io plan

## License

For non-profit sponsorship outreach use.
