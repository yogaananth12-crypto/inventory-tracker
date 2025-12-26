import streamlit as st
import pandas as pd
import requests

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Spare Parts Inventory", layout="wide")
st.title("🔧 Spare Parts Inventory")

# =========================
# CONFIG – CHANGE THESE
# =========================
SHEET_ID = "1PY9T5x0sqaDnHTZ5RoDx3LYGBu8bqOT7j4itdlC9yuE"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

SAVE_URL = "https://script.google.com/macros/s/AKfycbx0WFr35KlCjlSgCwOJB0waE86knqMt__xDy1bNKolTVdxve6LV4bwR-E9PJe13K8u8Gw/exec"

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_CSV_URL)

    # Clean headers
    df.columns = df.columns.astype(str).str.strip().str.upper()

    # Remove UNNAMED columns
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]

    # Required columns
    required_cols = [
        "S.NO", "PART NO", "DESCRIPTION", "BOX NO",
        "QTY", "LIFT NO", "CALL OUT", "DATE"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0).astype(int)

    return df[required_cols]


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
            original = df[df["S.NO"] == row["S.NO"]].iloc[0]

            if (
                row["QTY"] != original["QTY"]
                or row["LIFT NO"] != original["LIFT NO"]
                or row["CALL OUT"] != original["CALL OUT"]
                or row["DATE"] != original["DATE"]
            ):
                updates.append({
                    "sno": str(row["S.NO"]),
                    "qty": int(row["QTY"]),
                    "lift_no": str(row["LIFT NO"]),
                    "call_out": str(row["CALL OUT"]),
                    "date": str(row["DATE"]),
                })

        if not updates:
            st.info("No changes to save.")
        else:
            payload = {"updates": updates}

            r = requests.post(SAVE_URL, json=payload, timeout=20)

            if r.status_code == 200:
                st.success("✅ Saved successfully")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"❌ Save failed (Status {r.status_code})")
                st.write(r.text)










