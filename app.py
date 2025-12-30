import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER =================
st.markdown(
    """
    <h1 style="text-align:center; color:#003A8F; margin-bottom:0;">KONE</h1>
    <p style="text-align:center; margin-top:4px; color:#444;">
        Inventory Management System
    </p>
    """,
    unsafe_allow_html=True
)

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

KEY_COL = "S.NO"

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
df = pd.DataFrame(sheet.get_all_records())

if df.empty:
    st.error("Google Sheet is empty")
    st.stop()

# ---------- FORCE SAFE DATA TYPES ----------
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df["LIFT NO"].astype(str)
df["CALL OUT"] = pd.to_numeric(df["CALL OUT"], errors="coerce").fillna(0).astype(int)
df["DATE"] = df["DATE"].astype(str)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "S.NO": st.column_config.TextColumn("S.NO", disabled=True),
        "PART NO": st.column_config.TextColumn("PART NO", disabled=True),
        "DESCRIPTION": st.column_config.TextColumn("DESCRIPTION", disabled=True),
        "BOX NO": st.column_config.TextColumn("BOX NO", disabled=True),

        "QTY": st.column_config.NumberColumn("QTY"),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.NumberColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),
    },
    key="editor"
)

# ================= SAVE =================
if st.button("💾 SAVE CHANGES"):
    updated = 0

    for _, row in edited.iterrows():
        s_no = int(row["S.NO"])
        sheet_row = s_no + 1  # header row offset

        original = df[df["S.NO"] == s_no].iloc[0]

        new_values = []
        changed = False

        for col in df.columns:
            new = "" if pd.isna(row[col]) else str(row[col])
            old = "" if pd.isna(original[col]) else str(original[col])

            if new != old:
                changed = True

            new_values.append(new)

        if changed:
            sheet.update(f"A{sheet_row}", [new_values])
            updated += 1

    if updated:
        st.success(f"✅ {updated} row(s) saved")
    else:
        st.info("No changes detected")















