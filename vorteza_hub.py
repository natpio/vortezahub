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
    page_title="VORTEZA ENTERPRISE v24.1",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# Funkcja pomocnicza do konwersji obrazu na base64 (dla tła CSS)
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- 3. DYNAMICZNY SILNIK STATYSTYK (LIVE DATA) ---
def get_dashboard_stats():
    """Pobiera realne dane z Google Sheets i lokalnych JSONów dla Dashboardu."""
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
    # Pobieranie tła w base64
    bg_img = get_base64_image("tlo_hub_2.jpg")
    bg_style = ""
    if bg_img:
        bg_style = f"""
            background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpg;base64,{bg_img}");
            background-size: cover;
            background-attachment: fixed;
        """

    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono&display=swap');
            :root {{ --v-copper: #B58863; --v-dark: #060606; }}
            
            .stApp {{ 
                {bg_style}
                color: #FFFFFF; 
                font-family: 'Montserrat', sans-serif; 
            }}
            
            section[data-testid="stSidebar"] {{ 
                background-color: rgba(3, 3, 3, 0.9) !important; 
                border-right: 1px solid rgba(181, 136, 99, 0.3); 
                width: 350px !important; 
            }}
            
            .v-status-glow {{ color: #00FF41; text-shadow: 0 0 10px #00FF41; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }}
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 6px !important; font-weight: 700 !important; }}
            
            .stButton>button {{ 
                background-color: transparent !important; 
                color: var(--v-copper) !important; 
                border: 1px solid var(--v-copper) !important; 
                width: 100%; 
                transition: 0.4s; 
                font-weight: bold;
            }}
            .stButton>button:hover {{ background-color: var(--v-copper) !important; color: black !important; }}
            
            /* Stylizacja formularza logowania */
            [data-testid="stForm"] {{
                background-color: rgba(0, 0, 0, 0.8);
                border: 1px solid var(--v-copper);
                border-radius: 10px;
                padding: 30px;
            }}
        </style>
    """, unsafe_allow_html=True)

# --- 5. GŁÓWNA LOGIKA HUB-A ---
def main_hub():
    inject_hub_theme()
    
    if "global_auth" not in st.session_state: 
        st.session_state.global_auth = False
    if "username" not in st.session_state: 
        st.session_state.username = "UNAUTHORIZED"

    # --- EKRAN LOGOWANIA Z VIDEO (SINGLE PLAY) ---
    if not st.session_state.global_auth:
        _, col, _ = st.columns([0.8, 2, 0.8])
        with col:
            st.markdown("<br><br>", unsafe_allow_html=True)
            # Wyświetlanie Logo na ekranie logowania
            if os.path.exists("logo_vorteza.jpg"):
                st.image("logo_vorteza.jpg", width=250)

            # Implementacja video promocyjnego - Loop ustawiony na False
            video_path = os.path.join("assets", "video 1.mp4")
            if os.path.exists(video_path):
                # Video odtwarza się tylko raz (loop=False)
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
        # Integracja Logo w pasku bocznym
        if os.path.exists("logo_vorteza.jpg"):
            st.image("logo_vorteza.jpg", use_column_width=True)
        
        st.markdown("<h2 style='letter-spacing:10px; text-align:center;'>VORTEZA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'><span class='v-status-glow'>● SYSTEM STATUS: ONLINE</span></p>", unsafe_allow_html=True)
        st.divider()
        app_mode = st.radio("MODUŁY SYSTEMOWE", ["PULPIT (DASHBOARD)", "PLANER 3D (STACK)", "FINANSE (FLOW)", "FLOTA (BASE)"])
        st.divider()
        st.markdown(f"**OPERATOR:** {st.session_state.username}")
        st.markdown(f"**CZAS:** {datetime.now().strftime('%H:%M:%S')}")
        if st.button("TERMINATE SESSION"):
            st.session_state.global_auth = False
            st.session_state.username = "UNAUTHORIZED"
            st.rerun()

    # --- ROUTING (PRZEŁĄCZANIE MODUŁÓW) ---
    if app_mode == "PULPIT (DASHBOARD)":
        # Integracja Baner 1 jako nagłówek Dashboardu
        if os.path.exists("baner 1.jpg"):
            st.image("baner 1.jpg", use_column_width=True)
            
        st.markdown("<h1>MISSION CONTROL</h1>", unsafe_allow_html=True)
        st.markdown("---")
        with st.spinner("Pobieranie statusu operacyjnego..."):
            s = get_dashboard_stats()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY W SYSTEMIE", s["vehicles"])
        a_color = "inverse" if s["alerts"] > 0 else "normal"
        c2.metric("AKTYWNE ALERTY", s["alerts"], delta=s["alerts"], delta_color=a_color)
        c3.metric("KURS EURO (V)", f"{s['euro']} PLN")
        c4.metric("BAZA SKU", s["skus"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if s["alerts"] > 0:
            st.error(f"UWAGA: Wykryto {s['alerts']} usterki w module BASE. Wymagana weryfikacja.")
        else:
            st.success("Status floty: NOMINALNY. Wszystkie systemy sprawne.")

    elif app_mode == "PLANER 3D (STACK)": 
        run_stack()
    elif app_mode == "FINANSE (FLOW)": 
        run_flow()
    elif app_mode == "FLOTA (BASE)": 
        run_base()

if __name__ == "__main__":
    main_hub()
