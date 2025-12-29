import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Inventory Tracker", layout="wide")

# =============================
# CONFIG
# =============================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# =============================
# AUTH
# =============================
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1

# =============================
# LOAD DATA
# =============================
data = sheet.get_all_records()
df = pd.DataFrame(data)

if df.empty:
    st.error("Sheet is empty or headers missing.")
    st.stop()

st.title("📦 Spare Parts Inventory")

# =============================
# SEARCH BAR
# =============================
search = st.text_input("🔍 Search Part No / Description")

if search:
    df = df[
        df["PART NO"].astype(str).str.contains(search, case=False, na=False) |
        df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# =============================
# EDITABLE TABLE
# =============================
st.subheader("✏️ Edit Inventory")

editable_columns = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

edited_df = st.data_editor(
    df,
    use_container_width=True,
    disabled=[c for c in df.columns if c not in editable_columns],
    num_rows="fixed"
)

# =============================
# SAVE BUTTON
# =============================
if st.button("💾 Save Changes to Google Sheet"):
    with st.spinner("Saving..."):
        # Convert everything to string (Google Sheets safe)
        edited_df = edited_df.fillna("").astype(str)

        sheet.clear()
        sheet.update(
            [edited_df.columns.tolist()] +
            edited_df.values.tolist()
        )

    st.success("✅ Saved! All users will see updates.")


















