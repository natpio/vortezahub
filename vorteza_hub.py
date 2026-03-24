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
    st.error(f"KRYTYCZNY BŁĄD IMPORTU: {e}")

# --- 2. KONFIGURACJA ---
st.set_page_config(
    page_title="VORTEZA APEX SYSTEMS v25.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# --- 3. STATYSTYKI LIVE ---
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

# --- 4. SILNIK UI (LOGO I KONTRAST SIDEBARA) ---
def inject_hub_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono&display=swap');
            :root { --v-copper: #B58863; --v-dark: #060606; }
            .stApp { background-color: var(--v-dark); color: #FFFFFF; font-family: 'Montserrat', sans-serif; }
            
            /* STYLIZACJA SIDEBARA DLA MAKSYMALNEJ CZYTELNOŚCI */
            section[data-testid="stSidebar"] { 
                background-color: #030303 !important; 
                border-right: 1px solid rgba(181, 136, 99, 0.3); 
            }
            section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p, 
            section[data-testid="stSidebar"] label p, 
            section[data-testid="stSidebar"] .stMarkdown p { 
                color: var(--v-copper) !important; 
                font-weight: 700 !important;
                font-size: 0.95rem !important;
                letter-spacing: 1px;
            }
            .v-status-glow { color: #00FF41; text-shadow: 0 0 10px #00FF41; font-family: 'JetBrains Mono'; font-size: 0.8rem; }
            h1, h2, h3 { color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 6px !important; }
            .stButton>button { background-color: transparent !important; color: var(--v-copper) !important; border: 1px solid var(--v-copper) !important; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

def main_hub():
    inject_hub_theme()
    if "global_auth" not in st.session_state: st.session_state.global_auth = False

    if not st.session_state.global_auth:
        _, col, _ = st.columns([1, 1.5, 1])
        with col:
            st.markdown("<br><br><h1 style='text-align:center;'>VORTEZA LOGIN</h1>", unsafe_allow_html=True)
            with st.form("ApexAuth"):
                pwd_input = st.text_input("GOLIATH SECURITY KEY", type="password")
                if st.form_submit_button("VALIDATE ACCESS"):
                    if pwd_input == st.secrets["password"]:
                        st.session_state.global_auth = True
                        st.session_state.username = st.secrets["USERS"].get("admin", "NeonParrot821")
                        st.rerun()
                    else: st.error("ACCESS DENIED")
        return

    with st.sidebar:
        if os.path.exists("assets/logo_vorteza.png"):
            st.image("assets/logo_vorteza.png", use_container_width=True)
        st.markdown("<h2 style='letter-spacing:5px; text-align:center;'>VORTEZA</h2>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;'><span class='v-status-glow'>● SYSTEM STATUS: ONLINE</span></div>", unsafe_allow_html=True)
        st.divider()
        app_mode = st.radio("NAWIGACJA MODUŁÓW", ["PULPIT (DASHBOARD)", "PLANER 3D (STACK)", "FINANSE (FLOW)", "FLOTA (BASE)"])
        st.divider()
        st.markdown(f"**OPERATOR:** {st.session_state.username}")
        if st.button("TERMINATE SESSION"):
            st.session_state.global_auth = False
            st.rerun()

    if app_mode == "PULPIT (DASHBOARD)":
        st.markdown("<h1>MISSION CONTROL</h1>", unsafe_allow_html=True)
        s = get_dashboard_stats()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("POJAZDY", s["vehicles"])
        c2.metric("ALERTY", s["alerts"], delta=s["alerts"], delta_color="inverse" if s["alerts"] > 0 else "normal")
        c3.metric("KURS EURO", f"{s['euro']} PLN")
        c4.metric("BAZA SKU", s["skus"])
        if s["alerts"] > 0: st.error(f"Wykryto {s['alerts']} usterki w module BASE.")
    elif app_mode == "PLANER 3D (STACK)": run_stack()
    elif app_mode == "FINANSE (FLOW)": run_flow()
    elif app_mode == "FLOTA (BASE)": run_base()

if __name__ == "__main__":
    main_hub()
