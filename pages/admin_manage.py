import streamlit as st
import pandas as pd
import os

CSV_FILE = "pemilih.csv"

@st.cache_data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, dtype={"no_kp": str})
    else:
        return pd.DataFrame()

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def render_manage():
    st.subheader("📋 Senarai Pengundi (Edit / Tambah / Delete)")

    df = load_data()
    if df.empty:
        st.info("❌ Belum ada data pengundi.")
        return

    df_temp = df.copy()
    if "selected" not in df_temp.columns:
        df_temp.insert(0, "selected", False)

    edited_df = st.data_editor(
        df_temp,
        num_rows="dynamic",
        width="stretch",
        hide_index=True
    )

    selected_rows = edited_df[edited_df["selected"] == True]

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Save Selected"):
            for idx in selected_rows.index:
                for col in df.columns:
                    df.at[idx, col] = edited_df.at[idx, col]
            save_data(df)
            st.success("✅ Rekod dipilih berjaya disimpan!")

    with c2:
        if st.button("🗑️ Delete Selected"):
            df = df.drop(selected_rows.index)
            save_data(df)
            st.success("✅ Rekod dipilih berjaya dipadam!")

    with c3:
        if st.button("🔄 Refresh Table"):
            st.rerun()
