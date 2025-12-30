import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="KONE Inventory",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= MOBILE SAFE CSS =================
st.markdown(
    """
    <style>
        body {
            background-color: #ffffff;
        }
        .kone-header {
            text-align: center;
            font-size: 34px;
            font-weight: 800;
            color: #003A8F;
            margin-top: 10px;
            margin-bottom: 0px;
        }
        .kone-sub {
            text-align: center;
            font-size: 15px;
            color: #444;
            margin-bottom: 15px;
        }
        .hint {
            font-size: 13px;
            color: #666;
            text-align: center;
            margin-bottom: 8px;
        }
        @media (max-width: 768px) {
            .kone-header { font-size: 26px; }
            .kone-sub { font-size: 13px; }
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ================= HEADER =================
st.markdown('<div class="kone-header">KONE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="kone-sub">Inventory Management System</div>',
    unsafe_allow_html=True
)

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

KEY_COL = "S.NO"
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

if KEY_COL not in df.columns:
    st.error("❌ Column 'S.NO' not found in Google Sheet")
    st.stop()

# Ensure editable columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# ================= SEARCH =================
search = st.text_input(
    "🔍 Search (Part No / Description / Box No)",
    placeholder="Type to search..."
)

view = df.copy()
if search:
    view = view[
        view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

st.markdown('<div class="hint">⬅️ Swipe left/right on mobile to see all columns</div>', unsafe_allow_html=True)

# ================= DATA EDITOR =================
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in view.columns if c not in EDITABLE_COLS],
    column_config={
        "QTY": st.column_config.NumberColumn("QTY"),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.NumberColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),
    },
    key="editor",
)

# ================= SAVE =================
st.markdown("<br>", unsafe_allow_html=True)

if st.button("💾 SAVE CHANGES", use_container_width=True):
    updated = 0

    for _, row in edited.iterrows():
        s_no = int(row[KEY_COL])
        sheet_row = s_no + 1  # header row = 1

        original = df[df[KEY_COL] == s_no].iloc[0]

        changed = False
        values = []

        for col in df.columns:
            new_val = "" if pd.isna(row[col]) else str(row[col])
            old_val = "" if pd.isna(original[col]) else str(original[col])

            if new_val != old_val:
                changed = True

            values.append(new_val)

        if changed:
            sheet.update(f"A{sheet_row}", [values])
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) updated successfully")
    else:
        st.info("No changes detected")














