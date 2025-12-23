import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Spare Parts Inventory Dashboard",
    layout="wide"
)

# --------------------------------------------------
# Load Data
# --------------------------------------------------
def load_data():
    try:
        df = pd.read_excel("PCB BOARDS (CUP BOARD).xlsx")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

    # Normalize column names
    df.columns = df.columns.str.strip().str.upper()

    # Ensure QTY numeric
    if "QTY" in df.columns:
        df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    # Normalize Critical Part
    if "CRITICAL PART" in df.columns:
        df["CRITICAL PART"] = (
            df["CRITICAL PART"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    # Priority Logic
    df["PRIORITY LEVEL"] = "NORMAL"

    if "QTY" in df.columns:
        df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
        df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"

    if "CRITICAL PART" in df.columns:
        df.loc[
            df["CRITICAL PART"].isin(["YES", "Y", "TRUE", "1"]),
            "PRIORITY LEVEL"
        ] = "HIGH"

    return df


df = load_data()

if df is None or df.empty:
    st.error("Excel file could not be loaded or is empty.")
    st.stop()

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🔧 Spare Parts Inventory Dashboard (POC)")

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

search = st.sidebar.text_input("Search Part No / Description")
low_stock = st.sidebar.checkbox("Low Stock Only (Qty ≤ 3)")
critical = st.sidebar.checkbox("Critical Parts Only")

priority_filter = st.sidebar.multiselect(
    "Priority Level",
    ["URGENT", "HIGH", "NORMAL"],
    default=["URGENT", "HIGH", "NORMAL"]
)

# --------------------------------------------------
# Apply Filters
# --------------------------------------------------
filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False) |
        filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

if low_stock:
    filtered_df = filtered_df[filtered_df["QTY"] <= 3]

if critical:
    filtered_df = filtered_df[
        filtered_df["CRITICAL PART"].isin(["YES", "Y", "TRUE", "1"])
    ]

filtered_df = filtered_df[
    filtered_df["PRIORITY LEVEL"].isin(priority_filter)
]

# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Parts", len(df))
c2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
c3.metric("High Priority", (df["PRIORITY LEVEL"] == "HIGH").sum())
c4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())

# --------------------------------------------------
# Charts
# --------------------------------------------------
st.subheader("📊 Priority Distribution")

priority_chart = (
    df["PRIORITY LEVEL"]
    .value_counts()
    .reindex(["URGENT", "HIGH", "NORMAL"], fill_value=0)
)

st.bar_chart(priority_chart)

# --------------------------------------------------
# Color Styling
# --------------------------------------------------
def highlight_priority(row):
    if row["PRIORITY LEVEL"] == "URGENT":
        return ["background-color: #ffcccc"] * len(row)
    elif row["PRIORITY LEVEL"] == "HIGH":
        return ["background-color: #fff2cc"] * len(row)
    else:
        return [""] * len(row)

# --------------------------------------------------
# Tables
# --------------------------------------------------
st.subheader("📋 Spare Parts List")

styled_df = filtered_df.style.apply(highlight_priority, axis=1)

st.dataframe(styled_df, use_container_width=True)

# --------------------------------------------------
# Download Button
# --------------------------------------------------
st.download_button(
    label="⬇️ Download Filtered Data (Excel)",
    data=filtered_df.to_excel(index=False, engine="openpyxl"),
    file_name="filtered_spare_parts.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --------------------------------------------------
# Urgent & High
# --------------------------------------------------
st.subheader("🚨 Urgent & High Priority Parts")

priority_df = df[df["PRIORITY LEVEL"].isin(["URGENT", "HIGH"])]

st.dataframe(
    priority_df.style.apply(highlight_priority, axis=1),
    use_container_width=True
)

# --------------------------------------------------
# Debug Info
# --------------------------------------------------
with st.expander("🛠 Debug Info"):
st.write(df.columns.tolist())








