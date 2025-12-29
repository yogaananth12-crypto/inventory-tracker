import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="KONE Inventory",
    layout="wide"
)

# ================= HEADER =================
st.markdown("""
<div style="text-align:center;margin-bottom:10px">
  <div style="display:flex;justify-content:center;gap:6px">
    <div style="width:50px;height:50px;background:#005EB8;color:white;
                font-size:30px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">K</div>
    <div style="width:50px;height:50px;background:#005EB8;color:white;
                font-size:30px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">O</div>
    <div style="width:50px;height:50px;background:#005EB8;color:white;
                font-size:30px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">N</div>
    <div style="width:50px;height:50px;background:#005EB8;color:white;
                font-size:30px;font-weight:900;display:flex;
                align-items:center;justify-content:center;border-radius:6px;">E</div>
  </div>
  <div style="font-size:18px;font-weight:700;margin-top:4px">
    Spare Parts Inventory
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

# Ensure editable columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# Convert types (IMPORTANT)
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df["LIFT NO"].astype(str)
df["CALL OUT"] = df["CALL OUT"].astype(str)
df["DATE"] = df["DATE"].astype(str)

# Add stable Google Sheet row index
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search Part No / Description")

view_df = df.copy()
if search:
    view_df = view_df[
        view_df.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    view_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", min_value=0),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.TextColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),
        "_ROW": None
    },
    key="editor"
)

# ================= SAVE BUTTON =================
st.markdown(
    "<div style='position:fixed;bottom:20px;right:20px'>",
    unsafe_allow_html=True
)

if st.button("💾 Save Changes", use_container_width=True):
    updated = 0

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
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) saved to Google Sheet")
    else:
        st.info("No changes detected")

st.markdown("</div>", unsafe_allow_html=True)








