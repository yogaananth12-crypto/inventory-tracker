dict_keys(['gcp_service_account'])
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("WRITE TEST")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

if st.button("TEST WRITE"):
    sheet.update("A1", "STREAMLIT WRITE SUCCESS")
    st.success("Updated A1")















