#!/usr/bin/env python3
"""Write operations for Google Sheets."""

import json
import sys
from pathlib import Path

import gspread

CONFIG_DIR = Path.home() / ".config" / "google-sheets"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "authorized_user.json"


def output_success(message: str) -> None:
    """Print successful JSON output and exit."""
    print(json.dumps({"success": True, "message": message}))
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


def set_cell(spreadsheet: str, sheet: str, cell: str, value: str) -> None:
    """Update a single cell."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        ws = ss.worksheet(sheet)
        ws.update_acell(cell, value)
        output_success(f"Cell {cell} updated.")
    except gspread.WorksheetNotFound:
        output_error(f"Worksheet not found: {sheet}")
    except Exception as e:
        output_error(f"Failed to update cell: {e}")


def set_range(spreadsheet: str, sheet: str, range_notation: str, json_data: str) -> None:
    """Update a range with values from JSON array."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        values = json.loads(json_data)
        if not isinstance(values, list):
            output_error("Data must be a 2D array (list of lists).")
    except json.JSONDecodeError as e:
        output_error(f"Invalid JSON: {e}")

    try:
        ws = ss.worksheet(sheet)
        ws.update(range_notation, values)
        output_success(f"Range {range_notation} updated.")
    except gspread.WorksheetNotFound:
        output_error(f"Worksheet not found: {sheet}")
    except Exception as e:
        output_error(f"Failed to update range: {e}")


def append_row(spreadsheet: str, sheet: str, json_array: str) -> None:
    """Append a row to the end of the sheet."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        values = json.loads(json_array)
        if not isinstance(values, list):
            output_error("Data must be an array.")
    except json.JSONDecodeError as e:
        output_error(f"Invalid JSON: {e}")

    try:
        ws = ss.worksheet(sheet)
        ws.append_row(values)
        output_success("Row appended.")
    except gspread.WorksheetNotFound:
        output_error(f"Worksheet not found: {sheet}")
    except Exception as e:
        output_error(f"Failed to append row: {e}")


def clear_range(spreadsheet: str, sheet: str, range_notation: str) -> None:
    """Clear values in a range."""
    gc = get_client()
    ss = open_spreadsheet(gc, spreadsheet)

    try:
        ws = ss.worksheet(sheet)
        ws.batch_clear([range_notation])
        output_success(f"Range {range_notation} cleared.")
    except gspread.WorksheetNotFound:
        output_error(f"Worksheet not found: {sheet}")
    except Exception as e:
        output_error(f"Failed to clear range: {e}")


def main() -> None:
    if len(sys.argv) < 2:
        output_error(
            "Usage: write_sheet.py <set-cell|set-range|append-row|clear-range> [args...]"
        )

    command = sys.argv[1]

    if command == "set-cell":
        if len(sys.argv) != 6:
            output_error(
                "Usage: write_sheet.py set-cell <spreadsheet> <sheet> <cell> <value>"
            )
        set_cell(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    elif command == "set-range":
        if len(sys.argv) != 6:
            output_error(
                "Usage: write_sheet.py set-range <spreadsheet> <sheet> <range> <json_data>"
            )
        set_range(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    elif command == "append-row":
        if len(sys.argv) != 5:
            output_error(
                "Usage: write_sheet.py append-row <spreadsheet> <sheet> <json_array>"
            )
        append_row(sys.argv[2], sys.argv[3], sys.argv[4])

    elif command == "clear-range":
        if len(sys.argv) != 5:
            output_error(
                "Usage: write_sheet.py clear-range <spreadsheet> <sheet> <range>"
            )
        clear_range(sys.argv[2], sys.argv[3], sys.argv[4])

    else:
        output_error(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
