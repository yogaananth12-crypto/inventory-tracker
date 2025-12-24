import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard")

SHEET_ID = "PASTE_YOUR_SHEET_ID_HERE"
SHEET_NAME = "Sheet1"   # change if your tab name is different

# =========================
# GOOGLE SHEETS CONNECTION
# =========================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=5)
def load_data():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Clean column names
    df.columns = df.columns.astype(str).str.strip().str.upper()

    # Ensure columns
    for col in ["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]:
        if col not in df.columns:
            df[col] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    # Priority
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"

    return df

df = load_data()

# =========================
# METRICS
# =========================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Parts", len(df))
c2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
c3.metric("High", (df["PRIORITY LEVEL"] == "HIGH").sum())
c4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())

# =========================
# SEARCH
# =========================
st.subheader("📋 Spare Parts List")
search = st.text_input("🔍 Search Part Number or Description")

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# =========================
# EDITABLE TABLE (QTY ONLY)
# =========================
edited_df = st.data_editor(
    filtered_df,
    use_container_width=True,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "PRIORITY LEVEL"]
)

# =========================
# SAVE TO GOOGLE SHEETS
# =========================
if st.button("💾 Save Changes"):
    try:
        for i, row in edited_df.iterrows():
            sheet.update_cell(i + 2, 5, int(row["QTY"]))  # QTY column

        st.cache_data.clear()
        st.success("✅ Quantity updated for ALL users!")

    except Exception as e:
        st.error(f"❌ Error saving data: {e}")






















