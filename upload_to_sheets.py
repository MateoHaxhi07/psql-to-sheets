#!/usr/bin/env python3
import os
import urllib.parse as urlparse

import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ─── CONFIG VIA ENV VARS ────────────────────────────────────────────
# Postgres connection (same as before)
DATABASE_URL   = os.environ['DATABASE_URL']

# Google Sheets details
#  • The service‑account JSON must be committed or provided via secret
#  • Or set GOOGLE_CREDS_JSON to its path
CREDS_JSON     = os.getenv('GOOGLE_CREDS_JSON', 'service-account.json')
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
TARGET_SHEET   = os.getenv('TARGET_SHEET', 'SalesData')
# ───────────────────────────────────────────────────────────────────

def fetch_sales():
    """Connects to Postgres, returns (columns, rows) from sales table."""
    # Parse the URL
    result = urlparse.urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port,
        sslmode='require'
    )
    cur = conn.cursor()
    cur.execute('SELECT * FROM sales;')
    cols = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return cols, rows

def write_to_sheet(cols, rows):
    """Authenticates to Google Sheets and writes header + data."""
    # 1) Auth
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON, scope)
    client = gspread.authorize(creds)

    # 2) Open the target worksheet (create if missing)
    ss = client.open_by_key(SPREADSHEET_ID)
    try:
        ws = ss.worksheet(TARGET_SHEET)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(TARGET_SHEET, rows=len(rows)+10, cols=len(cols)+1)

    # 3) Clear and write
    ws.clear()
    ws.append_row(cols, value_input_option='RAW')
    # gspread can append multiple rows in one call:
    ws.append_rows(rows, value_input_option='RAW')

def main():
    print("🔄 Fetching sales from Postgres…")
    cols, rows = fetch_sales()
    print(f"📊 Retrieved {len(rows)} rows.")
    print("✏️  Writing to Google Sheet…")
    write_to_sheet(cols, rows)
    print("✅ Done.")

if __name__ == '__main__':
    main()
