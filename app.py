import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE =================
st.set_page_config(page_title="KONE Lift Inventory", layout="wide")

# ===== BACKGROUND =====
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#e6f0fa 0%,#ffffff 45%,#f2f7fc 100%);
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
today = date.today().strftime("%d %b %Y")

st.markdown(
    f"""
    <style>
    .header {{
        text-align: center;
        margin-bottom: 20px;
    }}
    .kone {{
        display: inline-flex;
        gap: 6px;
    }}
    .kone span {{
        width: 50px;
        height: 50px;
        background: #005EB8;
        color: white;
        font-size: 32px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: Arial, Helvetica, sans-serif;
    }}
    .subtitle {{
        margin-top: 10px;
        font-size: 20px;
        font-weight: 600;
    }}
    .date {{
        font-size: 14px;
        color: #555;
    }}
    </style>

    <div class="header">
        <div class="kone">
            <span>K</span><span>O</span><span>N</span><span>E</span>
        </div>
        <div class="subtitle">Lift Inventory Tracker</div>
        <div class="date">{today}</div>
    </div>
    """,
    unsafe_allow_html=True
)


# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
MAIN_SHEET = "Sheet1"
HISTORY_SHEET = "EDIT_HISTORY"

EDITABLE_COLS = ["QTY", "LIFT NO", "CALL OUT", "DATE"]
TRACKED_COLS = ["QTY", "LIFT NO", "CALL OUT"]

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
sheet = client.open_by_key(SHEET_ID).worksheet(MAIN_SHEET)
history_sheet = client.open_by_key(SHEET_ID).worksheet(HISTORY_SHEET)

# ================= LOAD DATA =================
df = pd.DataFrame(sheet.get_all_records())

if df.empty:
    st.error("Sheet is empty")
    st.stop()

# ================= FIX TYPES =================
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

df = df.astype(str)
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view.drop(columns=["_ROW"]),
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in view.columns if c not in EDITABLE_COLS],
    key="editor"
)

# ================= SAVE + HISTORY =================
if st.button("💾 Save Changes", use_container_width=True):
    updated = 0

    with st.spinner("Saving changes..."):
        for i, row in edited.iterrows():
            original = df.iloc[i]
            sheet_row = int(original["_ROW"])

            changed = False
            new_values = []

            for col in df.columns:
                if col == "_ROW":
                    continue

                new_val = row[col]
                old_val = original[col]

                # 🔥 TRACK HISTORY
                if col in TRACKED_COLS and new_val != old_val:
                    history_sheet.append_row([
                        today,
                        original.get("PART NO", ""),
                        col,
                        old_val,
                        new_val,
                        "Streamlit App"
                    ])
                    changed = True

                new_values.append(new_val)

            if changed:
                sheet.update(f"A{sheet_row}", [new_values])
                updated += 1

    if updated:
        st.success(f"{updated} row(s) updated successfully")
    else:
        st.info("No changes detected")

# ================= HISTORY VIEW =================
st.markdown("---")
st.subheader("📜 Edit History (QTY / LIFT NO / CALL OUT)")

history_df = pd.DataFrame(history_sheet.get_all_records())

if history_df.empty:
    st.info("No history recorded yet.")
else:
    filter_part = st.text_input("Filter history by PART NO")

    if filter_part:
        history_df = history_df[
            history_df["PART NO"]
            .astype(str)
            .str.contains(filter_part, case=False, na=False)
        ]

    st.dataframe(history_df, use_container_width=True, hide_index=True)
















