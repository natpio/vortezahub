import streamlit as st
import json
import os
import pandas as pd
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

# --- 3. DYNAMICZNY SILNIK STATYSTYK (LIVE DATA) ---
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
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono&display=swap');
            :root { --v-copper: #B58863; --v-dark: #060606; }
            .stApp { background-color: var(--v-dark); color: #FFFFFF; font-family: 'Montserrat', sans-serif; }
            section[data-testid="stSidebar"] { background-color: #030303 !important; border-right: 1px solid rgba(181, 136, 99, 0.3); width: 350px !important; }
            .v-status-glow { color: #00FF41; text-shadow: 0 0 10px #00FF41; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }
            h1, h2, h3 { color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 6px !important; font-weight: 700 !important; }
            .stButton>button { background-color: transparent !important; color: var(--v-copper) !important; border: 1px solid var(--v-copper) !important; width: 100%; transition: 0.4s; }
            .stButton>button:hover { background-color: var(--v-copper) !important; color: black !important; }
        </style>
    """, unsafe_allow_html=True)

# --- 5. GŁÓWNA LOGIKA HUB-A ---
def main_hub():
    inject_hub_theme()
    
    # --- INICJALIZACJA SESJI ---
    if "global_auth" not in st.session_state: 
        st.session_state.global_auth = False
    if "username" not in st.session_state: 
        st.session_state.username = "UNAUTHORIZED"

    # --- EKRAN LOGOWANIA Z VIDEO ---
    if not st.session_state.global_auth:
        _, col, _ = st.columns([0.8, 2, 0.8])
        with col:
            # Implementacja video promocyjnego
            video_path = os.path.join("assets", "video 1.mp4")
            if os.path.exists(video_path):
                st.video(video_path, autoplay=True, muted=True, loop=True)
            else:
                st.markdown("<br><br>", unsafe_allow_html=True)
            
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
        st.markdown("<h2 style='letter-spacing:10px;'>VORTEZA</h2>", unsafe_allow_html=True)
        st.markdown("<span class='v-status-glow'>● SYSTEM STATUS: ONLINE</span>", unsafe_allow_html=True)
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
        st.markdown("<h1>MISSION CONTROL</h1>", unsafe_allow_html=True)
        st.markdown("---")
        with st.spinner("Pobieranie statusu operacyjnego..."):
            s = get_dashboard_stats()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY W SYSTEMIE", s["vehicles"])
        
        # Logika kolorowania alertów
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
