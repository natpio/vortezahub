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
    st.error(f"KRYTYCZNY BŁĄD IMPORTU: Upewnij się, że pliki vorteza_stack.py, vorteza_flow.py i vorteza_base.py znajdują się w głównym folderze. Szczegóły: {e}")

# --- 2. KONFIGURACJA APEX ULTIMATE PLUS ---
st.set_page_config(
    page_title="VORTEZA APEX SYSTEMS v24.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# Funkcja pomocnicza do obrazów (Base64) - rozwiązuje problemy ze ścieżkami
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. PEŁNY SILNIK STATYSTYK (TWOJA LOGIKA BIZNESOWA) ---
def get_dashboard_stats():
    """Pobiera realne dane z Google Sheets i lokalnych JSONów dla Dashboardu."""
    stats = {"vehicles": 0, "alerts": 0, "euro": 0.0, "skus": 0}
    
    # Dane z Google Sheets (BASE)
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

    # Dane z lokalnych plików JSON (FLOW i STACK)
    try:
        if os.path.exists("data/config.json"):
            with open("data/config.json", "r", encoding="utf-8") as f:
                stats["euro"] = json.load(f).get("EURO_RATE", 0.0)
        
        if os.path.exists("data/products.json"):
            with open("data/products.json", "r", encoding="utf-8") as f:
                stats["skus"] = len(json.load(f))
    except: pass
    
    return stats

# --- 4. SILNIK WIZUALNY VORTEZA ---
def inject_hub_theme():
    bg_img = get_base64_image(os.path.join("assets", "tlo_hub_2.jpg"))
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono&display=swap');
            :root {{ --v-copper: #B58863; --v-dark: #060606; }}
            
            /* Tło główne */
            .stApp {{ 
                background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpg;base64,{bg_img}");
                background-size: cover; background-attachment: fixed; color: #FFFFFF; font-family: 'Montserrat', sans-serif; 
            }}
            
            /* Pasek boczny - stabilizacja layoutu i kolorystyki */
            section[data-testid="stSidebar"] {{ 
                background-color: rgba(3, 3, 3, 0.98) !important; 
                border-right: 2px solid var(--v-copper); 
            }}
            
            [data-testid="stSidebarNav"] span, 
            [data-testid="stSidebar"] .stMarkdown p, 
            [data-testid="stSidebar"] label {{
                color: var(--v-copper) !important;
                font-weight: 600 !important;
            }}

            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 4px !important; font-weight: 700 !important; text-align: center; }}
            
            /* INTERAKTYWNE KARTY DASHBOARDU */
            .module-container {{ position: relative; text-align: center; margin-bottom: 20px; }}
            .module-card {{
                background: rgba(10, 10, 10, 0.9);
                border: 2px solid var(--v-copper);
                border-radius: 15px;
                padding: 50px 10px;
                transition: 0.4s;
                height: 280px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}
            .module-container:hover .module-card {{
                background: rgba(181, 136, 99, 0.25);
                transform: translateY(-8px);
                box-shadow: 0 15px 35px rgba(181, 136, 99, 0.5);
            }}
            .module-card img {{ width: 130px; margin-bottom: 20px; filter: drop-shadow(0 0 10px rgba(181, 136, 99, 0.5)); }}
            .module-card h3 {{ margin: 0; font-size: 2rem !important; letter-spacing: 6px !important; }}

            /* Nakładka przycisku na całą ramkę */
            .stButton button {{
                position: absolute; top: 0; left: 0; width: 100%; height: 280px;
                background: transparent !important; border: none !important; color: transparent !important;
                z-index: 10; cursor: pointer;
            }}
            
            [data-testid="stMetricValue"] {{ color: var(--v-copper) !important; }}
            [data-testid="stMetricLabel"] {{ color: #FFFFFF !important; }}
            .v-status-glow {{ color: #00FF41; text-shadow: 0 0 10px #00FF41; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }}
        </style>
    """, unsafe_allow_html=True)

# --- 5. GŁÓWNA LOGIKA HUB-A ---
def main_hub():
    inject_hub_theme()
    
    # Inicjalizacja stanów sesji
    if "global_auth" not in st.session_state: st.session_state.global_auth = False
    if "app_mode" not in st.session_state: st.session_state.app_mode = "PULPIT (DASHBOARD)"
    if "username" not in st.session_state: st.session_state.username = "UNAUTHORIZED"

    # --- EKRAN LOGOWANIA ---
    if not st.session_state.global_auth:
        _, col, _ = st.columns([0.8, 2, 0.8])
        with col:
            logo_b64 = get_base64_image(os.path.join("assets", "logo_vorteza.jpg"))
            if logo_b64: st.markdown(f'<p style="text-align:center;"><img src="data:image/jpg;base64,{logo_b64}" width="280"></p>', unsafe_allow_html=True)
            
            video_path = os.path.join("assets", "video 1.mp4")
            if os.path.exists(video_path): st.video(video_path, autoplay=True, muted=True, loop=False)
            
            st.markdown("<h1 style='text-align:center;'>VORTEZA LOGIN</h1>", unsafe_allow_html=True)
            with st.form("ApexAuth"):
                pwd_input = st.text_input("GOLIATH SECURITY KEY", type="password")
                if st.form_submit_button("VALIDATE ACCESS"):
                    if pwd_input == st.secrets["password"]:
                        st.session_state.global_auth = True
                        st.session_state.username = st.secrets["USERS"].get("admin", "GOLIATH-OPERATOR")
                        st.rerun()
                    else: st.error("ACCESS DENIED")
        return

    # --- PASEK BOCZNY (SIDEBAR) ---
    with st.sidebar:
        logo_sidebar_b64 = get_base64_image(os.path.join("assets", "logo_vorteza.jpg"))
        if logo_sidebar_b64:
            st.markdown(f'<p style="text-align:center; margin-bottom: -15px;"><img src="data:image/jpg;base64,{logo_sidebar_b64}" style="width: 100%; max-width: 250px;"></p>', unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align:center; margin-top: 0;'>VORTEZA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'><span class='v-status-glow'>● SYSTEM ONLINE</span></p>", unsafe_allow_html=True)
        
        # Czysta nawigacja bez emotikon
        modes_map = {"DASHBOARD": "PULPIT (DASHBOARD)", "STACK": "PLANER 3D (STACK)", "FLOW": "FINANSE (FLOW)", "BASE": "FLOTA (BASE)"}
        current_display = "DASHBOARD"
        for k, v in modes_map.items():
            if v == st.session_state.app_mode: current_display = k
            
        choice = st.radio("NAWIGACJA", list(modes_map.keys()), index=list(modes_map.keys()).index(current_display))
        st.session_state.app_mode = modes_map[choice]
        
        st.divider()
        st.markdown(f"**OPERATOR:** {st.session_state.username}")
        st.markdown(f"**DATA:** {datetime.now().strftime('%d/%m/%Y')}")
        if st.button("TERMINATE SESSION"):
            st.session_state.global_auth = False
            st.rerun()

    # --- ROUTING (MISSION CONTROL) ---
    if st.session_state.app_mode == "PULPIT (DASHBOARD)":
        banner_path = os.path.join("assets", "baner 1.jpg")
        if os.path.exists(banner_path):
            _, mid_col, _ = st.columns([1, 1.8, 1])
            with mid_col: st.image(banner_path, use_column_width=True)
            
        st.markdown("<h1 style='text-align:center;'>MISSION CONTROL</h1>", unsafe_allow_html=True)
        
        # Statystyki realne
        s = get_dashboard_stats()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY", s["vehicles"])
        a_color = "inverse" if s["alerts"] > 0 else "normal"
        c2.metric("ALERTY", s["alerts"], delta=s["alerts"], delta_color=a_color)
        c3.metric("KURS EUR", f"{s['euro']} PLN")
        c4.metric("BAZA SKU", s["skus"])

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # SIATKA KLIKALNYCH MODUŁÓW
        m1, m2, m3 = st.columns(3)
        i_stack = get_base64_image(os.path.join("assets", "icon_stack.png"))
        i_flow = get_base64_image(os.path.join("assets", "icon_flow.png"))
        i_base = get_base64_image(os.path.join("assets", "icon_base.png"))

        with m1:
            st.markdown(f"<div class='module-container'><div class='module-card'><img src='data:image/png;base64,{i_stack}'><h3>STACK</h3></div></div>", unsafe_allow_html=True)
            if st.button(" ", key="btn_stack"):
                st.session_state.app_mode = "PLANER 3D (STACK)"
                st.rerun()
        with m2:
            st.markdown(f"<div class='module-container'><div class='module-card'><img src='data:image/png;base64,{i_flow}'><h3>FLOW</h3></div></div>", unsafe_allow_html=True)
            if st.button(" ", key="btn_flow"):
                st.session_state.app_mode = "FINANSE (FLOW)"
                st.rerun()
        with m3:
            st.markdown(f"<div class='module-container'><div class='module-card'><img src='data:image/png;base64,{i_base}'><h3>BASE</h3></div></div>", unsafe_allow_html=True)
            if st.button(" ", key="btn_base"):
                st.session_state.app_mode = "FLOTA (BASE)"
                st.rerun()

        if s["alerts"] > 0:
            st.error(f"UWAGA: Wykryto {s['alerts']} usterki w module BASE. Wymagana weryfikacja.")

    # Pozostałe moduły systemu
    elif st.session_state.app_mode == "PLANER 3D (STACK)": run_stack()
    elif st.session_state.app_mode == "FINANSE (FLOW)": run_flow()
    elif st.session_state.app_mode == "FLOTA (BASE)": run_base()

if __name__ == "__main__":
    main_hub()
