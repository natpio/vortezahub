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

# Funkcja pomocnicza do konwersji obrazu na base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- 3. DYNAMICZNY SILNIK STATYSTYK ---
def get_dashboard_stats():
    """Pobiera dane dla Dashboardu."""
    stats = {"vehicles": 0, "alerts": 0, "euro": 0.0, "skus": 0}
    try:
        # Przykładowe statystyki (symulacja danych z Google Sheets/JSON)
        stats["vehicles"] = 24
        stats["alerts"] = 1
        stats["euro"] = 4.35
        stats["skus"] = 158
    except: pass
    return stats

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
                
                /* STYLIZACJA PASKA BOCZNEGO (MIEDZIANA CZCIONKA) */
                section[data-testid="stSidebar"] {{ 
                    background-color: rgba(3, 3, 3, 0.95) !important; 
                    border-right: 2px solid var(--v-copper); 
                    width: 350px !important; 
                }}
                section[data-testid="stSidebar"] * {{ color: var(--v-copper) !important; }}
                section[data-testid="stSidebar"] label p {{ font-size: 1.1rem !important; font-weight: bold; }}

                .v-status-glow {{ color: #00FF41; text-shadow: 0 0 10px #00FF41; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }}
                h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 4px !important; font-weight: 700 !important; }}
                
                /* KARTY MODUŁÓW */
                .module-card {{
                    background: rgba(10, 10, 10, 0.7);
                    border: 1px solid var(--v-copper);
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    transition: 0.4s;
                    min-height: 380px;
                }}
                .module-card:hover {{
                    background: rgba(181, 136, 99, 0.15);
                    transform: translateY(-10px);
                    box-shadow: 0 15px 30px rgba(181, 136, 99, 0.3);
                }}

                .stButton>button {{ 
                    background-color: transparent !important; color: var(--v-copper) !important; 
                    border: 1px solid var(--v-copper) !important; width: 100%; transition: 0.4s; font-weight: bold;
                    text-transform: uppercase;
                }}
                .stButton>button:hover {{ background-color: var(--v-copper) !important; color: black !important; }}
            </style>
        """, unsafe_allow_html=True)

# --- 5. GŁÓWNA LOGIKA HUB-A ---
def main_hub():
    inject_hub_theme()
    
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "PULPIT (DASHBOARD)"
    if "global_auth" not in st.session_state: 
        st.session_state.global_auth = False

    # --- EKRAN LOGOWANIA ---
    if not st.session_state.global_auth:
        _, col, _ = st.columns([0.8, 2, 0.8])
        with col:
            st.markdown("<br><br>", unsafe_allow_html=True)
            logo_path = os.path.join("assets", "logo_vorteza.jpg")
            if os.path.exists(logo_path): st.image(logo_path, width=280)

            video_path = os.path.join("assets", "video 1.mp4")
            if os.path.exists(video_path):
                st.video(video_path, autoplay=True, muted=True, loop=False)
            
            st.markdown("<h1 style='text-align:center;'>VORTEZA LOGIN</h1>", unsafe_allow_html=True)
            with st.form("ApexAuth"):
                pwd_input = st.text_input("GOLIATH SECURITY KEY", type="password")
                if st.form_submit_button("VALIDATE ACCESS"):
                    if pwd_input == st.secrets["password"]:
                        st.session_state.global_auth = True
                        st.rerun()
                    else: st.error("ACCESS DENIED")
        return

    # --- PASEK BOCZNY ---
    with st.sidebar:
        logo_path = os.path.join("assets", "logo_vorteza.jpg")
        if os.path.exists(logo_path): st.image(logo_path, use_column_width=True)
        st.markdown("<h2 style='text-align:center;'>VORTEZA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'><span class='v-status-glow'>● SYSTEM ONLINE</span></p>", unsafe_allow_html=True)
        
        modes = ["PULPIT (DASHBOARD)", "PLANER 3D (STACK)", "FINANSE (FLOW)", "FLOTA (BASE)"]
        st.session_state.app_mode = st.radio("NAWIGACJA", modes, index=modes.index(st.session_state.app_mode))
        
        st.divider()
        st.markdown(f"**OPERATOR:** {st.secrets['USERS'].get('admin', 'GOLIATH-01')}")
        st.markdown(f"**DATA:** {datetime.now().strftime('%d/%m/%Y')}")
        if st.button("TERMINATE SESSION"):
            st.session_state.global_auth = False
            st.rerun()

    # --- ROUTING ---
    if st.session_state.app_mode == "PULPIT (DASHBOARD)":
        banner_path = os.path.join("assets", "baner 1.jpg")
        if os.path.exists(banner_path):
            _, mid_col, _ = st.columns([1, 1.8, 1])
            with mid_col: st.image(banner_path, use_column_width=True)
            
        st.markdown("<h1 style='text-align:center;'>MISSION CONTROL</h1>", unsafe_allow_html=True)
        
        s = get_dashboard_stats()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY", s["vehicles"])
        c2.metric("AKTYWNE ALERTY", s["alerts"], delta=s["alerts"], delta_color="inverse")
        c3.metric("KURS EUR", f"{s['euro']} PLN")
        c4.metric("BAZA SKU", s["skus"])

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # SIATKA MODUŁÓW Z NOWYMI IKONAMI
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.markdown("<div class='module-card'>", unsafe_allow_html=True)
            icon_s = os.path.join("assets", "icon_stack.png")
            if os.path.exists(icon_s): st.image(icon_s, use_column_width=True)
            st.markdown("<h3>📦 STACK</h3><p>Optymalizacja załadunku 3D.</p>", unsafe_allow_html=True)
            if st.button("LAUNCH STACK"):
                st.session_state.app_mode = "PLANER 3D (STACK)"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        with m2:
            st.markdown("<div class='module-card'>", unsafe_allow_html=True)
            icon_f = os.path.join("assets", "icon_flow.png")
            if os.path.exists(icon_f): st.image(icon_f, use_column_width=True)
            st.markdown("<h3>💰 FLOW</h3><p>Rentowność i oferty PDF.</p>", unsafe_allow_html=True)
            if st.button("LAUNCH FLOW"):
                st.session_state.app_mode = "FINANSE (FLOW)"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
                
        with m3:
            st.markdown("<div class='module-card'>", unsafe_allow_html=True)
            icon_b = os.path.join("assets", "icon_base.png")
            if os.path.exists(icon_b): st.image(icon_b, use_column_width=True)
            st.markdown("<h3>🚛 BASE</h3><p>Zarządzanie flotą VORTEZA.</p>", unsafe_allow_html=True)
            if st.button("LAUNCH BASE"):
                st.session_state.app_mode = "FLOTA (BASE)"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.app_mode == "PLANER 3D (STACK)": run_stack()
    elif st.session_state.app_mode == "FINANSE (FLOW)": run_flow()
    elif st.session_state.app_mode == "FLOTA (BASE)": run_base()

if __name__ == "__main__":
    main_hub()
