import streamlit as st
import pandas as pd
import requests

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")

SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SAVE_URL = "https://script.google.com/macros/s/AKfycbx0WFr35KlCjlSgCwOJB0waE86knqMt__xDy1bNKolTVdxve6LV4bwR-E9PJe13K8u8Gw/exec"

st.title("🔧 Spare Parts Inventory")

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_CSV_URL)

    # Clean column names
    df.columns = df.columns.astype(str).str.strip().str.upper()

    # Remove UNNAMED columns
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # Ensure required columns
    required = [
        "S.NO", "PART NO", "DESCRIPTION", "BOX NO",
        "QTY", "LIFT NO", "CALL OUT", "DATE"
    ]
    for col in required:
        if col not in df.columns:
            df[col] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    return df[required]


df = load_data()

# =========================
# SEARCH BAR
# =========================
st.subheader("🔍 Search")

search = st.text_input(
    "Search by Part No / Description / Box No",
    placeholder="Type here..."
).strip().lower()

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        df["PART NO"].astype(str).str.lower().str.contains(search, na=False)
        | df["DESCRIPTION"].astype(str).str.lower().str.contains(search, na=False)
        | df["BOX NO"].astype(str).str.lower().str.contains(search, na=False)
    ]

# =========================
# DATA EDITOR
# =========================
edited_df = st.data_editor(
    filtered_df,
    disabled=["S.NO", "PART NO", "DESCRIPTION", "BOX NO"],
    use_container_width=True,
    hide_index=True,
    num_rows="fixed"
)

# =========================
# SAVE CHANGES
# =========================
if st.button("💾 Save Changes"):
    with st.spinner("Saving changes..."):
        updates = []

        for _, row in edited_df.iterrows():
            original_row = df[df["S.NO"] == row["S.NO"]].iloc[0]

            if (
                row["QTY"] != original_row["QTY"]
                or row["LIFT NO"] != original_row["LIFT NO"]
                or row["CALL OUT"] != original_row["CALL OUT"]
                or row["DATE"] != original_row["DATE"]
            ):
                updates.append({
                    "sno": row["S.NO"],
                    "qty": int(row["QTY"]),
                    "lift_no": str(row["LIFT NO"]),
                    "call_out": str(row["CALL OUT"]),
                    "date": str(row["DATE"]),
                })

        if not updates:
            st.info("No changes to save.")
        else:
            r = requests.post(
                SAVE_URL,
                json={"updates": updates},
                timeout=20
            )

            if r.status_code == 200 and r.text.strip() == "OK":
                st.success("✅ Saved successfully")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ Save failed. Check Apps Script.")









