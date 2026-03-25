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
    st.error(f"KRYTYCZNY BŁĄD IMPORTU: {e}")

# --- 2. KONFIGURACJA APEX ULTIMATE PLUS ---
st.set_page_config(
    page_title="VORTEZA ENTERPRISE v24.2",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def get_dashboard_stats():
    # ... (logika pobierania statystyk bez zmian) ...
    return {"vehicles": 12, "alerts": 1, "euro": 4.32, "skus": 145}

# --- 4. SILNIK WIZUALNY VORTEZA ---
def inject_hub_theme():
    bg_path = os.path.join("assets", "tlo_hub_2.jpg")
    bg_img = get_base64_image(bg_path)
    
    if bg_img:
        st.markdown(f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono&display=swap');
                :root {{ --v-copper: #B58863; --v-dark: #060606; }}
                
                .stApp {{ 
                    background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("data:image/jpg;base64,{bg_img}");
                    background-size: cover; background-attachment: fixed; color: #FFFFFF; font-family: 'Montserrat', sans-serif; 
                }}
                
                section[data-testid="stSidebar"] {{ background-color: rgba(3, 3, 3, 0.9) !important; border-right: 2px solid var(--v-copper); width: 350px !important; }}
                section[data-testid="stSidebar"] *, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {{ color: var(--v-copper) !important; }}

                .v-status-glow {{ color: #00FF41; text-shadow: 0 0 10px #00FF41; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }}
                h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 6px !important; font-weight: 700 !important; }}
                
                /* Styl kart modułów na Dashboardzie */
                .module-card {{
                    background: rgba(20, 20, 20, 0.6);
                    border: 1px solid var(--v-copper);
                    border-radius: 15px;
                    padding: 25px;
                    text-align: center;
                    transition: 0.3s;
                    height: 100%;
                }}
                .module-card:hover {{
                    background: rgba(181, 136, 99, 0.1);
                    transform: translateY(-5px);
                    box-shadow: 0 10px 20px rgba(181, 136, 99, 0.2);
                }}

                .stButton>button {{ 
                    background-color: transparent !important; color: var(--v-copper) !important; 
                    border: 1px solid var(--v-copper) !important; width: 100%; transition: 0.4s; font-weight: bold;
                }}
                .stButton>button:hover {{ background-color: var(--v-copper) !important; color: black !important; }}
            </style>
        """, unsafe_allow_html=True)

# --- 5. GŁÓWNA LOGIKA HUB-A ---
def main_hub():
    inject_hub_theme()
    
    # Inicjalizacja stanu nawigacji
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "PULPIT (DASHBOARD)"
    if "global_auth" not in st.session_state: 
        st.session_state.global_auth = False

    # --- LOGOWANIE (Bez zmian) ---
    if not st.session_state.global_auth:
        # ... (kod logowania z poprzedniej wersji) ...
        # Po poprawnym hasle: st.session_state.global_auth = True; st.rerun()
        _, col, _ = st.columns([0.8, 2, 0.8])
        with col:
            logo_path = os.path.join("assets", "logo_vorteza.jpg")
            if os.path.exists(logo_path): st.image(logo_path, width=250)
            st.markdown("<h1 style='text-align:center;'>VORTEZA LOGIN</h1>", unsafe_allow_html=True)
            with st.form("ApexAuth"):
                pwd_input = st.text_input("GOLIATH SECURITY KEY", type="password")
                if st.form_submit_button("VALIDATE ACCESS"):
                    if pwd_input == st.secrets["password"]:
                        st.session_state.global_auth = True
                        st.rerun()
        return

    # --- PASEK BOCZNY ---
    with st.sidebar:
        logo_path = os.path.join("assets", "logo_vorteza.jpg")
        if os.path.exists(logo_path): st.image(logo_path, use_column_width=True)
        st.markdown("<h2 style='text-align:center;'>VORTEZA</h2>", unsafe_allow_html=True)
        
        # Nawigacja powiązana z session_state
        modes = ["PULPIT (DASHBOARD)", "PLANER 3D (STACK)", "FINANSE (FLOW)", "FLOTA (BASE)"]
        st.session_state.app_mode = st.radio("MODUŁY SYSTEMOWE", modes, index=modes.index(st.session_state.app_mode))
        
        st.divider()
        if st.button("TERMINATE SESSION"):
            st.session_state.global_auth = False
            st.rerun()

    # --- ROUTING ---
    if st.session_state.app_mode == "PULPIT (DASHBOARD)":
        banner_path = os.path.join("assets", "baner 1.jpg")
        if os.path.exists(banner_path):
            _, mid_col, _ = st.columns([1, 2, 1])
            with mid_col: st.image(banner_path, use_column_width=True)
            
        st.markdown("<h1 style='text-align:center;'>MISSION CONTROL</h1>", unsafe_allow_html=True)
        
        # STATYSTYKI
        s = get_dashboard_stats()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY", s["vehicles"])
        c2.metric("ALERTY", s["alerts"], delta=s["alerts"], delta_color="inverse")
        c3.metric("EURO", f"{s['euro']} PLN")
        c4.metric("SKU", s["skus"])

        st.markdown("<br><h3 style='text-align:center;'>MODULAR ACCESS</h3>", unsafe_allow_html=True)
        
        # SIATKA MODUŁÓW (INTERAKTYWNA NAWIGACJA)
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.markdown("""<div class='module-card'><h3>📦 STACK</h3><p>Optymalizacja załadunku 3D i rozmieszczenia towaru.</p></div>""", unsafe_allow_html=True)
            if st.button("LAUNCH STACK"):
                st.session_state.app_mode = "PLANER 3D (STACK)"
                st.rerun()
        
        with m2:
            st.markdown("""<div class='module-card'><h3>💰 FLOW</h3><p>Analiza rentowności tras i automatyczne oferty PDF.</p></div>""", unsafe_allow_html=True)
            if st.button("LAUNCH FLOW"):
                st.session_state.app_mode = "FINANSE (FLOW)"
                st.rerun()
                
        with m3:
            st.markdown("""<div class='module-card'><h3>🚛 BASE</h3><p>Zarządzanie flotą, przeglądy i statusy kierowców.</p></div>""", unsafe_allow_html=True)
            if st.button("LAUNCH BASE"):
                st.session_state.app_mode = "FLOTA (BASE)"
                st.rerun()

    elif st.session_state.app_mode == "PLANER 3D (STACK)": run_stack()
    elif st.session_state.app_mode == "FINANSE (FLOW)": run_flow()
    elif st.session_state.app_mode == "FLOTA (BASE)": run_base()

if __name__ == "__main__":
    main_hub()
