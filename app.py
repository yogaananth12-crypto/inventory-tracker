import streamlit as st
import pandas as pd
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="KONE Lift Inventory",
    layout="wide"
)

# ---------------- HEADER (STREAMLIT SAFE) ----------------
st.markdown("##")

col1, col2, col3, col4 = st.columns([1,1,1,1])

with col1:
    st.markdown(
        "<div style='background:#0047BA;color:white;"
        "font-size:36px;font-weight:900;"
        "text-align:center;padding:18px;border-radius:6px;'>K</div>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        "<div style='background:#0047BA;color:white;"
        "font-size:36px;font-weight:900;"
        "text-align:center;padding:18px;border-radius:6px;'>O</div>",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        "<div style='background:#0047BA;color:white;"
        "font-size:36px;font-weight:900;"
        "text-align:center;padding:18px;border-radius:6px;'>N</div>",
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        "<div style='background:#0047BA;color:white;"
        "font-size:36px;font-weight:900;"
        "text-align:center;padding:18px;border-radius:6px;'>E</div>",
        unsafe_allow_html=True
    )

st.markdown("### Lift Inventory Tracker")
st.caption(date.today().strftime("%d %B %Y"))
st.divider()

# ---------------- DATA ----------------
df = pd.DataFrame({
    "S.NO": [1, 2],
    "PART NO": ["P-001", "P-002"],
    "DESCRIPTION": ["Motor", "Panel"],
    "BOX NO": ["B1", "B2"],
    "QTY": [1, 2],
    "LIFT NO": [1111, 2222],
    "CALL OUT": [3333, 4444],
    "DATE": ["2025-12-01", "2025-12-02"]
})

# ---------------- DATA EDITOR ----------------
edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    key="editor"
)

st.success("✅ Header visible + All columns editable")





















