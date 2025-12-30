import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= CSS FIX =================
st.markdown("""
<style>
/* Force horizontal scroll */
[data-testid="stDataEditor"] {
    overflow-x: auto;
}

/* Fix header clarity */
.kone-title {
    font-size: 60px;
    font-weight: 900;
    letter-spacing: 10px;
    color: #005EB8;
    margin-bottom: -10px;
}
.subtitle {
    font-size: 22px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center">
  <div class="kone-title">KONE</div>
  <div class="subtitle">Lift Inventory Tracker</div>
</div>
""", unsafe_allow_html=True)

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_NAME = "Sheet1"

EDITABLE = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

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

# Force correct types
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df["LIFT NO"].astype(str)
df["CALL OUT"] = df["CALL OUT"].astype(str)
df["DATE"] = df["DATE"].astype(str)

# Row number for update
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= COLUMN ORDER (IMPORTANT) =================
COLUMN_ORDER = [
    "PART NO",
    "DESCRIPTION",
    "BOX NO",
    "QTY",
    "LIFT NO",
    "CALL OUT",
    "DATE",
]

view = view[COLUMN_ORDER + ["_ROW"]]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "PART NO": st.column_config.TextColumn("PART NO", width=120),
        "DESCRIPTION": st.column_config.TextColumn("DESCRIPTION", width=300),
        "BOX NO": st.column_config.TextColumn("BOX NO", width=120),
        "QTY": st.column_config.NumberColumn("QTY", step=1, width=80),
        "LIFT NO": st.column_config.TextColumn("LIFT NO", width=150),
        "CALL OUT": st.column_config.TextColumn("CALL OUT", width=150),
        "DATE": st.column_config.TextColumn("DATE", width=130),
    },
    disabled=[c for c in COLUMN_ORDER if c not in EDITABLE],
    frozen_columns=3,
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    count = 0

    for _, row in edited.iterrows():
        row_no = int(row["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        new_values = []
        changed = False

        for col in headers:
            new = str(row[col]) if col in row else ""
            old = str(original[col])

            new_values.append(new)
            if new != old:
                changed = True

        if changed:
            sheet.update(f"A{row_no}", [new_values])
            count += 1

    if count:
        st.success(f"✅ {count} row(s) updated successfully")
        st.rerun()
    else:
        st.info("No changes detected")











