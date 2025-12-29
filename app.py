import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER =================
st.markdown("""
<div style="text-align:center;margin-bottom:24px">
  <div style="display:flex;justify-content:center;gap:8px">
    <div style="width:52px;height:52px;background:#005EB8;color:white;
                font-size:32px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">K</div>
    <div style="width:52px;height:52px;background:#005EB8;color:white;
                font-size:32px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">O</div>
    <div style="width:52px;height:52px;background:#005EB8;color:white;
                font-size:32px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">N</div>
    <div style="width:52px;height:52px;background:#005EB8;color:white;
                font-size:32px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">E</div>
  </div>
  <div style="font-size:18px;font-weight:700;margin-top:6px">
    Lift Inventory Tracker
  </div>
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
records = sheet.get_all_records()
df = pd.DataFrame(records)

if df.empty:
    st.error("Google Sheet is empty")
    st.stop()

# ================= FORCE TYPES =================
df["QTY"] = pd.to_numeric(df.get("QTY", 0), errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df.get("LIFT NO", "").astype(str)
df["CALL OUT"] = df.get("CALL OUT", "").astype(str)
df["DATE"] = df.get("DATE", "").astype(str)

# Read-only columns (force string to prevent editor issues)
for col in ["PART NO", "DESCRIPTION", "BOX NO"]:
    if col in df.columns:
        df[col] = df[col].astype(str)

# Stable row reference
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search (Part No / Description / Lift No)")

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
    column_config={
        "PART NO": st.column_config.TextColumn("PART NO", disabled=True),
        "DESCRIPTION": st.column_config.TextColumn(
            "DESCRIPTION", width="large", disabled=True
        ),
        "BOX NO": st.column_config.TextColumn("BOX NO", disabled=True),

        "QTY": st.column_config.NumberColumn("QTY", min_value=0),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.TextColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),

        "_ROW": None
    },
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes", use_container_width=True):
    updates = 0

    for _, row in edited_df.iterrows():
        row_no = int(row["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        values = []
        changed = False

        for col in df.columns:
            if col == "_ROW":
                continue

            new_val = "" if pd.isna(row[col]) else str(row[col])
            old_val = "" if pd.isna(original[col]) else str(original[col])

            if new_val != old_val:
                changed = True

            values.append(new_val)

        if changed:
            sheet.update(f"A{row_no}", [values])
            updates += 1

    if updates:
        st.success(f"✅ {updates} row(s) saved")
    else:
        st.info("No changes detected")









