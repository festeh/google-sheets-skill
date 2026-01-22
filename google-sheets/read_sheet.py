#!/usr/bin/env python3
"""Read operations for Google Sheets."""

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


def get_cell(spreadsheet: str, sheet: str, cell: str) -> None:
    """Get a single cell value."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        ws = ss.worksheet(sheet)
        value = ws.acell(cell).value
        output_success(value)
    except gspread.WorksheetNotFound:
        output_error(f"Worksheet not found: {sheet}")
    except Exception as e:
        output_error(f"Failed to get cell: {e}")


def get_range(spreadsheet: str, sheet: str, range_notation: str) -> None:
    """Get values from a range."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        ws = ss.worksheet(sheet)
        values = ws.get(range_notation)
        output_success(values)
    except gspread.WorksheetNotFound:
        output_error(f"Worksheet not found: {sheet}")
    except Exception as e:
        output_error(f"Failed to get range: {e}")


def get_all(spreadsheet: str, sheet: str) -> None:
    """Get all values from a worksheet."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        ws = ss.worksheet(sheet)
        values = ws.get_all_values()
        output_success(values)
    except gspread.WorksheetNotFound:
        output_error(f"Worksheet not found: {sheet}")
    except Exception as e:
        output_error(f"Failed to get all values: {e}")


def list_sheets(spreadsheet: str) -> None:
    """List all worksheet names in a spreadsheet."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        sheets = [ws.title for ws in ss.worksheets()]
        output_success(sheets)
    except Exception as e:
        output_error(f"Failed to list sheets: {e}")


def main() -> None:
    if len(sys.argv) < 2:
        output_error(
            "Usage: read_sheet.py <get-cell|get-range|get-all|list-sheets> [args...]"
        )

    command = sys.argv[1]

    if command == "get-cell":
        if len(sys.argv) != 5:
            output_error("Usage: read_sheet.py get-cell <spreadsheet> <sheet> <cell>")
        get_cell(sys.argv[2], sys.argv[3], sys.argv[4])

    elif command == "get-range":
        if len(sys.argv) != 5:
            output_error("Usage: read_sheet.py get-range <spreadsheet> <sheet> <range>")
        get_range(sys.argv[2], sys.argv[3], sys.argv[4])

    elif command == "get-all":
        if len(sys.argv) != 4:
            output_error("Usage: read_sheet.py get-all <spreadsheet> <sheet>")
        get_all(sys.argv[2], sys.argv[3])

    elif command == "list-sheets":
        if len(sys.argv) != 3:
            output_error("Usage: read_sheet.py list-sheets <spreadsheet>")
        list_sheets(sys.argv[2])

    else:
        output_error(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
