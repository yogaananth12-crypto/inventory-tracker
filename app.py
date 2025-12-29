import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------------- CONFIG ----------------
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"   # change if your tab name is different

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ---------------- AUTH ----------------
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ---------------- LOAD DATA ----------------
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("📦 Inventory Tracker")

edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    key="editor"
)

# ---------------- SAVE BUTTON ----------------
if st.button("💾 Save to Google Sheet"):
    try:
        sheet.clear()
        sheet.update(
            [edited_df.columns.tolist()] +
            edited_df.astype(str).values.tolist()
        )
        st.success("✅ Data saved to Google Sheet!")
    except Exception as e:
        st.error(f"❌ Save failed: {e}")















