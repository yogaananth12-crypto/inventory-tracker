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

# Ensure editable columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# Add stable row number (Google Sheet row)
df["_ROW_"] = range(2, len(df) + 2)

# ================= SEARCH =================
st.subheader("🔍 Search")
search = st.text_input("Search any value")

df_view = df.copy()
if search:
    df_view = df_view[
        df_view.astype(str)
        .apply(lambda r: r.str.contains(search, case=False, na=False))
        .any(axis=1)
    ]

# ================= DATA EDITOR =================
st.subheader("📋 Inventory")

disabled_cols = [
    c for c in df_view.columns if c not in EDITABLE_COLS and c != "_ROW_"
]

edited_df = st.data_editor(
    df_view,
    use_container_width=True,
    hide_index=True,
    disabled=disabled_cols,
    key="editor",   # ✅ VERY IMPORTANT
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updated = 0

    for _, row in edited_df.iterrows():
        row_no = int(row["_ROW_"])
        original = df[df["_ROW_"] == row_no].iloc[0]

        changes = False
        values = []

        for col in df.columns:
            if col == "_ROW_":
                continue

            new = row[col]
            old = original[col]

            if pd.isna(new):
                new = ""

            if str(new) != str(old):
                changes = True

            values.append(new)

        if changes:
            sheet.update(f"A{row_no}", [values])
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) updated in Google Sheet")
        st.experimental_rerun()
    else:
        st.info("No changes detected")


