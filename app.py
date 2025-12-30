import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="KONE Inventory Tracker",
    layout="wide"
)

# ================= BRAND COLORS =================
KONE_BLUE = "#005EB8"
KONE_DARK = "#003A8F"

# ================= STYLES =================
st.markdown(
    f"""
    <style>
        html, body, [class*="css"] {{
            font-size: 16px;
        }}

        .kone-header {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            padding: 14px 0 18px 0;
        }}

        .kone-title {{
            font-size: 40px;
            font-weight: 900;
            color: {KONE_BLUE};
            letter-spacing: 1px;
            line-height: 1;
        }}

        .kone-subtitle {{
            font-size: 18px;
            font-weight: 600;
            color: {KONE_DARK};
            margin-top: 4px;
        }}

        /* Save button */
        div.stButton > button {{
            background-color: {KONE_BLUE};
            color: white;
            font-weight: 700;
            padding: 0.6rem 1.4rem;
            border-radius: 8px;
            border: none;
        }}

        div.stButton > button:hover {{
            background-color: {KONE_DARK};
            color: white;
        }}

        /* Data editor font */
        div[data-testid="stDataEditor"] {{
            font-size: 16px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ================= HEADER =================
col1, col2 = st.columns([1, 4])

with col1:
    try:
        logo = Image.open("kone_logo.png")
        st.image(logo, width=90)
    except:
        pass

with col2:
    st.markdown(
        """
        <div>
            <div class="kone-title">KONE</div>
            <div class="kone-subtitle">Inventory Management System</div>
        </div>
        """,
        unsafe_allow_html=True
    )

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

# Google Sheet row number
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search Part No / Description / Box No")

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
    disabled=[c for c in view.columns if c not in EDITABLE_COLS],
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updates = 0

    for _, row in edited.iterrows():
        row_no = int(row["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        changed = False
        values = []

        for col in df.columns:
            if col == "_ROW":
                continue

            new_val = "" if pd.isna(row[col]) else str(row[col])
            old_val = "" if pd.isna(original[col]) else str(original[col])

            if new_val != old_val:
                changed = True

            values.append(new_val)

        if changed:
            sheet.update(f"A{row_no}", [values])
            updates += 1

    if updates:
        st.success(f"✅ {updates} row(s) updated successfully")
    else:
        st.info("No changes detected")












