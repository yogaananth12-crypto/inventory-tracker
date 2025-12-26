import streamlit as st
import pandas as pd

st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory")

FILE_NAME = "PCB BOARDS (CUP BOARD).xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_NAME, skiprows=1)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    required = ["S.NO", "PART NO", "DESCRIPTION", "BOX NO",
                "QTY", "LIFT NO", "CALL OUT", "DATE"]

    for c in required:
        if c not in df.columns:
            df[c] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)
    return df[required]

df = load_data()

# 🔍 SEARCH
search = st.text_input("🔍 Search Part No or Description")
if search:
    df_view = df[
        df["PART NO"].astype(str).str.contains(search, case=False, na=False)
        | df["DESCRIPTION"].astype(str).str.contains(search, case=False, na=False)
    ]
else:
    df_view = df.copy()

# ✏️ EDITOR
edited_df = st.data_editor(
    df_view,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    hide_index=True,
    use_container_width=True
)

# 💾 SAVE
if st.button("💾 SAVE"):
    editable_cols = ["QTY", "LIFT NO", "CALL OUT", "DATE"]

    df_idx = df.set_index("S.NO")
    edited_idx = edited_df.set_index("S.NO")

    changes = 0
    for sno in edited_idx.index:
        for col in editable_cols:
            if df_idx.loc[sno, col] != edited_idx.loc[sno, col]:
                df_idx.loc[sno, col] = edited_idx.loc[sno, col]
                changes += 1

    df_final = df_idx.reset_index()
    df_final.to_excel(FILE_NAME, index=False)

    st.success(f"Saved {changes} change(s)")














