import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px

CSV_FILE = "pemilih.csv"

@st.cache_data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, dtype={"no_kp": str})
    else:
        return pd.DataFrame()

def render_analisis():
    st.subheader("📊 Analisis Data Pengundi")

    df = load_data()
    if df.empty:
        st.info("❌ Belum ada data pengundi.")
        return

    # === FILTERS ===
    st.subheader("🔍 Filter Data")
    col1, col2, col3, col4, col5 = st.columns(5)
    col6, col7, col8, col9, col10 = st.columns(5)

    with col1:
        chk_dun = st.checkbox("DUN", value=False)
        opt_dun = st.selectbox("DUN", ["Semua"] + sorted(df["dun"].dropna().unique().tolist()))
    with col2:
        chk_daerah = st.checkbox("Daerah", value=False)
        opt_daerah = st.selectbox("Daerah", ["Semua"] + sorted(df["daerah_mengundi"].dropna().unique().tolist()))
    with col3:
        chk_lokaliti = st.checkbox("Lokaliti", value=False)
        opt_lokaliti = st.selectbox("Lokaliti", ["Semua"] + sorted(df["lokaliti"].dropna().unique().tolist()))
    with col4:
        chk_status = st.checkbox("Status", value=False)
        opt_status = st.selectbox("Status", ["Semua"] + sorted(df["status"].dropna().unique().tolist()))
    with col5:
        chk_sikap = st.checkbox("Sikap", value=False)
        opt_sikap = st.selectbox("Sikap", ["Semua"] + sorted(df["sikap"].dropna().unique().tolist()))

    with col6:
        chk_umno = st.checkbox("UMNO", value=False)
        opt_umno = st.selectbox("UMNO", ["Semua"] + sorted(df["umno"].dropna().unique().tolist()))
    with col7:
        chk_blok = st.checkbox("Blok", value=False)
        opt_blok = st.selectbox("Blok", ["Semua"] + sorted(df["blok"].dropna().unique().tolist()))
    with col8:
        chk_jawatan = st.checkbox("Jawatan PDM", value=False)
        opt_jawatan = st.selectbox("Jawatan PDM", ["Semua"] + sorted(df["jawatan_pdm"].dropna().unique().tolist()))
    with col9:
        chk_prbm = st.checkbox("PRBM", value=False)
        opt_prbm = st.selectbox("PRBM", ["Semua"] + sorted(df["prbm"].dropna().unique().tolist()))
    with col10:
        chk_penilaian = st.checkbox("Penilaian", value=False)
        opt_penilaian = st.selectbox("Penilaian", ["Semua"] + sorted(df["penilaian"].dropna().unique().tolist()))

    chart_df = df.copy()
    if chk_dun and opt_dun != "Semua": chart_df = chart_df[chart_df["dun"] == opt_dun]
    if chk_daerah and opt_daerah != "Semua": chart_df = chart_df[chart_df["daerah_mengundi"] == opt_daerah]
    if chk_lokaliti and opt_lokaliti != "Semua": chart_df = chart_df[chart_df["lokaliti"] == opt_lokaliti]
    if chk_status and opt_status != "Semua": chart_df = chart_df[chart_df["status"] == opt_status]
    if chk_sikap and opt_sikap != "Semua": chart_df = chart_df[chart_df["sikap"] == opt_sikap]
    if chk_umno and opt_umno != "Semua": chart_df = chart_df[chart_df["umno"] == opt_umno]
    if chk_blok and opt_blok != "Semua": chart_df = chart_df[chart_df["blok"] == opt_blok]
    if chk_jawatan and opt_jawatan != "Semua": chart_df = chart_df[chart_df["jawatan_pdm"] == opt_jawatan]
    if chk_prbm and opt_prbm != "Semua": chart_df = chart_df[chart_df["prbm"] == opt_prbm]
    if chk_penilaian and opt_penilaian != "Semua": chart_df = chart_df[chart_df["penilaian"] == opt_penilaian]

    # === CHARTS ===
    if not chart_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("Status Distribution")
            fig, ax = plt.subplots()
            chart_df["status"].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
            st.pyplot(fig)
        with col2:
            st.write("Sikap Distribution")
            fig, ax = plt.subplots()
            chart_df["sikap"].value_counts().plot.bar(ax=ax)
            st.pyplot(fig)
    else:
        st.warning("⚠️ Tiada data untuk dipaparkan berdasarkan tick filter.")

    # 3D Chart
    if not chart_df.empty:
        st.subheader("🌐 3D Statistik Interaktif (Status vs Sikap)")
        counts = chart_df.groupby(["status","sikap"]).size().reset_index(name="jumlah")
        fig = px.scatter_3d(
            counts,
            x="status", y="sikap", z="jumlah",
            color="jumlah", size="jumlah",
            hover_data=["status","sikap","jumlah"]
        )
        st.plotly_chart(fig, use_container_width=True)

    # Gabungan semua filter
    st.subheader("📊 Gabungan Semua Filter (Ikut Tick)")
    fields = ["dun","daerah_mengundi","lokaliti","status","sikap","umno","blok","jawatan_pdm","prbm","penilaian"]
    all_data = []
    for col in fields:
        if col in chart_df.columns:
            counts = chart_df[col].value_counts().reset_index()
            counts.columns = ["kategori","jumlah"]
            counts["filter"] = col
            all_data.append(counts)
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        fig = px.bar(combined, x="kategori", y="jumlah", color="filter", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    # === ChatGPT Q&A (with smart fallback) ===
    st.subheader("💬 Tanya Data (AI Assistant)")
    user_q = st.text_area("Soalan anda:", placeholder="Contoh: Pecahan sikap di DUN Gum-Gum untuk UMNO")
    if st.button("📊 Analisa dengan AI") and user_q.strip():
        with st.spinner("⏳ AI sedang analisa data..."):
            try:
                import openai, os
                openai.api_key = os.getenv("OPENAI_API_KEY")
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Anda pembantu analisis data."},
                        {"role": "user", "content": user_q}
                    ],
                    max_tokens=400
                )
                answer = response["choices"][0]["message"]["content"]
                st.success("💡 Jawapan AI:")
                st.write(answer)

            except Exception as e:
                st.warning(f"⚠️ AI tidak aktif ({e}). Fallback ke analisis manual.")
                q = user_q.lower()
                df_fallback = chart_df.copy()

                mapping = {
                    "umno": "umno",
                    "status": "status",
                    "sikap": "sikap",
                    "dun": "dun",
                    "daerah": "daerah_mengundi",
                    "lokaliti": "lokaliti",
                    "blok": "blok",
                    "jawatan": "jawatan_pdm",
                    "prbm": "prbm",
                    "penilaian": "penilaian"
                }

                filters = []
                focus_col = None

                # Detect keywords
                for keyword, col in mapping.items():
                    if keyword in q:
                        filters.append(col)
                        if "pecahan" in q:
                            focus_col = col  # column to group by

                # Apply filters
                for f in filters:
                    for val in df_fallback[f].dropna().unique():
                        if str(val).lower() in q:
                            df_fallback = df_fallback[df_fallback[f] == val]

                if focus_col and focus_col in df_fallback.columns:
                    counts = df_fallback[focus_col].value_counts()
                    st.info(f"📊 Pecahan {focus_col} berdasarkan syarat: {dict(counts)}")

                    fig = px.bar(
                        counts.reset_index(),
                        x="index", y=focus_col,
                        color="index", title=f"Pecahan {focus_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.info(f"📊 Jumlah rekod padan: **{len(df_fallback)} orang**")

    # Table bawah
    st.subheader(f"📋 Senarai Pengundi (Jumlah: {len(chart_df)})")
    st.dataframe(chart_df, width="stretch")
