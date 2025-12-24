import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import os

# ===============================
# APP CONFIG
# ===============================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard")

DATA_FOLDER = "inventory_files"

# ===============================
# AUTO-CREATE FOLDER
# ===============================
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    st.warning(
        f"Folder '{DATA_FOLDER}' has been created.\n\n"
        "Please add Excel files (.xlsx) into this folder and refresh the app."
    )
    st.stop()

# ===============================
# DETECT HEADER ROW
# ===============================
def detect_header_row(filepath):
    preview = pd.read_excel(filepath, header=None, nrows=6)
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.upper()
        if any(any(k in cell for k in ["PART", "QTY", "DESC"]) for cell in row):
            return i
    return 0

# ===============================
# LOAD SINGLE EXCEL FILE
# ===============================
def load_single_file(filepath):
    header_row = detect_header_row(filepath)
    original_df = pd.read_excel(filepath, header=header_row)

    df = original_df.copy()
    df.columns = df.columns.astype(str).str.strip().str.upper()

    # REMOVE UNNAMED COLUMNS
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    def find_column(cols, keys):
        for c in cols:
            for k in keys:
                if k in c:
                    return c
        return None

    cols = df.columns.tolist()

    col_map = {
        "PART NO": ["PART", "ITEM"],
        "DESCRIPTION": ["DESC", "DESCRIPTION"],
        "BOX NO": ["BOX", "BIN", "LOCATION"],
        "QTY": ["QTY", "QUANTITY", "STOCK", "BALANCE"]
    }

    rename = {}
    reverse_qty = None

    for std, keys in col_map.items():
        detected = find_column(cols, keys)
        if detected:
            rename[detected] = std
            if std == "QTY":
                reverse_qty = detected

    df = df.rename(columns=rename)

    # ENSURE REQUIRED COLUMNS
    for c in ["PART NO", "DESCRIPTION", "BOX NO", "QTY"]:
        if c not in df.columns:
            df[c] = 0 if c == "QTY" else ""

    df = df[["PART NO", "DESCRIPTION", "BOX NO", "QTY"]]
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    df["SOURCE FILE"] = os.path.basename(filepath)

    return df, original_df, reverse_qty

# ===============================
# PRIORITY LOGIC
# ===============================
def apply_priority(df):
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
    return df

# ===============================
# LOAD ALL FILES
# ===============================
files = [
    os.path.join(DATA_FOLDER, f)
    for f in os.listdir(DATA_FOLDER)
    if f.lower().endswith(".xlsx")
]

if not files:
    st.info("No Excel files found. Add files to 'inventory_files' folder.")
    st.stop()

all_dfs = []
file_cache = {}

for f in files:
    df, original, qty_col = load_single_file(f)
    all_dfs.append(df)
    file_cache[os.path.basename(f)] = {
        "original": original,
        "qty_col": qty_col
    }

inventory = apply_priority(pd.concat(all_dfs, ignore_index=True))

if "inventory" not in st.session_state:
    st.session_state.inventory = inventory

df = st.session_state.inventory

# ===============================
# METRICS
# ===============================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Parts", len(df))
c2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
c3.metric("High", (df["PRIORITY LEVEL"] == "HIGH").sum())
c4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())

# ===============================
# SEARCH & FILTER
# ===============================
search = st.text_input("🔍 Search Part No / Description")

filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# ===============================
# EDITABLE TABLE (ONLY QTY)
# ===============================
edited_df = st.data_editor(
    filtered_df,
    use_container_width=True,
    disabled=["PART NO", "DESCRIPTION", "BOX NO", "SOURCE FILE", "PRIORITY LEVEL"]
)

if not edited_df.equals(filtered_df):
    st.session_state.inventory.update(edited_df)
    st.session_state.inventory = apply_priority(st.session_state.inventory)

# ===============================
# DOWNLOAD UPDATED FILES
# ===============================
st.subheader("💾 Download Updated Excel Files")

zip_buffer = BytesIO()
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
    for fname, meta in file_cache.items():
        original = meta["original"].copy()
        qty_col = meta["qty_col"]

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
    "⬇️ Download ALL Updated Excel Files (ZIP)",
    zip_buffer,
    "updated_inventory.zip",
    "application/zip"
)





















