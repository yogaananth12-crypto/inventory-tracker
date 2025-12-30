import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ================= PAGE CONFIG =================
st.set_page_config(page_title="KONE Inventory", layout="wide")

# ================= HEADER =================
today = date.today().strftime("%d %b %Y")

st.markdown(
    f"""
    <div style="text-align:center; padding:10px 0;">
        <h1 style="color:#003A8F; margin-bottom:0;">KONE</h1>
        <p style="margin-top:5px; font-size:16px;">
            Inventory Tracker • {today}
        </p>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)

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

# Ensure editable columns exist
for col in EDITABLE_COLS:
    if col not in df.columns:
        df[col] = ""

# Google Sheet row numbers
df["_ROW"] = range(2, len(df) + 2)

# ================= SEARCH =================
search = st.text_input("🔍 Search")

view = df.copy()
if search:
    view = view[view.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

# ================= DEVICE DETECTION =================
is_mobile = st.checkbox("📱 Mobile View", value=False)

# ================= DESKTOP VIEW =================
if not is_mobile:
    edited = st.data_editor(
        view.drop(columns=["_ROW"]),
        use_container_width=True,
        hide_index=True,
        disabled=[c for c in view.columns if c not in EDITABLE_COLS and c != "_ROW"],
        key="editor"
    )

    if st.button("💾 Save Changes"):
        updated = 0
        for i, row in edited.iterrows():
            sheet_row = int(view.iloc[i]["_ROW"])
            values = row.tolist()
            sheet.update(f"A{sheet_row}", [values])
            updated += 1

        st.success(f"✅ {updated} row(s) saved")

# ================= MOBILE VIEW =================
else:
    st.info("📱 Mobile card view enabled")

    for i, row in view.iterrows():
        with st.container():
            st.markdown(
                """
                <div style="border:1px solid #ddd; padding:12px; border-radius:10px; margin-bottom:12px;">
                """,
                unsafe_allow_html=True
            )

            st.markdown(f"**Part No:** {row.get('PART NO','')}")
            st.markdown(f"**Description:** {row.get('DESCRIPTION','')}")
            st.markdown(f"**Box No:** {row.get('BOX NO','')}")

            qty = st.text_input("QTY", row["QTY"], key=f"qty_{i}")
            lift = st.text_input("LIFT NO", row["LIFT NO"], key=f"lift_{i}")
            call = st.text_input("CALL OUT", row["CALL OUT"], key=f"call_{i}")
            dte = st.text_input("DATE", row["DATE"], key=f"date_{i}")

            if st.button("💾 Save", key=f"save_{i}"):
                values = []
                for col in df.columns:
                    if col == "_ROW":
                        continue
                    if col == "QTY":
                        values.append(qty)
                    elif col == "LIFT NO":
                        values.append(lift)
                    elif col == "CALL OUT":
                        values.append(call)
                    elif col == "DATE":
                        values.append(dte)
                    else:
                        values.append(row[col])

                sheet.update(f"A{int(row['_ROW'])}", [values])
                st.success("Saved")

            st.markdown("</div>", unsafe_allow_html=True)



