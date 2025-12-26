import streamlit as st
import pandas as pd
import requests
import math

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SAVE_URL = "https://script.google.com/macros/s/AKfycbx0WFr35KlCjlSgCwOJB0waE86knqMt__xDy1bNKolTVdxve6LV4bwR-E9PJe13K8u8Gw/exec"

@st.cache_data(ttl=3)
def load_data():
    df = pd.read_csv(CSV_URL)

    df.columns = df.columns.str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # Ensure columns exist
    for col in ["LIFT NO", "CALL OUT", "DATE"]:
        if col not in df.columns:
            df[col] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    # 🔑 Google Sheet row number
    df["__ROW__"] = df.index + 2

    return df

st.title("🔧 Spare Parts Inventory")

df = load_data()

edited_df = st.data_editor(
    df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "__ROW__"],
    use_container_width=True
)

def safe(val):
    if val is None:
        return ""
    if isinstance(val, float) and math.isnan(val):
        return ""
    return str(val)

if st.button("💾 Save Changes"):
    payload = []

    for _, row in edited_df.iterrows():
        payload.append({
            "row": int(row["__ROW__"]),
            "qty": int(row["QTY"]),
            "lift_no": safe(row["LIFT NO"]),
            "call_out": safe(row["CALL OUT"]),
            "date": safe(row["DATE"]),
        })

    with st.spinner("Saving to Google Sheet..."):
        r = requests.post(SAVE_URL, json=payload, timeout=20)

    if r.status_code == 200:
        st.success("✅ All rows saved accurately (100%)")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("❌ Save failed")




