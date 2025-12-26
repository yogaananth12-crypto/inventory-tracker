import streamlit as st
import pandas as pd

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory")

FILE_NAME = "PCB BOARDS (CUP BOARD).xlsx"

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    df = pd.read_excel(FILE_NAME, skiprows=1)

    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    required_cols = [
        "S.NO", "PART NO", "DESCRIPTION", "BOX NO",
        "QTY", "LIFT NO", "CALL OUT", "DATE"
    ]

    for c in required_cols:
        if c not in df.columns:
            df[c] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    return df[required_cols]

df = load_data()

# ======================
# SEARCH
# ======================
search = st.text_input("🔍 Search Part No or Description")

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | filtered_df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]

# ======================
# DATA EDITOR
# ======================
edited_df = st.data_editor(
    filtered_df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    hide_index=True,
    use_container_width=True
)

# ======================
# SAVE (SAFE & CORRECT)
# ======================
if st.button("💾 SAVE"):
    editable_cols = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

    # Use S.NO as key
    df.set_index("S.NO", inplace=True)
    edited_df.set_index("S.NO", inplace=True)

    changes = 0

    for sno in edited_df.index:
        for col in editable_cols:
            if df.loc[sno, col] != edited_df.loc[sno, col]:
                df.loc[sno, col] = edited_df.loc[sno, col]
                changes += 1

    df.reset_index(inplace=True)

    if changes == 0:
        st.info("No changes detected")
    else:
        df.to_excel(FILE_NAME, index=False)
        st.success(f"Saved {changes} change(s) successfully")

# ======================
# DEBUG
# ======================
with st.expander("🛠 Debug"):
    st.write("Columns:", df.columns.tolist())















