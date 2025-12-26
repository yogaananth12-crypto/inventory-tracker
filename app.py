import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SAVE_URL ="https://script.google.com/macros/s/AKfycbytnU2dNxvfVyhR9E9vIu8YiRn0CCiV5vl-Z28jikDe-x8V8hp9zuOF8jcaNnAdXxUECA/exec"

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    def find(keys):
        for c in df.columns:
            for k in keys:
                if k in c:
                    return c
        return None

    df = df.rename(columns={
        find(["S.NO", "SNO"]): "S.NO",
        find(["PART"]): "PART NO",
        find(["DESC"]): "DESCRIPTION",
        find(["BOX"]): "BOX NO",
        find(["QTY"]): "QTY"
    })

    df = df[["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]]
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    return df


st.title("🔧 Spare Parts Inventory Dashboard")

df = load_data()

search = st.text_input("🔍 Search")

if search:
    df = df[
        df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

edited_df = st.data_editor(
    df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    use_container_width=True
)

if st.button("💾 Save QTY"):
    updates = []
    for _, r in edited_df.iterrows():
        updates.append({"part_no": r["PART NO"], "qty": int(r["QTY"])})

    with st.spinner("Saving changes..."):
        res = requests.post(SAVE_URL, json=updates, timeout=20)

    if res.status_code == 200:
        st.success("Saved")
        st.cache_data.clear()
        st.rerun()
    else:
        st.error("Save failed")
