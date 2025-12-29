import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SHEET_ID)
sheet = spreadsheet.get_worksheet(0)

st.title("Inventory Tracker")

df = pd.DataFrame(sheet.get_all_records())

edited_df = st.data_editor(df, use_container_width=True)

if st.button("Save"):
    sheet.clear()
    sheet.update(
        [edited_df.columns.tolist()] +
        edited_df.astype(str).values.tolist()
    )
    st.success("Saved to Google Sheets ✅")
















