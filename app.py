import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard (POC)")

EXCEL_FILE = "PCB BOARDS (CUP BOARD).xlsx"

# =========================
# LOAD DATA
# =========================
def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE, skiprows=1)
    except FileNotFoundError:
        st.error(f"❌ Excel file not found: {EXCEL_FILE}")
        return None
    except Exception as e:
        st.error(f"❌ Error loading Excel file: {e}")
        return None

    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    def detect_column(columns, keywords):
        for col in columns:
            for key in keywords:
                if key in col:
                    return col
        return None

    cols = df.columns.tolist()

    col_sno  = detect_column(cols, ["S.NO", "SNO", "SERIAL"])
    col_part = detect_column(cols, ["PART", "ITEM"])
    col_desc = detect_column(cols, ["DESC", "DESCRIPTION"])
    col_box  = detect_column(cols, ["BOX", "BIN", "LOCATION"])
    col_qty  = detect_column(cols, ["QTY", "QUANTITY", "STOCK"])

    rename_map = {}
    if col_sno:  rename_map[col_sno]  = "S.NO"
    if col_part: rename_map[col_part] = "PART NO"
    if col_desc: rename_map[col_desc] = "DESCRIPTION"
    if col_box:  rename_map[col_box]  = "BOX NO"
    if col_qty:  rename_map[col_qty]  = "QTY"

    df = df.rename(columns=rename_map)

    for c in ["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]:
        if c not in df.columns:
            df[c] = "" if c != "QTY" else 0

    df = df[["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]]
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"

    return df

# =========================
# LOAD INTO SESSION
# =========================
if "data" not in st.session_state:
    st.session_state.data = load_data()

df = st.session_state.data

if df is None or df.empty:
    st.warning("⚠ No data available.")
    st.stop()

# =========================
# METRICS
# =========================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Parts", len(df))
c2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
c3.metric("High", (df["PRIORITY LEVEL"] == "HIGH").sum())
c4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())

# =========================
# SEARCH
# =========================
st.subheader("📋 Spare Parts List")
search = st.text_input("🔍 Search Part Number or Description")

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# =========================
# EDITABLE TABLE (ONLY QTY)
# =========================
edited_df = st.data_editor(
    filtered_df,
    use_container_width=True,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "PRIORITY LEVEL"],
    key="editor"
)

# =========================
# SAVE BUTTON
# =========================
if st.button("💾 Save Changes to Excel"):
    try:
        # Update main dataframe
        df.update(edited_df)

        # Recalculate priority
        df["PRIORITY LEVEL"] = "NORMAL"
        df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
        df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"

        # Save back to Excel
        df.drop(columns=["PRIORITY LEVEL"]).to_excel(EXCEL_FILE, index=False)

        st.session_state.data = df
        st.success("✅ Quantity updated and saved successfully!")

    except Exception as e:
        st.error(f"❌ Error saving file: {e}")

# =========================
# DOWNLOAD BACKUP
# =========================
output = BytesIO()
df.to_excel(output, index=False)
output.seek(0)

st.download_button(
    "⬇️ Download Backup Excel",
    output,
    "spare_parts_backup.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write(df.head())
st.write("Columns:", list(df.columns))





















