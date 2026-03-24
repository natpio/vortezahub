import streamlit as st
import pandas as pd
import json
import requests
import base64
from PIL import Image
import io

# =========================================================
# KONFIGURACJA GITHUB I SEKRETÓW
# =========================================================
# Dane pobierane z Streamlit Secrets Cloud lub .streamlit/secrets.toml
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]
    USER_DB = st.secrets["credentials"]["usernames"]
except Exception:
    GITHUB_TOKEN = "BRAK"
    USER_DB = {}

# Dane repozytorium GitHub
REPO_OWNER = "natpio"
REPO_NAME = "vortezaflowpepel"
FILE_PATH = "config.json"

# =========================================================
# FUNKCJE POMOCNICZE (DANE I GITHUB)
# =========================================================
def get_base64_of_bin_file(bin_file):
    """Konwertuje plik binarny na format base64 (używane do tła)."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def get_github_data():
    """Pobiera aktualny plik config.json z GitHub API wraz z SHA."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(decoded), content['sha']
        else:
            if st.session_state.get("authenticated"):
                st.error(f"Błąd GitHub API ({response.status_code}): {response.text}")
            return None, None
    except Exception as e:
        if st.session_state.get("authenticated"):
            st.error(f"Błąd połączenia z bazą Cloud: {e}")
        return None, None

def update_github_data(new_data, sha):
    """Wysyła zaktualizowany JSON na GitHub (commit)."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    updated_content = json.dumps(new_data, indent=4, ensure_ascii=False)
    encoded = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": "Update from VORTEZA FLOW Interface",
        "content": encoded,
        "sha": sha
    }
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code in [200, 201]

# =========================================================
# SYSTEM LOGOWANIA
# =========================================================
def check_password():
    """Zarządza dostępem do aplikacji na podstawie st.secrets."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        # Layout formularza logowania
        empty_top = st.empty()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.form("Login"):
                st.markdown("<h3 style='text-align: center;'>VORTEZA | SECURE ACCESS</h3>", unsafe_allow_html=True)
                user = st.text_input("Użytkownik", placeholder="User ID")
                password = st.text_input("Hasło", type="password", placeholder="Access Key")
                submit = st.form_submit_button("AUTORYZUJ")
                
                if submit:
                    if user in USER_DB and USER_DB[user] == password:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user
                        st.rerun()
                    else:
                        st.error("Błąd autoryzacji: Nieprawidłowe poświadczenia.")
        return False
    return True

