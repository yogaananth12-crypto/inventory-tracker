import streamlit as st
import pandas as pd
from io import BytesIO
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
EXCEL_FILE = "PCB BOARDS (CUP BOARD).xlsx"

st.title("🔧 Spare Parts Inventory Dashboard")

# =========================
# LOAD DATA
# =========================
@st.cache_data(show_spinner=False)
def load_data():
    if not os.path.exists(EXCEL_FILE):
        st.error(f"❌ Excel file not found: {EXCEL_FILE}")
        return None

    # Read Excel (skip first title row if needed)
    df = pd.read_excel(EXCEL_FILE, skiprows=1)

    # Clean column names
    df.columns = df.columns.astype(str).str.strip().str.upper()

    # Remove UNNAMED columns
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # ---------- AUTO COLUMN DETECTION ----------
    def detect_column(columns, keywords):
        for col in columns:
            for key in keywords:
                if key in col:
                    return col
        return None

    cols = df.columns.tolist()

    col_sno  = detect_column(cols, ["S.NO", "SNO", "SERIAL"])
    col_part = detect_column(cols, ["PART"])
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

    # Keep only required columns
    required = ["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]
    df = df[[c for c in required if c in df.columns]]

    # Drop empty rows (IMPORTANT)
    df = df.dropna(subset=["PART NO", "DESCRIPTION"], how="all")

    # Ensure QTY numeric
    df["QTY"] = pd.to_numeric(df.get("QTY", 0), errors="coerce").fillna(0).astype(int)

    # Priority
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"

    return df.reset_index(drop=True)

# =========================
# SAVE DATA
# =========================
def save_data(df):
    save_df = df.drop(columns=["PRIORITY LEVEL"])
    save_df.to_excel(EXCEL_FILE, index=False)

# =========================
# MAIN
# =========================
df = load_data()

if df is None or df.empty:
    st.warning("⚠ No valid spare parts found.")
    st.stop()

# =========================
# KPI
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
# EDITABLE TABLE (QTY ONLY)
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
if st.button("💾 Save Changes"):
    df.update(edited_df)

    # Recalculate priority
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"

    save_data(df)
    st.success("✅ Inventory updated successfully!")

# =========================
# DOWNLOAD
# =========================
output = BytesIO()
df.to_excel(output, index=False, engine="openpyxl")
output.seek(0)

st.download_button(
    "⬇️ Download Current Inventory",
    data=output,
    file_name="spare_parts_inventory.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write("Columns Used:")
st.write(list(df.columns))






















