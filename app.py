import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

# ---------------- AUTH ----------------
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ---------------- LOAD ----------------
data = sheet.get_all_records()
df = pd.DataFrame(data)

df.columns = df.columns.str.strip().str.upper()

required = ["S.NO", "PART NO", "DESCRIPTION", "BOX NO",
            "QTY", "LIFT NO", "CALL OUT", "DATE"]

for c in required:
    if c not in df.columns:
        df[c] = ""

df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

# ---------------- SEARCH ----------------
search = st.text_input("🔍 Search Part No or Description")

view_df = df.copy()
if search:
    view_df = view_df[
        view_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | view_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# ---------------- EDIT ----------------
edited_df = st.data_editor(
    view_df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    hide_index=True,
    use_container_width=True
)

# ---------------- SAVE ----------------
if st.button("💾 SAVE"):
    df_idx = df.set_index("S.NO")
    edited_idx = edited_df.set_index("S.NO")

    updates = []

    for sno in edited_idx.index:
        for col in ["QTY", "LIFT NO", "CALL OUT", "DATE"]:
            if df_idx.loc[sno, col] != edited_idx.loc[sno, col]:
                row_num = df_idx.index.get_loc(sno) + 2
                col_num = df.columns.get_loc(col) + 1
                updates.append({
                    "range": gspread.utils.rowcol_to_a1(row_num, col_num),
                    "values": [[edited_idx.loc[sno, col]]]
                })

    if updates:
        sheet.batch_update([{
            "range": u["range"],
            "values": u["values"]
        } for u in updates])
        st.success("Saved to Google Sheet ✅")
    else:
        st.info("No changes detected")

