# =========================================================
# STYLIZACJA VORTEZA SYSTEMS (Pełny CSS)
# =========================================================
def apply_vorteza_theme():
    # Próba wczytania tła
    bin_str = get_base64_of_bin_file('bg_vorteza.png')
    bg_css = f'background-image: url("data:image/png;base64,{bin_str}");' if bin_str else "background-color: #0E0E0E;"
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');

            :root {{
                --v-copper: #B58863;
                --v-dark: #0E0E0E;
                --v-panel: rgba(20, 20, 20, 0.95);
                --v-text: #E0E0E0;
            }}

            .stApp {{
                {bg_css}
                background-size: cover;
                background-attachment: fixed;
                color: var(--v-text);
                font-family: 'Montserrat', sans-serif;
            }}

            h1, h2, h3, .stSubheader {{
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }}

            label[data-testid="stWidgetLabel"] {{
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                font-size: 0.8rem !important;
            }}

            div[data-baseweb="select"] > div, input {{
                background-color: rgba(15, 15, 15, 0.9) !important;
                color: white !important;
                border: 1px solid #444 !important;
            }}
            
            .vorteza-card {{
                background-color: var(--v-panel);
                padding: 30px;
                border-radius: 5px;
                border-left: 5px solid var(--v-copper);
                box-shadow: 0 10px 40px rgba(0,0,0,0.8);
                backdrop-filter: blur(15px);
                margin-bottom: 25px;
            }}

            .route-preview {{
                background-color: rgba(181, 136, 99, 0.1);
                border: 1px solid var(--v-copper);
                padding: 15px;
                margin-top: 15px;
                border-radius: 4px;
                font-size: 0.9rem;
            }}

            [data-testid="stMetricValue"] {{
                color: var(--v-copper) !important;
                font-size: 2rem !important;
                font-weight: 700 !important;
            }}

            .stButton > button {{
                background-color: rgba(0, 0, 0, 0.7);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 12px;
                width: 100%;
                font-weight: 700;
                text-transform: uppercase;
                transition: 0.3s;
            }}

            .stButton > button:hover {{
                background-color: var(--v-copper);
                color: black;
            }}

            .cost-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}

            .cost-table th {{
                text-align: left;
                color: var(--v-copper);
                border-bottom: 1px solid #444;
                padding: 8px;
                font-size: 0.8rem;
                text-transform: uppercase;
            }}

            .cost-table td {{
                padding: 10px 8px;
                border-bottom: 1px solid #222;
                font-size: 0.95rem;
            }}
            
            .stTabs [data-baseweb="tab-list"] {{
                gap: 10px;
                background-color: transparent;
            }}

            .stTabs [data-baseweb="tab"] {{
                background-color: rgba(20,20,20,0.5);
                border: 1px solid #333;
                color: white;
                padding: 10px 20px;
            }}

            .stTabs [aria-selected="true"] {{
                background-color: var(--v-copper) !important;
                color: black !important;
            }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# GŁÓWNA APLIKACJA
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW | VORTEZA SYSTEMS 2026", layout="wide")
apply_vorteza_theme()

if check_password():
    # --- Nagłówek ---
    col_logo, col_title, col_logout = st.columns([1, 4, 1])
    with col_logo:
        try:
            logo = Image.open('logo_vorteza.png')
            st.image(logo, use_container_width=True)
        except:
            st.markdown("<h2 style='color:#B58863;'>VORTEZA</h2>", unsafe_allow_html=True)

    with col_title:
        st.markdown("<h1 style='margin-bottom:0;'>VORTEZA FLOW</h1>", unsafe_allow_html=True)
        st.markdown("<p style='letter-spacing:3px; color:#666;'>VORTEZA SYSTEMS | LOGISTICS INTERFACE</p>", unsafe_allow_html=True)
    
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("WYLOGUJ SYSTEM"):
            del st.session_state["authenticated"]
            st.rerun()

    # --- Pobieranie Danych ---
    if GITHUB_TOKEN == "BRAK":
        st.error("KRYTYCZNY BŁĄD SYSTEMU: Brak GITHUB_TOKEN w Streamlit Secrets.")
    else:
        config, file_sha = get_github_data()

        if config:
            tab1, tab2 = st.tabs(["📊 ANALIZA KOSZTÓW I MARŻY", "⚙️ RDZEŃ SYSTEMU (ADMIN)"])

            # ---------------------------------------------------------
            # TAB 1: KALKULATOR LOGISTYCZNY
            # ---------------------------------------------------------
            with tab1:
                col_cfg, col_res = st.columns([1, 1], gap="large")
                
                with col_cfg:
                    st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                    st.subheader("Konfiguracja Transportu")
                    
                    v_type = st.selectbox("Typ Jednostki Floty", list(config["VEHICLE_DATA"].keys()))
                    start_p = st.selectbox("Punkt Załadunku", list(config["DISTANCES_AND_MYTO"].keys()))
                    
                    available_dests = list(config["DISTANCES_AND_MYTO"][start_p].keys())
                    route = st.selectbox("Punkt Rozładunku (Cel)", available_dests) if available_dests else None
                    extra_km = st.number_input("Dodatkowy Dystans / Objazdy (KM)", value=0, step=10)
                    
                    if route:
                        r_info = config["DISTANCES_AND_MYTO"][start_p][route]
                        total_dist_calc = r_info['distPL'] + r_info['distEU'] + extra_km
                        st.markdown(f"""
                            <div class="route-preview">
                                <b style="color:#B58863;">PARAMETRY TRASY BAZOWEJ:</b><br>
                                Dystans PL: <b>{r_info['distPL']} km</b><br>
                                Dystans EU: <b>{r_info['distEU']} km</b><br>
                                Dystans Dodatkowy: <b>{extra_km} km</b><br>
                                <hr style="border:0; border-top:1px solid #444; margin:10px 0;">
                                CAŁKOWITY DYSTANS OBLICZENIOWY: <b style="font-size:1.1rem; color:#B58863;">{total_dist_calc} km</b>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_res:
                    if route:
                        st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                        st.subheader("Analiza Kosztów Operacyjnych")
                        
                        v_info = config["VEHICLE_DATA"][v_type]
                        prices = config["PRICE"]
                        euro_rate = config["EURO_RATE"]
                        
                        # Logika paliwa
                        total_fuel_l = (r_info["distPL"] + r_info["distEU"] + extra_km) * v_info["fuelUsage"]
                        pl_l = min(total_fuel_l, v_info["tankCapacity"])
                        eu_l = max(0, total_fuel_l - pl_l)
                        
                        c_fuel_pln = (pl_l * prices["fuelPLN"]) + (eu_l * prices["fuelEUR"] * euro_rate)
                        
                        # AdBlue i Serwis
                        total_km = r_info["distPL"] + r_info["distEU"] + extra_km
                        c_adblue_pln = (total_km * v_info["adBlueUsage"]) * prices["adBluePLN"]
                        c_service_pln = (r_info["distPL"] * v_info["serviceCostPLN"]) + ((r_info["distEU"] + extra_km) * v_info["serviceCostEUR"] * euro_rate)
                        
                        # Myto (pobierane dynamicznie)
                        myto_key = f"myto{v_type}"
                        c_myto_eur = r_info.get(myto_key, 0)
                        c_myto_pln = c_myto_eur * euro_rate
                        
                        total_pln = c_fuel_pln + c_adblue_pln + c_service_pln + c_myto_pln
                        total_eur = total_pln / euro_rate

                        m1, m2 = st.columns(2)
                        m1.metric("KOSZT CAŁKOWITY (PLN)", f"{total_pln:,.2f} zł")
                        m2.metric("KOSZT CAŁKOWITY (EUR)", f"€ {total_eur:,.2f}")

                        st.markdown(f"""
                            <table class="cost-table">
                                <tr><th>Kategoria</th><th>Wartość PLN</th><th>Wartość EUR</th></tr>
                                <tr><td>Paliwo (Tankowanie PL/EU)</td><td>{c_fuel_pln:,.2f} zł</td><td>€ {c_fuel_pln/euro_rate:,.2f}</td></tr>
                                <tr><td>Opłaty Drogowe (Myto)</td><td>{c_myto_pln:,.2f} zł</td><td>€ {c_myto_eur:,.2f}</td></tr>
                                <tr><td>Serwis i Eksploatacja</td><td>{c_service_pln:,.2f} zł</td><td>€ {c_service_pln/euro_rate:,.2f}</td></tr>
                                <tr><td>Płyny eksploatacyjne (AdBlue)</td><td>{c_adblue_pln:,.2f} zł</td><td>€ {c_adblue_pln/euro_rate:,.2f}</td></tr>
                            </table>
                            <div style="margin-top:20px; font-size:0.7rem; color:#555; text-transform:uppercase; text-align:right;">
                                Kurs: 1 EUR = {euro_rate} PLN | System: VORTEZA CORE v2.6
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

            # ---------------------------------------------------------
            # TAB 2: ZARZĄDZANIE KONFIGURACJĄ (ADMIN)
            # ---------------------------------------------------------
            with tab2:
                if st.session_state.get("username") == "admin":
                    st.subheader("Panel Zarządzania Rdzeniem")
                    
                    st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                    st.markdown("### 1. Globalne Współczynniki Ekonomiczne")
                    e1, e2, e3, e4 = st.columns(4)
                    with e1: n_euro = st.number_input("Kurs EURO (PLN)", value=float(config["EURO_RATE"]), format="%.4f")
                    with e2: n_fpl = st.number_input("ON Polska (PLN/L)", value=float(config["PRICE"]["fuelPLN"]))
                    with e3: n_feu = st.number_input("ON Europa (EUR/L)", value=float(config["PRICE"]["fuelEUR"]))
                    with e4: n_apl = st.number_input("AdBlue (PLN/L)", value=float(config["PRICE"]["adBluePLN"]))
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                    st.markdown("### 2. Edytor Bazy Tras i Opłat")
                    adm_mode = st.radio("Tryb bazy danych:", ["Dodaj nową trasę", "Edytuj / Usuń istniejącą"], horizontal=True)

                    if adm_mode == "Dodaj nową trasę":
                        c1, c2 = st.columns(2)
                        with c1:
                            exist_starts = list(config["DISTANCES_AND_MYTO"].keys())
                            s_city = st.selectbox("Miasto Startowe", ["+ NOWE MIASTO"] + exist_starts)
                            if s_city == "+ NOWE MIASTO": s_city = st.text_input("Wpisz nazwę nowego miasta startowego")
                        with c2: d_city = st.text_input("Nazwa Miasta Docelowego")
                        v_pl, v_eu, v_mftl, v_msolo, v_mbus = 0, 0, 0.0, 0.0, 0.0
                    else:
                        c1, c2 = st.columns(2)
                        with c1: s_city = st.selectbox("Wybierz Start", list(config["DISTANCES_AND_MYTO"].keys()))
                        with c2: 
                            d_list = list(config["DISTANCES_AND_MYTO"][s_city].keys())
                            d_city = st.selectbox("Wybierz Cel do edycji", d_list) if d_list else None
                        
                        if d_city:
                            curr = config["DISTANCES_AND_MYTO"][s_city][d_city]
                            v_pl, v_eu = curr["distPL"], curr["distEU"]
                            v_mftl = curr.get("mytoFTL", 0.0)
                            v_msolo = curr.get("mytoSolo", 0.0)
                            v_mbus = curr.get("mytoBus", 0.0)

                    if s_city and d_city and s_city != "+ NOWE MIASTO":
                        st.markdown(f"**Modyfikacja relacji:** `{s_city}` ➔ `{d_city}`")
                        ed1, ed2, ed3 = st.columns(3)
                        with ed1:
                            new_pl = st.number_input("Dystans PL (km)", value=int(v_pl if 'v_pl' in locals() else 0))
                            new_eu = st.number_input("Dystans EU (km)", value=int(v_eu if 'v_eu' in locals() else 0))
                        with ed2:
                            new_mftl = st.number_input("Myto FTL (EUR)", value=float(v_mftl if 'v_mftl' in locals() else 0.0))
                            new_msolo = st.number_input("Myto Solo (EUR)", value=float(v_msolo if 'v_msolo' in locals() else 0.0))
                        with ed3:
                            new_mbus = st.number_input("Myto Bus (EUR)", value=float(v_mbus if 'v_mbus' in locals() else 0.0))

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("ZAPISZ I SYNCHRONIZUJ Z CHMURĄ"):
                                if s_city not in config["DISTANCES_AND_MYTO"]: config["DISTANCES_AND_MYTO"][s_city] = {}
                                config["DISTANCES_AND_MYTO"][s_city][d_city] = {
                                    "distPL": new_pl, "distEU": new_eu, 
                                    "mytoFTL": new_mftl, "mytoSolo": new_msolo, "mytoBus": new_mbus
                                }
                                # Aktualizacja stałych
                                config["EURO_RATE"] = n_euro
                                config["PRICE"]["fuelPLN"] = n_fpl
                                config["PRICE"]["fuelEUR"] = n_feu
                                config["PRICE"]["adBluePLN"] = n_apl
                                
                                if update_github_data(config, file_sha):
                                    st.success("Zsynchronizowano pomyślnie!")
                                    st.rerun()
                        
                        with col_btn2:
                            if adm_mode == "Edytuj / Usuń istniejącą" and st.button("USUŃ TĘ TRASĘ NA ZAWSZE"):
                                del config["DISTANCES_AND_MYTO"][s_city][d_city]
                                if not config["DISTANCES_AND_MYTO"][s_city]: del config["DISTANCES_AND_MYTO"][s_city]
                                if update_github_data(config, file_sha):
                                    st.warning("Trasa usunięta z bazy.")
                                    st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("DOSTĘP ZABLOKOWANY: Sekcja zastrzeżona dla rangi ADMINISTRATOR.")
        else:
            st.error("Błąd krytyczny: Nie udało się pobrać danych z GitHub Cloud.")