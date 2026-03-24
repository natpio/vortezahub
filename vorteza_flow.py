# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import json
import math

# ==============================================================================
# 0. KONFIGURACJA I MASTER DATA (SYNCHRONIZACJA Z FLOTĄ STACK)
# ==============================================================================
PATH_BG = os.path.join("assets", "bg_vorteza.png")

# Te same dane techniczne co w module STACK, rozszerzone o parametry kosztowe
FLEET_MASTER_DATA = {
    "BUS Opel Movano": {"max_w": 1300, "L": 420, "W": 210, "H": 230, "axles": 2, "total_ldm": 4.2, "cons": 11.5},
    "Solo 6m Light": {"max_w": 5000, "L": 610, "W": 245, "H": 250, "axles": 2, "total_ldm": 6.1, "cons": 19.0},
    "Solo 7m Medium": {"max_w": 7000, "L": 720, "W": 245, "H": 260, "axles": 2, "total_ldm": 7.2, "cons": 21.0},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "axles": 2, "total_ldm": 9.2, "cons": 23.5},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "axles": 3, "total_ldm": 13.6, "cons": 28.5},
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "axles": 3, "total_ldm": 13.6, "cons": 30.0}
}

def inject_vorteza_flow_ui():
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700&family=JetBrains+Mono&display=swap');
            
            /* Kafelki Finansowe Apex Style */
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
            .v-flow-value {{ color: #FFFFFF; font-size: 1.8rem; font-family: 'JetBrains Mono', monospace; font-weight: 500; }}
            .v-flow-sub {{ color: #888; font-size: 0.8rem; margin-top: 5px; }}
            .v-positive {{ color: #00FF41 !important; }}
            .v-negative {{ color: #FF3131 !important; }}
            
            /* Naprawa czytelności etykiet */
            div[data-testid="stWidgetLabel"] p {{ color: #B58863 !important; font-weight: 700 !important; letter-spacing: 1px; }}
            div[data-testid="stRadio"] label p {{ color: #B58863 !important; }}
            
            /* Tabela Wyników */
            .v-table-flow {{ width: 100%; border-collapse: collapse; background: rgba(0,0,0,0.5); border: 1px solid #333; }}
            .v-table-flow td {{ padding: 12px; border-bottom: 1px solid #222; color: #EEE; font-family: 'JetBrains Mono', monospace; }}
            .v-table-flow tr:hover {{ background: rgba(181,136,99,0.05); }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 1. SILNIK FLOW
# ==============================================================================
def run_flow():
    inject_vorteza_flow_ui()
    st.markdown(f"<h2 style='color:#B58863; letter-spacing:10px;'>VORTEZA FLOW</h2>", unsafe_allow_html=True)

    # --- SIDEBAR: KONFIGURACJA BIZNESOWA ---
    with st.sidebar:
        st.markdown("### 🛠️ TRYB OBLICZEŃ")
        source_mode = st.radio("ŹRÓDŁO DANYCH", ["🔗 SYNC (Z PLANERA STACK)", "⚡ MANUAL (SZYBKA WYCENA)"], label_visibility="collapsed")
        st.divider()
        
        st.markdown("### ⛽ KOSZTY TRASY")
        dist = st.number_input("DYSTANS CAŁKOWITY (KM)", min_value=1, value=500)
        fuel_p = st.number_input("CENA PALIWA (PLN/L)", min_value=0.0, value=6.55, step=0.01)
        additional_costs = st.number_input("OPŁATY (BRAMKI/INNE) [PLN]", value=200)
        
        st.divider()
        st.markdown("### 📈 MODEL PRZYCHODU")
        rate_type = st.selectbox("TYP ROZLICZENIA", ["ZA KILOMETR", "ZA CAŁY KURS (RYCZAŁT)", "ZA OPAKOWANIE / PALETĘ"])
        rate_val = st.number_input("WARTOŚĆ STAWKI (PLN)", value=6.20 if rate_type == "ZA KILOMETR" else 2800.0)

    # --- LOGIKA POBIERANIA DANYCH ---
    active_veh_name = ""
    total_cases = 0
    total_weight = 0

    if source_mode == "🔗 SYNC (Z PLANERA STACK)":
        if 'v_manifest' not in st.session_state or not st.session_state.v_manifest:
            st.warning("⚠️ BRAK DANYCH W STACK. NAJPIERW DODAJ TOWAR DO PLANERA 3D LUB PRZEŁĄCZ NA TRYB MANUAL.")
            return
        
        # Pobieranie realnych danych z sesji
        total_cases = sum(math.ceil(it['p_act'] / it.get('itemsPerCase', 1)) for it in st.session_state.v_manifest)
        total_weight = sum(it['weight'] * math.ceil(it['p_act'] / it.get('itemsPerCase', 1)) for it in st.session_state.v_manifest)
        
        # W trybie Sync pozwalamy wybrać auto, które aktualnie analizujemy finansowo
        st.markdown(f"<div class='v-badge-unit'>POBRANO ZE STACK: {total_cases} OPAKOWAŃ | {total_weight} KG</div>", unsafe_allow_html=True)
        active_veh_name = st.selectbox("WYBIERZ AUTO DO ANALIZY KOSZTÓW", list(FLEET_MASTER_DATA.keys()))
        
    else: # TRYB MANUAL
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            active_veh_name = st.selectbox("TYP POJAZDU", list(FLEET_MASTER_DATA.keys()))
        with col_m2:
            total_cases = st.number_input("LICZBA OPAKOWAŃ (ESTYMACJA)", min_value=1, value=12)
        total_weight = total_cases * 450 # Średnia estymacja dla trybu szybkiego

    # --- OBLICZENIA FINANSOWE ---
    veh_spec = FLEET_MASTER_DATA[active_veh_name]
    avg_cons = veh_spec['cons']
    
    # Koszty
    cost_fuel = (dist / 100) * avg_cons * fuel_p
    cost_driver = 450 + (dist * 0.15) # Koszt kierowcy (podstawa + km)
    cost_maint = dist * 0.35 # Amortyzacja i serwis
    total_cost = cost_fuel + cost_driver + cost_maint + additional_costs
    
    # Przychód
    if rate_type == "ZA KILOMETR": revenue = dist * rate_val
    elif rate_type == "ZA CAŁY KURS (RYCZAŁT)": revenue = rate_val
    else: revenue = total_cases * rate_val
    
    margin = revenue - total_cost
    margin_pct = (margin / revenue * 100) if revenue > 0 else 0

    # ==============================================================================
    # 2. DASHBOARD FINANSOWY
    # ==============================================================================
    c1, c2, c3 = st.columns(3)
    
    c1.markdown(f'<div class="v-flow-card"><div class="v-flow-label">PRZYCHÓD NETTO</div><div class="v-flow-value">{revenue:,.2f} PLN</div><div class="v-flow-sub">STAWKA: {revenue/dist:.2f} PLN/KM</div></div>', unsafe_allow_html=True)
    
    c2.markdown(f'<div class="v-flow-card"><div class="v-flow-label">KOSZT CAŁKOWITY</div><div class="v-flow-value">{total_cost:,.2f} PLN</div><div class="v-flow-sub">PALIWO: {cost_fuel:,.0f} PLN</div></div>', unsafe_allow_html=True)
    
    m_color = "v-positive" if margin > 0 else "v-negative"
    c3.markdown(f'<div class="v-flow-card"><div class="v-flow-label">ZYSK OPERACYJNY</div><div class="v-flow-value {m_color}">{margin:,.2f} PLN</div><div class="{m_color}" style="font-size:0.9rem; font-weight:700;">{margin_pct:.1f}% RENTOWNOŚCI</div></div>', unsafe_allow_html=True)

    # --- ANALIZA SZCZEGÓŁOWA ---
    st.divider()
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.markdown("### 📊 STRUKTURA RENTOWNOŚCI")
        df_costs = pd.DataFrame({
            "SKŁADNIK KOSZTÓW": ["Paliwo", "Wynagrodzenie i Diety", "Amortyzacja i Serwis", "Opłaty dodatkowe"],
            "PLN": [cost_fuel, cost_driver, cost_maint, additional_costs]
        })
        st.table(df_costs)
        
    with col_b:
        st.markdown("### 🚀 KPI TRASY")
        st.markdown(f"""
        <table class="v-table-flow">
            <tr><td>PRÓG RENTOWNOŚCI (BEP)</td><td class="v-positive">{total_cost/dist:.2f} PLN/KM</td></tr>
            <tr><td>KOSZT NA OPAKOWANIE</td><td>{total_cost/total_cases:.2f} PLN</td></tr>
            <tr><td>WAGA ŁADUNKU</td><td>{total_weight} KG</td></tr>
            <tr><td>LDM POJAZDU</td><td>{veh_spec['total_ldm']} LDM</td></tr>
        </table>
        """, unsafe_allow_html=True)

    st.divider()
    
    # --- AKCJA ---
    if st.button("📄 GENERUJ OFERTĘ DLA KLIENTA"):
        offer_text = f"""
        OFERTA TRANSPORTOWA VORTEZA
        ---------------------------
        Pojazd: {active_veh_name}
        Trasa: {dist} KM
        Ładunek: {total_cases} palet/opakowań
        
        CENA NETTO: {revenue:,.2f} PLN
        TERMIN WAŻNOŚCI: 24H
        """
        st.code(offer_text, language="text")
        st.toast("Oferta gotowa do skopiowania!")

if __name__ == "__main__":
    run_flow()
