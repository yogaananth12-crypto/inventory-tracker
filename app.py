import streamlit as st
import pandas as pd
import requests
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory (shared live)")
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SAVE_URL = "https://script.google.com/macros/s/AKfycbzr0HSp2GQKW8MNZi2WfZA5SP3XJOjgbHa_P0g3803_yVVgAFcak_6nV1_Tk31TJmad/exec"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.upper()

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Ensure QTY is numeric
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

# ================= SAVE =================
if st.button("💾 Save QTY"):
    updates = []
for _, row in edited_df.iterrows():
        updates.append({
            "part_no": row["PART NO"],
            "qty": int(row["QTY"])
        })
st.spinner("Saving changes...")
response = requests.post(SAVE_URL, json=updates)
if response.status_code == 200:
        st.success("✅ Saved successfully! Refreshing data...")
        st.rerun()
    else:
        st.error("❌ Save failed. Check Apps Script.")

# ================= FOOTER =================
st.caption("ℹ️ After one user saves, other users press F5 to see updates")



























