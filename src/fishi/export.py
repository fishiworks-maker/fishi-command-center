"""Convert Reddit submissions into stable, auditable CSV exports."""
import csv
from datetime import datetime, timezone
from pathlib import Path

PUBLICATION_FIELDS = ["publication_id", "platform", "account", "platform_post_id", "published_utc", "subreddit", "post_url", "title", "publication_type", "source_post_id", "record_origin"]
METRIC_FIELDS = ["publication_id", "captured_utc", "score", "comments", "data_source", "metric_period"]


def transform(posts, account, captured_at=None):
    captured_at = captured_at or datetime.now(timezone.utc).isoformat()
    publications, metrics = [], []
    for post in posts:
        post_id = post["id"]
        publication_id = f"reddit:t3_{post_id}"
        source_id = post.get("crosspost_parent") or ""
        permalink = post.get("permalink", "")
        publications.append({
            "publication_id": publication_id, "platform": "reddit", "account": account,
            "platform_post_id": f"t3_{post_id}",
            "published_utc": datetime.fromtimestamp(post["created_utc"], timezone.utc).isoformat(),
            "subreddit": post.get("subreddit", ""),
            "post_url": f"https://www.reddit.com{permalink}" if permalink.startswith("/") else permalink,
            "title": post.get("title", ""),
            "publication_type": "crosspost" if source_id else "original_or_repost_unverified",
            "source_post_id": source_id, "record_origin": "reddit_api",
        })
        metrics.append({"publication_id": publication_id, "captured_utc": captured_at,
                        "score": post.get("score", ""), "comments": post.get("num_comments", ""),
                        "data_source": "reddit_api", "metric_period": "cumulative_at_capture"})
    return publications, metrics


def write_csv(directory, publications, metrics):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for filename, fields, rows in (("publications.csv", PUBLICATION_FIELDS, publications), ("metrics.csv", METRIC_FIELDS, metrics)):
        with (directory / filename).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
