import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER =================
st.markdown(
    """
    <div style="
        background-color:#003A8F;
        padding:18px;
        border-radius:12px;
        text-align:center;
        margin-bottom:20px;
    ">
        <h1 style="color:white; margin:0;">KONE</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

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

# Convert DATE column safely
if "DATE" in df.columns:
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce").dt.date

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[
        view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    height=500,   # 🔑 prevents invisible rows
    column_config={
        "QTY": st.column_config.NumberColumn(),
        "LIFT NO": st.column_config.NumberColumn(),
        "CALL OUT": st.column_config.NumberColumn(),
        "DATE": st.column_config.DateColumn(),
    },
    disabled=[c for c in df.columns if c not in EDITABLE_COLS],
    key="editor",
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updated = 0

    for i, row in edited.iterrows():
        sheet_row = i + 2  # Google Sheet row (after header)

        new_values = []
        for col in df.columns:
            val = row[col]

            if pd.isna(val):
                val = ""

            # Ensure JSON-safe values
            if isinstance(val, date):
                val = val.isoformat()

            new_values.append(str(val))

        sheet.update(f"A{sheet_row}", [new_values])
        updated += 1

    st.success(f"✅ {updated} row(s) updated successfully")

















