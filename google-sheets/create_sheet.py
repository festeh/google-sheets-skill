#!/usr/bin/env python3
"""Create operations for Google Sheets."""

import json
import sys
from pathlib import Path

import gspread

CONFIG_DIR = Path.home() / ".config" / "google-sheets"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "authorized_user.json"


def output_success(data) -> None:
    """Print successful JSON output and exit."""
    print(json.dumps({"success": True, "data": data}))
    sys.exit(0)


def output_error(message: str) -> None:
    """Print error JSON output and exit."""
    print(json.dumps({"success": False, "error": message}))
    sys.exit(1)


def get_client() -> gspread.Client:
    """Get authenticated gspread client."""
    if not TOKEN_FILE.exists():
        output_error("Not authenticated. Run 'auth.py setup' first.")

    try:
        return gspread.oauth(
            credentials_filename=str(CREDENTIALS_FILE),
            authorized_user_filename=str(TOKEN_FILE),
        )
    except Exception as e:
        output_error(f"Authentication failed: {e}")


def open_spreadsheet(gc: gspread.Client, spreadsheet: str) -> gspread.Spreadsheet:
    """Open a spreadsheet by ID or URL."""
    try:
        if spreadsheet.startswith("http"):
            return gc.open_by_url(spreadsheet)
        else:
            return gc.open_by_key(spreadsheet)
    except gspread.SpreadsheetNotFound:
        output_error(f"Spreadsheet not found: {spreadsheet}")
    except gspread.exceptions.APIError as e:
        output_error(f"API error: {e}")


def create(title: str) -> None:
    """Create a new spreadsheet."""
    gc = get_client()

    try:
        ss = gc.create(title)
        output_success({
            "spreadsheet_id": ss.id,
            "url": ss.url,
            "title": ss.title,
        })
    except Exception as e:
        output_error(f"Failed to create spreadsheet: {e}")


def add_worksheet(spreadsheet: str, title: str, rows: int = 1000, cols: int = 26) -> None:
    """Add a new worksheet to an existing spreadsheet."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        ws = ss.add_worksheet(title=title, rows=rows, cols=cols)
        output_success({
            "worksheet_title": ws.title,
            "rows": rows,
            "cols": cols,
        })
    except Exception as e:
        output_error(f"Failed to add worksheet: {e}")


def delete_worksheet(spreadsheet: str, title: str) -> None:
    """Delete a worksheet from a spreadsheet."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        ws = ss.worksheet(title)
        ss.del_worksheet(ws)
        output_success({"deleted": title})
    except gspread.WorksheetNotFound:
        output_error(f"Worksheet not found: {title}")
    except Exception as e:
        output_error(f"Failed to delete worksheet: {e}")


def share(spreadsheet: str, email: str, role: str = "writer") -> None:
    """Share a spreadsheet with a user."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    if role not in ("reader", "writer"):
        output_error("Role must be 'reader' or 'writer'.")

    try:
        ss.share(email, perm_type="user", role=role)
        output_success({"shared_with": email, "role": role})
    except Exception as e:
        output_error(f"Failed to share spreadsheet: {e}")


def main() -> None:
    if len(sys.argv) < 2:
        output_error(
            "Usage: create_sheet.py <create|add-worksheet|delete-worksheet|share> [args...]"
        )

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) != 3:
            output_error("Usage: create_sheet.py create <title>")
        create(sys.argv[2])

    elif command == "add-worksheet":
        if len(sys.argv) < 4 or len(sys.argv) > 6:
            output_error(
                "Usage: create_sheet.py add-worksheet <spreadsheet> <title> [rows] [cols]"
            )
        rows = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
        cols = int(sys.argv[5]) if len(sys.argv) > 5 else 26
        add_worksheet(sys.argv[2], sys.argv[3], rows, cols)

    elif command == "delete-worksheet":
        if len(sys.argv) != 4:
            output_error(
                "Usage: create_sheet.py delete-worksheet <spreadsheet> <title>"
            )
        delete_worksheet(sys.argv[2], sys.argv[3])

    elif command == "share":
        if len(sys.argv) < 4 or len(sys.argv) > 5:
            output_error(
                "Usage: create_sheet.py share <spreadsheet> <email> [role]"
            )
        role = sys.argv[4] if len(sys.argv) > 4 else "writer"
        share(sys.argv[2], sys.argv[3], role)

    else:
        output_error(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
