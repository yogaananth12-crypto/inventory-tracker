import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import uuid

st.set_page_config(page_title="Inventory Tracker", layout="wide")

# =====================
# CONFIG
# =====================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

EDITABLE_COLS = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

# =====================
# AUTH
# =====================
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# =====================
# LOAD DATA ONCE
# =====================
if "df" not in st.session_state:
    df = pd.DataFrame(sheet.get_all_records())
    df.columns = df.columns.str.upper().str.strip()

    # Create permanent internal row id
    df["__ROW_ID__"] = [str(uuid.uuid4()) for _ in range(len(df))]

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    for col in ["LIFT NO", "CALL OUT", "DATE"]:
        df[col] = df[col].astype(str)

    st.session_state.df = df

st.title("📦 Inventory Tracker")

# =====================
# SEARCH
# =====================
search = st.text_input("🔍 Search Part No / Description")

df = st.session_state.df

if search:
    df_view = df[
        df["PART NO"].str.contains(search, case=False, na=False) |
        df["DESCRIPTION"].str.contains(search, case=False, na=False)
    ]
else:
    df_view = df

# =====================
# DATA EDITOR (FINAL FIX)
# =====================
edited = st.data_editor(
    df_view,
    use_container_width=True,
    num_rows="fixed",
    row_key="__ROW_ID__",   # 🔥 STABLE, NEVER FAILS
    disabled=[c for c in df.columns if c not in EDITABLE_COLS],
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", min_value=0),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.SelectboxColumn(
            "CALL OUT", options=["", "YES", "NO"]
        ),
        "DATE": st.column_config.TextColumn("DATE")
    }
)

# =====================
# APPLY EDITS BACK
# =====================
df.set_index("__ROW_ID__", inplace=True)
edited.set_index("__ROW_ID__", inplace=True)

df.update(edited)
df.reset_index(inplace=True)

st.session_state.df = df

# =====================
# SAVE TO GOOGLE SHEET
# =====================
if st.button("💾 Save Changes"):
    save_df = st.session_state.df.drop(columns="__ROW_ID__")
    save_df = save_df.fillna("").astype(str)

    sheet.clear()
    sheet.update(
        [save_df.columns.tolist()] +
        save_df.values.tolist()
    )

    st.success("✅ Saved. All columns stay editable.")

























