
"""FISHI Reddit Google Sheets connector.

Read-only functions for checking existing publications.
"""

PUBLICATIONS_TAB = "Publications"


def get_existing_publication_ids(service, spreadsheet_id):
    """Read existing publication IDs without changing the sheet."""

    sheet = service.spreadsheets().values()

    response = sheet.get(
        spreadsheetId=spreadsheet_id,
        range=f"'{PUBLICATIONS_TAB}'!A1:H",
    ).execute()

    rows = response.get("values", [])

    if not rows:
        raise ValueError("Publications sheet is empty or missing.")

    expected_headers = [
        "publication_id",
        "plan_id",
        "asset_id",
        "account_id",
        "destination_id",
        "published_datetime",
        "post_url",
        "platform_post_id",
    ]

    if rows[0][:8] != expected_headers:
        raise ValueError(
            "Publications headers do not match expected schema."
        )

    existing_ids = set()

    for row in rows[1:]:
        if row and row[0]:
            existing_ids.add(str(row[0]).strip())

    return existing_ids
