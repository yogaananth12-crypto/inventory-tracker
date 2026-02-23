import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import matplotlib.pyplot as plt

# ================= PAGE =================
st.set_page_config(page_title="KONE Lift Inventory", layout="wide")

today = datetime.today().strftime("%d-%b-%Y")

st.markdown(f"""
<div style="text-align:center;">
    <h1 style="color:#005EB8;">KONE Lift Inventory Tracker</h1>
    <p>{today}</p>
</div>
""", unsafe_allow_html=True)

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
spreadsheet = client.open_by_key(SHEET_ID)

# ================= SAFE SHEET ACCESS =================
sheet = spreadsheet.worksheet(MAIN_SHEET)

try:
    history_sheet = spreadsheet.worksheet(HISTORY_SHEET)
except:
    history_sheet = spreadsheet.add_worksheet(title=HISTORY_SHEET, rows=1000, cols=10)
    history_sheet.append_row(["DATE", "PART NO", "FIELD", "OLD VALUE", "NEW VALUE", "UPDATED VIA"])

# ================= LOAD DATA =================
df = pd.DataFrame(sheet.get_all_records())

if df.empty:
    st.error("Main sheet is empty")
    st.stop()

# Clean headers
df.columns = df.columns.str.strip().str.upper()

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

                new_val = str(row.get(col, ""))
                old_val = str(original.get(col, ""))

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

# ================= LOAD HISTORY =================
history_df = pd.DataFrame(history_sheet.get_all_records())

if not history_df.empty:

    history_df.columns = history_df.columns.str.strip().str.upper()

    # Safe column check
    required_cols = ["DATE", "FIELD"]

    for col in required_cols:
        if col not in history_df.columns:
            st.warning("History sheet structure incorrect.")
            st.stop()

    history_df["DATE"] = pd.to_datetime(history_df["DATE"], errors="coerce")

    # ================= MONTH BUTTON FILTER =================
    st.markdown("---")
    st.subheader("📅 Monthly Filter")

    history_df["MONTH"] = history_df["DATE"].dt.month

    month_map = {
        1: "JAN", 2: "FEB", 3: "MAR", 4: "APR",
        5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG",
        9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"
    }

    cols = st.columns(13)

    selected_month = st.session_state.get("selected_month", "ALL")

    if cols[0].button("ALL"):
        selected_month = "ALL"

    for i in range(1, 13):
        if cols[i].button(month_map[i]):
            selected_month = i

    st.session_state["selected_month"] = selected_month

    if selected_month != "ALL":
        history_df = history_df[history_df["MONTH"] == selected_month]

    st.dataframe(history_df, use_container_width=True)

    # ================= DASHBOARD =================
    st.markdown("---")
    st.header("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Parts", len(df))

    with col2:
        total_qty = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).sum()
        st.metric("Total QTY", int(total_qty))

    with col3:
        st.metric("Total Edits", len(history_df))

    # ---------------- QTY TREND ----------------
    st.subheader("QTY Changes")

    if "FIELD" in history_df.columns:
        qty_history = history_df[history_df["FIELD"] == "QTY"]

        if not qty_history.empty:
            trend = qty_history.groupby("DATE").size()

            fig = plt.figure()
            trend.plot()
            plt.xlabel("Date")
            plt.ylabel("Changes")
            st.pyplot(fig)
        else:
            st.info("No QTY changes recorded.")

    # ---------------- LOW STOCK ----------------
    st.subheader("⚠ Low Stock Alert")

    df["QTY_NUM"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)
    low_stock = df[df["QTY_NUM"] <= 5]

    if not low_stock.empty:
        st.warning(f"{len(low_stock)} item(s) low in stock")
        st.dataframe(low_stock[["PART NO", "QTY"]])
    else:
        st.success("No low stock items 🎉")

else:
    st.info("No history recorded yet.")















