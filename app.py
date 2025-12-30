import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER =================
st.markdown(
    """
    <div style="
        background:#003A8F;
        color:white;
        padding:18px;
        border-radius:12px;
        font-size:26px;
        font-weight:700;
        text-align:center;
        margin-bottom:20px;
    ">
        KONE – Lift Inventory Tracker
    </div>
    """,
    unsafe_allow_html=True
)

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

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
data = sheet.get_all_values()
headers = data[0]
rows = data[1:]

df = pd.DataFrame(rows, columns=headers)

# Convert numeric columns
for col in ["QTY", "LIFT NO", "CALL OUT"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ================= DATA EDITOR =================
edited = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "S.NO": st.column_config.NumberColumn(disabled=True),
        "PART NO": st.column_config.TextColumn(disabled=True),
        "DESCRIPTION": st.column_config.TextColumn(disabled=True),
        "BOX NO": st.column_config.TextColumn(disabled=True),
        "QTY": st.column_config.NumberColumn("QTY"),
        "LIFT NO": st.column_config.NumberColumn("LIFT NO"),
        "CALL OUT": st.column_config.NumberColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),
    },
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    sheet.clear()
    sheet.update([headers] + edited.fillna("").astype(str).values.tolist())
    st.success("✅ Google Sheet updated successfully")

















