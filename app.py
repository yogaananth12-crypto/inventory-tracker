import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard")

# =========================
# AUTO HEADER DETECTION
# =========================
def detect_header_row(file):
    preview = pd.read_excel(file, header=None, nrows=6)
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.upper()
        if any("PART" in c or "QTY" in c or "DESC" in c for c in row):
            return i
    return 0

# =========================
# LOAD DATA
# =========================
def load_data(file):
    header_row = detect_header_row(file)
    df = pd.read_excel(file, header=header_row)

    df.columns = df.columns.astype(str).str.strip().str.upper()

    # Remove UNNAMED columns
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    def detect_column(columns, keywords):
        for col in columns:
            for key in keywords:
                if key in col:
                    return col
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

    keep_cols = ["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]
    df = df[[c for c in keep_cols if c in df.columns]]

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    return df

# =========================
# PRIORITY LOGIC
# =========================
def apply_priority(df):
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"
    return df

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader("📤 Upload Spare Parts Excel File", type=["xlsx"])

if not uploaded_file:
    st.info("Please upload an Excel file.")
    st.stop()

if "data" not in st.session_state:
    st.session_state.data = apply_priority(load_data(uploaded_file))

df = st.session_state.data

# =========================
# METRICS
# =========================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Parts", len(df))
c2.metric("Urgent", (df["PRIORITY LEVEL"] == "URGENT").sum())
c3.metric("High", (df["PRIORITY LEVEL"] == "HIGH").sum())
c4.metric("Normal", (df["PRIORITY LEVEL"] == "NORMAL").sum())

# =========================
# SEARCH
# =========================
st.subheader("📋 Spare Parts List")
search = st.text_input("🔍 Search Part No / Description")

filtered_df = df.copy()
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
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "PRIORITY LEVEL"],
    key="editor"
)

# =========================
# UPDATE SESSION DATA
# =========================
if not edited_df.equals(filtered_df):
    st.session_state.data.update(edited_df)
    st.session_state.data = apply_priority(st.session_state.data)

# =========================
# DOWNLOAD
# =========================
output = BytesIO()
st.session_state.data.to_excel(output, index=False, engine="openpyxl")
output.seek(0)

st.download_button(
    "⬇️ Download Updated Inventory",
    data=output,
    file_name="updated_spare_parts.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write(list(df.columns))






















