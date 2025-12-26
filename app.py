import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SAVE_URL = "https://script.google.com/macros/s/AKfycbyCgYxOPz7M7pWRKC0fSMxSyiOzx6TtEHb6irnVwBm8QdGzZpV-_J_f3edls6jz-KxS_Q/exec"

@st.cache_data(ttl=3)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    for col in ["LIFT NO", "CALL OUT", "DATE"]:
        if col not in df.columns:
            df[col] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    return df

st.title("🔧 Spare Parts Inventory")

df = load_data()

edited_df = st.data_editor(
    df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    use_container_width=True
)

if st.button("💾 Save Changes"):
    payload = []

    for _, row in edited_df.iterrows():
        payload.append({
            "sno": str(row["S.NO"]),
            "qty": int(row["QTY"]),
            "lift_no": "" if pd.isna(row["LIFT NO"]) else str(row["LIFT NO"]),
            "call_out": "" if pd.isna(row["CALL OUT"]) else str(row["CALL OUT"]),
            "date": "" if pd.isna(row["DATE"]) else str(row["DATE"]),
        })

    payload = json.loads(json.dumps(payload))

    with st.spinner("Saving to Google Sheet..."):
        r = requests.post(
            SAVE_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=20
        )

    if r.status_code == 200:
        st.success("✅ Sheet updated successfully (stable & accurate)")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("❌ Save failed")








