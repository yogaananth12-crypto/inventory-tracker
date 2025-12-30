import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE =================
st.set_page_config(page_title="Inventory Tracker", layout="wide")

st.markdown(
    """
    <div style="text-align:center; padding:12px 0;">
        <h1 style="margin-bottom:5px;">KONE</h1>
        <h4 style="color:gray; margin-top:0;">
            Spare Parts Inventory Management System
        </h4>
        <hr style="margin-top:15px;">
    </div>
    """,
    unsafe_allow_html=True
)

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

EDITABLE = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

COLUMN_ORDER = [
    "S.NO",
    "PART NO",
    "DESCRIPTION",
    "BOX NO",
    "QTY",
    "LIFT NO",
    "CALL OUT",
    "DATE",
]

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

# Ensure all columns exist
for col in COLUMN_ORDER:
    if col not in df.columns:
        df[col] = ""

# Reorder
df = df[COLUMN_ORDER]

# Convert numeric fields
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df["LIFT NO"].astype(str)
df["CALL OUT"] = df["CALL OUT"].astype(str)
df["DATE"] = df["DATE"].astype(str)

# Add row number for saving
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search Part No / Description / Box No")

view = df.copy()
if search:
    view = view[
        view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= EDITOR =================
edited = st.data_editor(
    view,
    hide_index=True,
    use_container_width=True,
    disabled=[c for c in view.columns if c not in EDITABLE],
    key="editor",
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updated = 0

    for _, row in edited.iterrows():
        row_no = int(row["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        changed = False
        values = []

        for col in COLUMN_ORDER:
            new = "" if pd.isna(row[col]) else str(row[col])
            old = "" if pd.isna(original[col]) else str(original[col])

            if new != old:
                changed = True

            values.append(new)

        if changed:
            sheet.update(f"A{row_no}", [values])
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) saved to Google Sheet")
    else:
        st.info("No changes detected")











