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
    st.error("Sheet is empty")
    st.stop()

# Ensure editable columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# Add row number for updates
df["_ROW_"] = range(2, len(df) + 2)

# FORCE ALL TO STRING (critical)
df = df.astype(str)

# ================= SEARCH =================
st.subheader("🔍 Search")
search = st.text_input("Search")

df_view = df.copy()
if search:
    df_view = df_view[
        df_view.apply(lambda r: search.lower() in " ".join(r).lower(), axis=1)
    ]

# ================= EDITOR =================
st.subheader("📋 Inventory")

edited_df = st.experimental_data_editor(
    df_view,
    use_container_width=True,
    hide_index=True,
    key="editor",
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updated = 0

    for _, row in edited_df.iterrows():
        row_no = int(row["_ROW_"])
        original = df[df["_ROW_"] == str(row_no)].iloc[0]

        values = []
        changed = False

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
        st.experimental_rerun()
    else:
        st.info("No changes detected")


