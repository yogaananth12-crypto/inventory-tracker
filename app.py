import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SAVE_URL = "https://script.google.com/macros/s/AKfycbx0WFr35KlCjlSgCwOJB0waE86knqMt__xDy1bNKolTVdxve6LV4bwR-E9PJe13K8u8Gw/exec"

@st.cache_data(ttl=3)
def load_data():
    df = pd.read_csv(CSV_URL)

    df.columns = df.columns.str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # Ensure optional columns exist
    for col in ["LIFT NO", "CALL OUT", "DATE"]:
        if col not in df.columns:
            df[col] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    # 🔑 INTERNAL ROW NUMBER (HIDDEN)
    df["_ROW"] = df.index + 2  # Google Sheet row

    return df

st.title("🔧 Spare Parts Inventory")

df = load_data()

# 👁️ HIDE INTERNAL COLUMN FROM USERS
display_df = df.drop(columns=["_ROW"])

edited_df = st.data_editor(
    display_df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    use_container_width=True
)

if st.button("💾 Save Changes"):
    payload = []

    for i, row in edited_df.iterrows():
        payload.append({
            "row": int(df.loc[i, "_ROW"]),  # use hidden row
            "qty": int(row["QTY"]),
            "lift_no": "" if pd.isna(row["LIFT NO"]) else str(row["LIFT NO"]),
            "call_out": "" if pd.isna(row["CALL OUT"]) else str(row["CALL OUT"]),
            "date": "" if pd.isna(row["DATE"]) else str(row["DATE"]),
        })

    payload = json.loads(json.dumps(payload))  # force JSON-safe

    with st.spinner("Saving changes..."):
        r = requests.post(
            SAVE_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=20
        )

    if r.status_code == 200:
        st.success("✅ Saved successfully (synced for all users)")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("❌ Save failed")







