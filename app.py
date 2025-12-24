import streamlit as st
import pandas as pd
from io import BytesIO

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(page_title="Spare Parts Inventory Dashboard", layout="wide")

# --------------------------------------------------
# Column Detection Helper
# --------------------------------------------------
def detect_column(columns, keywords):
    for col in columns:
        for key in keywords:
            if key in col:
                return col
    return None
# --------------------------------------------------
# Load Data
# --------------------------------------------------
def load_data():
    try:
        # ⬇️ Skip the title row
        df = pd.read_excel(
            "PCB BOARDS (CUP BOARD).xlsx",
            skiprows=1
        )
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

    # Normalize column names
    df.columns = df.columns.str.strip().str.upper()

    # Remove UNNAMED columns
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # ---------- AUTO-DETECT ----------
    def detect_column(columns, keywords):
        for col in columns:
            for key in keywords:
                if key in col:
                    return col
        return None

    cols = df.columns.tolist()

    col_sno  = detect_column(cols, ["S.NO", "SNO", "SR", "SERIAL"])
    col_part = detect_column(cols, ["PART", "ITEM", "MATERIAL"])
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

    # Ensure QTY numeric
    if "QTY" in df.columns:
        df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    # Priority
    df["PRIORITY LEVEL"] = "NORMAL"
    if "QTY" in df.columns:
        df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
        df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"

    return df


if df is None or df.empty:
    st.error("Excel file could not be loaded or is empty.")
    st.stop()

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🔧 Spare Parts Inventory Dashboard")

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

search = st.sidebar.text_input("Search (Part No / Description / Box)")
low_stock = st.sidebar.checkbox("Low Stock Only (Qty ≤ 3)")

priority_filter = st.sidebar.multiselect(
    "Priority Level",
    ["URGENT", "HIGH", "NORMAL"],
    default=["URGENT", "HIGH", "NORMAL"]
)

# --------------------------------------------------
# Apply Filters
# --------------------------------------------------
filtered_df = df.copy()

# Search across all text columns
if search:
    search = search.lower()
    text_cols = filtered_df.select_dtypes(include=["object"]).columns
    filtered_df = filtered_df[
        filtered_df[text_cols]
        .astype(str)
        .apply(lambda r: r.str.lower().str.contains(search).any(), axis=1)
    ]

if low_stock and "QTY" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["QTY"] <= 3]

filtered_df = filtered_df[
    filtered_df["PRIORITY LEVEL"].isin(priority_filter)
]

# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------
c1, c2, c3 = st.columns(3)

c1.metric("Total Parts", len(df))
c2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
c3.metric("High Priority", (df["PRIORITY LEVEL"] == "HIGH").sum())

# --------------------------------------------------
# Priority Chart
# --------------------------------------------------
st.subheader("📊 Priority Distribution")

priority_chart = (
    df["PRIORITY LEVEL"]
    .value_counts()
    .reindex(["URGENT", "HIGH", "NORMAL"], fill_value=0)
)

st.bar_chart(priority_chart)

# --------------------------------------------------
# Highlight Rows
# --------------------------------------------------
def highlight_priority(row):
    if row["PRIORITY LEVEL"] == "URGENT":
        return ["background-color:#ffcccc"] * len(row)
    elif row["PRIORITY LEVEL"] == "HIGH":
        return ["background-color:#fff2cc"] * len(row)
    return [""] * len(row)

# --------------------------------------------------
# Table
# --------------------------------------------------
st.subheader("📋 Spare Parts List")

st.dataframe(
    filtered_df.style.apply(highlight_priority, axis=1),
    use_container_width=True
)

# --------------------------------------------------
# Download
# --------------------------------------------------
output = BytesIO()
filtered_df.to_excel(output, index=False)
output.seek(0)

st.download_button(
    "⬇️ Download Filtered Data",
    data=output,
    file_name="spare_parts_filtered.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write("Final Columns Used:")
st.write(df.columns.tolist())














