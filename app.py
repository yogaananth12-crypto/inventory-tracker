import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard (Multi-File + Save Back)")

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
    original_df = pd.read_excel(file, header=header)

    df = original_df.copy()
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    def detect_column(cols, keys):
        for c in cols:
            for k in keys:
                if k in c:
                    return c
        return None

    cols = df.columns.tolist()

    mapping = {
        "S.NO": ["S.NO", "SNO", "SERIAL"],
        "PART NO": ["PART", "ITEM"],
        "DESCRIPTION": ["DESC", "DESCRIPTION"],
        "BOX NO": ["BOX", "BIN", "LOCATION"],
        "QTY": ["QTY", "QUANTITY", "STOCK", "BALANCE"]
    }

    rename_map = {}
    for std, keys in mapping.items():
        col = detect_column(cols, keys)
        if col:
            rename_map[col] = std

    df = df.rename(columns=rename_map)

    for col in ["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]:
        if col not in df.columns:
            df[col] = 0 if col == "QTY" else ""

    df = df[["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]]
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    df["SOURCE FILE"] = source_name
    df["__ROW_ID__"] = df.index  # used for writing back

    return df, original_df, header

# =========================
# PRIORITY
# =========================
def apply_priority(df):
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
    return df

# =========================
# FILE UPLOAD
# =========================
files = st.file_uploader(
    "📤 Upload ONE or MORE Excel files",
    type=["xlsx"],
    accept_multiple_files=True
)

if not files:
    st.info("Upload Excel files to continue.")
    st.stop()

# =========================
# LOAD FILES
# =========================
all_data = []
file_store = {}

for file in files:
    df, original_df, header = load_single_file(file, file.name)
    all_data.append(df)
    file_store[file.name] = {
        "original": original_df,
        "header": header
    }

inventory = pd.concat(all_data, ignore_index=True)
inventory = apply_priority(inventory)

if "inventory" not in st.session_state:
    st.session_state.inventory = inventory

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
# FILTER
# =========================
st.subheader("📋 Spare Parts List")

search = st.text_input("🔍 Search Part No / Description")
source_filter = st.multiselect(
    "Source File",
    df["SOURCE FILE"].unique(),
    df["SOURCE FILE"].unique()
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
    disabled=[
        "S.NO", "PART NO", "DESCRIPTION",
        "BOX NO", "SOURCE FILE",
        "PRIORITY LEVEL", "__ROW_ID__"
    ]
)

if not edited_df.equals(filtered_df):
    st.session_state.inventory.update(edited_df)
    st.session_state.inventory = apply_priority(st.session_state.inventory)

# =========================
# SAVE BACK TO FILES
# =========================
st.subheader("💾 Save Updates")

zip_buffer = BytesIO()
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:

    for fname, info in file_store.items():
        original = info["original"].copy()
        header = info["header"]

        updates = st.session_state.inventory[
            st.session_state.inventory["SOURCE FILE"] == fname
        ]

        for _, row in updates.iterrows():
            original.loc[row["__ROW_ID__"], original.columns[-1]] = row["QTY"]

        out = BytesIO()
        original.to_excel(out, index=False, startrow=header)
        out.seek(0)

        zipf.writestr(f"UPDATED_{fname}", out.read())

zip_buffer.seek(0)

st.download_button(
    "⬇️ Download UPDATED FILES (ZIP)",
    data=zip_buffer,
    file_name="updated_inventory_files.zip",
    mime="application/zip"
)
st.write(df.head())
















