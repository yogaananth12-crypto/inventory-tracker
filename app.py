import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Lift Inventory", layout="wide")

# ================= HEADER =================
st.markdown(
    """
    <div style="text-align:center; padding:10px 0;">
        <div style="
            display:inline-block;
            background:#0071CE;
            color:white;
            font-size:36px;
            font-weight:700;
            padding:8px 24px;
            border-radius:6px;
            letter-spacing:2px;">
            KONE
        </div>
        <div style="margin-top:8px; font-size:18px; font-weight:500;">
            Lift Inventory Tracker
        </div>
        <div style="font-size:14px; color:#666;">
            {today}
        </div>
    </div>
    """.format(today=date.today().strftime("%d %b %Y")),
    unsafe_allow_html=True
)

st.divider()

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

EDITABLE_COLS = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

# ================= AUTH =================
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes,
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

# Add hidden row pointer for saving
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[
        view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in view.columns if c not in EDITABLE_COLS],
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes", use_container_width=True):
    changed_rows = 0

    with st.spinner("Saving changes..."):
        for _, row in edited.iterrows():
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
                changed_rows += 1

    if changed_rows:
        st.toast("✅ Saved successfully", icon="✅")
        st.success(f"{changed_rows} row(s) updated")
    else:
        st.info("No changes detected")














