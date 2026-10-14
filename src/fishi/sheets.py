
"""Google Sheets staging connector for FISHI Command Center."""

import json

import google.auth
from googleapiclient.discovery import build


STAGING_TAB = "Import_Staging"

STAGING_HEADERS = [
    "staging_id",
    "batch_id",
    "external_post_id",
    "post_url",
    "published_at",
    "raw_caption",
    "raw_metrics",
    "matched_asset_id",
    "validation_status",
    "notes",
]


def connect():
    """Connect using Google Cloud's existing credentials."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=credentials)


def upload_to_staging(service, spreadsheet_id, records, batch_id):
    """Append new records, skipping existing staging IDs."""

    sheet = service.spreadsheets().values()

    response = sheet.get(
        spreadsheetId=spreadsheet_id,
        range=f"'{STAGING_TAB}'!A1:J",
    ).execute()

    rows = response.get("values", [])

    if not rows or rows[0] != STAGING_HEADERS:
        raise ValueError(
            "Import_Staging headers do not match expected schema."
        )

    existing_ids = {
        row[0] for row in rows[1:] if row and row[0]
    }

    new_rows = []
    seen_ids = set(existing_ids)

    for record in records:
        post_id = str(record["platform_post_id"])
        staging_id = f"FISHI_{batch_id}_{post_id}"

        if staging_id in seen_ids:
            continue

        seen_ids.add(staging_id)

        metrics = {
            "score": record.get("score", ""),
            "comments": record.get("comments", ""),
        }

        new_rows.append([
            staging_id,
            batch_id,
            post_id,
            record.get("post_url", ""),
            record.get("published_utc", ""),
            record.get("title", ""),
            json.dumps(metrics),
            "",
            "TEST",
            "Sample data only - not a real Reddit API import",
        ])

    if not new_rows:
        print("No new staging records. All IDs already exist.")
        return 0

    result = sheet.append(
        spreadsheetId=spreadsheet_id,
        range=f"'{STAGING_TAB}'!A:J",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": new_rows},
    ).execute()

    print(
        f"Uploaded {len(new_rows)} records to "
        f"{result['updates']['updatedRange']}"
    )

    return len(new_rows)
