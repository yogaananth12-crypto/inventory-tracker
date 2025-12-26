import json
import streamlit as st
import pandas as pd
import requests

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory (Shared Live)")

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SAVE_URL = "https://script.google.com/macros/s/AKfycbw3uSVNIBC01cDjtMNrVfuwnmO16OA0rb_dgoRDRwZzafigwJrsJKUfK_qFzvUx1FwJ0Q/exec"

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# ================= LOAD DATA =================
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.upper()
    df = df.dropna(how="all")

    if "QTY" in df.columns:
        df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    return df


df = load_data()

# ================= SEARCH =================
search = st.text_input("🔍 Search Part No or Description")

if search:
    df = df[
        df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# ================= EDIT TABLE =================
edited_df = st.data_editor(
    df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    use_container_width=True,
    num_rows="fixed"
)

if st.button("💾 Save QTY"):
    updates = []

    for _, row in edited_df.iterrows():
        updates.append({
            "part_no": str(row["PART NO"]),
            "qty": int(row["QTY"])
        })

       st.spinner("Saving changes..."):
        response = requests.post(
            SAVE_URL,
            data=json.dumps(updates),          # 👈 IMPORTANT
            headers={"Content-Type": "application/json"},
            timeout=20
        )

    if response.status_code == 200:
        st.success("✅ Saved successfully!")
        st.rerun()
    else:
        st.error("❌ Save failed")


# ================= FOOTER =================
st.caption("ℹ️ After one user saves, other users press F5 to see updates")




























