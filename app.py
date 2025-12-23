import streamlit as st
import pandas as pd
st.set_page_config(
    page_title="Spare Parts Dashboard",
    layout="wide"
)
def load_data():
    df = pd.read_excel("PCB BOARDS (CUP BOARD).xlsx")
    # Normalize column names (VERY IMPORTANT)
    df.columns = df.columns.str.strip().str.upper()
    return df
df = load_data()
st.title("🔧 Spare Parts Inventory Dashboard (POC)")
st.sidebar.header("Filters")
search = st.sidebar.text_input("Search Part No / Description")
low_stock = st.sidebar.checkbox("Low Stock Only (Qty ≤ 2)")
critical = st.sidebar.checkbox("Critical Parts Only")
filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False) |
        filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]
if low_stock and "QTY" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["QTY"] <= 2]
if critical and "CRITICAL PART" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["CRITICAL PART"] == "YES"]
col1, col2, col3 = st.columns(3)
col1.metric("Total Parts", len(df))
if "QTY" in df.columns:
    col2.metric("Low Stock Items", (df["QTY"] <= 2).sum())
else:
    col2.metric("Low Stock Items", 0)
if "CRITICAL PART" in df.columns:
    col3.metric("Critical Parts", (df["CRITICAL PART"] == "YES").sum())
else:
    col3.metric("Critical Parts", 0)
st.subheader("📋 Spare Parts List")
st.dataframe(filtered_df, use_container_width=True)
st.subheader("🚨 High Priority Parts")
if "PRIORITY LEVEL" in df.columns:
    high_priority = df[df["PRIORITY LEVEL"] == "HIGH"]
    st.dataframe(high_priority, use_container_width=True)
else:
    st.info("No 'Priority Level' column found in Excel.")
with st.expander("🔍 Debug: Excel Columns"):
    st.write(df.columns.tolist())



