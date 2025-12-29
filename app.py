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
df = pd.DataFrame(sheet.get_all_records())

if df.empty:
    st.error("Google Sheet is empty")
    st.stop()

# Ensure columns exist and correct types
df["QTY"] = pd.to_numeric(df.get("QTY", 0), errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df.get("LIFT NO", "").astype(str)
df["CALL OUT"] = df.get("CALL OUT", "").astype(str)
df["DATE"] = pd.to_datetime(df.get("DATE", ""), errors="coerce")

# Stable row index
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

df_view = df.copy()
if search:
    df_view = df_view[df_view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    df_view,
    hide_index=True,
    use_container_width=True,
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", step=1),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.SelectboxColumn(
            "CALL OUT", options=["YES", "NO"]
        ),
        "DATE": st.column_config.DateColumn("DATE"),
    },
    disabled=[c for c in df_view.columns if c not in EDITABLE_COLS],
    key="editor",
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updates = 0

    for _, row in edited_df.iterrows():
        row_num = int(row["_ROW"])
        original = df[df["_ROW"] == row_num].iloc[0]

        changed = False
        values = []

        for col in df.columns:
            if col == "_ROW":
                continue

            new = "" if pd.isna(row[col]) else str(row[col])
            old = "" if pd.isna(original[col]) else str(original[col])

            if new != old:
                changed = True

            values.append(new)

        if changed:
            sheet.update(f"A{row_num}", [values])
            updates += 1

    if updates:
        st.success(f"✅ {updates} row(s) saved to Google Sheet")
    else:
        st.info("No changes detected")


