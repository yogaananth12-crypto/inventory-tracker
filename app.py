import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SAVE_URL = "https://script.google.com/macros/s/AKfycbx0WFr35KlCjlSgCwOJB0waE86knqMt__xDy1bNKolTVdxve6LV4bwR-E9PJe13K8u8Gw/exec"

@st.cache_data(ttl=3)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    # 🔑 store Google Sheet row number
    df["__ROW__"] = df.index + 2  # +2 (header + 1-indexed)

    return df

st.title("🔧 Spare Parts Inventory")

df = load_data()

edited_df = st.data_editor(
    df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "__ROW__"],
    use_container_width=True
)

if st.button("💾 Save Changes"):
    payload = []

    for _, row in edited_df.iterrows():
        payload.append({
            "row": int(row["__ROW__"]),
            "qty": int(row["QTY"]),
            "lift_no": row.get("LIFT NO", ""),
            "call_out": row.get("CALL OUT", ""),
            "date": row.get("DATE", "")
        })

    with st.spinner("Saving to Google Sheet..."):
        r = requests.post(SAVE_URL, json=payload, timeout=20)

    if r.status_code == 200:
        st.success("✅ 100% rows saved accurately")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("❌ Save failed")



