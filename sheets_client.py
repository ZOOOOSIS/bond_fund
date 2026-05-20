import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet(tab_name: str):
    creds = Credentials.from_service_account_file(
        os.getenv("SERVICE_ACCOUNT_PATH"), scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(os.getenv("SPREADSHEET_ID"))
    return spreadsheet.worksheet(tab_name)

def read_sheet(tab_name: str) -> list[dict]:
    ws = get_sheet(tab_name)
    return ws.get_all_records()

def append_row(tab_name: str, row: list):
    ws = get_sheet(tab_name)
    ws.append_row(row, value_input_option="USER_ENTERED")

def overwrite_sheet(tab_name: str, data: list[list], header: list):
    ws = get_sheet(tab_name)
    ws.clear()
    ws.append_row(header)
    if data:
        ws.append_rows(data)