import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Inventory Tracker", layout="wide")

st.title("📦 Inventory Tracker")

# --------------------------------------------------
# File upload
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload inventory file (Excel or CSV)",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.info("Please upload an inventory file to begin.")
    st.stop()

# --------------------------------------------------
# Load file
# --------------------------------------------------
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error("Failed to read file")
    st.exception(e)
    st.stop()

# --------------------------------------------------
# Normalize column names (CRITICAL FIX)
# --------------------------------------------------
df.columns = (
    df.columns
      .astype(str)
      .str.strip()
      .str.upper()
)

# --------------------------------------------------
# Validate required columns
# --------------------------------------------------
REQUIRED_COLUMNS = {"PART NO", "QTY"}

missing = REQUIRED_COLUMNS - set(df.columns)
if missing:
    st.error(f"Missing required columns: {missing}")
    st.write("Detected columns:", df.columns.tolist())
    st.stop()

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.header("Filters")

search = st.sidebar.text_input("Search PART NO")

low_stock_only = st.sidebar.checkbox(
    "Show low stock only (QTY ≤ 3)",
    value=False
)

# --------------------------------------------------
# Filtering logic
# --------------------------------------------------
filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"]
        .astype(str)
        .str.contains(search, case=False, na=False)
    ]

if low_stock_only:
    filtered_df = filtered_df[filtered_df["QTY"] <= 3]

# --------------------------------------------------
# Display table
# --------------------------------------------------
st.subheader("Inventory")

st.dataframe(
    filtered_df,
    use_container_width=True
)

st.caption(f"Rows shown: {len(filtered_df)} / {len(df)}")

# --------------------------------------------------
# Download Excel
# --------------------------------------------------
output = BytesIO()
filtered_df.to_excel(output, index=False)
output.seek(0)

st.download_button(
    label="⬇️ Download filtered inventory (Excel)",
    data=output,
    file_name="filtered_inventory.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)









