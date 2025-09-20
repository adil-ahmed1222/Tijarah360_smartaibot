# src/backend/sheets_service.py
"""
Google Sheets helper for the AI-chatbot app.

• Looks for a service-account key via env-var SERVICE_ACCOUNT_JSON
• Falls back to <project_root>/credentials/service_account.json
• Provides get_sheet_data() -> list[dict]
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List

import gspread
from google.oauth2.service_account import Credentials

# ────────────────────────────────────────────────────────────────────────────
# 1.  Resolve the service-account JSON location (env only)
# ────────────────────────────────────────────────────────────────────────────
env_path = os.getenv("SERVICE_ACCOUNT_JSON")
if not env_path:
    raise RuntimeError(
        "SERVICE_ACCOUNT_JSON is not set. Set it to the absolute path of your Google service account JSON file."
    )

SERVICE_ACCOUNT_JSON = Path(env_path)
if not SERVICE_ACCOUNT_JSON.exists():
    raise FileNotFoundError(
        f"Service-account file not found at:\n  {SERVICE_ACCOUNT_JSON}\n"
    )

# ────────────────────────────────────────────────────────────────────────────
# 2.  Authorise gspread
# ────────────────────────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

creds: Credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_JSON, scopes=SCOPES
)
client = gspread.authorize(creds)

# ────────────────────────────────────────────────────────────────────────────
# 3.  Sheet metadata
# ────────────────────────────────────────────────────────────────────────────
SHEET_ID = "1IE6Ic3g6lTScdD65ZLq8aNDiB0w0ktr-9vl16TtChbM"
SHEET_TAB = "Issues and video_links"  # adjust if your tab name differs

# ────────────────────────────────────────────────────────────────────────────
# 4.  Public helper
# ────────────────────────────────────────────────────────────────────────────
def get_sheet_data() -> List[dict[str, Any]]:
    """
    Return all rows from the sheet as list of dictionaries.
    Includes all rows, even if there are blanks in between.
    """
    try:
        sheet = client.open_by_key(SHEET_ID)
        ws = sheet.worksheet(SHEET_TAB)
        print(f"✅ Connected → {sheet.title} / {SHEET_TAB} (rows: {ws.row_count})")

        raw = ws.get_all_values()
        headers = raw[0]
        rows = raw[1:]

        data = []
        for row in rows:
            if any(cell.strip() for cell in row):  # skip completely empty rows
                row_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                data.append(row_dict)

        return data
    except Exception as exc:
        print(f"❌ Error reading Google Sheet: {exc}")
        return []
