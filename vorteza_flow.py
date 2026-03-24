# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import json
import math
import base64

# ==============================================================================
# 0. ZASOBY I KONFIGURACJA (STRUKTURA GITHUB)
# ==============================================================================
PATH_CONFIG = os.path.join("data", "config.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")

def load_config():
    """Wczytuje parametry kosztowe i bazę tras z folderu data/."""
    try:
        if os.path.exists(PATH_CONFIG):
            with open(PATH_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"BŁĄD KRYTYCZNY CONFIGA: {e}")
        return {}

def save_config(config_data):
    """Zapisuje zmiany wprowadzone przez klienta do pliku config.json."""
    try:
        with open(PATH_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"BŁĄD ZAPISU: {e}")
        return False

CONF = load_config()

# Mapowanie floty na kategorie kosztowe z config.json
VEH_MAP = {
    "TIR FTL Mega 13.6m": "FTL", 
    "TIR FTL Standard 13.6m": "FTL",
    "Solo 9m Heavy Duty": "Solo", 
    "Solo 7m Medium": "Solo", 
    "Solo 6m Light": "Solo",
    "BUS Opel Movano": "Bus"
}

# ==============================================================================
# 1. UI ENGINE: APEX FLOW CONTRAST FIX
# ==============================================================================
def inject_vorteza_flow_ui():
    bg_data = ""
    if os.path.exists(PATH_BG):
        with open(PATH_BG, "rb") as f:
            bg_data = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700&family=JetBrains+Mono&display=swap');
            
            .stApp {{ 
                background-image: url("data:image/png;base64,{bg_data}"); 
                background-size: cover; background-attachment: fixed; 
            }}

            /* Kafelki Finansowe */
            .v-flow-card {{
                background: rgba(10, 10, 10, 0.9);
                border: 1px solid rgba(181, 136, 99, 0.3);
                border-top: 4px solid #B58863;
                padding: 20px;
                text-align: center;
                backdrop-filter: blur(10px);
                margin-bottom: 15px;
            }}
            .v-flow-label {{ color: #B58863; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; margin-bottom: 8px; }}
            .v-flow-value-main {{ color: #FFFFFF; font-size: 1.7rem; font-family: 'JetBrains Mono', monospace; font-weight: 500; }}
            .v-flow-value-sub {{ color: #B58863; font-size: 1.1rem; font-family: 'JetBrains Mono', monospace; margin-top: 5px; border-top: 1px solid rgba(181,136,99,0.2); padding-top: 5px; }}
            
            /* TABELA - POPRAWKA KONTRASTU */
            div[data-testid="stTable"] {{
                background-color: rgba(0, 0, 0, 0.75) !important;
                border-radius: 4px;
                padding: 10px;
            }}
            div[data-testid="stTable"] td {{
                color: #FFFFFF !important;
                font-family: 'JetBrains Mono', monospace !important;
                border-bottom: 1px solid rgba(181, 136, 99, 0.2) !important;
            }}
            div[data-testid="stTable"] th {{
                color: #B58863 !important;
                text-transform: uppercase !important;
                background-color: rgba(15, 15, 15, 0.9) !important;
            }}
            
            .v-positive {{ color: #00FF41 !important; }}
            .v-negative {{ color: #FF3131 !important; }}
            
            div[data-testid="stWidgetLabel"] p {{ color: #B58863 !important; font-weight: 700 !important; }}
            div[data-testid="stRadio"] label p {{ color: #B58863 !important; }}
            .v-badge-unit {{ background: rgba(181,136,99,0.15); border: 1px solid #B58863; padding: 12px; color: #B58863; font-size: 0.85rem; text-align: center; margin-bottom: 15px; font-weight: 700; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. MODUŁ ANALIZY FINANSOWEJ (PEŁNY KOSZT)
# ==============================================================================
def show_financial_analysis():
    with st.sidebar:
        st.markdown("### 🛠️ KONFIGURACJA")
        source_mode = st.radio("ŹRÓDŁO DANYCH", ["🔗 SYNC (ZE STACK)", "⚡ MANUAL (SZYBKI)"], label_visibility="collapsed")
        st.divider()
        origin = st.selectbox("PUNKT STARTU", list(CONF["DISTANCES_AND_MYTO"].keys()))
        dest = st.selectbox("PUNKT DOCELOWY", list(CONF["DISTANCES_AND_MYTO"][origin].keys()))
        
        # Pobranie kursu EURO z bazy
        eur_rate = st.number_input("KURS EUR/PLN", value=CONF.get("EURO_RATE", 4.30), step=0.01)
        
        st.divider()
        st.markdown("### 📈 MODEL PRZYCHODU")
        c_cols = st.columns([2, 1])
        with c_cols[0]: rate_type = st.selectbox("MODEL", ["KM", "RYCZAŁT", "OPAKOWANIE"])
        with c_cols[1]: rate_curr = st.selectbox("WALUTA", ["PLN", "EUR"])
        rate_val = st.number_input(f"STAWKA ({rate_curr})", value=6.50 if rate_curr == "PLN" else 1.50)
        
        st.divider()
        view_curr = st.radio("POKAZUJ KOSZTY W:", ["PLN", "EUR"], horizontal=True)

    # Pobranie szczegółów trasy
    route = CONF["DISTANCES_AND_MYTO"][origin][dest]
    dPL, dEU = route["distPL"], route["distEU"]
    total_dist = dPL + dEU

    if source_mode == "🔗 SYNC (ZE STACK)":
        if 'v_manifest' not in st.session_state or not st.session_state.v_manifest:
            st.warning("⚠️ BRAK DANYCH W STACK."); return
        total_cases = sum(math.ceil(it['p_act'] / it.get('itemsPerCase', 1)) for it in st.session_state.v_manifest)
        active_veh_name = st.selectbox("POJAZD", list(VEH_MAP.keys()))
    else:
        col1, col2 = st.columns(2)
        with col1: active_veh_name = st.selectbox("TYP POJAZDU", list(VEH_MAP.keys()))
        with col2: total_cases = st.number_input("OPAKOWANIA", min_value=1, value=12)

    cat = VEH_MAP[active_veh_name]
    v_spec = CONF["VEHICLE_DATA"][cat] #
    prices = CONF["PRICE"] #

    # --- OBLICZENIA SMART TANKING (v2.0) ---
    total_fuel_needed = total_dist * v_spec["fuelUsage"]
    # Priorytet tankowania w Polsce do pełna (limit tankCapacity)
    fuel_from_pl = min(total_fuel_needed, v_spec["tankCapacity"])
    fuel_from_eu = max(0, total_fuel_needed - fuel_from_pl)
    
    cost_fuel_pln = (fuel_from_pl * prices["fuelPLN"]) + (fuel_from_eu * prices["fuelEUR"] * eur_rate)
    cost_adblue_pln = (total_dist * v_spec["adBlueUsage"] * prices["adBluePLN"])
    
    # Serwis i Amortyzacja
    cost_service_pln = (dPL * v_spec["serviceCostPLN"]) + (dEU * v_spec["serviceCostEUR"] * eur_rate)
    
    # MYTO: Pobieramy z bazy (EUR) i przeliczamy na PLN
    myto_key = f"myto{cat}"
    cost_tolls_eur = route.get(myto_key, 0)
    cost_tolls_pln = cost_tolls_eur * eur_rate
    
    # Kierowca (Stała dieta + km)
    cost_driver_pln = 500 + (total_dist * 0.15)
    
    # PEŁNY KOSZT CAŁKOWITY (PLN)
    total_cost_pln = cost_fuel_pln + cost_adblue_pln + cost_service_pln + cost_tolls_pln + cost_driver_pln

    # Przychód (Konwersja na PLN dla bazy obliczeniowej)
    raw_rev = total_dist * rate_val if rate_type == "KM" else (rate_val if rate_type == "RYCZAŁT" else total_cases * rate_val)
    revenue_pln = raw_rev if rate_curr == "PLN" else (raw_rev * eur_rate)
    
    margin_pln = revenue_pln - total_cost_pln
    margin_pct = (margin_pln / revenue_pln * 100) if revenue_pln > 0 else 0

    # DASHBOARD GŁÓWNY
    st.markdown(f"#### 📍 RELACJA: {origin.upper()} ➔ {dest.upper()}")
    # Rozbicie dystansu PL vs EU
    st.markdown(f"<div class='v-badge-unit'>DYSTANS: {total_dist} KM (POLSKA: {dPL} KM | ZAGRANICA: {dEU} KM)</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="v-flow-card"><div class="v-flow-label">PRZYCHÓD NETTO</div><div class="v-flow-value-main">{revenue_pln:,.2f} PLN</div><div class="v-flow-value-sub">{revenue_pln/eur_rate:,.2f} EUR</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="v-flow-card"><div class="v-flow-label">PEŁNY KOSZT</div><div class="v-flow-value-main">{total_cost_pln:,.2f} PLN</div><div class="v-flow-value-sub">{total_cost_pln/eur_rate:,.2f} EUR</div></div>', unsafe_allow_html=True)
    
    m_clr = "v-positive" if margin_pln > 0 else "v-negative"
    c3.markdown(f'<div class="v-flow-card"><div class="v-flow-label">MARŻA (ZYSK)</div><div class="v-flow-value-main {m_clr}">{margin_pln:,.2f} PLN</div><div class="v-flow-value-sub {m_clr}">{margin_pct:.1f}% RENTOWNOŚCI</div></div>', unsafe_allow_html=True)

    st.divider()
    ca, cb = st.columns(2)
    mult = 1.0 if view_curr == "PLN" else (1.0 / eur_rate)
    
    with ca:
        st.markdown(f"### 📊 STRUKTURA KOSZTÓW ({view_curr})")
        # Wyświetlanie składowych z zaokrągleniem do 2 miejsc
        cost_df = pd.DataFrame({
            "SKŁADNIK": ["Paliwo (Smart)", "AdBlue", "Myto (Opłaty)", "Serwis i Amort.", "Kierowca"],
            "WARTOŚĆ": [round(x * mult, 2) for x in [cost_fuel_pln, cost_adblue_pln, cost_tolls_pln, cost_service_pln, cost_driver_pln]]
        })
        st.table(cost_df.set_index("SKŁADNIK"))
        
    with cb:
        st.markdown("### ⛽ ANALIZA OPERACYJNA")
        st.info(f"**PRÓG RENTOWNOŚCI (BEP):** {round((total_cost_pln/total_dist)*mult, 2)} {view_curr}/KM")
        st.write(f"**Tankowanie PL (6.40 PLN/L):** {round(fuel_from_pl, 1)} L")
        st.write(f"**Tankowanie UE (1.65 EUR/L):** {round(fuel_from_eu, 1)} L")

# ==============================================================================
# 3. MODUŁ EDYTORA TRAS (ROUTE MASTER)
# ==============================================================================
def show_route_editor():
    st.markdown("### 🗺️ ZARZĄDZANIE BAZĄ TRAS")
    st.write("Edytuj kilometry i opłaty drogowe bezpośrednio w tabeli. Kliknij 'Zapisz', aby zaktualizować config.json.")
    
    # Przygotowanie danych do edycji (spłaszczenie słownika)
    flat_data = []
    for origin, destinations in CONF["DISTANCES_AND_MYTO"].items():
        for d_name, d_val in destinations.items():
            flat_data.append({
                "SKĄD": origin, "DOKĄD": d_name,
                "KM POLSKA": d_val["distPL"], "KM ZAGRANICA": d_val["distEU"],
                "MYTO FTL (EUR)": d_val["mytoFTL"], "MYTO SOLO (EUR)": d_val["mytoSolo"], "MYTO BUS (EUR)": d_val["mytoBus"]
            })
    
    df_routes = pd.DataFrame(flat_data)
    edited_df = st.data_editor(df_routes, num_rows="dynamic", use_container_width=True, key="route_master_editor")
    
    if st.button("💾 ZAPISZ ZMIANY W BAZIE"):
        new_dist = {}
        for _, row in edited_df.iterrows():
            o, d = row["SKĄD"], row["DOKĄD"]
            if o not in new_dist: new_dist[o] = {}
            new_dist[o][d] = {
                "distPL": int(row["KM POLSKA"]), "distEU": int(row["KM ZAGRANICA"]),
                "mytoFTL": float(row["MYTO FTL (EUR)"]), "mytoSolo": float(row["MYTO SOLO (EUR)"]), "mytoBus": float(row["MYTO BUS (EUR)"])
            }
        
        CONF["DISTANCES_AND_MYTO"] = new_dist
        if save_config(CONF):
            st.success("Baza danych tras została zaktualizowana!"); st.rerun()

# ==============================================================================
# 4. PUNKT WEJŚCIA MODUŁU
# ==============================================================================
def run_flow():
    inject_vorteza_flow_ui()
    st.markdown(f"<h2 style='color:#B58863; letter-spacing:10px;'>VORTEZA FLOW</h2>", unsafe_allow_html=True)
    
    if not CONF:
        st.error("Błąd: Plik konfiguracyjny nie został załadowany.")
        return

    with st.sidebar:
        st.markdown("### 🕹️ TRYB OPERACYJNY")
        app_mode = st.radio("WYBIERZ ZADANIE:", ["🛰️ ANALIZA FINANSOWA", "🗺️ EDYTOR TRAS"], label_visibility="collapsed")
        st.divider()

    if app_mode == "🛰️ ANALIZA FINANSOWA":
        show_financial_analysis()
    else:
        show_route_editor()

if __name__ == "__main__":
    run_flow()
