import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard (Multi-File)")

# =========================
# AUTO HEADER DETECTION
# =========================
def detect_header_row(file):
    preview = pd.read_excel(file, header=None, nrows=6)
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.upper()
        if any(k in cell for cell in row for k in ["PART", "QTY", "DESC"]):
            return i
    return 0

# =========================
# LOAD SINGLE FILE
# =========================
def load_single_file(file, source_name):
    header = detect_header_row(file)
    df = pd.read_excel(file, header=header)

    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    def detect_column(cols, keys):
        for c in cols:
            for k in keys:
                if k in c:
                    return c
        return None

    cols = df.columns.tolist()

    rename_map = {}
    mapping = {
        "S.NO": ["S.NO", "SNO", "SERIAL"],
        "PART NO": ["PART", "ITEM"],
        "DESCRIPTION": ["DESC", "DESCRIPTION"],
        "BOX NO": ["BOX", "BIN", "LOCATION"],
        "QTY": ["QTY", "QUANTITY", "STOCK"]
    }

    for std, keys in mapping.items():
        col = detect_column(cols, keys)
        if col:
            rename_map[col] = std

    df = df.rename(columns=rename_map)

    keep = ["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]
    df = df[[c for c in keep if c in df.columns]]

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)
    df["SOURCE FILE"] = source_name

    return df

# =========================
# PRIORITY
# =========================
def apply_priority(df):
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
    return df

# =========================
# FILE UPLOAD (MULTI)
# =========================
files = st.file_uploader(
    "📤 Upload ONE or MORE Excel files",
    type=["xlsx"],
    accept_multiple_files=True
)

if not files:
    st.info("Upload one or more Excel inventory files.")
    st.stop()

# =========================
# LOAD ALL FILES
# =========================
all_data = []

for file in files:
    df = load_single_file(file, file.name)
    all_data.append(df)

master_df = pd.concat(all_data, ignore_index=True)
master_df = apply_priority(master_df)

if "inventory" not in st.session_state:
    st.session_state.inventory = master_df

df = st.session_state.inventory

# =========================
# METRICS
# =========================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Parts", len(df))
c2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
c3.metric("High", (df["PRIORITY LEVEL"] == "HIGH").sum())
c4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())

# =========================
# FILTERS
# =========================
st.subheader("📋 Spare Parts List")

search = st.text_input("🔍 Search Part No / Description")
source_filter = st.multiselect(
    "Source File",
    options=df["SOURCE FILE"].unique(),
    default=df["SOURCE FILE"].unique()
)

filtered_df = df[df["SOURCE FILE"].isin(source_filter)]

if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# =========================
# EDITABLE TABLE
# =========================
edited_df = st.data_editor(
    filtered_df,
    use_container_width=True,
    num_rows="fixed",
    disabled=[
        "S.NO", "PART NO", "DESCRIPTION",
        "BOX NO", "SOURCE FILE", "PRIORITY LEVEL"
    ]
)

if not edited_df.equals(filtered_df):
    st.session_state.inventory.update(edited_df)
    st.session_state.inventory = apply_priority(st.session_state.inventory)

# =========================
# DOWNLOAD
# =========================
output = BytesIO()
st.session_state.inventory.to_excel(output, index=False, engine="openpyxl")
output.seek(0)

st.download_button(
    "⬇️ Download Combined Inventory",
    data=output,
    file_name="combined_inventory.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write("Columns:", list(df.columns))
st.write("Files Loaded:", df["SOURCE FILE"].unique())















