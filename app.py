import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard (Multi-File + Safe Save)")

# =========================
# HEADER DETECTION
# =========================
def detect_header_row(file):
    preview = pd.read_excel(file, header=None, nrows=6)
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.upper()
        if any(k in cell for cell in row for k in ["PART", "QTY", "DESC"]):
            return i
    return 0

# =========================
# LOAD FILE
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
            reverse_map[std] = col  # for writeback

    df = df.rename(columns=rename_map)

    # Ensure required columns
    for col in ["PART NO", "DESCRIPTION", "BOX NO", "QTY"]:
        if col not in df.columns:
            df[col] = 0 if col == "QTY" else ""

    df = df[["PART NO", "DESCRIPTION", "BOX NO", "QTY"]]
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    df["SOURCE FILE"] = source_name

    return df, original_df, reverse_map, header

# =========================
# PRIORITY
# =========================
def apply_priority(df):
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
    return df

# =========================
# UPLOAD
# =========================
files = st.file_uploader(
    "📤 Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True
)

if not files:
    st.stop()

dataframes = []
file_store = {}

for file in files:
    df, original, col_map, header = load_single_file(file, file.name)
    dataframes.append(df)
    file_store[file.name] = {
        "original": original,
        "qty_col": col_map.get("QTY"),
        "header": header
    }

inventory = apply_priority(pd.concat(dataframes, ignore_index=True))

if "inventory" not in st.session_state:
    st.session_state.inventory = inventory

df = st.session_state.inventory

# =========================
# SEARCH
# =========================
search = st.text_input("🔍 Search Part No / Description")

if search:
    df = df[
        df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# =========================
# EDIT
# =========================
edited = st.data_editor(
    df,
    use_container_width=True,
    disabled=["PART NO", "DESCRIPTION", "BOX NO", "SOURCE FILE", "PRIORITY LEVEL"]
)

if not edited.equals(df):
    st.session_state.inventory.update(edited)
    st.session_state.inventory = apply_priority(st.session_state.inventory)

# =========================
# SAVE BACK
# =========================
st.subheader("💾 Download Updated Files")

zip_buffer = BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zipf:

    for fname, info in file_store.items():
        original = info["original"].copy()
        qty_col = info["qty_col"]

        if not qty_col:
            continue

        updates = st.session_state.inventory[
            st.session_state.inventory["SOURCE FILE"] == fname
        ]

        for _, row in updates.iterrows():
            mask = (
                original.astype(str)
                .apply(lambda r: r.str.contains(str(row["PART NO"]), case=False, na=False))
                .any(axis=1)
            )
            original.loc[mask, qty_col] = row["QTY"]

        out = BytesIO()
        original.to_excel(out, index=False)
        zipf.writestr(f"UPDATED_{fname}", out.getvalue())

zip_buffer.seek(0)

st.download_button(
    "⬇️ Download UPDATED Excel Files (ZIP)",
    zip_buffer,
    "updated_inventory.zip",
    "application/zip"
)

















