import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

# ================= PAGE =================
st.set_page_config(
    page_title="KONE Lift Inventory",
    layout="wide"
)

# ================= TIMEZONE =================
sg_timezone = pytz.timezone("Asia/Singapore")
today = datetime.now(sg_timezone)
today_str = today.strftime("%d %b %Y")

# ================= CUSTOM STYLE =================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    text-align: center;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 60px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
today = datetime.today()
today_str = today.strftime("%d %b %Y")

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
    height: 90px;
    background: #005EB8;
    color: white;
    font-size: 36px;
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

sheet = client.open_by_key(SHEET_ID).worksheet(MAIN_SHEET)
history_sheet = client.open_by_key(SHEET_ID).worksheet(HISTORY_SHEET)

# ================= LOAD DATA =================
df = pd.DataFrame(sheet.get_all_records())

if df.empty:
    st.warning("Sheet is empty.")
    st.stop()

for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

df = df.astype(str)
df["_ROW"] = range(2, len(df) + 2)

df["QTY_NUM"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

# ================= LOW STOCK ALERT =================
df["QTY_NUM"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

low_stock = df[df["QTY_NUM"] <= 2]

if not low_stock.empty:
    st.error(f"⚠ {len(low_stock)} Item(s) Low Stock (≤ 2 Qty)")

# ================= KPI SECTION =================
total_parts = len(df)
low_stock_count = (df["QTY_NUM"] <= 2).sum()

try:
    history_df = pd.DataFrame(history_sheet.get_all_records())
    total_callouts = len(history_df[history_df["FIELD"] == "CALL OUT"])
except:
    total_callouts = 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Parts", total_parts)

with col2:
    st.metric("Low Stock Items (≤2)", low_stock_count)

with col3:
    st.metric("Total Call Outs Logged", total_callouts)

# ================= PIE CHART =================
st.markdown('<div class="section-title">Stock Distribution</div>', unsafe_allow_html=True)

low = (df["QTY_NUM"] <= 2).sum()
medium = ((df["QTY_NUM"] > 2) & (df["QTY_NUM"] <= 4)).sum()
high = (df["QTY_NUM"] > 4).sum()

stock_df = pd.DataFrame({
    "Category": ["Low (≤2)", "Medium (3-4)", "In Stock (5+)"],
    "Count": [low, medium, high]
})

fig = px.pie(
    stock_df,
    names="Category",
    values="Count",
    hole=0.45
)

fig.update_layout(
    margin=dict(t=20, b=20, l=20, r=20)
)

st.plotly_chart(fig, use_container_width=True)

# ================= SEARCH =================
st.markdown('<div class="section-title">Inventory Table</div>', unsafe_allow_html=True)

search = st.text_input("Search Part / Description / Lift")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

edited = st.data_editor(
    view.drop(columns=["_ROW", "QTY_NUM"]),
    use_container_width=True,
    hide_index=True,
    disabled=[c for c in view.columns if c not in EDITABLE_COLS],
)

# ================= SAVE =================
if st.button("Save Changes", use_container_width=True):

    updated = 0

    for i, row in edited.iterrows():

        original = df.iloc[i]
        sheet_row = int(original["_ROW"])
        changed = False
        new_values = []

        for col in df.columns:
            if col in ["_ROW", "QTY_NUM"]:
                continue

            new_val = str(row[col])
            old_val = str(original[col])

            if col in TRACKED_COLS and new_val != old_val:

                history_sheet.append_row([
                    datetime.now(sg_timezone).strftime("%Y-%m-%d %H:%M:%S"),
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
        st.rerun()
    else:
        st.info("No changes detected.")

# ================= HISTORY =================
st.markdown("---")
st.subheader("📜 Edit History")

history_df = pd.DataFrame(history_sheet.get_all_records())

if history_df.empty:
    st.info("No history recorded yet.")
else:

    if "DATE" in history_df.columns:
        history_df["DATE"] = pd.to_datetime(history_df["DATE"], errors="coerce")

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

    filter_part = st.text_input("Filter by PART NO")

    if filter_part and "PART NO" in history_df.columns:
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













