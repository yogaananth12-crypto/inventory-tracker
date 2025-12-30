import streamlit as st
import pandas as pd
import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="KONE Lift Inventory",
    layout="wide"
)

# ---------------- KONE HEADER ----------------
today = datetime.date.today().strftime("%d %b %Y")

st.markdown(
    f"""
    <style>
    .kone-header {{
        background: white;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        text-align: center;
    }}

    .kone-header img {{
        height: 60px;
    }}

    .kone-title {{
        font-size: 22px;
        font-weight: 700;
        color: #003A8F;
        margin-top: 6px;
    }}

    .kone-date {{
        font-size: 13px;
        color: #6b7280;
    }}
    </style>

    <div class="kone-header">
        <img src="kone_logo.png">
        <div class="kone-title">Lift Inventory Tracker</div>
        <div class="kone-date">{today}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- LOAD DATA ----------------
# Replace this with Google Sheet later
# This structure MATCHES your sheet

data = {
    "S.NO": [1, 2, 3],
    "PART NO": ["PN-1001", "PN-1002", "PN-1003"],
    "DESCRIPTION": ["Motor", "Panel", "Cable"],
    "BOX NO": ["B1", "B2", "B3"],
    "QTY": [2, 4, 1],
    "LIFT NO": [9877666, 8947467, 8977655],
    "CALL OUT": [23449876, 89787667, 21324556],
    "DATE": [
        datetime.date(2025, 12, 1),
        datetime.date(2025, 12, 4),
        datetime.date(2025, 12, 12),
    ],
}

df = pd.DataFrame(data)

# ---------------- SEARCH ----------------
search = st.text_input("🔍 Search")

if search:
    df_view = df[df.apply(
        lambda r: r.astype(str).str.contains(search, case=False).any(),
        axis=1
    )]
else:
    df_view = df.copy()

# ---------------- DATA EDITOR ----------------
edited_df = st.data_editor(
    df_view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "S.NO": st.column_config.NumberColumn(
            "S.NO",
            disabled=True
        ),
        "PART NO": st.column_config.TextColumn(
            "PART NO",
            disabled=True
        ),
        "DESCRIPTION": st.column_config.TextColumn(
            "DESCRIPTION",
            disabled=True
        ),
        "BOX NO": st.column_config.TextColumn(
            "BOX NO",
            disabled=True
        ),
        "QTY": st.column_config.NumberColumn(
            "QTY",
            min_value=0,
            step=1
        ),
        "LIFT NO": st.column_config.NumberColumn(
            "LIFT NO"
        ),
        "CALL OUT": st.column_config.NumberColumn(
            "CALL OUT"
        ),
        "DATE": st.column_config.DateColumn(
            "DATE"
        ),
    },
    key="editor"
)

# ---------------- SAVE BUTTON (PLACEHOLDER) ----------------
st.markdown("---")
if st.button("💾 Save Changes"):
    st.success("Changes captured successfully (backend save can be added).")
















