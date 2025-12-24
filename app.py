import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import os

# =========================
# APP CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard")

DATA_FOLDER = "inventory_files"

# =========================
# SAFETY CHECK
# =========================
if not os.path.exists(DATA_FOLDER):
    st.error(
        f"Folder '{DATA_FOLDER}' not found.\n\n"
        "Create the folder and place Excel files inside it."
    )
    st.stop()

# =========================
# HEADER DETECTION
# =========================
def detect_header_row(filepath):
    preview = pd.read_excel(filepath, header=None, nrows=6)
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.upper()
        if any(k in cell for cell in row for k in ["PART", "QTY", "DESC"]):
            return i
    return 0

# =========================
# LOAD ONE FILE
# =========================
def load_single_file(filepath):
    header = detect_header_row(filepath)
    original_df = pd.read_excel(filepath, header=header)

    df = original_df.copy()
    df.columns = df.columns.astype(str).str.strip().str.upper()

    # Remove UNNAMED columns
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    def detect_column(cols, keys):
        for c in cols:
            for k in keys:
                if k in c:
                    return c
        return None

    cols = df.columns.tolist()

    mapping = {
        "PART NO": ["PART", "ITEM"],
        "DESCRIPTION": ["DESC", "DESCRIPTION"],
        "BOX NO": ["BOX", "BIN", "LOCATION"],
        "QTY": ["QTY", "QUANTITY", "STOCK", "BALANCE"]
    }

    rename_map = {}
    reverse_map = {}

    for std, keys in mapping.items():
        col = detect_column(cols, keys)
        if col:
            rename_map[col] = std
            reverse_map[std] = col

    df = df.rename(columns=rename_map)

    # Ensure required columns
    for col in ["PART NO", "DESCRIPTION", "BOX NO", "QTY"]:
        if col not in df.columns:
            df[col] = 0 if col == "QTY" else ""

    df = df[["PART NO", "DESCRIPTION", "BOX NO", "QTY"]]
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    df["SOURCE FILE"] = os.path.basename(filepath)

    return df, original_df, reverse_map.get("QTY")

# =========================
# PRIORITY LOGIC
# =========================
def apply_priority(df):
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
    return df

# =========================
# LOAD ALL EXCEL FILES
# =========================
excel_files = [
    os.path.join(DATA_FOLDER, f)
    for f in os.listdir(DATA_FOLDER)
    if f.lower().endswith(".xlsx")
]

if not excel_files:
    st.error("No Excel files found inside inventory_files folder.")
    st.stop()

all_data = []
file_store = {}

for path in excel_files:
    df, original, qty_col = load_single_file(path)
    all_data.append(df)
    file_store[os.path.basename(path)] = {
        "original": original,
        "qty_col": qty_col
    }

inventory = apply_priority(pd.concat(all_data, ignore_index=True))

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
# FILTERS
# =========================
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
    disabled=["PART NO", "DESCRIPTION", "BOX NO", "SOURCE FILE", "PRIORITY LEVEL"]
)

if not edited_df.equals(filtered_df):
    st.session_state.inventory.update(edited_df)
    st.session_state.inventory = apply_priority(st.session_state.inventory)

# =========================
# DOWNLOAD UPDATED FILES
# =========================
st.subheader("💾 Download Updated Excel Files")

zip_buffer = BytesIO()
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:

    for fname, info in file_store.items():
        original = info["original"].copy()
        qty_col = info["qty_col"]

        if not qty_col:
            continue

        updates = st.session_state.inventory[
            st.session_state.inventory["SOURCE FILE"] == fname
        ]

        for _, row in updates.iterrows():
            mask = original.astype(str).apply(
                lambda r: r.str.contains(str(row["PART NO"]), case=False, na=False)
            ).any(axis=1)
            original.loc[mask, qty_col] = row["QTY"]

        out = BytesIO()
        original.to_excel(out, index=False)
        zipf.writestr(f"UPDATED_{fname}", out.getvalue())

zip_buffer.seek(0)

st.download_button(
    "⬇️ Download ALL Updated Files (ZIP)",
    zip_buffer,
    "updated_inventory.zip",
    "application/zip"
)




















