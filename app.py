import streamlit as st
import pandas as pd
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="KONE Inventory",
    layout="wide"
)

# ---------------- KONE HEADER ----------------
today = date.today().strftime("%d %b %Y")

st.markdown(
    f"""
    <style>
    .kone-header {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 25px;
    }}

    .kone-logo {{
        display: flex;
        gap: 6px;
    }}

    .kone-box {{
        width: 60px;
        height: 60px;
        background-color: #005EB8;
        color: white;
        font-size: 36px;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: Arial, Helvetica, sans-serif;
    }}

    .kone-date {{
        margin-top: 8px;
        font-size: 14px;
        color: #555;
    }}
    </style>

    <div class="kone-header">
        <div class="kone-logo">
            <div class="kone-box">K</div>
            <div class="kone-box">O</div>
            <div class="kone-box">N</div>
            <div class="kone-box">E</div>
        </div>
        <div class="kone-date">{today}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- LOAD DATA ----------------
# Replace this with your Google Sheet loading logic if already present
data = {
    "PART NO": ["P-001", "P-002"],
    "DESCRIPTION": ["Motor", "Panel"],
    "BOX NO": ["B1", "B2"],
    "QTY": [1, 2],
    "LIFT NO": ["1111", "2222"],
    "CALL OUT": ["3333", "4444"],
    "DATE": ["2025-12-01", "2025-12-02"]
}

df = pd.DataFrame(data)

# ---------------- DATA EDITOR ----------------
edited = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "LIFT NO": st.column_config.TextColumn(),
        "CALL OUT": st.column_config.TextColumn(),
        "DATE": st.column_config.TextColumn(),
    },
    key="editor"
)

# ---------------- SAVE PREVIEW ----------------
st.write("### Live Data Preview")
st.dataframe(edited, use_container_width=True)







