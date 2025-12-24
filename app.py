import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard")

# =========================
# AUTO HEADER DETECTION
# =========================
def detect_header_row(file):
    preview = pd.read_excel(file, header=None, nrows=6)
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.upper()
        if any("PART" in c or "QTY" in c or "DESC" in c for c in row):
            return i
    return 0

# =========================
# LOAD DATA
# =========================
def load_data(file):
    header_row = detect_header_row(file)

    df = pd.read_excel(file, header=header_row)
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

    # Qty numeric
    if "QTY" in df.columns:
        df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    # Priority
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"

    return df

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "📤 Upload Spare Parts Excel File",
    type=["xlsx"]
)

if not uploaded_file:
    st.info("Please upload an Excel file to continue.")
    st.stop()

df = load_data(uploaded_file)

if df.empty:
    st.warning("No valid data detected.")
    st.stop()

# =========================
# KPI METRICS
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

search = st.text_input("🔍 Search Part No or Description")

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# =========================
# COLOR PRIORITY
# =========================
def color_priority(row):
    if row["PRIORITY LEVEL"] == "URGENT":
        return ["background-color:#ffcccc"] * len(row)
    if row["PRIORITY LEVEL"] == "HIGH":
        return ["background-color:#fff2cc"] * len(row)
    return [""] * len(row)

st.dataframe(
    filtered_df.style.apply(color_priority, axis=1),
    use_container_width=True
)

# =========================
# DOWNLOAD
# =========================
output = BytesIO()
filtered_df.to_excel(output, index=False, engine="openpyxl")
output.seek(0)

st.download_button(
    "⬇️ Download Filtered Data (Excel)",
    data=output,
    file_name="filtered_spare_parts.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write("Detected Columns:", list(df.columns))















