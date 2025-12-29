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
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes,
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ================= LOAD DATA =================
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.error("Google Sheet is empty")
    st.stop()

# Ensure columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# Stable row number (Google Sheet row)
df["_ROW_"] = range(2, len(df) + 2)

# 🚨 CRITICAL: force ALL columns to string
df = df.astype(str)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

df_view = df.copy()
if search:
    df_view = df_view[
        df_view.apply(lambda r: search.lower() in " ".join(r).lower(), axis=1)
    ]

# ================= COLUMN CONFIG =================
column_config = {
    col: st.column_config.TextColumn(col)
    for col in EDITABLE_COLS
}

# Hide internal column
column_config["_ROW_"] = None

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    df_view,
    use_container_width=True,
    hide_index=True,
    column_config=column_config,
    disabled=[c for c in df_view.columns if c not in EDITABLE_COLS],
    key="editor",
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updated = 0

    for _, row in edited_df.iterrows():
        row_no = int(row["_ROW_"])
        original = df[df["_ROW_"] == str(row_no)].iloc[0]

        changed = False
        values = []

        for col in df.columns:
            if col == "_ROW_":
                continue

            if col in EDITABLE_COLS:
                new = row[col].strip()
                old = original[col].strip()
                if new != old:
                    changed = True
                values.append(new)
            else:
                values.append(original[col])

        if changed:
            sheet.update(f"A{row_no}", [values])
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) updated")
        st.rerun()
    else:
        st.info("No changes detected")



