import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ================= PAGE =================
st.set_page_config(page_title="KONE Lift Inventory", layout="wide")

# ================= HEADER =================
today_str = datetime.today().strftime("%d %b %Y")

st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(135deg,#e6f0fa 0%,#ffffff 45%,#f2f7fc 100%);
}}
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
    <div class="date">{today_str}</div>
</div>
""", unsafe_allow_html=True)

# ================= CONFIG =================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
MAIN_SHEET = "Sheet1"
HISTORY_SHEET = "EDIT_HISTORY"

# 🔥 DATE removed from editable
EDITABLE_COLS = ["QTY", "LIFT NO", "CALL OUT"]
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

try:
    sheet = client.open_by_key(SHEET_ID).worksheet(MAIN_SHEET)
    history_sheet = client.open_by_key(SHEET_ID).worksheet(HISTORY_SHEET)
except Exception:
    st.error("Google Sheet not accessible. Check Sheet ID / Permissions.")
    st.stop()

# ================= LOAD MAIN DATA =================
try:
    df = pd.DataFrame(sheet.get_all_records())
except Exception:
    st.error("Google API Error. Check Drive storage or permissions.")
    st.stop()

if df.empty:
    st.warning("Sheet is empty.")
    st.stop()

# Ensure editable columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

df = df.astype(str)
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search Part / Description / Lift")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DATA EDITOR =================
edited = st.data_editor(
    view.drop(columns=["_ROW"]),
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in view.columns if c not in EDITABLE_COLS],
)

# ================= SAVE + HISTORY =================
from zoneinfo import ZoneInfo

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

                new_val = str(row[col])
                old_val = str(original[col])

                # Track changes
                if col in TRACKED_COLS and new_val != old_val:

                    current_time = datetime.now(
                        ZoneInfo("Asia/Singapore")
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    history_sheet.append_row([
                        current_time,
                        original.get("PART NO", ""),
                        col,
                        new_val,
                        old_val,
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
        st.info("No changes detected.")
# ================= DASHBOARD =================
st.markdown("---")
st.subheader("📊 Inventory Overview")

# Convert QTY to numeric safely
df["QTY_NUM"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

# Stock categories
low_stock = df[df["QTY_NUM"] <= 2]
medium_stock = df[(df["QTY_NUM"] > 2) & (df["QTY_NUM"] <= 4)]
high_stock = df[df["QTY_NUM"] > 4]

col1, col2, col3 = st.columns(3)

col1.metric("🔴 Low Stock (≤2)", len(low_stock))
col2.metric("🟡 Medium Stock (3-4)", len(medium_stock))
col3.metric("🟢 In Stock (5+)", len(high_stock))

# Pie Chart
fig, ax = plt.subplots()

sizes = [
    len(low_stock),
    len(medium_stock),
    len(high_stock)
]

labels = ["Low (≤2)", "Medium (3-4)", "In Stock (5+)"]

ax.pie(sizes, labels=labels, autopct="%1.1f%%")
ax.set_title("Stock Distribution")

st.pyplot(fig)
# ================= HISTORY SECTION =================
st.markdown("---")
st.subheader("📜 Edit History")

try:
    history_df = pd.DataFrame(history_sheet.get_all_records())
except:
    st.warning("History sheet not accessible.")
    st.stop()

if history_df.empty:
    st.info("No history recorded yet.")
else:

    # Ensure DATE column exists
    if "DATE" not in history_df.columns:
        st.warning("DATE column missing in history sheet.")
        st.dataframe(history_df)
        st.stop()

    # Convert DATE safely
    history_df["DATE"] = pd.to_datetime(history_df["DATE"], errors="coerce")

    # ---- Monthly Filter ----
    months = {
        "All": None,
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    selected_month = st.selectbox("📅 Filter by Month", list(months.keys()))

    if months[selected_month]:
        history_df = history_df[
            history_df["DATE"].dt.month == months[selected_month]
        ]

    # ---- Filter by PART NO ----
    filter_part = st.text_input("Filter by PART NO")

    if filter_part:
        history_df = history_df[
            history_df["PART NO"]
            .astype(str)
            .str.contains(filter_part, case=False, na=False)
        ]

    st.dataframe(
        history_df.sort_values("DATE", ascending=False),
        use_container_width=True,
        hide_index=True
    )















