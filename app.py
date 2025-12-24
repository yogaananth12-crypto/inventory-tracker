import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

st.title("🔧 Spare Parts Inventory Dashboard (POC)")

# =========================
# LOAD DATA FUNCTION
# =========================
def load_data():
    try:
        # Skip title row
        df = pd.read_excel(
            "PCB BOARDS (CUP BOARD).xlsx",
            skiprows=1
        )
    except Exception as e:
        st.error(f"❌ Error loading Excel file: {e}")
        return None

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

    # Keep only required columns
    final_cols = ["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]
    df = df[[c for c in final_cols if c in df.columns]]

    # Ensure QTY numeric
    if "QTY" in df.columns:
        df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    # Priority logic
    df["PRIORITY LEVEL"] = "NORMAL"
    if "QTY" in df.columns:
        df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
        df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"

    return df


# =========================
# LOAD DATA SAFELY
# =========================
df = load_data()

if df is None or df.empty:
    st.warning("⚠ No data available after processing.")
    st.stop()

# =========================
# KPI METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Parts", len(df))
col2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
col3.metric("High Priority", (df["PRIORITY LEVEL"] == "HIGH").sum())
col4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())

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

st.dataframe(filtered_df, use_container_width=True)

# =========================
# DOWNLOAD
# =========================
output = BytesIO()
filtered_df.to_excel(output, index=False, engine="openpyxl")
output.seek(0)

st.download_button(
    label="⬇️ Download Filtered Data (Excel)",
    data=output,
    file_name="filtered_spare_parts.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write("Final Columns Used:")
st.write(list(df.columns))















