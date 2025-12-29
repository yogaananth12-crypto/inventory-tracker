import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 6rem; }
.header { text-align:center; margin-bottom:12px; }
.logo { display:flex; justify-content:center; gap:6px; }
.box {
    width:46px; height:46px;
    background:#1f4bff; color:white;
    font-size:26px; font-weight:900;
    display:flex; align-items:center; justify-content:center;
    border-radius:4px;
}
.subtitle { font-weight:600; color:#444; }
.date { font-size:12px; color:#777; }

.save {
    position:fixed; bottom:14px; right:14px; z-index:9999;
}
.save button {
    background:#1f4bff !important;
    color:white !important;
    border-radius:50px !important;
    padding:12px 22px !important;
    font-weight:700 !important;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
today = datetime.now().strftime("%d %b %Y")
st.markdown(f"""
<div class="header">
  <div class="logo">
    <div class="box">K</div><div class="box">O</div>
    <div class="box">N</div><div class="box">E</div>
  </div>
  <div class="subtitle">Lift Inventory Tracker</div>
  <div class="date">{today}</div>
</div>
""", unsafe_allow_html=True)

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
    st.secrets["gcp_service_account"], scopes=scopes
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ================= LOAD DATA =================
df = pd.DataFrame(sheet.get_all_records())
if df.empty:
    st.stop()

# 🔴 CRITICAL FIX: FORCE STRING TYPE
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].astype(str)

df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")
df_view = df.copy()
if search:
    df_view = df_view[df_view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    df_view,
    hide_index=True,
    use_container_width=True,
    disabled=[c for c in df_view.columns if c not in EDITABLE_COLS],
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", step=1),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.TextColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),
        "_ROW": None,
    },
    key="editor",
)

# ================= SAVE =================
st.markdown('<div class="save">', unsafe_allow_html=True)
save = st.button("💾 Save")
st.markdown('</div>', unsafe_allow_html=True)

if save:
    updated = 0
    for _, row in edited_df.iterrows():
        row_no = int(row["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        values, changed = [], False
        for col in df.columns:
            if col == "_ROW":
                continue
            new = "" if pd.isna(row[col]) else str(row[col])
            old = "" if pd.isna(original[col]) else str(original[col])
            if new != old:
                changed = True
            values.append(new)

        if changed:
            sheet.update(f"A{row_no}", [values])
            updated += 1

    st.success(f"✅ {updated} row(s) saved")







