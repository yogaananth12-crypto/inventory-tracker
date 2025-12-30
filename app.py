import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER (BULLETPROOF) =================
st.markdown("""
<div style="text-align:center;margin-bottom:10px">
  <div style="display:flex;justify-content:center;gap:6px">
    <div style="width:50px;height:50px;background:#005EB8;color:white;
                font-size:30px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">K</div>
    <div style="width:50px;height:50px;background:#005EB8;color:white;
                font-size:30px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">O</div>
    <div style="width:50px;height:50px;background:#005EB8;color:white;
                font-size:30px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">N</div>
    <div style="width:50px;height:50px;background:#005EB8;color:white;
                font-size:30px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">E</div>
  </div>
  <div style="font-size:18px;font-weight:700;margin-top:4px">
    Spare Parts Inventory
  </div>
</div>
""", unsafe_allow_html=True)

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

# Force editable columns to text
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].astype(str)

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
    height=520,
    column_config={
        "QTY": st.column_config.TextColumn(),
        "LIFT NO": st.column_config.TextColumn(),
        "CALL OUT": st.column_config.TextColumn(),
        "DATE": st.column_config.TextColumn(),
    },
    disabled=[c for c in df.columns if c not in EDITABLE_COLS],
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    for i, row in edited.iterrows():
        sheet_row = i + 2  # header offset
        values = [str(row[c]) if not pd.isna(row[c]) else "" for c in df.columns]
        sheet.update(f"A{sheet_row}", [values])

    st.success("✅ Changes saved to Google Sheet")



















