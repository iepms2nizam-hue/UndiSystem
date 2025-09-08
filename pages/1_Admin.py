import streamlit as st
import json, os, sys, importlib.util

USER_FILE = "users.json"

# ====== Loader helper ======
def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load manage & analisis dari folder pages
manage = load_module(os.path.join("pages", "admin_manage.py"), "admin_manage")
analisis = load_module(os.path.join("pages", "admin_analisis.py"), "admin_analisis")

# ====== Users ======
@st.cache_data
def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

# ====== UI ======
st.set_page_config(layout="wide")
st.title("🔑 Admin Panel")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

if not st.session_state["logged_in"]:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users()
        user = next((u for u in users if u["username"] == username and u["password"] == password), None)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("❌ Username / Password salah")
else:
    st.success(f"✅ Anda login sebagai: {st.session_state['user']['username']} (ADMIN)")
    if st.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.rerun()

    # === Tabs ===
    tab1, tab2 = st.tabs(["📝 Manage Data", "📊 Analisis Data"])
    with tab1:
        manage.render_manage()
    with tab2:
        analisis.render_analisis()
