import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= KONE BLOCK HEADER =================
st.markdown(
    """
    <div style="display:flex; justify-content:center; margin-bottom:6px;">
        <div style="display:flex; gap:6px;">
            <div style="background:#0052CC;color:white;font-weight:700;
                        padding:12px 14px;border-radius:4px;font-size:20px;">K</div>
            <div style="background:#0052CC;color:white;font-weight:700;
                        padding:12px 14px;border-radius:4px;font-size:20px;">O</div>
            <div style="background:#0052CC;color:white;font-weight:700;
                        padding:12px 14px;border-radius:4px;font-size:20px;">N</div>
            <div style="background:#0052CC;color:white;font-weight:700;
                        padding:12px 14px;border-radius:4px;font-size:20px;">E</div>
        </div>
    </div>
    <p style="text-align:center;color:#666;font-size:13px;margin-top:4px;">
        Inventory Tracker • {date}
    </p>
    """.format(date=date.today().strftime("%d %b %Y")),
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
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ================= LOAD DATA =================
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.error("Google Sheet is empty")
    st.stop()

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR (SAFE MODE) =================
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "QTY": st.column_config.NumberColumn("QTY"),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.TextColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),
    },
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    sheet.clear()
    sheet.update([edited.columns.tolist()] + edited.astype(str).values.tolist())
    st.success("✅ Google Sheet updated successfully")





