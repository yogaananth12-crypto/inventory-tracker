import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Inventory Tracker", layout="wide")

# =========================
# CONFIG
# =========================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

COLUMNS = [
    "S.NO",
    "PART NO",
    "DESCRIPTION",
    "BOX NO",
    "QTY",
    "LIFT NO",
    "CALL OUT",
    "DATE"
]

EDITABLE = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

# =========================
# AUTH
# =========================
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1

# =========================
# LOAD ONCE
# =========================
if "df" not in st.session_state:
    df = pd.DataFrame(sheet.get_all_records())
    df.columns = df.columns.astype(str).str.strip().str.upper()

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLUMNS]

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
    df["LIFT NO"] = df["LIFT NO"].astype(str)
    df["CALL OUT"] = df["CALL OUT"].astype(str)
    df["DATE"] = df["DATE"].astype(str)

    st.session_state.df = df

st.title("📦 Spare Parts Inventory")

# =========================
# SEARCH
# =========================
search = st.text_input("🔍 Search Part No / Description")

view_df = st.session_state.df.copy()

if search:
    view_df = view_df[
        view_df["PART NO"].str.contains(search, case=False, na=False) |
        view_df["DESCRIPTION"].str.contains(search, case=False, na=False)
    ]

# =========================
# EDITOR (STABLE)
# =========================
edited_df = st.data_editor(
    view_df,
    use_container_width=True,
    num_rows="fixed",
    disabled=[c for c in COLUMNS if c not in EDITABLE],
    key="inventory_editor",
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", min_value=0),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.SelectboxColumn(
            "CALL OUT",
            options=["", "YES", "NO"]
        ),
        "DATE": st.column_config.TextColumn("DATE")
    }
)

# =========================
# MERGE BACK
# =========================
st.session_state.df.update(edited_df)

# =========================
# SAVE
# =========================
if st.button("💾 Save Changes"):
    with st.spinner("Saving to Google Sheets..."):
        save_df = st.session_state.df.copy().fillna("").astype(str)

        sheet.clear()
        sheet.update(
            [save_df.columns.tolist()] +
            save_df.values.tolist()
        )

    st.success("✅ Saved. Editable again immediately.")























