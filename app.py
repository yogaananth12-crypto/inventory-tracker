import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE CONFIG =================
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

# Stable Google Sheet row number
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

df_view = df.copy()
if search:
    df_view = df_view[
        df_view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= COLUMN CONFIG (CRITICAL) =================
column_config = {
    "QTY": st.column_config.NumberColumn("QTY", step=1),
    "LIFT NO": st.column_config.TextColumn("LIFT NO"),
    "CALL OUT": st.column_config.TextColumn("CALL OUT"),
    "DATE": st.column_config.TextColumn("DATE"),
    "_ROW": st.column_config.Column(disabled=True),
}

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
        row_number = int(row["_ROW"])
        original = df[df["_ROW"] == row_number].iloc[0]

        new_values = []
        changed = False

        for col in df.columns:
            if col == "_ROW":
                continue

            new_val = "" if pd.isna(row[col]) else str(row[col])
            old_val = "" if pd.isna(original[col]) else str(original[col])

            if new_val != old_val:
                changed = True

            new_values.append(new_val)

        if changed:
            sheet.update(f"A{row_number}", [new_values])
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) updated in Google Sheet")
        st.rerun()
    else:
        st.info("No changes to save")




