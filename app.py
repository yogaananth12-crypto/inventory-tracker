import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ================= PAGE =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

st.markdown("""
<div style="text-align:center">
  <h1 style="color:#005EB8;letter-spacing:6px;">KONE</h1>
  <h3>Lift Inventory Tracker</h3>
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

# ================= LOAD =================
data = sheet.get_all_values()
headers = data[0]
rows = data[1:]

df = pd.DataFrame(rows, columns=headers)

# Force column types (THIS IS THE FIX)
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
df["LIFT NO"] = df["LIFT NO"].astype(str)
df["CALL OUT"] = df["CALL OUT"].astype(str)
df["DATE"] = df["DATE"].astype(str)

# Row number for saving
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= COLUMN ORDER =================
ORDER = [
    "PART NO",
    "DESCRIPTION",
    "BOX NO",
    "QTY",
    "LIFT NO",
    "CALL OUT",
    "DATE",
]

cols = [c for c in ORDER if c in view.columns]
view = view[cols + ["_ROW"]]

# ================= EDITOR =================
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "QTY": st.column_config.NumberColumn("QTY", step=1),
        "LIFT NO": st.column_config.TextColumn("LIFT NO"),
        "CALL OUT": st.column_config.TextColumn("CALL OUT"),
        "DATE": st.column_config.TextColumn("DATE"),
    },
    disabled=[c for c in cols if c not in EDITABLE],
    key="editor"
)

# ================= SAVE =================
if st.button("💾 Save Changes"):
    saved = 0

    for _, row in edited.iterrows():
        row_no = int(row["_ROW"])
        original = df[df["_ROW"] == row_no].iloc[0]

        updates = []
        changed = False

        for col in headers:
            new = str(row[col]) if col in row else ""
            old = str(original[col])

            updates.append(new)
            if new != old:
                changed = True

        if changed:
            sheet.update(f"A{row_no}", [updates])
            saved += 1

    if saved:
        st.success(f"✅ {saved} row(s) updated")
        st.rerun()
    else:
        st.info("No changes detected")











