import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Inventory Tracker", layout="wide")

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

# Ensure editable columns
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# Sheet row number
df["_ROW"] = range(2, len(df) + 2)

# Type safety
df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
df["CALL OUT"] = pd.to_numeric(df["CALL OUT"], errors="coerce").fillna(0).astype(int)
df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce").dt.date

# ================= SEARCH =================
search = st.text_input("🔍 Search")

df_view = df.copy()
if search:
    df_view = df_view[
        df_view.apply(lambda r: search.lower() in str(r).lower(), axis=1)
    ]

# ================= MOBILE DETECTION =================
st.markdown(
    """
    <script>
    const isMobile = window.innerWidth < 768;
    window.parent.postMessage(
        { type: "streamlit:setSessionState", key: "is_mobile", value: isMobile },
        "*"
    );
    </script>
    """,
    unsafe_allow_html=True,
)

is_mobile = st.session_state.get("is_mobile", False)

# ================= DESKTOP =================
if not is_mobile:
    st.subheader("🖥 Desktop Editor")

    edited = st.data_editor(
        df_view,
        hide_index=True,
        use_container_width=True,
        disabled=[c for c in df_view.columns if c not in EDITABLE_COLS],
        column_config={
            "QTY": st.column_config.NumberColumn(min_value=0),
            "CALL OUT": st.column_config.NumberColumn(min_value=0),
            "DATE": st.column_config.DateColumn(),
        },
        key="desktop_editor",
    )

    if st.button("💾 Save All Changes"):
        updates = 0

        for _, row in edited.iterrows():
            row_no = int(row["_ROW"])
            original = df[df["_ROW"] == row_no].iloc[0]

            values = []
            changed = False

            for col in df.columns:
                if col == "_ROW":
                    continue

                new = row[col]
                old = original[col]

                if pd.isna(new):
                    new = ""

                if isinstance(new, date):
                    new = new.strftime("%Y-%m-%d")

                if str(new) != str(old):
                    changed = True

                values.append(str(new))

            if changed:
                sheet.update(f"A{row_no}", [values])
                updates += 1

        st.success(f"✅ {updates} row(s) updated")

# ================= MOBILE UI (IMPROVED) =================
else:
    st.subheader("📱 Mobile Inventory")

    for idx, row in df_view.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div style="border-radius:12px;padding:14px;margin-bottom:14px;
                background:#111; border:1px solid #333;">
                <b>{row[df_view.columns[0]]}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form(f"row_{row['_ROW']}"):
                qty = st.number_input(
                    "QTY", value=row["QTY"], min_value=0, key=f"q_{idx}"
                )

                lift = st.text_input(
                    "LIFT NO", value=str(row["LIFT NO"]), key=f"l_{idx}"
                )

                callout = st.number_input(
                    "CALL OUT",
                    value=row["CALL OUT"],
                    min_value=0,
                    key=f"c_{idx}",
                )

                d = st.date_input(
                    "DATE",
                    value=row["DATE"] if row["DATE"] else date.today(),
                    key=f"d_{idx}",
                )

                save = st.form_submit_button("💾 Save")

                if save:
                    values = []

                    for col in df.columns:
                        if col == "_ROW":
                            continue

                        if col == "QTY":
                            values.append(str(qty))
                        elif col == "LIFT NO":
                            values.append(lift)
                        elif col == "CALL OUT":
                            values.append(str(callout))
                        elif col == "DATE":
                            values.append(d.strftime("%Y-%m-%d"))
                        else:
                            values.append(str(row[col]))

                    sheet.update(f"A{int(row['_ROW'])}", [values])
                    st.success("✅ Updated")




