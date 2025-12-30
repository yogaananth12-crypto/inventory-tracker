import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER (BLUE BLOCK) =================
today = date.today().strftime("%d %b %Y")

st.markdown(
    f"""
    <div style="
        background-color:#003A8F;
        padding:16px;
        border-radius:8px;
        text-align:center;
        margin-bottom:20px;
    ">
        <h1 style="color:white; margin:0;">KONE</h1>
        <p style="color:white; margin:4px 0 0 0; font-size:14px;">
            Inventory Tracker • {today}
        </p>
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

# Keep Google Sheet row index internally
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
# 🔴 CRITICAL FIX:
# Do NOT use disabled list (this breaks LIFT NO editing)
edited = st.data_editor(
    view.drop(columns=["_ROW"]),
    use_container_width=True,
    hide_index=True,
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updated = 0

    for i, row in edited.iterrows():
        sheet_row = int(view.iloc[i]["_ROW"])

        values = []
        for col in df.columns:
            if col == "_ROW":
                continue
            values.append("" if pd.isna(row[col]) else str(row[col]))

        sheet.update(f"A{sheet_row}", [values])
        updated += 1

    st.success(f"✅ {updated} row(s) saved to Google Sheet")




