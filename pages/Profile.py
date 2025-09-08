# Profile.py (patch v1.4.1)
import streamlit as st
import fitz  # PyMuPDF
import os
import pandas as pd
import json, urllib.parse

st.set_page_config(layout="wide")
st.title("✅ Semakan Kad Penghargaan Barisan Nasional")
st.markdown("---")

CSV_FILE = "pemilih.csv"
SLIP_FOLDER = "slip"

# ===== Helpers =====
def mask_ic(ic: str) -> str:
    ic = str(ic)
    return ic[:2] + "***" + ic[5:8] + "***" + ic[-1] if len(ic) == 12 else ic

def load_setup_safe():
    try:
        return json.load(open("setup.json", "r"))
    except Exception:
        return {}

def render_share_buttons(nama: str, masked_ic: str, profile_url: str):
    text = f"Kad Penghargaan BN\nNama: {nama}\nIC: {masked_ic}\nSemak: {profile_url}"
    enc_text = urllib.parse.quote(text)
    enc_url  = urllib.parse.quote(profile_url)
    wa = f"https://wa.me/?text={enc_text}"
    tg = f"https://t.me/share/url?url={enc_url}&text={enc_text}"
    fb = f"https://www.facebook.com/sharer/sharer.php?u={enc_url}"
    xx = f"https://twitter.com/intent/tweet?text={enc_text}&url={enc_url}"
    try:
        c1, c2, c3, c4 = st.columns(4)
        c1.link_button("🟢 WhatsApp", wa)
        c2.link_button("🔵 Telegram", tg)
        c3.link_button("🔷 Facebook", fb)
        c4.link_button("⚫ X (Twitter)", xx)
    except Exception:
        st.markdown(
            f"[🟢 WhatsApp]({wa}) &nbsp;|&nbsp; [🔵 Telegram]({tg}) &nbsp;|&nbsp; "
            f"[🔷 Facebook]({fb}) &nbsp;|&nbsp; [⚫ X]({xx})",
            unsafe_allow_html=True
        )

# ===== Query param =====
qp_ic = st.query_params.get("ic", "")
auto_ic = qp_ic if isinstance(qp_ic, str) else (qp_ic[0] if qp_ic else "")

# ===== IC state & live validation (input di LUAR form) =====
if "kp_input" not in st.session_state:
    st.session_state["kp_input"] = auto_ic

if "ic_valid" not in st.session_state:
    st.session_state["ic_valid"] = st.session_state["kp_input"].isdigit() and len(st.session_state["kp_input"]) == 12

def _validate_ic_state():
    ic = st.session_state.get("kp_input", "").strip()
    st.session_state["ic_valid"] = ic.isdigit() and len(ic) == 12

# Kotak input (luar form → boleh on_change)
with st.container():
    st.text_input(
        "Masukkan No Kad Pengenalan (12 digit tanpa -)",
        key="kp_input",
        value=st.session_state["kp_input"],
        on_change=_validate_ic_state,
    )

# Form hanya untuk butang submit (boleh disabled dinamik)
with st.form("semak_ic"):
    submit = st.form_submit_button("🔍 Semak", disabled=not st.session_state.get("ic_valid", False))

no_kp = st.session_state.get("kp_input", "").strip()

# Auto-trigger bila datang dari Client dengan ?ic=
trigger = submit or (auto_ic.isdigit() and len(auto_ic) == 12)

# Cuba guna path sebenar dari session_state dahulu (paling tepat)
session_pdf  = st.session_state.get("last_profile_pdf")
session_name = st.session_state.get("last_profile_name")
session_ic   = st.session_state.get("last_profile_ic")

if session_pdf and os.path.exists(session_pdf) and session_ic:
    nama = session_name or "Pengundi"
    no_kp = session_ic
    st.success(f"✅ Rekod dijumpai untuk: **{str(nama).upper()}**")

    try:
        with fitz.open(session_pdf) as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                st.image(pix.tobytes("png"), use_column_width=True)
    except Exception as e:
        st.error(f"❌ Gagal buka fail PDF: {e}")

    public_base = load_setup_safe().get("public_base_url", "http://localhost:8501")
    profile_url = f"{public_base}/Profile?ic={no_kp}"
    st.info("📣 Kongsi kad ini:")
    render_share_buttons(nama, mask_ic(no_kp), profile_url)

elif trigger:
    if not no_kp.isdigit() or len(no_kp) != 12:
        st.warning("❌ Sila masukkan 12 digit nombor IC yang sah.")
    else:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE, dtype={"no_kp": str})
            df["no_kp"] = df["no_kp"].astype(str).str.replace("^'", "", regex=True)
            row = df[df["no_kp"] == no_kp]
            if not row.empty:
                nama = row.iloc[0]["nama"]
                nama_slug = str(nama).replace(" ", "_").lower()
                pdf_path = f"{SLIP_FOLDER}/output_kad_penghargaan_{nama_slug}.pdf"

                st.success(f"✅ Rekod dijumpai untuk: **{str(nama).upper()}**")

                if os.path.exists(pdf_path):
                    try:
                        with fitz.open(pdf_path) as doc:
                            for page in doc:
                                pix = page.get_pixmap(dpi=150)
                                st.image(pix.tobytes("png"), use_column_width=True)
                    except Exception as e:
                        st.error(f"❌ Gagal buka fail PDF: {e}")
                else:
                    st.warning("⚠️ Fail PDF tidak dijumpai walaupun rekod wujud.")

                public_base = load_setup_safe().get("public_base_url", "http://localhost:8501")
                profile_url = f"{public_base}/Profile?ic={no_kp}"
                st.info("📣 Kongsi kad ini:")
                render_share_buttons(nama, mask_ic(no_kp), profile_url)

            else:
                st.error("❌ Maaf, IC ini belum didaftarkan. Sila daftar di halaman 'Client'.")
                st.page_link("pages/2_Client.py", label="➡ Pergi ke Halaman Daftar (Client)")
        else:
            st.error("❌ Fail pemilih.csv tidak dijumpai.")
else:
    st.info("Masukkan 12 digit IC dan tekan **Semak** — atau datang dari halaman Client, kad akan dipaparkan automatik.")
