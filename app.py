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

REQUIRED_COLUMNS = [
    "S.NO",
    "PART NO",
    "DESCRIPTION",
    "BOX NO",
    "QTY",
    "LIFT NO",
    "CALL OUT",
    "DATE"
]

EDITABLE_COLUMNS = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

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

if df.empty:
    st.error("❌ Sheet is empty or headers missing")
    st.stop()

# Normalize column names
df.columns = df.columns.astype(str).str.strip().str.upper()

# Ensure required columns exist
for col in REQUIRED_COLUMNS:
    if col not in df.columns:
        df[col] = ""

# Reorder columns
df = df[REQUIRED_COLUMNS]

st.title("📦 Spare Parts Inventory")

# =========================
# SEARCH BAR
# =========================
search = st.text_input("🔍 Search Part No or Description")

if search:
    df = df[
        df["PART NO"].astype(str).str.contains(search, case=False, na=False) |
        df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# =========================
# EDIT TABLE
# =========================
edited_df = st.data_editor(
    df,
    use_container_width=True,
    disabled=[c for c in df.columns if c not in EDITABLE_COLUMNS],
    num_rows="fixed"
)

# =========================
# SAVE
# =========================
if st.button("💾 Save Changes"):
    with st.spinner("Saving to Google Sheets..."):
        edited_df = edited_df.fillna("").astype(str)

        sheet.clear()
        sheet.update(
            [edited_df.columns.tolist()] +
            edited_df.values.tolist()
        )

    st.success("✅ Saved successfully. All users will see updates.")




















