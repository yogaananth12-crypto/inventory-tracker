import streamlit as st
import pandas as pd
import requests
import json

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SAVE_URL = "https://script.google.com/macros/s/AKfycbxyha6E0BNwYksazDMMW2cG2q5I8K6xZPFMfnpuN12Bo62ya1nRzLG9Z1ukCW4ZY7LKvw/exec"

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Clean columns
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # Auto detect columns
    def find_col(keys):
        for c in df.columns:
            for k in keys:
                if k in c:
                    return c
        return None

    rename_map = {
        find_col(["S.NO", "SNO"]): "S.NO",
        find_col(["PART"]): "PART NO",
        find_col(["DESC"]): "DESCRIPTION",
        find_col(["BOX"]): "BOX NO",
        find_col(["QTY", "QUANTITY"]): "QTY",
    }

    rename_map = {k: v for k, v in rename_map.items() if k}
    df = df.rename(columns=rename_map)

    df = df[["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]]

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    return df


# =========================
# UI
# =========================
st.title("🔧 Spare Parts Inventory Dashboard")

df = load_data()

# KPI
c1, c2, c3 = st.columns(3)
c1.metric("Total Parts", len(df))
c2.metric("Low Stock (≤3)", (df["QTY"] <= 3).sum())
c3.metric("Critical (≤1)", (df["QTY"] <= 1).sum())

# Search
search = st.text_input("🔍 Search Part No or Description")

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

st.subheader("📋 Edit QTY (only QTY is editable)")

edited_df = st.data_editor(
    filtered_df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    use_container_width=True,
    key="editor"
)

# =========================
# SAVE TO GOOGLE SHEET
# =========================
if st.button("💾 Save QTY"):
    updates = []

    for _, row in edited_df.iterrows():
        updates.append({
            "part_no": str(row["PART NO"]),
            "qty": int(row["QTY"])
        })

    with st.spinner("Saving changes..."):
        response = requests.post(
            SAVE_URL,
            json=updates,
            timeout=20
        )

    if response.status_code == 200:
        st.success("✅ Saved successfully")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("❌ Save failed. Check Apps Script.")

# =========================
# FOOTER
# =========================
with st.expander("🛠 Debug Info"):
    st.write("Columns:", list(df.columns))





























