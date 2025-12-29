import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER =================
st.markdown("""
<div style="text-align:center;margin-bottom:20px">
  <h1 style="color:#005EB8;font-weight:900;letter-spacing:6px;">KONE</h1>
  <div style="font-size:18px;font-weight:600;">Lift Inventory Tracker</div>
</div>
""", unsafe_allow_html=True)

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

EDITABLE_COLS = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

# ================= AUTH =================
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

# ================= LOAD DATA =================
data = sheet.get_all_values()
headers = data[0]
rows = data[1:]

df = pd.DataFrame(rows, columns=headers)

if df.empty:
    st.error("Sheet is empty")
    st.stop()

# ================= FORCE SAFE TYPES =================
for col in df.columns:
    df[col] = df[col].astype(str)

if "QTY" in df.columns:
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

# ================= COLUMN ORDER (CRITICAL) =================
desired_order = [
    "PART NO",
    "DESCRIPTION",
    "BOX NO",
    "QTY",
    "LIFT NO",
    "CALL OUT",
    "DATE"
]

final_cols = [c for c in desired_order if c in df.columns]
df = df[final_cols]

# ================= ADD ROW INDEX =================
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view_df = df.copy()
if search:
    view_df = view_df[
        view_df.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    view_df,
    hide_index=True,
    use_container_width=True,
    disabled=[c for c in view_df.columns if c not in EDITABLE_COLS],
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes", use_container_width=True):
    updated = 0

    for _, row in edited_df.iterrows():
        row_no = int(row["_ROW"])

        values = []
        for col in headers:
            if col in edited_df.columns:
                val = row[col]
            else:
                val = sheet.cell(row_no, headers.index(col) + 1).value

            values.append("" if pd.isna(val) else str(val))

        sheet.update(f"A{row_no}", [values])
        updated += 1

    st.success(f"✅ {updated} row(s) saved")









