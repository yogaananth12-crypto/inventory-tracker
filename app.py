import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER =================
today = date.today().strftime("%d %b %Y")

st.markdown(
    f"""
    <div style="text-align:center; margin-bottom:15px;">
        <div style="
            display:inline-block;
            background:#005EB8;
            color:white;
            font-weight:800;
            font-size:34px;
            padding:10px 30px;
            border-radius:6px;
            letter-spacing:2px;
        ">
            KONE
        </div>
        <div style="font-size:18px; margin-top:6px; font-weight:600;">
            Lift Inventory Tracker
        </div>
        <div style="font-size:14px; color:gray;">
            {today}
        </div>
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
    "https://www.googleapis.com/auth/drive"
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

# Ensure editable columns exist + FORCE STRING
df["LIFT NO"] = df["LIFT NO"].astype(str)
df["CALL OUT"] = df["CALL OUT"].astype(str)
df["DATE"] = df["DATE"].astype(str)
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

# Hidden row index for saving
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[
        view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    view.drop(columns=["_ROW"]),
    use_container_width=True,
    hide_index=True,
    key="editor",
    column_config={
        "QTY": st.column_config.NumberColumn("QTY"),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.TextColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),
    },
    disabled=[c for c in view.columns if c not in EDITABLE_COLS]
)

# ================= SAVE (FAST) =================
if st.button("💾 Save Changes"):
    updates = 0

    for i in range(len(edited_df)):
        original = df.iloc[i]
        edited = edited_df.iloc[i]

        if not edited.equals(original.drop("_ROW")):
            values = ["" if pd.isna(v) else str(v) for v in edited]
            sheet.update(f"A{int(original['_ROW'])}", [values])
            updates += 1

    if updates:
        st.success(f"✅ {updates} row(s) updated successfully")
    else:
        st.info("No changes detected")













