import streamlit as st
import pandas as pd
import requests

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SAVE_URL = "https://script.google.com/macros/s/AKfycbw5Hv59GMNeQnsc_QNQKPIkUYYvBXa6qbGVT1Bro6ktvWKtPFOHrZNM1gAMLaNmhL8X4Q/exec"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(layout="wide")
st.title("📦 Inventory Tracker")

# ================= LOAD DATA =================
@st.cache_data(ttl=5)
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

# ================= SEARCH =================
search = st.text_input("🔍 Search Part No / Description")

if search:
    df = df[
        df["PART NO"].astype(str).str.contains(search, case=False, na=False) |
        df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# ================= EDIT TABLE =================
editable_cols = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

edited_df = st.data_editor(
    df,
    disabled=[c for c in df.columns if c not in editable_cols],
    hide_index=True,
    use_container_width=True
)

# ================= SAVE =================
if st.button("💾 SAVE CHANGES"):
    updates = []

    for i in range(len(df)):
        if not df.iloc[i][editable_cols].equals(edited_df.iloc[i][editable_cols]):
            updates.append({
                "sno": str(df.iloc[i]["S.NO"]),
                "qty": int(edited_df.iloc[i]["QTY"]),
                "lift_no": str(edited_df.iloc[i]["LIFT NO"]),
                "call_out": str(edited_df.iloc[i]["CALL OUT"]),
                "date": str(edited_df.iloc[i]["DATE"])
            })

    if updates:
        with st.spinner("Saving..."):
            r = requests.post(SAVE_URL, json={"updates": updates}, timeout=20)

        if r.status_code == 200:
            st.success("✅ Saved successfully")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("❌ Save failed. Check Apps Script.")
    else:
        st.info("No changes detected")













