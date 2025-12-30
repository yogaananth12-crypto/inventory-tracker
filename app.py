import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER =================
st.markdown(
    f"""
    <div style="display:flex;justify-content:center;margin-bottom:6px;">
        <div style="display:flex;gap:6px;">
            <div style="background:#0052CC;color:white;font-weight:700;
                        padding:10px 14px;border-radius:4px;font-size:20px;">K</div>
            <div style="background:#0052CC;color:white;font-weight:700;
                        padding:10px 14px;border-radius:4px;font-size:20px;">O</div>
            <div style="background:#0052CC;color:white;font-weight:700;
                        padding:10px 14px;border-radius:4px;font-size:20px;">N</div>
            <div style="background:#0052CC;color:white;font-weight:700;
                        padding:10px 14px;border-radius:4px;font-size:20px;">E</div>
        </div>
    </div>
    <p style="text-align:center;color:#666;font-size:13px;">
        Inventory Tracker • {date.today().strftime("%d %b %Y")}
    </p>
    """,
    unsafe_allow_html=True
)

# ================= GOOGLE SHEET =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ================= LOAD DATA =================
data = sheet.get_all_records()
df = pd.DataFrame(data)

if df.empty:
    st.error("No data found")
    st.stop()

# 🔥 FORCE STRING FOR PROBLEM COLUMNS
for col in ["LIFT NO", "CALL OUT", "PART NO", "BOX NO"]:
    if col in df.columns:
        df[col] = df[col].astype(str)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    sheet.clear()
    sheet.update([edited.columns.tolist()] + edited.values.tolist())
    st.success("✅ Saved successfully")







