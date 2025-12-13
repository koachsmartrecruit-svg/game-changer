# Google Sheets Integration Setup Guide

This guide will help you set up Google Sheets integration to collect user details (name, phone, email, needs, etc.).

## Prerequisites

1. A Google account
2. A Google Sheet where you want to store the data

## Step 1: Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it (e.g., "GameChanger Leads")
4. Add headers in the first row:
   - Column A: Timestamp
   - Column B: Name
   - Column C: Phone
   - Column D: Email
   - Column E: Needs
   - Column F: Source

## Step 2: Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Enable the Google Drive API (same process)
5. Create a Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "gamechanger-sheets")
   - Click "Create and Continue"
   - Skip optional steps and click "Done"
6. Create a Key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the JSON file

## Step 3: Share the Google Sheet

1. Open your Google Sheet
2. Click the "Share" button (top right)
3. Add the service account email (found in the JSON file, looks like: `your-service-account@project-id.iam.gserviceaccount.com`)
4. Give it "Editor" permissions
5. Click "Send"

## Step 4: Get the Sheet ID

1. Open your Google Sheet
2. Look at the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
3. Copy the `SHEET_ID_HERE` part

## Step 5: Configure Environment Variables

Add these to your `.env` file:

```env
# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"your-project-id",...}'
GOOGLE_SHEET_ID=your_sheet_id_here
```

**Important:** The `GOOGLE_SHEETS_CREDENTIALS` should be the entire JSON content from the downloaded file, but as a single-line string. You can:
- Copy the entire JSON file content
- Remove all newlines and format it as a single line
- Or use a JSON minifier tool

Example:
```env
GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"my-project","private_key_id":"abc123",...}'
GOOGLE_SHEET_ID=1a2b3c4d5e6f7g8h9i0j
```

## Step 6: Install Dependencies

```bash
pip install gspread google-auth
```

Or if using requirements.txt:
```bash
pip install -r requirements.txt
```

## Step 7: Test the Integration

1. Start your Flask application
2. Use the chatbot and click "Contact Us"
3. Fill in the contact form
4. Submit it
5. Check your Google Sheet - you should see a new row with the data!

## Troubleshooting

- **"Google Sheets not available"**: Make sure `gspread` and `google-auth` are installed
- **"Credentials not configured"**: Check your `.env` file has the correct variables
- **"Permission denied"**: Make sure you shared the sheet with the service account email
- **"Sheet not found"**: Verify the `GOOGLE_SHEET_ID` is correct

## Notes

- The integration gracefully degrades if Google Sheets is not configured (users still see success message)
- Data is saved with timestamp automatically
- The "Source" column indicates where the lead came from (e.g., "chatbot", "contact_form")
