---
name: google-sheets
description: Read and write Google Sheets data. Use when working with spreadsheet data, extracting data from Google Sheets, or updating cells/ranges in a spreadsheet.
allowed-tools: Bash(uv:*)
---

# Google Sheets Skill

This skill enables reading and writing Google Sheets data using OAuth 2.0 authentication.

## Scripts Location

All scripts are in this directory and run via uv.

## Authentication Workflow

**Always check authentication status first before any operation:**

```bash
uv runauth.py check
```

If authentication fails, guide the user through setup:

1. Ensure credentials exist at `~/.config/google-sheets/credentials.json` (see README.md)
2. Run OAuth setup:
   ```bash
   uv runauth.py setup
   ```

To remove stored credentials:
```bash
uv runauth.py revoke
```

## Reading Data

### List worksheets in a spreadsheet
```bash
uv runread_sheet.py list-sheets "SPREADSHEET_ID"
```

### Get all data from a worksheet
```bash
uv runread_sheet.py get-all "SPREADSHEET_ID" "Sheet1"
```

### Get a specific cell
```bash
uv runread_sheet.py get-cell "SPREADSHEET_ID" "Sheet1" "A1"
```

### Get a range of cells
```bash
uv runread_sheet.py get-range "SPREADSHEET_ID" "Sheet1" "A1:C10"
```

## Writing Data

### Update a single cell
```bash
uv runwrite_sheet.py set-cell "SPREADSHEET_ID" "Sheet1" "A1" "New Value"
```

### Update a range with 2D array
```bash
uv runwrite_sheet.py set-range "SPREADSHEET_ID" "Sheet1" "A1:B2" '[["a","b"],["c","d"]]'
```

### Append a row to the end
```bash
uv runwrite_sheet.py append-row "SPREADSHEET_ID" "Sheet1" '["value1","value2","value3"]'
```

### Clear a range
```bash
uv runwrite_sheet.py clear-range "SPREADSHEET_ID" "Sheet1" "A1:C10"
```

## Creating & Managing Spreadsheets

### Create a new spreadsheet
```bash
uv runcreate_sheet.py create "My Spreadsheet"
```

### Add a worksheet (tab) to an existing spreadsheet
```bash
uv runcreate_sheet.py add-worksheet "SPREADSHEET_ID" "NewTab"
```

With custom size:
```bash
uv runcreate_sheet.py add-worksheet "SPREADSHEET_ID" "NewTab" 500 20
```

### Delete a worksheet
```bash
uv runcreate_sheet.py delete-worksheet "SPREADSHEET_ID" "SheetName"
```

### Share a spreadsheet
```bash
uv runcreate_sheet.py share "SPREADSHEET_ID" "user@example.com"
```

With read-only access:
```bash
uv runcreate_sheet.py share "SPREADSHEET_ID" "user@example.com" reader
```

## Output Format

All scripts output JSON:

**Success (read operations):**
```json
{"success": true, "data": [...]}
```

**Success (write operations):**
```json
{"success": true, "message": "..."}
```

**Error:**
```json
{"success": false, "error": "Error description"}
```

**Auth status:**
```json
{"status": "success|error", "message": "..."}
```

## Spreadsheet Identification

You can use either:
- **Spreadsheet ID**: The alphanumeric string from the URL (e.g., `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`)
- **Full URL**: The complete Google Sheets URL

## Error Handling

Common errors and solutions:

| Error | Solution |
|-------|----------|
| "Not authenticated" | Run `auth.py setup` |
| "Spreadsheet not found" | Check the spreadsheet ID/URL and sharing permissions |
| "Worksheet not found" | Verify the exact worksheet name (case-sensitive) |
| "Invalid JSON" | Ensure JSON arrays are properly formatted |

## Important Notes

- Worksheet names are case-sensitive
- JSON data for ranges must be a 2D array (list of lists)
- JSON data for append-row must be a 1D array
- The user must have edit access to the spreadsheet for write operations
- First-time setup requires browser access for OAuth consent
