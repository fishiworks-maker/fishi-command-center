
"""FISHI Command Center — Reddit historical importer."""

def reddit_publication_id(post_id):
    """Return a stable ID for a Reddit publication."""
    post_id = str(post_id).strip().lower()

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
