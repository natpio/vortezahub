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
    page_title="VORTEZA APEX SYSTEMS v24.2",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# Funkcja pomocnicza do Base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return ""
    return ""

# --- 3. DYNAMICZNY SILNIK STATYSTYK (TWOJA LOGIKA BIZNESOWA) ---
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

# --- 4. SILNIK WIZUALNY VORTEZA ---
def inject_hub_theme():
    bg_img = get_base64_image(os.path.join("assets", "tlo_hub_2.jpg"))
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono&display=swap');
            :root {{ --v-copper: #B58863; --v-dark: #060606; }}
            .stApp {{ 
                background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpg;base64,{bg_img}");
                background-size: cover; background-attachment: fixed; color: #FFFFFF; font-family: 'Montserrat', sans-serif; 
            }}
            section[data-testid="stSidebar"] {{ background-color: rgba(3, 3, 3, 0.98) !important; border-right: 2px solid var(--v-copper); }}
            [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {{
                color: var(--v-copper) !important; font-weight: 600 !important;
            }}
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 4px !important; font-weight: 700 !important; text-align: center; }}
            
            /* KARTY DASHBOARDU */
            .module-container {{ position: relative; text-align: center; margin-bottom: 25px; }}
            .module-card {{
                background: rgba(10, 10, 10, 0.9); border: 2px solid var(--v-copper); border-radius: 15px;
                padding: 45px 10px; transition: 0.4s; height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center;
            }}
            .module-container:hover .module-card {{ background: rgba(181, 136, 99, 0.25); transform: translateY(-5px); box-shadow: 0 15px 35px rgba(181, 136, 99, 0.5); }}
            .module-card img {{ width: 130px; margin-bottom: 20px; filter: drop-shadow(0 0 10px rgba(181, 136, 99, 0.5)); }}
            .module-card h3 {{ margin: 0; font-size: 1.8rem !important; letter-spacing: 5px !important; }}

            /* Przezroczysty przycisk na całą ramkę */
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
    
    # Inicjalizacja sesji (Kluczowe dla STACK!)
    if "global_auth" not in st.session_state: st.session_state.global_auth = False
    if "username" not in st.session_state: st.session_state.username = "UNAUTHORIZED"
    
    # Inicjalizacja trybu aplikacji - IDENTYCZNIE jak w Twoim kodzie rano
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "PULPIT (DASHBOARD)"

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
                        st.session_state.username = st.secrets["USERS"].get("admin", "NeonParrot821")
                        st.rerun()
                    else: st.error("ACCESS DENIED")
        return

    # --- PASEK BOCZNY ---
    with st.sidebar:
        logo_side_b64 = get_base64_image(os.path.join("assets", "logo_vorteza.jpg"))
        if logo_side_b64:
            st.markdown(f'<p style="text-align:center; margin-bottom: -15px;"><img src="data:image/jpg;base64,{logo_side_b64}" style="width: 100%; max-width: 250px;"></p>', unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align:center; margin-top: 0;'>VORTEZA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'><span class='v-status-glow'>● SYSTEM ONLINE</span></p>", unsafe_allow_html=True)
        
        # RADIO POWIĄZANE Z SESSION_STATE
        options = ["PULPIT (DASHBOARD)", "PLANER 3D (STACK)", "FINANSE (FLOW)", "FLOTA (BASE)"]
        
        # To ustawia radio na podstawie tego, co kliknąłeś na Dashboardzie
        st.session_state.app_mode = st.radio("NAWIGACJA", options, index=options.index(st.session_state.app_mode))
        
        st.divider()
        st.markdown(f"**OPERATOR:** {st.session_state.username}")
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
        st.markdown("---")
        
        with st.spinner("Pobieranie statusu..."):
            s = get_dashboard_stats()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY", s["vehicles"])
        a_color = "inverse" if s["alerts"] > 0 else "normal"
        c2.metric("ALERTY", s["alerts"], delta=s["alerts"], delta_color=a_color)
        c3.metric("KURS EUR", f"{s['euro']} PLN")
        c4.metric("BAZA SKU", s["skus"])

        st.markdown("<br><br>", unsafe_allow_html=True)
        
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

    # --- URUCHAMIANIE MODUŁÓW (Twoja oryginalna logika ranna) ---
    elif st.session_state.app_mode == "PLANER 3D (STACK)":
        run_stack()
    elif st.session_state.app_mode == "FINANSE (FLOW)":
        run_flow()
    elif st.session_state.app_mode == "FLOTA (BASE)":
        run_base()

if __name__ == "__main__":
    main_hub()
