
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
