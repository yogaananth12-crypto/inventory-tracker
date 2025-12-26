import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SAVE_URL = "PASTE_NEW_APPS_SCRIPT_WEB_APP_URL_HERE"

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Clean columns
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    def find(keys):
        for c in df.columns:
            for k in keys:
                if k in c:
                    return c
        return None

    # Rename columns
    df = df.rename(columns={
        find(["S.NO", "SNO"]): "S.NO",
        find(["PART"]): "PART NO",
        find(["DESC"]): "DESCRIPTION",
        find(["BOX"]): "BOX NO",
        find(["QTY"]): "QTY",
        find(["LIFT"]): "LIFT NO",
        find(["CALL"]): "CALL OUT",
        find(["DATE"]): "DATE",
    })

    # Keep required columns
    df = df[
        [
            "S.NO",
            "PART NO",
            "DESCRIPTION",
            "BOX NO",
            "QTY",
            "LIFT NO",
            "CALL OUT",
            "DATE",
        ]
    ]

    # Data types
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
    df["LIFT NO"] = df["LIFT NO"].astype(str)
    df["CALL OUT"] = df["CALL OUT"].astype(str)
    df["DATE"] = df["DATE"].astype(str)

    return df


# =========================
# UI
# =========================
st.title("🔧 Spare Parts Inventory Dashboard")

df = load_data()

# KPIs
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

st.subheader("📋 Edit Inventory (Editable fields highlighted)")

edited_df = st.data_editor(
    filtered_df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    use_container_width=True
)

# =========================
# SAVE TO GOOGLE SHEET
# =========================
if st.button("💾 Save Changes"):
    updates = []

    for _, r in edited_df.iterrows():
        updates.append({
            "part_no": str(r["PART NO"]),
            "qty": int(r["QTY"]),
            "lift_no": str(r["LIFT NO"]),
            "call_out": str(r["CALL OUT"]),
            "date": str(r["DATE"]),
        })

    with st.spinner("Saving changes..."):
        res = requests.post(SAVE_URL, json=updates, timeout=20)

    if res.status_code == 200:
        st.success("✅ Saved successfully")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("❌ Save failed. Check Apps Script.")
st.write(df.columns.tolist())

