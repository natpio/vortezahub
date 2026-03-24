import streamlit as st
import base64
from datetime import datetime

# Importy Twoich modułów (pliki muszą być w tym samym folderze)
try:
    from vorteza_stack import run_stack
    from vorteza_flow import run_flow
    from vorteza_base import run_base
except ImportError as e:
    st.error(f"BŁĄD IMPORTU: Upewnij się, że pliki .py mają poprawne nazwy. Szczegóły: {e}")

# --- 1. KONFIGURACJA APEX ULTIMATE PLUS ---
st.set_page_config(
    page_title="VORTEZA APEX SYSTEMS v24.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# --- 2. SILNIK WIZUALNY (Wspólny dla całego systemu) ---
def inject_hub_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-dark: #060606;
                --v-panel: rgba(15, 15, 15, 0.98);
            }

            .stApp {
                background-color: var(--v-dark);
                color: #FFFFFF;
                font-family: 'Montserrat', sans-serif;
            }

            /* Stylizacja Paska Bocznego */
            section[data-testid="stSidebar"] {
                background-color: #030303 !important;
                border-right: 1px solid rgba(181, 136, 99, 0.3);
                width: 350px !important;
            }

            .v-status-glow {
                color: #00FF41;
                text-shadow: 0 0 10px #00FF41;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
            }

            h1, h2, h3 {
                color: var(--v-copper) !important;
                text-transform: uppercase;
                letter-spacing: 6px !important;
                font-weight: 700 !important;
            }

            /* Custom Button Style */
            .stButton>button {
                background-color: transparent !important;
                color: var(--v-copper) !important;
                border: 1px solid var(--v-copper) !important;
                width: 100%;
                font-weight: 700;
                transition: 0.4s ease;
            }

            .stButton>button:hover {
                background-color: var(--v-copper) !important;
                color: black !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- 3. SYSTEM JEDNOLITEJ AUTORYZACJI ---
def check_global_access():
    if "global_auth" not in st.session_state:
        st.session_state.global_auth = False

    if not st.session_state.global_auth:
        _, col, _ = st.columns([1, 1.5, 1])
        with col:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align:center;'>VORTEZA LOGIN</h1>", unsafe_allow_html=True)
            with st.form("ApexAuth"):
                # Korzystamy z hasła zapisanego w st.secrets
                sys_pass = st.secrets.get("password", "vorteza2026")
                pwd_input = st.text_input("GOLIATH SECURITY KEY", type="password")
                if st.form_submit_button("VALIDATE ACCESS"):
                    if pwd_input == sys_pass:
                        st.session_state.global_auth = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID KEY")
        return False
    return True

# --- 4. GŁÓWNA LOGIKA OPERACYJNA ---
def main_hub():
    inject_hub_theme()

    if not check_global_access():
        return

    # --- PANEL BOCZNY (NAWIGACJA) ---
    with st.sidebar:
        st.markdown("<h2 style='letter-spacing:10px;'>VORTEZA</h2>", unsafe_allow_html=True)
        st.markdown("<span class='v-status-glow'>● SYSTEM STATUS: ONLINE</span>", unsafe_allow_html=True)
        st.divider()
        
        # Wybór modułu - to serce Twojego ekosystemu
        app_mode = st.radio(
            "MODUŁY SYSTEMOWE",
            ["PULPIT (DASHBOARD)", "PLANER 3D (STACK)", "FINANSE (FLOW)", "FLOTA (BASE)"],
            index=0
        )
        
        st.divider()
        st.markdown(f"**OPERATOR:** {st.secrets.get('USERS', {}).get('admin', 'GOLIATH_USER')}")
        st.markdown(f"**CZAS:** {datetime.now().strftime('%H:%M:%S')}")
        
        if st.button("TERMINATE SESSION"):
            st.session_state.global_auth = False
            st.rerun()

    # --- ROUTING (Przełączanie między Twoimi aplikacjami) ---
    if app_mode == "PULPIT (DASHBOARD)":
        st.markdown("<h1>MISSION CONTROL</h1>", unsafe_allow_html=True)
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("AKTYWNE POJAZDY", "12") # Tu docelowo dane z Base
        c2.metric("DZISIEJSZA MARŻA", "4.200 EUR") # Tu dane z Flow
        c3.metric("UTYLIZACJA FLOTY", "88%") # Tu dane ze Stack
        
        st.info("Witaj w systemie VORTEZA. Wybierz moduł operacyjny z lewego panelu, aby rozpocząć pracę.")

    elif app_mode == "PLANER 3D (STACK)":
        # Wywołujemy Twoją aplikację Stack
        try:
            run_stack()
        except NameError:
            st.warning("MODUŁ STACK: Oczekiwanie na poprawną konfigurację funkcji run_stack().")

    elif app_mode == "FINANSE (FLOW)":
        # Wywołujemy Twoją aplikację Flow
        try:
            run_flow()
        except NameError:
            st.warning("MODUŁ FLOW: Oczekiwanie na poprawną konfigurację funkcji run_flow().")

    elif app_mode == "FLOTA (BASE)":
        # Wywołujemy Twoją aplikację Base
        try:
            run_base()
        except NameError:
            st.warning("MODUŁ BASE: Oczekiwanie na poprawną konfigurację funkcji run_base().")

if __name__ == "__main__":
    main_hub()