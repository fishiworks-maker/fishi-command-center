
"""FISHI Command Center — Reddit historical importer."""

def reddit_publication_id(post_id):
    """Return a stable ID for a Reddit publication."""
    post_id = str(post_id).strip().lower()
    post_id = post_id.removeprefix("t3_")

    if not post_id:
        raise ValueError("Reddit post ID cannot be empty")

    return f"REDDIT_{post_id}"


def is_existing_publication(post_id, existing_ids):
    """Check whether this Reddit post is already registered."""
    publication_id = reddit_publication_id(post_id)
    return publication_id in existing_ids



def metrics_changed(new_metrics, previous_metrics):
    """Check whether any available Reddit metric has changed.

    Missing values are ignored, not treated as zero.
    """
    if previous_metrics is None:
        return True

    for field in ("views", "score", "comments"):
        new_value = new_metrics.get(field)

        if new_value is None or new_value == "":
            continue

        old_value = previous_metrics.get(field)

        if old_value is None or old_value == "":
            return True

        if int(new_value) != int(old_value):
            return True

    return False


def is_reddit_post(record):
    """Accept Reddit posts (t3), but reject comments (t1)."""

    reddit_type = str(
        record.get("type")
        or record.get("kind")
        or record.get("id")
        or ""
    ).strip().lower()

    return reddit_type == "t3" or reddit_type.startswith("t3_")


def preview_reddit_csv(csv_path):
    """Read a Reddit Exporter CSV without changing any data."""
    import csv

    posts = []
    comments_skipped = 0

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required = {
            "kind", "id", "author", "subreddit",
            "permalink", "created_utc", "title",
            "score", "num_comments",
        }

        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Missing CSV columns: {sorted(missing)}"
            )

        for row in reader:
            if not is_reddit_post(row):
                comments_skipped += 1
                continue

            post_id = row["id"].strip()
            if not post_id:
                raise ValueError("Post has no Reddit ID")

            permalink = row["permalink"].strip()

            posts.append({
                "publication_id": reddit_publication_id(post_id),
                "platform_post_id": post_id,
                "author": row["author"].strip(),
                "subreddit": row["subreddit"].strip(),
                "post_url": (
                    "https://www.reddit.com" + permalink
                    if permalink.startswith("/")
                    else permalink
                ),
                "published_utc": row["created_utc"].strip(),
                "title": row["title"].strip(),
                "score": row["score"].strip(),
                "comments": row["num_comments"].strip(),
            })

    return posts, comments_skipped


def dry_run_reddit_import(csv_path, existing_ids=None, destinations=None):
    """Preview a Reddit CSV import. Never writes to Google Sheets."""
    posts, skipped_comments = preview_reddit_csv(csv_path)

    existing_ids = set(existing_ids or [])
    destinations = dict(destinations or {})

    seen_ids = set()
    ready = []
    issues = []
    duplicates = []

    for post in posts:
        publication_id = post["publication_id"]
        subreddit = post["subreddit"].strip()

        if publication_id in seen_ids or publication_id in existing_ids:
            duplicates.append(publication_id)
            continue

        seen_ids.add(publication_id)

        if post["author"].lower() != "fishi_works":
            issues.append((publication_id, "Unexpected author"))
            continue

        if subreddit.lower() == "u_fishi_works":
            destination_id = "REDDIT_PROFILE_FISHI_WORKS"
        else:
            destination_id = destinations.get(subreddit.lower())

        if not destination_id:
            issues.append((publication_id, f"Unmatched destination: {subreddit}"))
            continue

        ready.append({
            **post,
            "account_id": "REDDIT_FISHI_WORKS",
            "destination_id": destination_id,
        })

    
    print("\n=== FISHI REDDIT IMPORT PREVIEW ===")
    print(f"Posts found:       {len(posts)}")
    print(f"Comments skipped:  {skipped_comments}")
    print(f"Ready to import:   {len(ready)}")
    print(f"Duplicates:        {len(duplicates)}")
    print(f"Issues:            {len(issues)}")

    for publication_id, reason in issues:
        print(f"ISSUE: {publication_id} - {reason}")

    print("DRY RUN ONLY - NO DATA WRITTEN")
    return ready, issues, duplicates
