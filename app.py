import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE =================
st.set_page_config(page_title="Inventory Tracker", layout="wide")
st.title("📦 Inventory Tracker")

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

# Fix data types
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
df["CALL OUT"] = pd.to_numeric(df["CALL OUT"], errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df["LIFT NO"].astype(str)
df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

# Google Sheet row number
df["_ROW"] = range(2, len(df) + 2)

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
    key="editor",
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", step=1),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.NumberColumn("CALL OUT", step=1),
        "DATE": st.column_config.DateColumn("DATE"),
        "_ROW": None,
    },
    disabled=[
        c for c in df_view.columns
        if c not in EDITABLE_COLS and c != "_ROW"
    ],
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updated = 0

    for _, row in edited_df.iterrows():
        row_no = int(row["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        changed = False
        values = []

        for col in df.columns:
            if col == "_ROW":
                continue

            new_val = row[col]
            old_val = original[col]

            # 🔑 CRITICAL FIX
            if pd.isna(new_val):
                new_val = ""
            elif isinstance(new_val, pd.Timestamp):
                new_val = new_val.strftime("%Y-%m-%d")

            if pd.isna(old_val):
                old_val = ""
            elif isinstance(old_val, pd.Timestamp):
                old_val = old_val.strftime("%Y-%m-%d")

            if str(new_val) != str(old_val):
                changed = True

            values.append(new_val)

        if changed:
            sheet.update(f"A{row_no}", [values])
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) saved to Google Sheet")
    else:
        st.info("No changes detected")




