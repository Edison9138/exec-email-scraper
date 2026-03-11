# Executive Email Scraper

Finds executive contact emails (CEO, CFO, CTO, etc.) from company websites for non-profit sponsorship outreach. Uses the Hunter.io API.

## Quick Start

1. **Install uv** – [Install uv](https://docs.astral.sh/uv/getting-started/installation/) (a fast Python package manager). uv will use Python 3.12+ automatically.
2. **Open a terminal** in this project folder.
3. **Run this command** (copy and paste):

```bash
uv sync
```

This creates a virtual environment and installs dependencies.

4. **Get a Hunter.io API key** – Sign up at [hunter.io](https://hunter.io/), then go to [API settings](https://hunter.io/api_keys) to copy your key.

5. **Create a `.env` file** – Duplicate `.env.example` and rename the copy to `.env`. Open `.env` and replace the placeholder with your API key(s):

```
HUNTER_API_KEY=your_key_here
HUNTER_API_KEY=backup_key_1
HUNTER_API_KEY=backup_key_2
```

You can list multiple keys. When one hits the rate limit, the scraper switches to the next automatically.

6. **Add companies** – Edit `companies.txt` and add company domains, one per line. Use `## Name` to group by team member. You can use `@domain.com`, full URLs, or plain `domain.com`—all work.

```
## Wesley
@dangfoods.com
https://www.michelesgranola.com/
stripe.com

## Clarisse
@hormel.com
https://tillamook.com/
```

7. **Run the scraper**:

```bash
uv run scraper.py
```

Results are saved to `executive_emails.xlsx` when all companies are done.

---

## Output

The scraper creates `executive_emails.xlsx` with two sheets:

- **Executive Emails** – Found contacts (domain, company, email, name, position, etc.)
- **No Results** – Companies where no executive emails were found

Progress is saved every 10 companies. If you stop the script or hit a rate limit, run it again—it will skip completed companies and continue.

---

## Troubleshooting

| Problem                        | Solution                                                                                  |
| ------------------------------ | ----------------------------------------------------------------------------------------- |
| "HUNTER_API_KEY not found"     | Create a `.env` file in the project folder with your API key.                             |
| "No results found"             | The company may not be in Hunter.io's database. Try the main domain (e.g. `company.com`). |
| Rate limit / too many requests | Add more API keys to `.env`. The scraper will switch to the next key automatically.       |
| Command not found              | Make sure uv is installed. Run `uv run scraper.py` (no need to activate anything).        |

---

## Hunter.io Limits

Free tier: 25 domain searches per month per API key. Add more keys in `.env` to increase capacity.

---

## Legal & Ethical Use

Use only for legitimate non-profit outreach. Respect opt-out requests and follow CAN-SPAM and GDPR guidelines. Do not send spam or sell the data.
