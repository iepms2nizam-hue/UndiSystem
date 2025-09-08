import streamlit as st
import pandas as pd
import os, urllib.parse, json, time, shutil, subprocess
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

CSV_FILE = "pemilih.csv"
SETUP_FILE = "setup.json"

FOLDER_PPTX = "pptx"
FOLDER_SLIP = "slip"
os.makedirs(FOLDER_PPTX, exist_ok=True)
os.makedirs(FOLDER_SLIP, exist_ok=True)

# ====== STATE ======
if "busy" not in st.session_state:
    st.session_state["busy"] = False
if "uploads_locked" not in st.session_state:
    st.session_state["uploads_locked"] = False
if "ic_depan_bytes" not in st.session_state:
    st.session_state["ic_depan_bytes"] = None
if "ic_belakang_bytes" not in st.session_state:
    st.session_state["ic_belakang_bytes"] = None

# ====== HELPERS ======
def load_setup():
    with open(SETUP_FILE, "r") as f:
        return json.load(f)

def mask_ic(ic: str) -> str:
    if len(ic) == 12:
        return ic[:2] + "***" + ic[5:8] + "***" + ic[-1]
    return ic

def generate_kad_penghargaan(nama, ic_masked, whatsapp, email, bil):
    template_pptx = "kad_penghargaan.pptx"
    output_pptx = f"{FOLDER_PPTX}/output_{nama.replace(' ', '_').lower()}.pptx"
    output_pdf = output_pptx.replace(".pptx", ".pdf").replace(FOLDER_PPTX, FOLDER_SLIP)

    if not os.path.exists(template_pptx):
        return None

    prs = Presentation(template_pptx)
    slide = prs.slides[0]
    for shape in slide.shapes:
        if shape.has_text_frame and "your text here" in shape.text.strip().lower():
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.text = f"{nama.upper()}\nIC: {ic_masked}\nWhatsApp: {whatsapp}\nEmail: {email}\nNo Pendaftaran: {bil}"
            p.font.name = "Aptos Narrow"
            p.font.size = Pt(20)
            p.font.bold = True
            p.font.color.rgb = RGBColor(0, 32, 96)
            p.alignment = 1
            break
    prs.save(output_pptx)

    # fallback: just return pptx → pdf optional
    return output_pdf

# === UI
st.title("📝 Borang Pengundi (Client)")

setup = load_setup()
dun = st.selectbox("DUN", setup.get("dun", []))
daerah = st.selectbox("Daerah Mengundi", setup.get("daerah_mengundi", []))
lokaliti = st.selectbox("Lokaliti", setup.get("lokaliti", []))

nama = st.text_input("Nama Penuh")
no_kp = st.text_input("No Kad Pengenalan (12 digit, tanpa -)")

ic_depan = st.file_uploader("📷 Upload IC Depan", type=["jpg","jpeg","png"])
ic_belakang = st.file_uploader("📷 Upload IC Belakang", type=["jpg","jpeg","png"])

whatsapp = st.text_input("No WhatsApp")
email = st.text_input("Email")

with st.form("borang_pendaftaran", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        status = st.radio("Status", ["A (Aktif)", "P (Pasif)"], horizontal=True)
        sikap = st.radio("Sikap", ["P (Penyokong)", "G (Goyang)", "W (Wait & See)"], horizontal=True)
        umno = st.radio("UMNO", ["Y (Ya)", "N (Tidak)", "G (Gantung)"], horizontal=True)
        prbm = st.selectbox("PRBM", ["Ahli Biasa", "Veteran", "Ahli Seumur Hidup"])
    with col2:
        jawatan = st.text_input("Jawatan PDM")
        penilaian = st.text_input("Penilaian")
        blok = st.text_input("Blok")
        psywar = st.text_input("Psywar")

    submit = st.form_submit_button("💾 Simpan Data")

# ====== PROSES SUBMIT ======
if submit:
    with st.status("⏳ Sedang memproses pendaftaran...", expanded=True) as status_box:
        prog = st.progress(0)

        st.write("📂 Semak input...")
        time.sleep(0.5)
        prog.progress(20)

        # semak + simpan CSV
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE, dtype={"no_kp": str})
        else:
            df = pd.DataFrame(columns=[
                "dun","daerah_mengundi","lokaliti","nama","no_kp","status","sikap","umno","prbm",
                "jawatan_pdm","penilaian","blok","psywar","ic_depan","ic_belakang","whatsapp","email"
            ])

        st.write("📝 Simpan data CSV...")
        new_row = [dun, daerah, lokaliti, nama, f"'{no_kp}", status, sikap, umno, prbm,
                   jawatan, penilaian, blok, psywar,
                   "ic_front.jpg" if ic_depan else "", "ic_back.jpg" if ic_belakang else "",
                   f"'{whatsapp}", email]
        df.loc[len(df)] = new_row
        df.to_csv(CSV_FILE, index=False)
        time.sleep(0.5)
        prog.progress(50)

        st.write("📄 Jana kad penghargaan...")
        kad_file = generate_kad_penghargaan(nama, mask_ic(no_kp), whatsapp, email, bil=len(df))
        time.sleep(0.5)
        prog.progress(80)

        st.write("✅ Pendaftaran berjaya!")
        status_box.update(label="✅ Selesai!", state="complete", expanded=False)
        prog.progress(100)

        if kad_file:
            st.success("Kad penghargaan dijana.")
            st.download_button("⬇️ Muat Turun Kad PDF", data=b"PDF Placeholder", file_name="kad.pdf")
