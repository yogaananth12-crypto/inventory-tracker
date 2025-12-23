import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Inventory Tracker", layout="wide")
st.title("📦 Inventory Tracker")

# --------------------------------------------------
# Upload file
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload inventory file (Excel or CSV)",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.stop()

# --------------------------------------------------
# Load file
# --------------------------------------------------
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# --------------------------------------------------
# Normalize column names
# --------------------------------------------------
df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.upper()
)

# --------------------------------------------------
# AUTO-MAP COLUMN NAMES (CRITICAL FIX)
# --------------------------------------------------
COLUMN_ALIASES = {
    "PART NO": [
        "PART NO", "PART NUMBER", "PARTNUMBER", "ITEM CODE",
        "ITEM NO", "MATERIAL", "MATERIAL CODE"
    ],
    "QTY": [
        "QTY", "QUANTITY", "QTY ISSUED", "BALANCE", "STOCK"
    ],
}

def find_column(possible_names, columns):
    for name in possible_names:
        if name in columns:
            return name
    return None

part_col = find_column(COLUMN_ALIASES["PART NO"], df.columns)
qty_col = find_column(COLUMN_ALIASES["QTY"], df.columns)

if not part_col or not qty_col:
    st.error("❌ Could not detect required columns automatically.")
    st.write("Detected columns:", df.columns.tolist())
    st.stop()

# Rename to internal standard names
df = df.rename(columns={
    part_col: "PART NO",
    qty_col: "QTY"
})

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.header("Filters")

search = st.sidebar.text_input("Search PART NO")
low_stock_only = st.sidebar.checkbox("Show low stock only (QTY ≤ 3)")

# --------------------------------------------------
# Filtering
# --------------------------------------------------
filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"]
        .astype(str)
        .str.contains(search, case=False, na=False)
    ]

if low_stock_only:
    filtered_df["QTY"] = pd.to_numeric(filtered_df["QTY"], errors="coerce")
    filtered_df = filtered_df[filtered_df["QTY"] <= 3]

# --------------------------------------------------
# Display
# --------------------------------------------------
st.subheader("Inventory Table")
st.dataframe(filtered_df, use_container_width=True)
st.caption(f"Rows shown: {len(filtered_df)} / {len(df)}")

# --------------------------------------------------
# Download
# --------------------------------------------------
output = BytesIO()
filtered_df.to_excel(output, index=False)
output.seek(0)

st.download_button(
    "⬇️ Download filtered inventory (Excel)",
    data=output,
    file_name="filtered_inventory.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)










