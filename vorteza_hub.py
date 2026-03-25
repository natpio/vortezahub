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
    page_title="VORTEZA ENTERPRISE v24.2",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# Funkcja pomocnicza do obrazów (Base64) dla CSS i HTML
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. DYNAMICZNY SILNIK STATYSTYK (TWOJA ORYGINALNA LOGIKA) ---
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
    bg_path = os.path.join("assets", "tlo_hub_2.jpg")
    bg_img = get_base64_image(bg_path)
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono&display=swap');
            :root {{ --v-copper: #B58863; --v-dark: #060606; }}
            
            /* Tło całej aplikacji */
            .stApp {{ 
                background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpg;base64,{bg_img}");
                background-size: cover; background-attachment: fixed; color: #FFFFFF; font-family: 'Montserrat', sans-serif; 
            }}
            
            /* Pasek boczny - miedziany tekst */
            section[data-testid="stSidebar"] {{ 
                background-color: rgba(3, 3, 3, 0.95) !important; 
                border-right: 2px solid var(--v-copper); 
                width: 350px !important; 
            }}
            section[data-testid="stSidebar"] * {{ color: var(--v-copper) !important; }}
            section[data-testid="stSidebar"] .stMarkdown p {{ font-weight: 600; }}

            .v-status-glow {{ color: #00FF41; text-shadow: 0 0 10px #00FF41; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }}
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 4px !important; font-weight: 700 !important; }}
            
            /* Karty modułów */
            .module-card {{
                background: rgba(10, 10, 10, 0.8);
                border: 2px solid var(--v-copper);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: 0.4s;
                margin-bottom: 10px;
            }}
            .module-card:hover {{
                background: rgba(181, 136, 99, 0.15);
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(181, 136, 99, 0.4);
            }}
            .module-card img {{
                width: 100px;
                margin-bottom: 15px;
                filter: drop-shadow(0 0 8px rgba(181, 136, 99, 0.6));
            }}

            .stButton>button {{ 
                background-color: transparent !important; color: var(--v-copper) !important; 
                border: 1px solid var(--v-copper) !important; width: 100%; transition: 0.4s; font-weight: bold;
            }}
            .stButton>button:hover {{ background-color: var(--v-copper) !important; color: black !important; }}
            
            /* Stylizacja metryk */
            [data-testid="stMetricValue"] {{ color: var(--v-copper) !important; }}
            [data-testid="stMetricLabel"] {{ color: #FFFFFF !important; }}
        </style>
    """, unsafe_allow_html=True)

# --- 5. GŁÓWNA LOGIKA HUB-A ---
def main_hub():
    inject_hub_theme()
    
    # Inicjalizacja sesji
    if "global_auth" not in st.session_state: 
        st.session_state.global_auth = False
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "PULPIT (DASHBOARD)"
    if "username" not in st.session_state: 
        st.session_state.username = "UNAUTHORIZED"

    # --- EKRAN LOGOWANIA Z VIDEO (SINGLE PLAY) ---
    if not st.session_state.global_auth:
        _, col, _ = st.columns([0.8, 2, 0.8])
        with col:
            logo_path = os.path.join("assets", "logo_vorteza.jpg")
            if os.path.exists(logo_path): st.image(logo_path, width=280)
            
            video_path = os.path.join("assets", "video 1.mp4")
            if os.path.exists(video_path):
                # Film odtwarza się raz (loop=False)
                st.video(video_path, autoplay=True, muted=True, loop=False)
            
            st.markdown("<h1 style='text-align:center;'>VORTEZA LOGIN</h1>", unsafe_allow_html=True)
            with st.form("ApexAuth"):
                pwd_input = st.text_input("GOLIATH SECURITY KEY", type="password")
                if st.form_submit_button("VALIDATE ACCESS"):
                    if pwd_input == st.secrets["password"]:
                        st.session_state.global_auth = True
                        st.session_state.username = st.secrets["USERS"].get("admin", "NeonParrot821")
                        st.rerun()
                    else: st.error("ACCESS DENIED: INVALID KEY")
        return

    # --- PASEK BOCZNY (NAWIGACJA) ---
    with st.sidebar:
        logo_path = os.path.join("assets", "logo_vorteza.jpg")
        if os.path.exists(logo_path): st.image(logo_path, use_column_width=True)
        st.markdown("<h2 style='text-align:center;'>VORTEZA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'><span class='v-status-glow'>● SYSTEM STATUS: ONLINE</span></p>", unsafe_allow_html=True)
        st.divider()
        
        modes = ["PULPIT (DASHBOARD)", "PLANER 3D (STACK)", "FINANSE (FLOW)", "FLOTA (BASE)"]
        st.session_state.app_mode = st.radio("NAWIGACJA", modes, index=modes.index(st.session_state.app_mode))
        
        st.divider()
        st.markdown(f"**OPERATOR:** {st.session_state.username}")
        st.markdown(f"**DATA:** {datetime.now().strftime('%d/%m/%Y')}")
        if st.button("TERMINATE SESSION"):
            st.session_state.global_auth = False
            st.rerun()

    # --- ROUTING (PRZEŁĄCZANIE MODUŁÓW) ---
    if st.session_state.app_mode == "PULPIT (DASHBOARD)":
        banner_path = os.path.join("assets", "baner 1.jpg")
        if os.path.exists(banner_path):
            _, mid_col, _ = st.columns([1, 1.8, 1])
            with mid_col: st.image(banner_path, use_column_width=True)
            
        st.markdown("<h1 style='text-align:center;'>MISSION CONTROL</h1>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.spinner("Aktualizacja systemów..."):
            s = get_dashboard_stats()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY", s["vehicles"])
        a_color = "inverse" if s["alerts"] > 0 else "normal"
        c2.metric("ALERTY", s["alerts"], delta=s["alerts"], delta_color=a_color)
        c3.metric("EURO", f"{s['euro']} PLN")
        c4.metric("SKU", s["skus"])

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # SIATKA MODUŁÓW Z IKONAMI WEWNĄTRZ RAMKI
        m1, m2, m3 = st.columns(3)
        
        i_stack = get_base64_image(os.path.join("assets", "icon_stack.png"))
        i_flow = get_base64_image(os.path.join("assets", "icon_flow.png"))
        i_base = get_base64_image(os.path.join("assets", "icon_base.png"))

        with m1:
            st.markdown(f"""<div class='module-card'><img src="data:image/png;base64,{i_stack}"><h3>📦 STACK</h3><p>Optymalizacja załadunku 3D.</p></div>""", unsafe_allow_html=True)
            if st.button("LAUNCH STACK"):
                st.session_state.app_mode = "PLANER 3D (STACK)"
                st.rerun()
        
        with m2:
            st.markdown(f"""<div class='module-card'><img src="data:image/png;base64,{i_flow}"><h3>💰 FLOW</h3><p>Rentowność i oferty PDF.</p></div>""", unsafe_allow_html=True)
            if st.button("LAUNCH FLOW"):
                st.session_state.app_mode = "FINANSE (FLOW)"
                st.rerun()
                
        with m3:
            st.markdown(f"""<div class='module-card'><img src="data:image/png;base64,{i_base}"><h3>🚛 BASE</h3><p>Zarządzanie flotą VORTEZA.</p></div>""", unsafe_allow_html=True)
            if st.button("LAUNCH BASE"):
                st.session_state.app_mode = "FLOTA (BASE)"
                st.rerun()

        if s["alerts"] > 0:
            st.error(f"UWAGA: Wykryto {s['alerts']} usterki w module BASE. Wymagana weryfikacja.")
        else:
            st.success("Status floty: NOMINALNY. Wszystkie systemy sprawne.")

    elif st.session_state.app_mode == "PLANER 3D (STACK)": 
        run_stack()
    elif st.session_state.app_mode == "FINANSE (FLOW)": 
        run_flow()
    elif st.session_state.app_mode == "FLOTA (BASE)": 
        run_base()

if __name__ == "__main__":
    main_hub()
