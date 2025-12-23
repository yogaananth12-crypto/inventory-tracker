import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Spare Parts Dashboard",
    layout="wide"
)

# --------------------------------------------------
# Load Data Function
# --------------------------------------------------
def load_data():
    try:
        df = pd.read_excel("PCB BOARDS (CUP BOARD).xlsx")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

    # Normalize column names
    df.columns = df.columns.str.strip().str.upper()

    # Create Priority Level column
    df["PRIORITY LEVEL"] = "NORMAL"

    # Quantity-based priority
    if "QTY" in df.columns:
        df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
        df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"

    # Critical parts override
    if "CRITICAL PART" in df.columns:
        df.loc[df["CRITICAL PART"] == "YES", "PRIORITY LEVEL"] = "HIGH"

    return df


# --------------------------------------------------
# Load Data
# --------------------------------------------------
df = load_data()

if df is None or df.empty:
    st.error("Excel file could not be loaded or is empty.")
    st.stop()

# --------------------------------------------------
# App Title
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
    if "PART NO" in filtered_df.columns and "DESCRIPTION" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False) |
            filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
        ]

if low_stock and "QTY" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["QTY"] <= 3]

if critical and "CRITICAL PART" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["CRITICAL PART"] == "YES"]

filtered_df = filtered_df[
    filtered_df["PRIORITY LEVEL"].isin(priority_filter)
]

# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Parts", len(df))
col2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
col3.metric("High Priority", (df["PRIORITY LEVEL"] == "HIGH").sum())
col4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())

# --------------------------------------------------
# Main Tables
# --------------------------------------------------
st.subheader("📋 Spare Parts List")
s






