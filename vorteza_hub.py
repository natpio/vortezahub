import streamlit as st
import json
import os
import pandas as pd
import base64
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# --- 1. IMPORTY MODUŁÓW VORTEZA ---
try:
    from vorteza_stack import run_stack
    from vorteza_flow import run_flow
    from vorteza_base import run_base
except ImportError as e:
    st.error(f"BŁĄD IMPORTU: {e}")

# --- 2. KONFIGURACJA ---
st.set_page_config(
    page_title="VORTEZA APEX SYSTEMS v24.2",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. LOGIKA STATYSTYK (TWOJA ORYGINALNA) ---
def get_dashboard_stats():
    stats = {"vehicles": 0, "alerts": 0, "euro": 0.0, "skus": 0}
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["GCP_SERVICE_ACCOUNT"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1JV-vXpwAbvvboQd7eijashVmS3kkOqTf_LJrbrsWSxo").sheet1
        df_base = pd.DataFrame(sheet.get_all_records())
        if not df_base.empty:
            stats["vehicles"] = len(df_base['Numer Rejestracyjny'].unique())
            stats["alerts"] = len(df_base[df_base['Wynik Kontroli'].astype(str).str.contains("ALERT", na=False)])
    except: pass
    try:
        if os.path.exists("data/config.json"):
            with open("data/config.json", "r", encoding="utf-8") as f:
                stats["euro"] = json.load(f).get("EURO_RATE", 0.0)
        if os.path.exists("data/products.json"):
            with open("data/products.json", "r", encoding="utf-8") as f:
                stats["skus"] = len(json.load(f))
    except: pass
    return stats

# --- 4. CSS (DESIGN CARBON & COPPER) ---
def inject_hub_theme():
    bg_img = get_base64_image(os.path.join("assets", "tlo_hub_2.jpg"))
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
            :root {{ --v-copper: #B58863; }}
            .stApp {{ 
                background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpg;base64,{bg_img}");
                background-size: cover; background-attachment: fixed; color: #FFFFFF; font-family: 'Montserrat', sans-serif; 
            }}
            section[data-testid="stSidebar"] {{ background-color: rgba(3, 3, 3, 0.98) !important; border-right: 2px solid var(--v-copper); }}
            [data-testid="stSidebar"] * {{ color: var(--v-copper) !important; }}
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; text-align: center; }}
            
            .module-card {{
                background: rgba(10, 10, 10, 0.9); border: 2px solid var(--v-copper); border-radius: 15px;
                padding: 40px 10px; height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center;
                position: relative; transition: 0.3s;
            }}
            .module-card:hover {{ background: rgba(181, 136, 99, 0.2); transform: translateY(-5px); }}
            .module-card img {{ width: 120px; margin-bottom: 20px; }}
            
            .stButton button {{
                position: absolute; top: 0; left: 0; width: 100%; height: 280px;
                background: transparent !important; border: none !important; color: transparent !important; z-index: 10;
            }}
        </style>
    """, unsafe_allow_html=True)

# --- 5. GŁÓWNA LOGIKA ---
def main_hub():
    inject_hub_theme()
    
    if "global_auth" not in st.session_state: st.session_state.global_auth = False
    
    # KLUCZOWE: Inicjalizacja trybu rano
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "PULPIT (DASHBOARD)"

    # LOGOWANIE
    if not st.session_state.global_auth:
        _, col, _ = st.columns([0.8, 2, 0.8])
        with col:
            st.markdown("<h1>VORTEZA LOGIN</h1>", unsafe_allow_html=True)
            pwd = st.text_input("GOLIATH KEY", type="password")
            if st.button("VALIDATE", key="login_btn"):
                if pwd == st.secrets["password"]:
                    st.session_state.global_auth = True
                    st.rerun()
        return

    # SIDEBAR
    with st.sidebar:
        logo_b64 = get_base64_image(os.path.join("assets", "logo_vorteza.jpg"))
        if logo_b64: st.markdown(f'<img src="data:image/jpg;base64,{logo_b64}" width="100%">', unsafe_allow_html=True)
        
        # Nawigacja - używamy 'key', żeby Streamlit sam pilnował stanu
        options = ["PULPIT (DASHBOARD)", "PLANER 3D (STACK)", "FINANSE (FLOW)", "FLOTA (BASE)"]
        st.radio("NAWIGACJA", options, key="app_mode")
        
        st.divider()
        if st.button("LOGOUT"):
            st.session_state.global_auth = False
            st.rerun()

    # ROUTING
    mode = st.session_state.app_mode

    if mode == "PULPIT (DASHBOARD)":
        st.markdown("<h1>MISSION CONTROL</h1>", unsafe_allow_html=True)
        s = get_dashboard_stats()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY", s["vehicles"])
        c2.metric("ALERTY", s["alerts"])
        c3.metric("EURO", f"{s['euro']} PLN")
        c4.metric("SKU", s["skus"])

        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        
        # Kafelki aktualizują session_state.app_mode
        with m1:
            st.markdown(f"<div class='module-card'><img src='data:image/png;base64,{get_base64_image(os.path.join('assets', 'icon_stack.png'))}'><h3>STACK</h3></div>", unsafe_allow_html=True)
            if st.button(" ", key="btn_s"):
                st.session_state.app_mode = "PLANER 3D (STACK)"
                st.rerun()
        with m2:
            st.markdown(f"<div class='module-card'><img src='data:image/png;base64,{get_base64_image(os.path.join('assets', 'icon_flow.png'))}'><h3>FLOW</h3></div>", unsafe_allow_html=True)
            if st.button(" ", key="btn_f"):
                st.session_state.app_mode = "FINANSE (FLOW)"
                st.rerun()
        with m3:
            st.markdown(f"<div class='module-card'><img src='data:image/png;base64,{get_base64_image(os.path.join('assets', 'icon_base.png'))}'><h3>BASE</h3></div>", unsafe_allow_html=True)
            if st.button(" ", key="btn_b"):
                st.session_state.app_mode = "FLOTA (BASE)"
                st.rerun()

    elif mode == "PLANER 3D (STACK)":
        run_stack()
    elif mode == "FINANSE (FLOW)":
        run_flow()
    elif mode == "FLOTA (BASE)":
        run_base()

if __name__ == "__main__":
    main_hub()
