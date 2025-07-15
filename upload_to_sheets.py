#!/usr/bin/env python3
import os
import urllib.parse as urlparse

import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ─── CONFIG VIA ENV VARS ────────────────────────────────────────────
DATABASE_URL   = os.environ['DATABASE_URL']

# Google Sheets details
CREDS_JSON     = os.getenv('GOOGLE_CREDS_JSON', 'service-account.json')
# ← your sheet URL: https://docs.google.com/spreadsheets/d/1VyLhwUiT_ZKTN7vqjBSpz6H7BMAQItDVLKVYNLOZaBI/edit
SPREADSHEET_ID = '1VyLhwUiT_ZKTN7vqjBSpz6H7BMAQItDVLKVYNLOZaBI'
TARGET_SHEET   = 'SalesData'
# ───────────────────────────────────────────────────────────────────

def fetch_sales():
    """Connects to Postgres, returns (columns, rows) from sales table."""
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
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON, scope)
    client = gspread.authorize(creds)

    ss = client.open_by_key(SPREADSHEET_ID)
    try:
        ws = ss.worksheet(TARGET_SHEET)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(TARGET_SHEET, rows=len(rows)+10, cols=len(cols)+1)

    ws.clear()
    ws.append_row(cols, value_input_option='RAW')
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
