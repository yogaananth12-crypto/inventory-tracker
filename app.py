import streamlit as st
import pandas as pd
st.set_page_config(page_title="Spare Parts Dashboard", layout="wide")
def load_data():
    df = pd.read_excel("PCB BOARDS (CUP BOARD).xlsx")
    df.columns = df.columns.str.strip().str.upper()
    df["PRIORITY LEVEL"] = "NORMAL"
    if "QTY" in df.columns:
        df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
        df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    if "CRITICAL PART" in df.columns:
        df.loc[df["CRITICAL PART"] == "YES", "PRIORITY LEVEL"] = "HIGH"
        return df   # <-- THIS LINE IS CRITICAL
df = load_data()
if df is None or df.empty:
    st.error("Excel file could not be loaded or is empty.")
    st.stop()
st.title("🔧 Spare Parts Inventory Dashboard (POC)")
st.sidebar.header("Filters")
search = st.sidebar.text_input("Search Part No / Description")
low_stock = st.sidebar.checkbox("Low Stock Only (Qty ≤ 3)")
critical = st.sidebar.checkbox("Critical Parts Only")
priority_filter = st.sidebar.multiselect(
    "Priority Level",
    ["URGENT", "HIGH", "NORMAL"],
    default=["URGENT", "HIGH", "NORMAL"]
)
filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False) |
        filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]
if low_stock and "QTY" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["QTY"] <= 3]
if critical and "CRITICAL PART" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["CRITICAL PART"] == "YES"]
filtered_df = filtered_df[filtered_df["PRIORITY LEVEL"].isin(priority_filter)]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Parts", len(df))
col2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
col3.metric("High Priority", (df["PRIORITY LEVEL"] == "HIGH").sum())
col4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())
st.subheader("📋 Spare Parts List")
st.dataframe(filtered_df, use_container_width=True)
st.subheader("🚨 Urgent & High Priority Parts")
priority_df = df[df["PRIORITY LEVEL"].isin(["URGENT", "HIGH"])]
st.dataframe(priority_df, use_container_width=True)
st.expander("🔍 Debug: Excel Columns"):
st.write(df.columns.tolist())





