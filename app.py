import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory Dashboard (POC)")

EXCEL_FILE = "PCB BOARDS (CUP BOARD).xlsx"

# =========================
# AUTO DETECT HEADER ROW
# =========================
def detect_header_row(file):
    preview = pd.read_excel(file, header=None, nrows=6)
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.upper()
        if any("PART" in cell or "QTY" in cell for cell in row):
            return i
    return 0

# =========================
# LOAD DATA
# =========================
def load_data():
    try:
        header_row = detect_header_row(EXCEL_FILE)
        df = pd.read_excel(EXCEL_FILE, header=header_row)
    except Exception as e:
        st.error(f"❌ Error loading Excel file: {e}")
        return None

    # Normalize columns
    df.columns = df.columns.astype(str).str.strip().str.upper()

    # Remove UNNAMED columns
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # ---------- AUTO COLUMN DETECTION ----------
    def detect_column(columns, keywords):
        for col in columns:
            for key in keywords:
                if key in col:
                    return col
        return None

    cols = df.columns.tolist()

    rename_map = {
        detect_column(cols, ["S.NO", "SNO", "SERIAL"]): "S.NO",
        detect_column(cols, ["PART", "ITEM"]): "PART NO",
        detect_column(cols, ["DESC", "DESCRIPTION"]): "DESCRIPTION",
        detect_column(cols, ["BOX", "BIN", "LOCATION"]): "BOX NO",
        detect_column(cols, ["QTY", "QUANTITY", "STOCK"]): "QTY",
    }

    rename_map = {k: v for k, v in rename_map.items() if k}
    df = df.rename(columns=rename_map)

    # Keep only required columns
    required = ["S.NO", "PART NO", "DESCRIPTION", "BOX NO", "QTY"]
    for c in required:
        if c not in df.columns:
            df[c] = "" if c != "QTY" else 0

    df = df[required]

    # Drop EMPTY rows (THIS FIXES YOUR SCREENSHOT ISSUE)
    df = df[
        df["PART NO"].astype(str).str.strip().ne("")
        | df["DESCRIPTION"].astype(str).str.strip().ne("")
    ]

    # Ensure QTY numeric
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    # PRIORITY LOGIC
    df["PRIORITY LEVEL"] = "NORMAL"
    df.loc[df["QTY"] <= 3, "PRIORITY LEVEL"] = "HIGH"
    df.loc[df["QTY"] <= 1, "PRIORITY LEVEL"] = "URGENT"

    return df.reset_index(drop=True)

# =========================
# LOAD DATA
# =========================
df = load_data()

if df is None or df.empty:
    st.warning("⚠ No valid spare parts found.")
    st.stop()

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
search = st.text_input("🔍 Search Part Number or Description")

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

st.dataframe(filtered_df, use_container_width=True)

# =========================
# DOWNLOAD
# =========================
output = BytesIO()
filtered_df.to_excel(output, index=False)
output.seek(0)

st.download_button(
    "⬇️ Download Filtered Data (Excel)",
    output,
    "filtered_spare_parts.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.write("Rows shown:", len(filtered_df))
st.write("Columns:", list(df.columns))






















