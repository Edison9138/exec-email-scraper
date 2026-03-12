# Executive Email Scraper

Finds executive contact emails (CEO, CFO, CTO, etc.) from company websites for non-profit sponsorship outreach. Uses the Hunter.io API.

## Setup

You can set up the project automatically or manually.

### Automated Setup (Recommended)

If you have minimal coding experience, you can use the automated setup scripts from your terminal!

1. Open a terminal in the project folder.
2. Run `./setup.sh` to install dependencies and create your settings file.

### Manual Setup (Skip this if you followed the Automated Setup above)

If you prefer to set up the scraper manually from the command line:

1. **Install uv** – [Install uv](https://docs.astral.sh/uv/getting-started/installation/) (a fast Python package manager). _uv will use Python 3.12+ automatically._
2. **Open a terminal** in this project folder.
3. **Install dependencies** by running:

```bash
uv sync
```

4. Duplicate `.env.example` and rename the copy to `.env`.

---

## Configuration

Before running the scraper, you need to configure your API key and company targets.

### 1. Get a Hunter.io API key

Sign up at [hunter.io](https://hunter.io/), then go to [API settings](https://hunter.io/api_keys) to copy your key.

### 2. Set up your `.env` file

Open the `.env` file that was generated in the previous setup step. Replace the placeholder with your API key(s):

```text
HUNTER_API_KEY=your_key_here
HUNTER_API_KEY=backup_key_1
HUNTER_API_KEY=backup_key_2
```

_Note: You can list multiple keys. When one hits the rate limit, the scraper switches to the next automatically._

### 3. Add Companies

Edit `companies.txt` and add company domains, one per line. Use `## Name` to group by team member. You can use `@domain.com`, full URLs, or plain `domain.com`—all work.

```text
## Wesley
@dangfoods.com
https://www.michelesgranola.com/
stripe.com

## Clarisse
@hormel.com
https://tillamook.com/
```

---

## Running the Scraper

Once your `.env` and `companies.txt` are configured, you are ready to start scraping!

### Automated (If you used Automated Setup):

Run the run script in your terminal:

```bash
./run.sh
```

### Manual (If you used Manual Setup):

Run the python script using uv:

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

## Understanding Retry & Error Messages

When scanning domains, you may see various messages in your terminal. Here's what they mean and what you should do:

| Message printed in terminal                                                     | What it means                                                                                          | What you should do                                                                                                                                           |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Rate limit hit (HTTP 429). Retrying in 5s (attempt 1/3)...`                    | The API received too many requests too quickly. The scraper is automatically pausing and trying again. | **Nothing.** The scraper handles this automatically via exponential backoff.                                                                                 |
| `Rate limit hit. Switching to backup API key 2 of 3...`                         | The current API key exhausted its monthly limit or strict rate limit.                                  | **Nothing.** The scraper automatically switches to your next key.                                                                                            |
| `Rate limit exceeded for [domain]. Please wait or upgrade your Hunter.io plan.` | All provided API keys have exhausted their limits.                                                     | Add more `HUNTER_API_KEY`s to your `.env` file and **run the script again**. The scraper automatically saves its progress and will resume where it left off! |
| `Request timeout for [domain]. Retrying...`                                     | Hunter.io didn't respond in time.                                                                      | **Nothing.** The scraper will retry automatically.                                                                                                           |
| `Error: Invalid API key. Check your HUNTER_API_KEY in .env file.`               | An API key is unauthorized or incorrect.                                                               | Check your Hunter API dashboard and ensure you copied the key exactly into `.env`.                                                                           |
| `Error: Failed to fetch [domain] after 3 attempts`                              | A specific company could not be processed due to persistent network issues.                            | **Nothing.** The scraper will note this failure and move on. If you run the scraper again later, it will attempt to retry this domain.                       |

---

## Legal & Ethical Use

Use only for legitimate non-profit outreach. Respect opt-out requests and follow CAN-SPAM and GDPR guidelines. Do not send spam or sell the data.
