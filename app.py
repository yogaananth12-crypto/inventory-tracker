import streamlit as st
import pandas as pd

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory")

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    df = pd.read_excel("PCB BOARDS (CUP BOARD).xlsx", skiprows=1)

    # Clean headers
    df.columns = df.columns.astype(str).str.strip().str.upper()

    # Remove UNNAMED columns
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # Required columns
    required_cols = [
        "S.NO", "PART NO", "DESCRIPTION", "BOX NO",
        "QTY", "LIFT NO", "CALL OUT", "DATE"
    ]

    # Add missing columns
    for c in required_cols:
        if c not in df.columns:
            df[c] = ""

    # Ensure QTY numeric
    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    return df[required_cols]

df = load_data()

# ======================
# SEARCH BAR
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
    use_container_width=True,
    hide_index=True
)

# ======================
# SAVE LOGIC (LOCAL ONLY)
# ======================
if st.button("💾 SAVE"):
    # Only compare columns that exist
    editable_cols = ["QTY", "LIFT NO", "CALL OUT", "DATE"]
    editable_cols = [c for c in editable_cols if c in df.columns]

    changes = 0

    for i in range(len(df)):
        if not df.loc[i, editable_cols].equals(edited_df.loc[i, editable_cols]):
            df.loc[i, editable_cols] = edited_df.loc[i, editable_cols]
            changes += 1

    if changes == 0:
        st.info("No changes detected")
    else:
        df.to_excel("PCB BOARDS (CUP BOARD).xlsx", index=False)
        st.success(f"Saved {changes} change(s) successfully")

# ======================
# DEBUG (OPTIONAL)
# ======================
with st.expander("🛠 Debug"):
    st.write("Columns:", df.columns.tolist())














