import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Inventory Tracker", layout="wide")

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

EDITABLE_COLS = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

# ================= AUTH =================
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

# ================= LOAD DATA =================
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.error("Google Sheet is empty")
    st.stop()

# Ensure editable columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# Add stable row id
df["__ROW_ID__"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

df_view = df.copy()
if search:
    df_view = df_view[
        df_view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    df_view,
    use_container_width=True,
    hide_index=True,
    row_key="__ROW_ID__",
    disabled=[c for c in df_view.columns if c not in EDITABLE_COLS]
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updates = 0

    for _, edited_row in edited_df.iterrows():
        row_id = int(edited_row["__ROW_ID__"])
        original_row = df[df["__ROW_ID__"] == row_id].iloc[0]

        changed = False
        values = []

        for col in df.columns:
            if col == "__ROW_ID__":
                continue

            new_val = edited_row[col]
            old_val = original_row[col]

            if pd.isna(new_val):
                new_val = ""

            if str(new_val) != str(old_val):
                changed = True

            values.append(new_val)

        if changed:
            sheet.update(f"A{row_id}", [values])
            updates += 1

    if updates:
        st.success(f"✅ {updates} row(s) saved to Google Sheet")
    else:
        st.info("No changes detected")
