import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= KONE HEADER (TEXT LOGO – ALWAYS VISIBLE) =================
st.markdown("""
<style>
.kone-header {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin: 25px 0 10px 0;
}
.kone-box {
    background-color: #003A8F;
    color: white;
    font-size: 36px;
    font-weight: 800;
    width: 55px;
    height: 55px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
}
.subtitle {
    text-align: center;
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
}
</style>

<div class="kone-header">
  <div class="kone-box">K</div>
  <div class="kone-box">O</div>
  <div class="kone-box">N</div>
  <div class="kone-box">E</div>
</div>
<div class="subtitle">Lift Inventory Tracker</div>
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

# FORCE TEXT TYPE FOR EDITABLE COLUMNS (VERY IMPORTANT)
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
    updated = 0

    for i, row in edited.iterrows():
        sheet_row = i + 2  # header offset

        values = []
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                val = ""
            values.append(str(val))

        sheet.update(f"A{sheet_row}", [values])
        updated += 1

    st.success(f"✅ {updated} row(s) updated successfully")



















