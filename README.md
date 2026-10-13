# FISHI WORKS Command Center

Private, read-only social media analytics for original creative projects (AIKO, Fishy Observatory, Crimson Harbor). This repository contains a Python starter importer for authorized Reddit API access, a sample-data test, and an export format designed for a future Google Sheets sync.

## Status

**Under development.** Reddit API access has been requested; this project does not assume approval. It does not post, vote, comment, message, or moderate. No credentials or private analytics are stored in the repository.

## Quick test (no API keys needed)

1. Open the repository in GitHub and select **Actions**.
2. Run **FISHI sample importer test** using **Run workflow**, or wait for the workflow to run automatically on a push.
3. Download the `fishi-sample-export` artifact. It contains `publications.csv` and `metrics.csv` generated from fictional sample data.

To run locally (Python 3.11+):

```bash
python -m unittest discover -s tests -v
python -m src.fishi.cli --sample --output-dir output
```

## Authorized Reddit import (after approval)

This initial implementation uses OAuth client credentials for reading publicly accessible post listings. Whether this is permitted for your use case depends on Reddit's approval and app configuration. Never attempt to bypass an API denial. Supply environment variables `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and `REDDIT_USER_AGENT` (a descriptive user agent identifying the application and contact). Do not commit secrets. Run:

```bash
python -m src.fishi.cli --reddit-user FISHI_WORKS --output-dir output
```

The importer respects rate limits and transient errors; it will stop on authentication or permission errors. The initial import reads up to 100 recent submissions per account. Pagination and historical reconciliation can be added after access approval and testing.

## Data model

- `publications.csv`: unique Reddit post IDs, account, subreddit, timestamps, URL, original/crosspost classification, title, source reference.
- `metrics.csv`: timestamped cumulative score and comment count; other platform-specific metrics are intentionally blank unless supplied by an authorized source.

The same post ID can be refreshed over time without duplicating the publication record; metric snapshots are separate observations, not additive totals. No fabricated 24-hour or 7-day history.

## Next phases

1. Confirm Reddit API approval and permitted endpoints.
2. Create/verify the native Google Sheet and connect a restricted Google service account or authorized OAuth flow.
3. Upsert publication records and append metric snapshots safely.
4. Add legacy accounts, import staging and audit logs.
5. Connect Looker Studio and additional platforms.

## Security

Never put OAuth tokens, client secrets, service account JSON, or personal data in GitHub source code, issue comments, or Google Sheets. Use GitHub Actions Secrets for automation after authorization. No automated Reddit interaction.
