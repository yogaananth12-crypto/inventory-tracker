import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory (Shared Live)")

# ================= CONFIG =================
SHEET_ID = "PASTE_YOUR_SHEET_ID_HERE"
SHEET_NAME = "Sheet1"
APPS_SCRIPT_URL = "PASTE_WEB_APP_URL_HERE"

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# ================= LOAD DATA =================
@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.upper()
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)
    return df

df = load_data()

# ================= SEARCH =================
search = st.text_input("🔍 Search Part No / Description")

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False) |
        filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# ================= EDIT =================
edited_df = st.data_editor(
    filtered_df,
    use_container_width=True,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    num_rows="fixed"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    for _, row in edited_df.iterrows():
        payload = {
            "part_no": row["PART NO"],
            "qty": int(row["QTY"])
        }
        requests.post(APPS_SCRIPT_URL, json=payload)

    st.success("✅ Changes saved for ALL users")
    st.cache_data.clear()






















