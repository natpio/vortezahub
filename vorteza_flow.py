# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import json
import math

# ==============================================================================
# 0. KONFIGURACJA I MASTER DATA
# ==============================================================================
PATH_BG = os.path.join("assets", "bg_vorteza.png")

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
            
            .stApp {{ 
                background-image: url("data:image/png;base64,{os.path.exists(PATH_BG)}"); 
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
            .v-flow-value-main {{ color: #FFFFFF; font-size: 1.6rem; font-family: 'JetBrains Mono', monospace; font-weight: 500; }}
            .v-flow-value-sub {{ color: #B58863; font-size: 1.1rem; font-family: 'JetBrains Mono', monospace; margin-top: 4px; border-top: 1px solid rgba(181,136,99,0.2); padding-top: 4px; }}
            
            .v-positive {{ color: #00FF41 !important; }}
            .v-negative {{ color: #FF3131 !important; }}
            
            div[data-testid="stWidgetLabel"] p {{ color: #B58863 !important; font-weight: 700 !important; }}
            div[data-testid="stRadio"] label p {{ color: #B58863 !important; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 1. SILNIK FLOW
# ==============================================================================
def run_flow():
    inject_vorteza_flow_ui()
    st.markdown(f"<h2 style='color:#B58863; letter-spacing:10px;'>VORTEZA FLOW</h2>", unsafe_allow_html=True)

    # --- SIDEBAR: KONFIGURACJA ---
    with st.sidebar:
        st.markdown("### 🛠️ TRYB OBLICZEŃ")
        source_mode = st.radio("ŹRÓDŁO DANYCH", ["🔗 SYNC (ZE STACK)", "⚡ MANUAL (SZYBKI)"], label_visibility="collapsed")
        
        st.divider()
        st.markdown("### 💶 WALUTA")
        eur_rate = st.number_input("KURS EUR/PLN", min_value=1.0, value=4.35, step=0.01)
        
        st.divider()
        st.markdown("### ⛽ TRASA")
        dist = st.number_input("DYSTANS (KM)", min_value=1, value=500)
        fuel_p = st.number_input("CENA PALIWA (PLN/L)", min_value=0.0, value=6.55)
        
        st.divider()
        st.markdown("### 📈 STAWKA")
        rate_type = st.selectbox("MODEL", ["PLN / KM", "PLN / RYCZAŁT", "PLN / OPAKOWANIE"])
        rate_val = st.number_input("WARTOŚĆ (PLN)", value=6.20 if "KM" in rate_type else 2800.0)

    # --- POBIERANIE DANYCH ---
    active_veh_name = ""
    total_cases = 0

    if source_mode == "🔗 SYNC (ZE STACK)":
        if 'v_manifest' not in st.session_state or not st.session_state.v_manifest:
            st.warning("⚠️ BRAK DANYCH W STACK. PRZEŁĄCZ NA MANUAL.")
            return
        total_cases = sum(math.ceil(it['p_act'] / it.get('itemsPerCase', 1)) for it in st.session_state.v_manifest)
        active_veh_name = st.selectbox("POJAZD ZE STACK", list(FLEET_MASTER_DATA.keys()))
    else:
        col1, col2 = st.columns(2)
        with col1: active_veh_name = st.selectbox("POJAZD", list(FLEET_MASTER_DATA.keys()))
        with col2: total_cases = st.number_input("OPAKOWANIA", min_value=1, value=12)

    # --- OBLICZENIA ---
    veh = FLEET_MASTER_DATA[active_veh_name]
    
    # Koszty (PLN)
    c_fuel = (dist / 100) * veh['cons'] * fuel_p
    c_driver = 500 + (dist * 0.20)
    c_extra = dist * 0.40
    t_cost_pln = c_fuel + c_driver + c_extra
    
    # Przychód (PLN)
    if "KM" in rate_type: revenue_pln = dist * rate_val
    elif "RYCZAŁT" in rate_type: revenue_pln = rate_val
    else: revenue_pln = total_cases * rate_val
    
    # Konwersja na EUR
    revenue_eur = revenue_pln / eur_rate
    t_cost_eur = t_cost_pln / eur_rate
    margin_pln = revenue_pln - t_cost_pln
    margin_eur = margin_pln / eur_rate
    margin_pct = (margin_pln / revenue_pln * 100) if revenue_pln > 0 else 0

    # ==============================================================================
    # 2. DASHBOARD FINANSOWY (DUAL CURRENCY)
    # ==============================================================================
    c1, c2, c3 = st.columns(3)
    
    # Przychód
    c1.markdown(f"""
        <div class="v-flow-card">
            <div class="v-flow-label">PRZYCHÓD NETTO</div>
            <div class="v-flow-value-main">{revenue_pln:,.2f} PLN</div>
            <div class="v-flow-value-sub">{revenue_eur:,.2f} EUR</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Koszt
    c2.markdown(f"""
        <div class="v-flow-card">
            <div class="v-flow-label">KOSZT CAŁKOWITY</div>
            <div class="v-flow-value-main">{t_cost_pln:,.2f} PLN</div>
            <div class="v-flow-value-sub">{t_cost_eur:,.2f} EUR</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Zysk
    m_color = "v-positive" if margin_pln > 0 else "v-negative"
    c3.markdown(f"""
        <div class="v-flow-card">
            <div class="v-flow-label">MARŻA (ZYSK)</div>
            <div class="v-flow-value-main {m_color}">{margin_pln:,.2f} PLN</div>
            <div class="v-flow-value-sub {m_color}">{margin_eur:,.2f} EUR</div>
            <div style="color:#CCC; font-size:0.8rem; margin-top:5px;">{margin_pct:.1f}% RENTOWNOŚCI</div>
        </div>
    """, unsafe_allow_html=True)

    # --- ANALIZA TAKTYCZNA ---
    st.divider()
    ca, cb = st.columns(2)
    with ca:
        st.markdown("### 📊 ANALIZA KOSZTÓW")
        df_c = pd.DataFrame({
            "SKŁADNIK": ["Paliwo", "Kierowca", "Amortyzacja"],
            "PLN": [c_fuel, c_driver, c_extra],
            "EUR": [c_fuel/eur_rate, c_driver/eur_rate, c_extra/eur_rate]
        })
        st.table(df_c.set_index("SKŁADNIK"))
        
    with cb:
        st.markdown("### 🚀 PROGI RENTOWNOŚCI")
        bep_pln = t_cost_pln / dist
        bep_eur = bep_pln / eur_rate
        st.info(f"MINIMALNA STAWKA (BEP): **{bep_pln:.2f} PLN/KM** | **{bep_eur:.2f} EUR/KM**")
        st.write(f"**Wykorzystanie LDM:** {(total_cases * 1.2 / veh['total_ldm'] * 100):.1f}% (Szacunkowo)")

    if st.button("📄 GENERUJ OFERTĘ DWUWALUTOWĄ"):
        st.code(f"""
        OFERTA VORTEZA FLOW
        Dystans: {dist} km | Pojazd: {active_veh_name}
        CENA PLN: {revenue_pln:,.2f} netto
        CENA EUR: {revenue_eur:,.2f} netto (Kurs: {eur_rate})
        """)

if __name__ == "__main__":
    run_flow()
