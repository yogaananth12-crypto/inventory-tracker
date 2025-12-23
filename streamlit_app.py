import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Spare Parts Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("spare_parts.xlsx")

df = load_data()

st.title("🔧 Spare Parts Inventory Dashboard (POC)")

# Sidebar filters
st.sidebar.header("Filters")

search = st.sidebar.text_input("Search Part No / Description")

low_stock = st.sidebar.checkbox("Low Stock Only (Qty ≤ 2)")
critical = st.sidebar.checkbox("Critical Parts Only")

# Apply filters
filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["Part No"].astype(str).str.contains(search, case=False) |
        filtered_df["Description"].astype(str).str.contains(search, case=False)
    ]

if low_stock:
    filtered_df = filtered_df[filtered_df["Quantity"] <= 2]

if critical:
    filtered_df = filtered_df[filtered_df["Critical Part"] == "YES"]

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Parts", len(df))
col2.metric("Low Stock Items", (df["Quantity"] <= 2).sum())
col3.metric("Critical Parts", (df["Critical Part"] == "YES").sum())

# Display table
st.subheader("📋 Spare Parts List")
st.dataframe(filtered_df, use_container_width=True)

# Priority highlight
st.subheader("🚨 High Priority Parts")
high_priority = df[df["Priority Level"] == "HIGH"]
st.dataframe(high_priority, use_container_width=True)
