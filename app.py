import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Inventory Tracker", layout="wide")

today_str = date.today().strftime("%d %b %Y")

# ================= HEADER =================
st.markdown(f"""
<style>
.kone-header {{
    display: flex;
    gap: 6px;
    margin-bottom: 6px;
}}
.kone-box {{
    background-color: #0071CE;
    color: white;
    font-weight: 700;
    font-size: 26px;
    padding: 6px 14px;
    border-radius: 4px;
}}
.subtitle {{
    font-size: 14px;
    color: #444;
    margin-bottom: 14px;
}}

/* Ensure table text visible */
[data-testid="stDataEditor"] {{
    background-color: white !important;
}}
thead th, tbody td {{
    color: black !important;
    font-size: 14px;
}}
</style>

<div class="kone-header">
    <div class="kone-box">K</div>
    <div class="kone-box">O</div>
    <div class="kone-box">N</div>
    <div class="kone-box">E</div>
</div>
<div class="subtitle">
Inventory Tracker — {today_str}
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

# Ensure editable columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# Google Sheet row index (hidden)
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search", placeholder="Search part no, description, box no...")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view,
    hide_index=True,
    use_container_width=True,
    disabled=[c for c in view.columns if c not in EDITABLE_COLS],
    key="editor",
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updated = 0

    for _, row in edited.iterrows():
        row_no = int(row["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        values = []
        changed = False

        for col in df.columns:
            if col == "_ROW":
                continue

            new = "" if pd.isna(row[col]) else str(row[col])
            old = "" if pd.isna(original[col]) else str(original[col])

            if new != old:
                changed = True

            values.append(new)

        if changed:
            sheet.update(f"A{row_no}", [values])
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) updated")
    else:
        st.info("No changes detected")






















