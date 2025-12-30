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
        width: 50px;
        height: 50px;
        background: #005EB8;
        color: white;
        font-size: 32px;
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

# FORCE LIFT NO AS TEXT (DO NOT REMOVE)
df["LIFT NO"] = df["LIFT NO"].astype(str)

# ================= 🔍 SEARCH BAR (ONLY ADDITION) =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[
        view.apply(lambda r: search.lower() in r.astype(str).str.lower().to_string(), axis=1)
    ]

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    view.drop(columns=["_ROW"]),
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in df.columns if c not in EDITABLE_COLS and c != "_ROW"],
    key="editor",
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    updates = []

    for idx, row in edited_df.iterrows():
        # Google Sheet row number ( +2 because header + 0-index )
        row_no = idx + 2

        original = df.iloc[idx]

        row_changed = False
        values = []

        for col in df.columns:
            new_val = row[col]
            old_val = original[col]

            new_val = "" if pd.isna(new_val) else str(new_val).strip()
            old_val = "" if pd.isna(old_val) else str(old_val).strip()

            if col in EDITABLE_COLS and new_val != old_val:
                row_changed = True

            values.append(new_val)

        if row_changed:
            updates.append({
                "range": f"A{row_no}",
                "values": [values]
            })

    if updates:
        sheet.batch_update(updates)
        st.success(f"✅ {len(updates)} row(s) saved")
    else:
        st.info("No changes to save")











