# intelligence-pack
An application that aggregates tech, financial and geopolitical news. It then sends them directly to my inbox. It a personal project so that I don't have to use social media.

## GitHub Actions schedule

This project can run automatically every morning with GitHub Actions.

The workflow file is at `.github/workflows/daily-news.yml` and is scheduled for `03:00 UTC`, which is `06:00` in Nairobi.

Add these repository secrets in GitHub before enabling the workflow:

- `SENDER_EMAIL`
- `SENDER_PASSWORD`
- `RECIPIENT_EMAIL`

If you use Gmail for sending, `SENDER_PASSWORD` should be a Gmail App Password.
