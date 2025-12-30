import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory Tracker", layout="wide")

# ================= COLORS =================
KONE_BLUE = "#005EB8"
KONE_DARK = "#003A8F"

# ================= STYLE =================
st.markdown(f"""
<style>
.kone-title {{
    font-size: 40px;
    font-weight: 900;
    color: {KONE_BLUE};
}}
.kone-sub {{
    font-size: 18px;
    font-weight: 600;
    color: {KONE_DARK};
}}
div.stButton > button {{
    background-color: {KONE_BLUE};
    color: white;
    font-weight: 700;
    border-radius: 8px;
}}
div.stButton > button:hover {{
    background-color: {KONE_DARK};
}}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
c1, c2 = st.columns([1, 4])
with c1:
    try:
        st.image("kone_logo.png", width=90)
    except:
        pass
with c2:
    st.markdown("<div class='kone-title'>KONE</div>", unsafe_allow_html=True)
    st.markdown("<div class='kone-sub'>Inventory Management System</div>", unsafe_allow_html=True)

st.divider()

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

# ================= FORCE EDITABLE COLS TO TEXT =================
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].astype(str)   # 🔥 THIS FIXES LIFT NO

# Sheet row number
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view,
    hide_index=True,
    use_container_width=True,
    disabled=[c for c in view.columns if c not in EDITABLE_COLS],
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updates = 0

    for _, r in edited.iterrows():
        row_no = int(r["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        values = []
        changed = False

        for col in df.columns:
            if col == "_ROW":
                continue

            new = "" if pd.isna(r[col]) else str(r[col])
            old = "" if pd.isna(original[col]) else str(original[col])

            if new != old:
                changed = True

            values.append(new)

        if changed:
            sheet.update(f"A{row_no}", [values])
            updates += 1

    if updates:
        st.success(f"✅ {updates} row(s) updated")
    else:
        st.info("No changes detected")













