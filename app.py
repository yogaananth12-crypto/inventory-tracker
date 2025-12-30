import streamlit as st
import pandas as pd
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- HEADER ----------------
today = date.today().strftime("%d %b %Y")

st.markdown("""
<style>
.kone-row {
    display:flex;
    justify-content:center;
    gap:6px;
    margin-top:20px;
}
.kone-box {
    background:#0047BA;
    color:white;
    font-size:34px;
    font-weight:900;
    width:58px;
    height:58px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:4px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kone-row">
  <div class="kone-box">K</div>
  <div class="kone-box">O</div>
  <div class="kone-box">N</div>
  <div class="kone-box">E</div>
</div>

<h3 style="text-align:center; margin-top:10px;">
Lift Inventory Tracker
</h3>

<p style="text-align:center; color:gray;">
{today}
</p>

<hr>
""", unsafe_allow_html=True)

# ---------------- SAMPLE DATA (REPLACE WITH GOOGLE SHEET LATER) ----------------
data = {
    "S.NO": [1, 2],
    "PART NO": ["P-001", "P-002"],
    "DESCRIPTION": ["Motor", "Panel"],
    "BOX NO": ["B1", "B2"],
    "QTY": [1, 2],
    "LIFT NO": [1111, 2222],
    "CALL OUT": [3333, 4444],
    "DATE": ["2025-12-01", "2025-12-02"]
}

df = pd.DataFrame(data)

# ---------------- DATA EDITOR ----------------
edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    key="editor"
)

# ---------------- DEBUG CONFIRMATION ----------------
st.success("✅ If you can edit ALL columns, this version is correct.")




















