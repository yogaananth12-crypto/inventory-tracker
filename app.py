import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

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
# LOAD DATA
# =========================
df = pd.DataFrame(sheet.get_all_records())

df.columns = df.columns.astype(str).str.strip().str.upper()

# Ensure columns exist
for col in COLUMNS:
    if col not in df.columns:
        df[col] = ""

df = df[COLUMNS]

# Force correct dtypes
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df["LIFT NO"].astype(str)
df["CALL OUT"] = df["CALL OUT"].astype(str)
df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

st.title("📦 Spare Parts Inventory")

# =========================
# SEARCH
# =========================
search = st.text_input("🔍 Search Part No / Description")

if search:
    df = df[
        df["PART NO"].str.contains(search, case=False, na=False) |
        df["DESCRIPTION"].str.contains(search, case=False, na=False)
    ]

# =========================
# DATA EDITOR
# =========================
edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    disabled=[c for c in COLUMNS if c not in EDITABLE],
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", min_value=0),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.SelectboxColumn(
            "CALL OUT",
            options=["", "YES", "NO"]
        ),
        "DATE": st.column_config.DateColumn("DATE")
    }
)

# =========================
# SAVE
# =========================
if st.button("💾 Save Changes"):
    with st.spinner("Saving to Google Sheets..."):
        save_df = edited_df.copy()
        save_df["DATE"] = save_df["DATE"].astype(str)

        sheet.clear()
        sheet.update(
            [save_df.columns.tolist()] +
            save_df.astype(str).values.tolist()
        )

    st.success("✅ Saved successfully. All users see updates.")






















