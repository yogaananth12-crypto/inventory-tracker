import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="KONE Inventory",
    layout="wide",
)

# ================= GLOBAL STYLES =================
st.markdown("""
<style>
/* Mobile padding fix */
.block-container {
    padding-top: 1rem;
    padding-bottom: 6rem;
}

/* Header */
.kone-header {
    text-align: center;
    padding: 14px 0 12px 0;
    border-bottom: 1px solid #e0e0e0;
}

/* Logo */
.kone-logo {
    display: flex;
    justify-content: center;
    gap: 6px;
}

/* Logo boxes */
.kone-box {
    width: 48px;
    height: 48px;
    background: #1f4bff;
    color: white;
    font-size: 28px;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    font-family: Arial, Helvetica, sans-serif;
}

/* Subtitle */
.kone-subtitle {
    font-size: 15px;
    font-weight: 600;
    color: #444;
    margin-top: 6px;
}

/* Date */
.kone-date {
    font-size: 12px;
    color: #777;
}

/* Floating Save Button */
.floating-save {
    position: fixed;
    bottom: 14px;
    right: 14px;
    z-index: 9999;
}

.floating-save button {
    background-color: #1f4bff !important;
    color: white !important;
    border-radius: 50px !important;
    padding: 12px 20px !important;
    font-weight: 700 !important;
}

/* Table theme */
thead tr th {
    background-color: #f3f6ff !important;
}

/* Mobile logo scaling */
@media (max-width: 640px) {
    .kone-box {
        width: 40px;
        height: 40px;
        font-size: 24px;
    }
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
today = datetime.now().strftime("%d %b %Y")

st.markdown(f"""
<div class="kone-header">
    <div class="kone-logo">
        <div class="kone-box">K</div>
        <div class="kone-box">O</div>
        <div class="kone-box">N</div>
        <div class="kone-box">E</div>
    </div>
    <div class="kone-subtitle">Lift Inventory Tracker</div>
    <div class="kone-date">{today}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

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

for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search", placeholder="Search part no, lift no, etc.")

df_view = df.copy()
if search:
    df_view = df_view[
        df_view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= DATA EDITOR =================
edited_df = st.data_editor(
    df_view,
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in df_view.columns if c not in EDITABLE_COLS],
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", step=1),
        "LIFT NO": st.column_config.NumberColumn("LIFT NO", step=1),
        "CALL OUT": st.column_config.NumberColumn("CALL OUT", step=1),
        "DATE": st.column_config.TextColumn("DATE"),
        "_ROW": None,
    },
    key="editor",
)

# ================= FLOATING SAVE =================
st.markdown('<div class="floating-save">', unsafe_allow_html=True)
save_clicked = st.button("💾 Save")
st.markdown('</div>', unsafe_allow_html=True)

if save_clicked:
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
        st.success(f"✅ {updated} row(s) saved")
    else:
        st.info("No changes detected")





