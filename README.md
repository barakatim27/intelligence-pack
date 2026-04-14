# Intelligence Pack

Intelligence Pack is a lightweight Python pipeline that collects RSS news from tech, finance, and geopolitics sources, ranks stories by relevance, de-duplicates similar headlines, and emails a daily digest.

It is designed for people who want a focused morning brief without opening social platforms.

## What It Does

- Collects RSS items from curated source lists.
- Normalizes article fields (title, link, source, summary, publish time).
- Scores and ranks articles by category-specific keywords.
- Filters near-duplicate stories across outlets.
- Builds a compact digest across categories.
- Sends the digest by email (Gmail SMTP).

## Project Structure

```text
.
+- app.py                         # Entry point
+- scheduler/daily_job.py         # End-to-end orchestration
+- collectors/                    # RSS source configs + collection logic
+- parsers/article_parser.py      # Article normalization
+- ranking/importance_score.py    # Keyword scoring + ranking
+- summarizer/ai_digest.py        # Dedup + digest formatting
+- delivery/email_sender.py       # SMTP email delivery
+- .github/workflows/daily-news.yml  # Daily automation in GitHub Actions
```

## Requirements

- Python 3.13 (matches workflow config)
- A Gmail account with an App Password for SMTP

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=recipient@example.com
```

Notes:

- `SENDER_PASSWORD` should be a Gmail App Password, not your regular Gmail login password.
- `RECIPIENT_EMAIL` can be the same as `SENDER_EMAIL` if you want to email yourself.

## Run Locally

```bash
python app.py
```

This runs the full pipeline:

1. Collect articles from all configured feeds.
2. Parse and rank by relevance.
3. Build a de-duplicated digest.
4. Send email to `RECIPIENT_EMAIL`.

## GitHub Actions Automation

The workflow at `.github/workflows/daily-news.yml` is scheduled to run at:

- `03:00 UTC` daily (`06:00` Nairobi time)

To enable it:

1. Push this repository to GitHub.
2. Add repository secrets:
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECIPIENT_EMAIL`
3. Enable Actions and run once via `workflow_dispatch` to verify setup.

## Customization

### 1) Add or remove sources

Edit:

- `collectors/tech_sources.py`
- `collectors/finance_sources.py`
- `collectors/geo_sources.py`

Each file defines a dictionary of RSS feed names and URLs.

### 2) Tune ranking

Edit keyword lists in `ranking/importance_score.py` under `KEYWORDS`.

Current logic:

- +10 for each keyword match in title
- +5 if a publish date exists

### 3) Control digest diversity

Edit defaults in `summarizer/ai_digest.py`:

- `per_category` (default: 3)
- `max_per_source` (default: 1)

This helps prevent one outlet or one repeated story from dominating the digest.

## Troubleshooting

- No email received:
  - Verify `.env` values.
  - Confirm Gmail App Password is correct.
  - Check spam/promotions folder.
- Empty or weak digest:
  - Some feeds may be temporarily down.
  - Add more sources or relax keyword filters.
- GitHub Action fails:
  - Confirm all three repository secrets are set exactly.
  - Check Action logs for SMTP authentication errors.

## License

MIT License. See `LICENSE`.
