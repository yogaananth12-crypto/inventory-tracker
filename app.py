import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------------- CONFIG ----------------
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"   # must match tab name exactly

EDITABLE_COLS = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

# ---------------- AUTH ----------------
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

# ---------------- LOAD DATA ----------------
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("Inventory Tracker")

# ---------------- SEARCH BAR ----------------
search = st.text_input("🔍 Search (Part No / Lift No / Call Out)")

if search:
    df = df[
        df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

# ---------------- EDIT TABLE ----------------
st.subheader("Edit Inventory")

edited_df = st.data_editor(
    df,
    disabled=[c for c in df.columns if c not in EDITABLE_COLS],
    use_container_width=True,
    num_rows="fixed",
    key="editor"
)

# ---------------- SAVE BUTTON ----------------
if st.button("💾 Save Changes"):
    try:
        updates = []

        for i in range(len(df)):
            if not df.loc[i, EDITABLE_COLS].equals(edited_df.loc[i, EDITABLE_COLS]):
                updates.append((i, edited_df.loc[i]))

        for row_index, row in updates:
            sheet_row = row_index + 2  # +2 because header row

            for col_name in EDITABLE_COLS:
                col_index = df.columns.get_loc(col_name) + 1
                sheet.update_cell(sheet_row, col_index, row[col_name])

        st.success("✅ Changes saved to Google Sheet!")

    except Exception as e:
        st.error(f"❌ Save failed: {e}")
















