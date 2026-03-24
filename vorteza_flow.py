# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import json
import math

# ==============================================================================
# 0. ŁADOWANIE KONFIGURACJI BIZNESOWEJ
# ==============================================================================
def load_config():
    """Wczytuje parametry kosztowe, trasy i stawki myta z bazy danych."""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("BŁĄD: Brak pliku config.json w katalogu głównym.")
        return {}

CONF = load_config()

# Mapowanie modeli transportowych na kategorie kosztowe z bazy danych
VEH_MAP = {
    "TIR FTL Mega 13.6m": "FTL",
    "TIR FTL Standard 13.6m": "FTL",
    "Solo 9m Heavy Duty": "Solo",
    "Solo 7m Medium": "Solo",
    "Solo 6m Light": "Solo",
    "BUS Opel Movano": "Bus"
}

def inject_vorteza_flow_ui():
    """Wstrzykuje stylizację APEX PRO dla modułu finansowego."""
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700&family=JetBrains+Mono&display=swap');
            
            /* Kafelki Finansowe Dual-Currency */
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
            
            /* Nagłówki Widgetów */
            div[data-testid="stWidgetLabel"] p {{ color: #B58863 !important; font-weight: 700 !important; letter-spacing: 1px; }}
            div[data-testid="stRadio"] label p {{ color: #B58863 !important; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 1. SILNIK OBLICZENIOWY FLOW
# ==============================================================================
def run_flow():
    inject_vorteza_flow_ui()
    st.markdown(f"<h2 style='color:#B58863; letter-spacing:10px;'>VORTEZA FLOW</h2>", unsafe_allow_html=True)

    if not CONF: return

    # --- SIDEBAR: KONFIGURACJA TRASY I STAWEK ---
    with st.sidebar:
        st.markdown("### 🛠️ TRYB OBLICZEŃ")
        source_mode = st.radio("ŹRÓDŁO DANYCH", ["🔗 SYNC (ZE STACK)", "⚡ MANUAL (SZYBKI)"], label_visibility="collapsed")
        
        st.divider()
        st.markdown("### 🗺️ WYBÓR TRASY")
        origin = st.selectbox("PUNKT STARTU", list(CONF["DISTANCES_AND_MYTO"].keys()))
        dest = st.selectbox("PUNKT DOCELOWY", list(CONF["DISTANCES_AND_MYTO"][origin].keys()))
        
        st.divider()
        st.markdown("### 💶 WALUTA I KURSY")
        eur_rate = st.number_input("KURS EUR/PLN", value=CONF.get("EURO_RATE", 4.30), step=0.01)
        
        st.divider()
        st.markdown("### 📈 MODEL PRZYCHODU")
        rate_type = st.selectbox("TYP ROZLICZENIA", ["PLN / KM", "PLN / RYCZAŁT", "PLN / OPAKOWANIE"])
        rate_val = st.number_input("WARTOŚĆ STAWKI (PLN)", value=6.50 if "KM" in rate_type else 3500.0)

    # Pobranie danych trasy z bazy config.json
    route = CONF["DISTANCES_AND_MYTO"][origin][dest]
    dPL, dEU = route["distPL"], route["distEU"]
    total_dist = dPL + dEU

    # --- DANE POJAZDU ---
    if source_mode == "🔗 SYNC (ZE STACK)":
        if 'v_manifest' not in st.session_state or not st.session_state.v_manifest:
            st.warning("⚠️ BRAK TOWARU W STACK. NAJPIERW ZAPLANUJ ZAŁADUNEK.") ; return
        total_cases = sum(math.ceil(it['p_act'] / it.get('itemsPerCase', 1)) for it in st.session_state.v_manifest)
        # Pobieramy pierwszy dostępny pojazd z listy dostępnych kluczy mapowania
        active_veh_name = st.selectbox("POJAZD DO ANALIZY", list(VEH_MAP.keys()))
    else:
        col1, col2 = st.columns(2)
        with col1: active_veh_name = st.selectbox("TYP POJAZDU", list(VEH_MAP.keys()))
        with col2: total_cases = st.number_input("OPAKOWANIA (PALETY)", min_value=1, value=12)

    # Pobranie specyfikacji kosztowej z bazy
    cat = VEH_MAP[active_veh_name]
    v_spec = CONF["VEHICLE_DATA"][cat]
    prices = CONF["PRICE"]

    # --- LOGIKA KOSZTÓW (TOTAL COST ENGINE) ---
    # 1. Paliwo i AdBlue (z uwzględnieniem cen krajowych i zagranicznych)
    fuel_cons_total = total_dist * v_spec["fuelUsage"]
    cost_fuel = (dPL * v_spec["fuelUsage"] * prices["fuelPLN"]) + (dEU * v_spec["fuelUsage"] * prices["fuelEUR"] * eur_rate)
    cost_adblue = (dPL * v_spec["adBlueUsage"] * prices["adBluePLN"]) + (dEU * v_spec["adBlueUsage"] * prices["adBlueEUR"] * eur_rate)
    
    # 2. Serwis i Amortyzacja (z bazy config.json)
    cost_service = (dPL * v_spec["serviceCostPLN"]) + (dEU * v_spec["serviceCostEUR"] * eur_rate)
    
    # 3. Myto (Opłaty drogowe wyciągane dynamicznie dla relacji i typu auta)
    myto_key = f"myto{cat}"
    cost_tolls = route.get(myto_key, 0)
    
    # 4. Kierowca i Diety (Uproszczone)
    cost_driver = 500 + (total_dist * 0.15)
    
    total_cost_pln = cost_fuel + cost_adblue + cost_service + cost_tolls + cost_driver

    # --- LOGIKA PRZYCHODÓW ---
    if "KM" in rate_type: revenue_pln = total_dist * rate_val
    elif "RYCZAŁT" in rate_type: revenue_pln = rate_val
    else: revenue_pln = total_cases * rate_val
    
    margin_pln = revenue_pln - total_cost_pln
    margin_pct = (margin_pln / revenue_pln * 100) if revenue_pln > 0 else 0

    # ==============================================================================
    # 2. DASHBOARD FINANSOWY
    # ==============================================================================
    st.markdown(f"#### 📍 RELACJA: {origin.upper()} ➔ {dest.upper()} | {total_dist} KM")
    
    c1, c2, c3 = st.columns(3)
    
    with c1: # Przychód
        st.markdown(f"""<div class="v-flow-card"><div class="v-flow-label">PRZYCHÓD NETTO</div>
            <div class="v-flow-value-main">{revenue_pln:,.2f} PLN</div>
            <div class="v-flow-value-sub">{revenue_pln/eur_rate:,.2f} EUR</div></div>""", unsafe_allow_html=True)
            
    with c2: # Koszt
        st.markdown(f"""<div class="v-flow-card"><div class="v-flow-label">KOSZT CAŁKOWITY</div>
            <div class="v-flow-value-main">{total_cost_pln:,.2f} PLN</div>
            <div class="v-flow-value-sub">{total_cost_pln/eur_rate:,.2f} EUR</div></div>""", unsafe_allow_html=True)
            
    with c3: # Zysk
        m_clr = "v-positive" if margin_pln > 0 else "v-negative"
        st.markdown(f"""<div class="v-flow-card"><div class="v-flow-label">MARŻA (ZYSK)</div>
            <div class="v-flow-value-main {m_clr}">{margin_pln:,.2f} PLN</div>
            <div class="v-flow-value-sub {m_clr}">{margin_pln/eur_rate:,.2f} EUR</div>
            <div style="color:#888; font-size:0.8rem; margin-top:5px;">RENTOWNOŚĆ: {margin_pct:.1f}%</div></div>""", unsafe_allow_html=True)

    # --- SZCZEGÓŁOWY RAPORT OPERACYJNY ---
    st.divider()
    ca, cb = st.columns(2)
    
    with ca:
        st.markdown("### 📊 STRUKTURA KOSZTÓW")
        cost_breakdown = pd.DataFrame({
            "SKŁADNIK": ["Paliwo", "AdBlue", "Opłaty Drogowe (Myto)", "Serwis i Amortyzacja", "Kierowca"],
            "PLN": [cost_fuel, cost_adblue, cost_tolls, cost_service, cost_driver],
            "EUR": [cost_fuel/eur_rate, cost_adblue/eur_rate, cost_tolls/eur_rate, cost_service/eur_rate, cost_driver/eur_rate]
        })
        st.table(cost_breakdown.set_index("SKŁADNIK"))
        
    with cb:
        st.markdown("### ⛽ DANE EKSPLOATACYJNE")
        st.info(f"**PRÓG RENTOWNOŚCI (BEP):** {total_cost_pln/total_dist:.2f} PLN/KM")
        st.write(f"**Pojazd:** {active_veh_name} (Kategoria: {cat})")
        st.write(f"**Spalanie całkowite:** {fuel_cons_total:.1f} L")
        st.write(f"**Wymagane tankowanie:** {1 if fuel_cons_total > v_spec['tankCapacity'] else 0} razy na trasie")
        st.write(f"**Koszt na opakowanie:** {total_cost_pln/total_cases:.2f} PLN")

    # --- GENEROWANIE OFERTY ---
    st.divider()
    if st.button("📄 GENERUJ OFERTĘ OFICJALNĄ"):
        offer = f"""
        VORTEZA HUB - OFERTA TRANSPORTOWA
        ---------------------------------
        TRASA: {origin} -> {dest} ({total_dist} km)
        POJAZD: {active_veh_name}
        ŁADUNEK: {total_cases} opakowań
        
        CENA NETTO: {revenue_pln:,.2f} PLN
        CENA NETTO: {revenue_pln/eur_rate:,.2f} EUR (Kurs: {eur_rate})
        ---------------------------------
        Oferta ważna 24h.
        """
        st.code(offer, language="text")
        st.toast("Oferta przygotowana!")

if __name__ == "__main__":
    run_flow()
