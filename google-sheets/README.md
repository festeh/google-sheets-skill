# Google Sheets API Setup Guide

This guide walks through setting up Google Cloud credentials for the Google Sheets skill.

## Prerequisites

- A Google account
- Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Claude Sheets Integration")
5. Click "Create"

## Step 2: Enable Required APIs

1. In the Cloud Console, go to "APIs & Services" > "Library"
2. Search for and enable these APIs:
   - **Google Sheets API** - Required for spreadsheet operations
   - **Google Drive API** - Required for accessing spreadsheets by URL/ID

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (unless you have a Workspace account)
3. Click "Create"
4. Fill in the required fields:
   - App name: "Claude Sheets" (or your preferred name)
   - User support email: Your email
   - Developer contact email: Your email
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Add these scopes:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.readonly`
8. Click "Save and Continue"
9. On "Test users", add your Google email address
10. Click "Save and Continue"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as the application type
4. Enter a name (e.g., "Claude Sheets Desktop")
5. Click "Create"
6. Click "Download JSON" on the confirmation dialog

## Step 5: Install Credentials

1. Create the credentials directory:
   ```bash
   mkdir -p ~/.config/google-sheets
   ```

2. Move the downloaded file:
   ```bash
   mv ~/Downloads/client_secret_*.json ~/.config/google-sheets/credentials.json
   ```

3. Set appropriate permissions:
   ```bash
   chmod 600 ~/.config/google-sheets/credentials.json
   ```

## Step 6: Authenticate

Run the authentication setup:
```bash
uv run auth.py setup
```

This will:
1. Open your browser to the Google sign-in page
2. Ask you to authorize the application
3. Save the authorization token to `~/.config/google-sheets/authorized_user.json`

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Ensure you've added your email as a test user in the OAuth consent screen

### "File not found: credentials.json"
- Verify the file is at `~/.config/google-sheets/credentials.json`
- Check file permissions

### "Insufficient permissions"
- Make sure both Sheets API and Drive API are enabled
- Verify the OAuth scopes match what's required

## Security Notes

- Keep `credentials.json` and `authorized_user.json` secure
- Never commit these files to version control
- The token in `authorized_user.json` grants access to your Google Sheets
- Use `auth.py revoke` to remove stored credentials when no longer needed
