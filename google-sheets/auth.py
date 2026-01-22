#!/usr/bin/env python3
"""OAuth authentication management for Google Sheets."""

import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "google-sheets"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "authorized_user.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def output(status: str, message: str) -> None:
    """Print JSON output and exit."""
    print(json.dumps({"status": status, "message": message}))
    sys.exit(0 if status == "success" else 1)


def setup() -> None:
    """Run OAuth flow to authorize the application."""
    if not CREDENTIALS_FILE.exists():
        output(
            "error",
            f"OAuth credentials not found at {CREDENTIALS_FILE}. "
            "Download credentials.json from Google Cloud Console.",
        )

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }
        TOKEN_FILE.write_text(json.dumps(token_data, indent=2))

        output("success", "Authentication successful. Token saved.")
    except Exception as e:
        output("error", f"Authentication failed: {e}")


def check() -> None:
    """Check if valid authentication exists."""
    if not TOKEN_FILE.exists():
        output("error", "Not authenticated. Run 'setup' to authenticate.")

    try:
        import gspread

        gc = gspread.oauth(
            credentials_filename=str(CREDENTIALS_FILE),
            authorized_user_filename=str(TOKEN_FILE),
        )
        # Test the connection by listing spreadsheets (limited to 1)
        gc.list_spreadsheet_files(title=None)
        output("success", "Authentication valid.")
    except Exception as e:
        output("error", f"Authentication check failed: {e}")


def revoke() -> None:
    """Remove stored authentication token."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        output("success", "Token removed.")
    else:
        output("success", "No token found to remove.")


def main() -> None:
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Usage: auth.py <setup|check|revoke>",
                }
            )
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "setup":
        setup()
    elif command == "check":
        check()
    elif command == "revoke":
        revoke()
    else:
        output("error", f"Unknown command: {command}")


if __name__ == "__main__":
    main()
