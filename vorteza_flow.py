# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import json
import math
import base64

# ==============================================================================
# 0. KONFIGURACJA ŚCIEŻEK I ŁADOWANIE BAZY
# ==============================================================================
PATH_CONFIG = os.path.join("data", "config.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")

def load_config():
    """Wczytuje całą konfigurację z pliku JSON."""
    try:
        if os.path.exists(PATH_CONFIG):
            with open(PATH_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_config(config_data):
    """Zapisuje zaktualizowaną konfigurację do pliku JSON."""
    with open(PATH_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)

CONF = load_config()
VEH_MAP = {
    "TIR FTL Mega 13.6m": "FTL", "TIR FTL Standard 13.6m": "FTL",
    "Solo 9m Heavy Duty": "Solo", "Solo 7m Medium": "Solo", "Solo 6m Light": "Solo",
    "BUS Opel Movano": "Bus"
}

# ==============================================================================
# 1. UI ENGINE: APEX FLOW STYLE (FIXED CONTRAST)
# ==============================================================================
def inject_vorteza_flow_ui():
    bg_data = ""
    if os.path.exists(PATH_BG):
        with open(PATH_BG, "rb") as f: bg_data = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700&family=JetBrains+Mono&display=swap');
            .stApp {{ background-image: url("data:image/png;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }}
            .v-flow-card {{
                background: rgba(10, 10, 10, 0.9); border: 1px solid rgba(181, 136, 99, 0.3);
                border-top: 4px solid #B58863; padding: 20px; text-align: center; margin-bottom: 15px;
            }}
            .v-flow-label {{ color: #B58863; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; }}
            .v-flow-value-main {{ color: #FFFFFF; font-size: 1.7rem; font-family: 'JetBrains Mono', monospace; }}
            .v-flow-value-sub {{ color: #B58863; font-size: 1.1rem; font-family: 'JetBrains Mono', monospace; margin-top: 5px; border-top: 1px solid rgba(181,136,99,0.2); padding-top: 5px; }}
            
            div[data-testid="stTable"] {{ background-color: rgba(0, 0, 0, 0.7) !important; border-radius: 4px; padding: 10px; }}
            div[data-testid="stTable"] td {{ color: #FFFFFF !important; font-family: 'JetBrains Mono', monospace !important; border-bottom: 1px solid rgba(181, 136, 99, 0.2) !important; }}
            div[data-testid="stTable"] th {{ color: #B58863 !important; text-transform: uppercase !important; background-color: rgba(15, 15, 15, 0.9) !important; }}
            
            .v-positive {{ color: #00FF41 !important; }}
            .v-negative {{ color: #FF3131 !important; }}
            div[data-testid="stWidgetLabel"] p {{ color: #B58863 !important; font-weight: 700 !important; }}
            .v-badge-unit {{ background: rgba(181,136,99,0.1); border: 1px solid #B58863; padding: 10px; color: #B58863; font-size: 0.8rem; text-align: center; margin-bottom: 15px; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. MODUŁ ANALIZY FINANSOWEJ
# ==============================================================================
def show_financial_analysis():
    with st.sidebar:
        st.markdown("### 🛠️ KONFIGURACJA")
        source_mode = st.radio("ŹRÓDŁO DANYCH", ["🔗 SYNC (ZE STACK)", "⚡ MANUAL (SZYBKI)"], label_visibility="collapsed")
        st.divider()
        origin = st.selectbox("PUNKT STARTU", list(CONF["DISTANCES_AND_MYTO"].keys()))
        dest = st.selectbox("PUNKT DOCELOWY", list(CONF["DISTANCES_AND_MYTO"][origin].keys()))
        eur_rate = st.number_input("KURS EUR/PLN", value=CONF.get("EURO_RATE", 4.30), step=0.01)
        
        st.divider()
        st.markdown("### 📈 MODEL PRZYCHODU")
        c_cols = st.columns([2, 1])
        with c_cols[0]: rate_type = st.selectbox("MODEL", ["KM", "RYCZAŁT", "OPAKOWANIE"])
        with c_cols[1]: rate_curr = st.selectbox("WALUTA", ["PLN", "EUR"])
        rate_val = st.number_input(f"STAWKA ({rate_curr})", value=6.50 if rate_curr == "PLN" else 1.50)
        
        st.divider()
        view_curr = st.radio("POKAZUJ KOSZTY W:", ["PLN", "EUR"], horizontal=True)

    # Pobranie danych trasy
    route = CONF["DISTANCES_AND_MYTO"][origin][dest]
    dPL, dEU = route["distPL"], route["distEU"]
    total_dist = dPL + dEU

    if source_mode == "🔗 SYNC (ZE STACK)":
        if 'v_manifest' not in st.session_state or not st.session_state.v_manifest:
            st.warning("⚠️ BRAK TOWARU W STACK."); return
        total_cases = sum(math.ceil(it['p_act'] / it.get('itemsPerCase', 1)) for it in st.session_state.v_manifest)
        active_veh_name = st.selectbox("POJAZD", list(VEH_MAP.keys()))
    else:
        c1, c2 = st.columns(2)
        with c1: active_veh_name = st.selectbox("TYP POJAZDU", list(VEH_MAP.keys()))
        with c2: total_cases = st.number_input("OPAKOWANIA", min_value=1, value=12)

    cat = VEH_MAP[active_veh_name]
    v_spec = CONF["VEHICLE_DATA"][cat]
    prices = CONF["PRICE"]

    # Obliczenia Smart Tanking (v2.0)
    total_fuel_needed = total_dist * v_spec["fuelUsage"]
    fuel_from_pl = min(total_fuel_needed, v_spec["tankCapacity"])
    fuel_from_eu = max(0, total_fuel_needed - fuel_from_pl)
    cost_fuel_pln = (fuel_from_pl * prices["fuelPLN"]) + (fuel_from_eu * prices["fuelEUR"] * eur_rate)
    
    cost_adblue_pln = (total_dist * v_spec["adBlueUsage"] * prices["adBluePLN"])
    cost_service_pln = (dPL * v_spec["serviceCostPLN"]) + (dEU * v_spec["serviceCostEUR"] * eur_rate)
    cost_tolls_pln = route.get(f"myto{cat}", 0) * eur_rate
    cost_driver_pln = 500 + (total_dist * 0.15)
    total_cost_pln = cost_fuel_pln + cost_adblue_pln + cost_service_pln + cost_tolls_pln + cost_driver_pln

    # Przychód
    raw_rev = total_dist * rate_val if rate_type == "KM" else (rate_val if rate_type == "RYCZAŁT" else total_cases * rate_val)
    revenue_pln = raw_rev if rate_curr == "PLN" else (raw_rev * eur_rate)
    margin_pln = revenue_pln - total_cost_pln
    margin_pct = (margin_pln / revenue_pln * 100) if revenue_pln > 0 else 0

    # Dashboard Główny
    st.markdown(f"#### 📍 RELACJA: {origin.upper()} ➔ {dest.upper()}")
    # Wyświetlanie dystansu
    st.markdown(f"<div class='v-badge-unit'>DYSTANS CAŁKOWITY: {total_dist} KM (POLSKA: {dPL} KM | ZAGRANICA: {dEU} KM)</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="v-flow-card"><div class="v-flow-label">PRZYCHÓD NETTO</div><div class="v-flow-value-main">{revenue_pln:,.2f} PLN</div><div class="v-flow-value-sub">{revenue_pln/eur_rate:,.2f} EUR</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="v-flow-card"><div class="v-flow-label">KOSZT CAŁKOWITY</div><div class="v-flow-value-main">{total_cost_pln:,.2f} PLN</div><div class="v-flow-value-sub">{total_cost_pln/eur_rate:,.2f} EUR</div></div>', unsafe_allow_html=True)
    
    m_clr = "v-positive" if margin_pln > 0 else "v-negative"
    c3.markdown(f'<div class="v-flow-card"><div class="v-flow-label">MARŻA (ZYSK)</div><div class="v-flow-value-main {m_clr}">{margin_pln:,.2f} PLN</div><div class="v-flow-value-sub {m_clr}">{margin_pct:.1f}% RENTOWNOŚCI</div></div>', unsafe_allow_html=True)

    st.divider()
    ca, cb = st.columns(2)
    mult = 1.0 if view_curr == "PLN" else (1.0 / eur_rate)
    with ca:
        st.markdown(f"### 📊 STRUKTURA KOSZTÓW ({view_curr})")
        cost_df = pd.DataFrame({
            "SKŁADNIK": ["Paliwo (Optimized)", "AdBlue", "Myto (EUR->PLN)", "Serwis", "Kierowca"],
            "WARTOŚĆ": [round(x * mult, 2) for x in [cost_fuel_pln, cost_adblue_pln, cost_tolls_pln, cost_service_pln, cost_driver_pln]]
        })
        st.table(cost_df.set_index("SKŁADNIK"))
    with cb:
        st.markdown("### ⛽ ANALIZA OPERACYJNA")
        st.info(f"**BEP:** {round((total_cost_pln/total_dist)*mult, 2)} {view_curr}/KM")
        st.write(f"**Tankowanie PL:** {round(fuel_from_pl, 1)} L")
        st.write(f"**Tankowanie UE:** {round(fuel_from_eu, 1)} L")

# ==============================================================================
# 3. MODUŁ EDYTORA TRAS
# ==============================================================================
def show_route_editor():
    st.markdown("### 🗺️ EDYTOR BAZY TRAS I OPŁAT")
    st.write("Wprowadź zmiany w tabeli poniżej. Możesz edytować istniejące trasy lub dodać nowe wiersze na końcu.")
    
    # Przekształcenie zagnieżdżonego słownika w płaską listę dla edytora
    flat_routes = []
    for origin, destinations in CONF["DISTANCES_AND_MYTO"].items():
        for dest, data in destinations.items():
            flat_routes.append({
                "SKĄD": origin, "DOKĄD": dest,
                "KM POLSKA": data["distPL"], "KM ZAGRANICA": data["distEU"],
                "MYTO FTL (EUR)": data["mytoFTL"], "MYTO SOLO (EUR)": data["mytoSolo"], "MYTO BUS (EUR)": data["mytoBus"]
            })
    
    df_routes = pd.DataFrame(flat_routes)
    edited_df = st.data_editor(df_routes, num_rows="dynamic", use_container_width=True, key="route_editor")
    
    if st.button("💾 ZAPISZ ZMIANY W BAZIE"):
        # Re-budowa struktury zagnieżdżonej z edytowanego DataFrame
        new_distances = {}
        for _, row in edited_df.iterrows():
            orig = row["SKĄD"]
            dest = row["DOKĄD"]
            if orig not in new_distances: new_distances[orig] = {}
            new_distances[orig][dest] = {
                "distPL": int(row["KM POLSKA"]), "distEU": int(row["KM ZAGRANICA"]),
                "mytoFTL": float(row["MYTO FTL (EUR)"]), "mytoSolo": float(row["MYTO SOLO (EUR)"]), "mytoBus": float(row["MYTO BUS (EUR)"])
            }
        
        CONF["DISTANCES_AND_MYTO"] = new_distances
        save_config(CONF)
        st.success("Baza tras została pomyślnie zaktualizowana!")
        st.rerun()

# ==============================================================================
# 4. GŁÓWNA FUNKCJA FLOW
# ==============================================================================
def run_flow():
    inject_vorteza_flow_ui()
    st.markdown(f"<h2 style='color:#B58863; letter-spacing:10px;'>VORTEZA FLOW</h2>", unsafe_allow_html=True)
    
    if not CONF:
        st.error("Baza danych nie została załadowana."); return

    # Nawigacja między trybami
    with st.sidebar:
        st.markdown("### 🕹️ TRYB PRACY")
        app_mode = st.radio("WYBIERZ:", ["🛰️ ANALIZA FINANSOWA", "🗺️ EDYTOR TRAS"], label_visibility="collapsed")
        st.divider()

    if app_mode == "🛰️ ANALIZA FINANSOWA":
        show_financial_analysis()
    else:
        show_route_editor()

if __name__ == "__main__":
    run_flow()
