import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

st.markdown("""
<div style="text-align:center;margin-bottom:10px">
  <h1 style="color:#005EB8;font-weight:900;letter-spacing:6px;">KONE</h1>
  <div style="font-size:18px;font-weight:600;">Lift Inventory Tracker</div>
</div>
""", unsafe_allow_html=True)

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

# ================= AUTH =================
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ================= LOAD DATA =================
values = sheet.get_all_values()
headers = values[0]
rows = values[1:]

df = pd.DataFrame(rows, columns=headers)

if df.empty:
    st.warning("Sheet is empty")
    st.stop()

df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view_df = df.copy()
if search:
    view_df = view_df[
        view_df.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= DISPLAY TABLE (READ ONLY) =================
st.subheader("📦 Inventory")
st.dataframe(
    view_df.drop(columns=["_ROW"]),
    use_container_width=True,
    height=420
)

# ================= EDIT SECTION =================
st.divider()
st.subheader("✏️ Edit Item")

row_map = {
    f"{r['PART NO']} | {r['DESCRIPTION']}": r["_ROW"]
    for _, r in view_df.iterrows()
}

selected = st.selectbox("Select Part", list(row_map.keys()))

if selected:
    row_no = row_map[selected]
    row = df[df["_ROW"] == row_no].iloc[0]

    with st.form("edit_form"):
        qty = st.number_input("QTY", value=int(row.get("QTY", 0)))
        lift_no = st.text_input("LIFT NO", value=row.get("LIFT NO", ""))
        call_out = st.text_input("CALL OUT", value=row.get("CALL OUT", ""))
        dt = st.date_input(
            "DATE",
            value=date.fromisoformat(row["DATE"])
            if row.get("DATE") else date.today()
        )

        save = st.form_submit_button("💾 Save")

    if save:
        col_index = {h: i + 1 for i, h in enumerate(headers)}

        sheet.update_cell(row_no, col_index["QTY"], qty)
        sheet.update_cell(row_no, col_index["LIFT NO"], lift_no)
        sheet.update_cell(row_no, col_index["CALL OUT"], call_out)
        sheet.update_cell(row_no, col_index["DATE"], dt.isoformat())

        st.success("✅ Updated successfully")
        st.rerun()










