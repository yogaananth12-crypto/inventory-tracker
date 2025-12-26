import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

SAVE_URL = "https://script.google.com/macros/s/AKfycbwrAPYoSJbu4o_-nbpbZf_N-VQH3DusxMEt7DUXIcwQQmJoQa1Uj_L3uyuiO082bAqjjA/exec"

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_CSV_URL)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    required = [
        "S.NO", "PART NO", "DESCRIPTION", "BOX NO",
        "QTY", "LIFT NO", "CALL OUT", "DATE"
    ]

    for col in required:
        if col not in df.columns:
            df[col] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
    return df[required]

df = load_data()

# =========================
# SEARCH
# =========================
search = st.text_input("🔍 Search Part / Description / Box").lower()

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        df["PART NO"].str.lower().str.contains(search, na=False)
        | df["DESCRIPTION"].str.lower().str.contains(search, na=False)
        | df["BOX NO"].str.lower().str.contains(search, na=False)
    ]

# =========================
# EDITOR
# =========================
edited_df = st.data_editor(
    filtered_df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    hide_index=True,
    use_container_width=True
)
if st.button("💾 Save Changes"):
    r = requests.post(SAVE_URL)
    st.write("STATUS:", r.status_code)
    st.write("TEXT:", r.text)












