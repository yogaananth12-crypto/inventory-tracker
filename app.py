import streamlit as st
import pandas as pd

st.set_page_config(page_title="KONE TEST", layout="wide")

st.markdown(
    """
    <div style="
        background:#003A8F;
        color:white;
        padding:20px;
        border-radius:12px;
        font-size:26px;
        font-weight:700;
        text-align:center;
        ">
        KONE – Lift Inventory Tracker
    </div>
    """,
    unsafe_allow_html=True
)

st.write("👇 IF YOU SEE BLUE HEADER, CODE IS RUNNING")

df = pd.DataFrame({
    "S.NO": [1, 2],
    "PART NO": ["P-001", "P-002"],
    "DESCRIPTION": ["Motor", "Panel"],
    "BOX NO": ["B1", "B2"],
    "QTY": [1, 2],
    "LIFT NO": [1111, 2222],
    "CALL OUT": [3333, 4444],
    "DATE": ["2025-12-01", "2025-12-02"],
})

st.data_editor(
    df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "S.NO": st.column_config.NumberColumn(disabled=True),
        "PART NO": st.column_config.TextColumn(disabled=True),
        "DESCRIPTION": st.column_config.TextColumn(disabled=True),
        "BOX NO": st.column_config.TextColumn(disabled=True),
        "QTY": st.column_config.NumberColumn(),
        "LIFT NO": st.column_config.NumberColumn(),
        "CALL OUT": st.column_config.NumberColumn(),
        "DATE": st.column_config.TextColumn(),
    }
)

















