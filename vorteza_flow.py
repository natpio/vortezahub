# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import json
import math
import base64

# ==============================================================================
# 0. KONFIGURACJA ŚCIEŻEK (ZGODNIE ZE STRUKTURĄ GITHUB)
# ==============================================================================
PATH_CONFIG = os.path.join("data", "config.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")

def load_config():
    """Wczytuje parametry kosztowe, trasy i stawki myta z bazy danych."""
    try:
        if os.path.exists(PATH_CONFIG):
            with open(PATH_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"BŁĄD ŁADOWANIA CONFIGA: {e}")
        return {}

CONF = load_config()

# Mapowanie modeli transportowych na kategorie kosztowe z bazy danych config.json
VEH_MAP = {
    "TIR FTL Mega 13.6m": "FTL",
    "TIR FTL Standard 13.6m": "FTL",
    "Solo 9m Heavy Duty": "Solo",
    "Solo 7m Medium": "Solo",
    "Solo 6m Light": "Solo",
    "BUS Opel Movano": "Bus"
}

# ==============================================================================
# 1. UI ENGINE: APEX FLOW STYLE
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
            
            .v-positive {{ color: #00FF41 !important; }}
            .v-negative {{ color: #FF3131 !important; }}
            
            div[data-testid="stWidgetLabel"] p {{ color: #B58863 !important; font-weight: 700 !important; letter-spacing: 1px; }}
            div[data-testid="stRadio"] label p {{ color: #B58863 !important; }}
            .v-badge-unit {{ background: rgba(181,136,99,0.1); border: 1px solid #B58863; padding: 10px; color: #B58863; font-size: 0.8rem; margin-bottom: 15px; text-align: center; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. SILNIK OBLICZENIOWY FLOW
# ==============================================================================
def run_flow():
    inject_vorteza_flow_ui()
    st.markdown(f"<h2 style='color:#B58863; letter-spacing:10px;'>VORTEZA FLOW</h2>", unsafe_allow_html=True)

    if not CONF:
        st.error("Baza danych nie została załadowana. Sprawdź plik data/config.json.")
        return

    # --- SIDEBAR: KONFIGURACJA TRASY I STAWEK ---
    with st.sidebar:
        st.markdown("### 🛠️ TRYB OBLICZEŃ")
        source_mode = st.radio("ŹRÓDŁO DANYCH", ["🔗 SYNC (ZE STACK)", "⚡ MANUAL (SZYBKI)"], label_visibility="collapsed")
        
        st.divider()
        st.markdown("### 🗺️ WYBÓR TRASY")
        origins = list(CONF["DISTANCES_AND_MYTO"].keys())
        origin = st.selectbox("PUNKT STARTU", origins)
        
        destinations = list(CONF["DISTANCES_AND_MYTO"][origin].keys())
        dest = st.selectbox("PUNKT DOCELOWY", destinations)
        
        st.divider()
        st.markdown("### 💶 WALUTA")
        eur_rate = st.number_input("KURS EUR/PLN", value=CONF.get("EURO_RATE", 4.30), step=0.01)
        
        st.divider()
        st.markdown("### 📈 MODEL PRZYCHODU")
        rate_type = st.selectbox("TYP ROZLICZENIA", ["PLN / KM", "PLN / RYCZAŁT", "PLN / OPAKOWANIE"])
        rate_val = st.number_input("WARTOŚĆ STAWKI (PLN)", value=6.50 if "KM" in rate_type else 3500.0)

    # Dane trasy pobrane z config.json
    route = CONF["DISTANCES_AND_MYTO"][origin][dest]
    dPL, dEU = route["distPL"], route["distEU"]
    total_dist = dPL + dEU

    # --- OBSŁUGA DANYCH WEJŚCIOWYCH ---
    if source_mode == "🔗 SYNC (ZE STACK)":
        if 'v_manifest' not in st.session_state or not st.session_state.v_manifest:
            st.warning("⚠️ BRAK DANYCH W STACK. NAJPIERW DODAJ TOWAR DO PLANERA 3D."); return
        total_cases = sum(math.ceil(it['p_act'] / it.get('itemsPerCase', 1)) for it in st.session_state.v_manifest)
        total_weight = sum(it.get('weight', 0) * math.ceil(it['p_act'] / it.get('itemsPerCase', 1)) for it in st.session_state.v_manifest)
        st.markdown(f"<div class='v-badge-unit'>POBRANO ZE STACK: {total_cases} OPAKOWAŃ | {total_weight} KG</div>", unsafe_allow_html=True)
        active_veh_name = st.selectbox("POJAZD DO ANALIZY", list(VEH_MAP.keys()))
    else:
        col1, col2 = st.columns(2)
        with col1: active_veh_name = st.selectbox("TYP POJAZDU", list(VEH_MAP.keys()))
        with col2: total_cases = st.number_input("OPAKOWANIA", min_value=1, value=12)
        total_weight = total_cases * 450

    # Parametry kosztowe wyciągnięte z bazy danych
    cat = VEH_MAP[active_veh_name]
    v_spec = CONF["VEHICLE_DATA"][cat]
    prices = CONF["PRICE"]

    # --- LOGIKA KOSZTÓW (TOTAL COST ENGINE) ---
    # Paliwo i AdBlue (ceny PL i EU z config.json)
    cost_fuel = (dPL * v_spec["fuelUsage"] * prices["fuelPLN"]) + (dEU * v_spec["fuelUsage"] * prices["fuelEUR"] * eur_rate)
    cost_adblue = (dPL * v_spec["adBlueUsage"] * prices["adBluePLN"]) + (dEU * v_spec["adBlueUsage"] * prices["adBlueEUR"] * eur_rate)
    
    # Serwis i Amortyzacja
    cost_service = (dPL * v_spec["serviceCostPLN"]) + (dEU * v_spec["serviceCostEUR"] * eur_rate)
    
    # Myto (dynamicznie pobierane dla trasy i kategorii pojazdu)
    myto_key = f"myto{cat}"
    cost_tolls = route.get(myto_key, 0)
    
    # Kierowca i Diety (Uproszczone)
    cost_driver = 500 + (total_dist * 0.15)
    
    total_cost_pln = cost_fuel + cost_adblue + cost_service + cost_tolls + cost_driver

    # --- LOGIKA PRZYCHODU ---
    if "KM" in rate_type: revenue_pln = total_dist * rate_val
    elif "RYCZAŁT" in rate_type: revenue_pln = rate_val
    else: revenue_pln = total_cases * rate_val
    
    margin_pln = revenue_pln - total_cost_pln
    margin_pct = (margin_pln / revenue_pln * 100) if revenue_pln > 0 else 0

    # ==============================================================================
    # 3. DASHBOARD FINANSOWY (PLN & EUR)
    # ==============================================================================
    st.markdown(f"#### 📍 RELACJA: {origin.upper()} ➔ {dest.upper()} | {total_dist} KM")
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="v-flow-card"><div class="v-flow-label">PRZYCHÓD NETTO</div><div class="v-flow-value-main">{revenue_pln:,.2f} PLN</div><div class="v-flow-value-sub">{revenue_pln/eur_rate:,.2f} EUR</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="v-flow-card"><div class="v-flow-label">KOSZT CAŁKOWITY</div><div class="v-flow-value-main">{total_cost_pln:,.2f} PLN</div><div class="v-flow-value-sub">{total_cost_pln/eur_rate:,.2f} EUR</div></div>', unsafe_allow_html=True)
    
    m_clr = "v-positive" if margin_pln > 0 else "v-negative"
    c3.markdown(f'<div class="v-flow-card"><div class="v-flow-label">MARŻA (ZYSK)</div><div class="v-flow-value-main {m_clr}">{margin_pln:,.2f} PLN</div><div class="v-flow-value-sub {m_clr}">{margin_pct:.1f}% RENTOWNOŚCI</div></div>', unsafe_allow_html=True)

    # Szczegółowa analiza
    st.divider()
    ca, cb = st.columns(2)
    with ca:
        st.markdown("### 📊 STRUKTURA KOSZTÓW (PLN)")
        cost_df = pd.DataFrame({
            "SKŁADNIK": ["Paliwo", "AdBlue", "Myto (Opłaty)", "Serwis", "Kierowca"],
            "WARTOŚĆ": [cost_fuel, cost_adblue, cost_tolls, cost_service, cost_driver]
        })
        st.table(cost_df.set_index("SKŁADNIK"))
        
    with cb:
        st.markdown("### ⛽ ANALIZA OPERACYJNA")
        st.info(f"**PRÓG RENTOWNOŚCI (BEP):** {total_cost_pln/total_dist:.2f} PLN/KM")
        st.write(f"**Pojazd:** {active_veh_name} (Kategoria: {cat})")
        st.write(f"**Spalanie całkowite:** {total_dist * v_spec['fuelUsage']:.1f} L")
        st.write(f"**Koszt na opakowanie:** {total_cost_pln/total_cases:.2f} PLN")

    if st.button("📄 GENERUJ OFERTĘ OFICJALNĄ"):
        offer = f"OFERTA VORTEZA: {origin}-{dest} | POJAZD: {active_veh_name} | CENA: {revenue_pln:,.2f} PLN / {revenue_pln/eur_rate:,.2f} EUR"
        st.code(offer, language="text")

if __name__ == "__main__":
    run_flow()
