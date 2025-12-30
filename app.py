import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Lift Inventory", layout="wide")

# ================= HEADER =================
today = date.today().strftime("%d %b %Y")

st.markdown(
    f"""
    <style>
    .header {{
        text-align: center;
        margin-bottom: 20px;
    }}
    .kone {{
        display: inline-flex;
        gap: 6px;
    }}
    .kone span {{
        width: 55px;
        height: 55px;
        background: #005EB8;
        color: white;
        font-size: 34px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: Arial, Helvetica, sans-serif;
    }}
    .subtitle {{
        margin-top: 10px;
        font-size: 20px;
        font-weight: 600;
    }}
    .date {{
        font-size: 14px;
        color: #555;
    }}
    </style>

    <div class="header">
        <div class="kone">
            <span>K</span><span>O</span><span>N</span><span>E</span>
        </div>
        <div class="subtitle">Lift Inventory Tracker</div>
        <div class="date">{today}</div>
    </div>
    """,
    unsafe_allow_html=True
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

# Add hidden Google Sheet row number
df["_ROW"] = range(2, len(df) + 2)

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    df.drop(columns=["_ROW"]),
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in df.columns if c not in EDITABLE_COLS and c != "_ROW"],
    key="editor",
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updates = 0

    for i, row in edited_df.iterrows():
        row_no = df.loc[i, "_ROW"]
        values = ["" if pd.isna(v) else str(v) for v in row.tolist()]
        sheet.update(f"A{row_no}", [values])
        updates += 1

    st.success(f"✅ {updates} row(s) saved successfully")








