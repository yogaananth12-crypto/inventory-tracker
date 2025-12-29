import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Inventory Tracker", layout="wide")

# ---------------- CONFIG ----------------
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

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

if df.empty:
    st.error("Sheet is empty")
    st.stop()

# Add internal row id
df["__ROW_ID__"] = range(2, len(df) + 2)

# ---------------- SEARCH ----------------
search = st.text_input("🔍 Search (Part No / Description)")

df_view = df.copy()
if search:
    df_view = df_view[
        df_view["PART NO"].astype(str).str.contains(search, case=False, na=False) |
        df_view["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# ---------------- EDITOR ----------------
column_config = {}

if "QTY" in df_view.columns:
    column_config["QTY"] = st.column_config.NumberColumn("QTY", min_value=0)

if "LIFT NO" in df_view.columns:
    column_config["LIFT NO"] = st.column_config.TextColumn("LIFT NO")

if "CALL OUT" in df_view.columns:
    column_config["CALL OUT"] = st.column_config.SelectboxColumn(
        "CALL OUT", options=["", "YES", "NO"]
    )

if "DATE" in df_view.columns:
    column_config["DATE"] = st.column_config.TextColumn("DATE")

edited = st.data_editor(
    df_view,
    use_container_width=True,
    num_rows="fixed",
    row_key="__ROW_ID__",
    disabled=[c for c in df_view.columns if c not in EDITABLE_COLS],
    column_config=column_config
)

# ---------------- SAVE ----------------
if st.button("💾 Save Changes"):
    updates = 0

    for _, row in edited.iterrows():
        row_id = int(row["__ROW_ID__"])

        original = df[df["__ROW_ID__"] == row_id].iloc[0]

        changed = False
        values = []

        for col in df.columns:
            if col == "__ROW_ID__":
                continue

            new_val = row[col]
            old_val = original[col]

            if pd.isna(new_val):
                new_val = ""

            if str(new_val) != str(old_val):
                changed = True

            values.append(new_val)

        if changed:
            sheet.update(f"A{row_id}:F{row_id}", [values])
            updates += 1

    if updates:
        st.success(f"✅ {updates} row(s) updated")
    else:
        st.info("No changes detected")


























