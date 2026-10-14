
"""FISHI Command Center - Import Validation v1.0."""

from datetime import datetime


def validate_record(record):
    """Check one imported record without changing it."""

    issues = []

    # Every imported post needs a unique ID.
    post_id = str(record.get("platform_post_id") or "").strip()

    if not post_id:
        issues.append("Missing platform post ID")

    # Check publication date.
    published_at = record.get("published_utc")

    if not published_at:
        issues.append("Missing publication date")
    else:
        try:
            datetime.fromisoformat(
                str(published_at).replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            issues.append("Invalid publication date")

    # We need a title or caption.
    title = str(record.get("title") or "").strip()

    if not title:
        issues.append("Missing title or caption")

    # A post without a URL needs manual review.
    post_url = str(record.get("post_url") or "").strip()

    if not post_url:
        issues.append("Missing post URL")
    elif not post_url.startswith(("https://", "http://")):
        issues.append("Invalid post URL")

    # Metrics must be valid numbers when supplied.
    for field in ("score", "comments"):
        value = record.get(field, "")

        if value is not None and value != "":
            try:
                number = int(value)
                if number < 0 and field == "comments":
                    issues.append("Negative comment count")
            except (ValueError, TypeError):
                issues.append(f"Invalid {field} metric")

    # Samples are always kept separate from real data.
    if record.get("is_sample", False):
        return "TEST", issues

    if issues:
        return "REVIEW", issues

    return "VALID", []


def validate_batch(records):
    """Validate a complete batch and summarize results."""

    results = []
    counts = {"VALID": 0, "REVIEW": 0, "TEST": 0}

    for record in records:
        status, issues = validate_record(record)

        results.append({
            "record": record,
            "status": status,
            "issues": issues,
        })

        counts[status] += 1

    return results, counts
