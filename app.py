import streamlit as st
import os, time

st.set_page_config(page_title="Sistem Rekod Pemilih", page_icon="🗳️")

# Cache working directory
@st.cache_data
def get_working_dir():
    return os.getcwd()

# Cache senarai fail dalam folder pages/
@st.cache_data
def list_pages_folder():
    try:
        return os.listdir("pages")
    except Exception as e:
        return f"❌ Gagal baca folder pages/: {e}"

# UI Loading
with st.spinner("Memuatkan sistem rekod pemilih..."):
    time.sleep(0.5)  
    cwd = get_working_dir()
    pages = list_pages_folder()

# Tajuk
st.title("🗳️ Sistem Rekod Pemilih")

# Papar gambar branding
st.image("data-sains.png", caption="Professional Data Designer", use_container_width=True)

st.markdown("""
Selamat datang ke sistem rekod pemilih.  
Gunakan menu di sidebar untuk akses:

- 🔑 Admin / Moderator Panel  
- 📝 Borang Client (Pengundi)
""")

st.write("📂 Working directory:", cwd)

if isinstance(pages, list):
    st.write("📄 Pages folder content:", pages)
else:
    st.error(pages)
