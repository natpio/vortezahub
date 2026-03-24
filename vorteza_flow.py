import streamlit as st
import pandas as pd
import json
import base64
import os
from PIL import Image

# =========================================================
# KONFIGURACJA ŚCIEŻEK LOKALNYCH
# =========================================================
PATH_CONFIG = os.path.join("data", "config.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")
PATH_LOGO = os.path.join("assets", "logo_vorteza.png")

# =========================================================
# FUNKCJE POMOCNICZE (DANE LOKALNE)
# =========================================================
def load_vorteza_asset_b64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def load_config():
    """Wczytuje konfigurację z lokalnego pliku JSON."""
    if os.path.exists(PATH_CONFIG):
        with open(PATH_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(new_data):
    """Zapisuje zaktualizowaną konfigurację lokalnie na serwerze."""
    try:
        with open(PATH_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Błąd zapisu danych: {e}")
        return False

# =========================================================
# STYLIZACJA MODUŁU
# =========================================================
def apply_flow_theme():
    bin_str = load_vorteza_asset_b64(PATH_BG)
    bg_css = f'background-image: url("data:image/png;base64,{bin_str}");' if bin_str else "background-color: #0E0E0E;"
    
    st.markdown(f"""
        <style>
            :root {{
                --v-copper: #B58863;
                --v-dark: #0E0E0E;
                --v-panel: rgba(20, 20, 20, 0.95);
            }}
            .stApp {{ {bg_css} background-size: cover; background-attachment: fixed; }}
            .vorteza-card {{
                background-color: var(--v-panel);
                padding: 30px; border-radius: 5px; border-left: 5px solid var(--v-copper);
                box-shadow: 0 10px 40px rgba(0,0,0,0.8); backdrop-filter: blur(15px); margin-bottom: 25px;
            }}
            .route-preview {{
                background-color: rgba(181, 136, 99, 0.1); border: 1px solid var(--v-copper);
                padding: 15px; margin-top: 15px; border-radius: 4px; font-size: 0.9rem;
            }}
            .cost-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            .cost-table th {{ text-align: left; color: var(--v-copper); border-bottom: 1px solid #444; padding: 8px; font-size: 0.8rem; text-transform: uppercase; }}
            .cost-table td {{ padding: 10px 8px; border-bottom: 1px solid #222; font-size: 0.95rem; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# GŁÓWNA FUNKCJA MODUŁU (WYWOŁYWANA PRZEZ HUB)
# =========================================================
def run_flow():
    apply_flow_theme()
    
    # Nagłówek modułu
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if os.path.exists(PATH_LOGO):
            st.image(PATH_LOGO, width=150)
    with col_title:
        st.markdown("<h1 style='margin-bottom:0;'>VORTEZA FLOW</h1>", unsafe_allow_html=True)
        st.markdown("<p style='letter-spacing:3px; color:#666;'>FINANCIAL LOGISTICS INTELLIGENCE</p>", unsafe_allow_html=True)

    config = load_config()

    if config:
        tab1, tab2 = st.tabs(["📊 ANALIZA KOSZTÓW I MARŻY", "⚙️ KONFIGURACJA BAZY"])

        with tab1:
            col_cfg, col_res = st.columns([1, 1], gap="large")
            
            with col_cfg:
                st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                st.subheader("Konfiguracja Transportu")
                
                v_type = st.selectbox("Typ Jednostki Floty", list(config["VEHICLE_DATA"].keys()))
                start_p = st.selectbox("Punkt Załadunku", list(config["DISTANCES_AND_MYTO"].keys()))
                
                available_dests = list(config["DISTANCES_AND_MYTO"][start_p].keys())
                route = st.selectbox("Punkt Rozładunku (Cel)", available_dests) if available_dests else None
                extra_km = st.number_input("Dodatkowy Dystans (KM)", value=0, step=10)
                
                if route:
                    r_info = config["DISTANCES_AND_MYTO"][start_p][route]
                    total_dist = r_info['distPL'] + r_info['distEU'] + extra_km
                    st.markdown(f"""
                        <div class="route-preview">
                            <b style="color:#B58863;">PODSUMOWANIE TRASY:</b><br>
                            Dystans całkowity: <b style="font-size:1.1rem; color:#B58863;">{total_dist} km</b>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_res:
                if route:
                    st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                    st.subheader("Wynik Analizy")
                    
                    v_info = config["VEHICLE_DATA"][v_type]
                    prices = config["PRICE"]
                    euro_rate = config["EURO_RATE"]
                    
                    total_fuel_l = (total_dist) * v_info["fuelUsage"]
                    pl_l = min(total_fuel_l, v_info["tankCapacity"])
                    eu_l = max(0, total_fuel_l - pl_l)
                    
                    c_fuel_pln = (pl_l * prices["fuelPLN"]) + (eu_l * prices["fuelEUR"] * euro_rate)
                    c_adblue_pln = (total_dist * v_info["adBlueUsage"]) * prices["adBluePLN"]
                    c_service_pln = (r_info["distPL"] * v_info["serviceCostPLN"]) + ((r_info["distEU"] + extra_km) * v_info["serviceCostEUR"] * euro_rate)
                    
                    myto_key = f"myto{v_type}"
                    c_myto_eur = r_info.get(myto_key, 0)
                    c_myto_pln = c_myto_eur * euro_rate
                    
                    total_pln = c_fuel_pln + c_adblue_pln + c_service_pln + c_myto_pln
                    total_eur = total_pln / euro_rate

                    m1, m2 = st.columns(2)
                    m1.metric("KOSZT (PLN)", f"{total_pln:,.2f} zł")
                    m2.metric("KOSZT (EUR)", f"€ {total_eur:,.2f}")

                    st.markdown(f"""
                        <table class="cost-table">
                            <tr><th>Kategoria</th><th>PLN</th><th>EUR</th></tr>
                            <tr><td>Paliwo</td><td>{c_fuel_pln:,.2f} zł</td><td>€ {c_fuel_pln/euro_rate:,.2f}</td></tr>
                            <tr><td>Myto</td><td>{c_myto_pln:,.2f} zł</td><td>€ {c_myto_eur:,.2f}</td></tr>
                            <tr><td>Serwis</td><td>{c_service_pln:,.2f} zł</td><td>€ {c_service_pln/euro_rate:,.2f}</td></tr>
                        </table>
                    """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.subheader("Ustawienia Globalne")
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            e1, e2, e3, e4 = st.columns(4)
            with e1: n_euro = st.number_input("Kurs EURO", value=float(config["EURO_RATE"]), format="%.4f")
            with e2: n_fpl = st.number_input("ON PL (zł/L)", value=float(config["PRICE"]["fuelPLN"]))
            with e3: n_feu = st.number_input("ON EU (€/L)", value=float(config["PRICE"]["fuelEUR"]))
            with e4: n_apl = st.number_input("AdBlue (zł/L)", value=float(config["PRICE"]["adBluePLN"]))
            
            if st.button("ZAPISZ ZMIANY W BAZIE LOKALNEJ"):
                config["EURO_RATE"] = n_euro
                config["PRICE"]["fuelPLN"] = n_fpl
                config["PRICE"]["fuelEUR"] = n_feu
                config["PRICE"]["adBluePLN"] = n_apl
                if save_config(config):
                    st.success("Dane zaktualizowane pomyślnie!")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Błąd krytyczny: Brak pliku data/config.json.")

if __name__ == "__main__":
    run_flow()
