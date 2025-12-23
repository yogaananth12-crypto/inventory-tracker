import streamlit as st
import pandas as pd
df=df.loc[:, ~df.columns.str.contains('^unnamed')]
df.columns = df.columns.str.strip()
st.set_page_config(page_title="Spare Parts Dashboard", layout="wide")
def load_data():
    return pd.read_excel("PCB BOARDS (CUP BOARD).xlsx")
df = load_data()
st.title("🔧 Spare Parts Inventory Dashboard (POC)")
st.sidebar.header("Filters")
search = st.sidebar.text_input("Search Part No / Description")
low_stock = st.sidebar.checkbox("Low Stock Only (Qty ≤ 2)")
critical = st.sidebar.checkbox("Critical Parts Only")
filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["Part No"].astype(str).str.contains(search, case=False) |
        filtered_df["Description"].astype(str).str.contains(search, case=False)
    ]
if low_stock:
    filtered_df = filtered_df[filtered_df["QTY"] <= 2]
if critical:
    filtered_df = filtered_df[filtered_df["Critical Part"] == "YES"]
    st.write("Excel columns:")
    st.write(df.columns.tolist())
col1, col2, col3 = st.columns(3)
col1.metric("Total Parts", len(df))
col2.metric("Low Stock Items", (df["QTY"] <= 2).sum())
col3.metric("Critical Parts", (df["Critical Part"] == "YES").sum())
st.subheader("📋 Spare Parts List")
st.dataframe(filtered_df, use_container_width=True)
st.subheader("🚨 High Priority Parts")
high_priority = df[df["Priority Level"] == "HIGH"]
st.dataframe(high_priority, use_container_width=True)


