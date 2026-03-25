# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
import os
import base64
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==============================================================================
# 1. KONFIGURACJA I ZASOBY
# ==============================================================================
PATH_CONFIG = os.path.join("data", "config.json")
PATH_PRODUCTS = os.path.join("data", "products.json")
PATH_BG = os.path.join("assets", "tlo_hub_2.jpg")
SHEET_ID = "1JV-vXpwAbvvboQd7eijashVmS3kkOqTf_LJrbrsWSxo"

def load_vorteza_asset_b64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def load_local_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

# ==============================================================================
# 2. GOOGLE SHEETS ENGINE (Dla zakładki "Zlecenia")
# ==============================================================================
def get_gspread_client():
    creds_info = st.secrets["GCP_SERVICE_ACCOUNT"]
    credentials = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(credentials)

def load_orders():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).worksheet("Zlecenia")
        return pd.DataFrame(sheet.get_all_records())
    except gspread.exceptions.WorksheetNotFound:
        st.error("KRYTYCZNY BŁĄD: Utwórz w Google Sheets zakładkę o nazwie 'Zlecenia'!")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Błąd bazy danych: {e}")
        return pd.DataFrame()

def save_new_order(row_data):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).worksheet("Zlecenia")
        sheet.append_row(row_data)
        return True
    except: return False

def update_order_status(order_id, new_status):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).worksheet("Zlecenia")
        records = sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get('ID')) == str(order_id):
                sheet.update_cell(i + 2, 2, new_status) # Kolumna 2 to Status
                return True
        return False
    except: return False

# ==============================================================================
# 3. INTERFEJS I MOTYW VORTEZA
# ==============================================================================
def inject_core_theme():
    bg_data = load_vorteza_asset_b64(PATH_BG)
    bg_style = f"""
        .stApp {{
            background: linear-gradient(rgba(6, 6, 6, 0.90), rgba(6, 6, 6, 0.90)), 
                        url("data:image/jpeg;base64,{bg_data}") !important;
            background-size: cover !important; background-attachment: fixed !important;
        }}
    """ if bg_data else ".stApp { background-color: #060606 !important; }"

    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700&family=JetBrains+Mono&display=swap');
            {bg_style}
            h1, h2, h3 {{ color: #B58863 !important; text-transform: uppercase; letter-spacing: 4px !important; font-weight: 700 !important; }}
            .order-card {{
                background: rgba(15, 15, 15, 0.85); border: 1px solid rgba(181, 136, 99, 0.3);
                border-left: 4px solid #B58863; padding: 15px; margin-bottom: 15px; border-radius: 4px;
            }}
            .order-card-title {{ color: #FFFFFF; font-size: 1.1rem; font-weight: bold; margin-bottom: 5px; }}
            .order-card-route {{ color: #B58863; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin-bottom: 10px; }}
            .order-card-details {{ color: #AAAAAA; font-size: 0.8rem; line-height: 1.4; }}
            .status-draft {{ border-left-color: #AAAAAA !important; }}
            .status-akcept {{ border-left-color: #2980B9 !important; }}
            .status-trasa {{ border-left-color: #E67E22 !important; }}
            .status-koniec {{ border-left-color: #27AE60 !important; opacity: 0.6; }}
            
            div[data-testid="stButton"] button {{ width: 100%; border-color: #B58863 !important; color: #B58863 !important; background: transparent !important; margin-bottom: 5px; }}
            div[data-testid="stButton"] button:hover {{ background: #B58863 !important; color: #000 !important; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. GŁÓWNA LOGIKA MODUŁU CORE
# ==============================================================================
def run_core():
    inject_core_theme()
    st.markdown("<h2>VORTEZA CORE | ORDER ROUTING</h2>", unsafe_allow_html=True)
    
    current_user = st.session_state.get("username", "OPERATOR")
    config_data = load_local_json(PATH_CONFIG)
    products_data = load_local_json(PATH_PRODUCTS)
    
    if "core_cart" not in st.session_state: st.session_state.core_cart = []

    with st.sidebar:
        st.markdown("### 🎛️ PANEL STEROWANIA")
        # --- DODANO TRZECI TRYB: BAZA / ARCHIWUM ---
        mode = st.radio("TRYB PRACY:", ["📊 TABLICA ZLECEŃ (KANBAN)", "➕ NOWE ZLECENIE", "🗄️ BAZA / ARCHIWUM"], label_visibility="collapsed")
        st.divider()

    df = load_orders()

    if mode == "📊 TABLICA ZLECEŃ (KANBAN)":
        if df.empty:
            st.info("Brak zleceń w systemie. Przejdź do zakładki 'NOWE ZLECENIE'.")
            return
            
        c1, c2, c3, c4 = st.columns(4)
        columns = {"DRAFT (NOWE)": c1, "ZAAKCEPTOWANE": c2, "W TRASIE": c3, "ZAKOŃCZONE": c4}
        
        for title, col in columns.items():
            with col:
                st.markdown(f"<h4 style='text-align:center; font-size:1rem; border-bottom:1px solid #B58863; padding-bottom:10px;'>{title}</h4>", unsafe_allow_html=True)
                
                df_filtered = df[df['Status'].astype(str) == title]
                
                for _, row in df_filtered.iterrows():
                    o_id = row.get('ID', 'N/A')
                    css_class = "order-card status-draft" if title == "DRAFT (NOWE)" else "order-card status-akcept" if title == "ZAAKCEPTOWANE" else "order-card status-trasa" if title == "W TRASIE" else "order-card status-koniec"
                    
                    st.markdown(f"""
                        <div class="{css_class}">
                            <div class="order-card-title">{o_id} | {row.get('Klient', '-')}</div>
                            <div class="order-card-route">📍 {row.get('Start', '-')} ➔ {row.get('Koniec', '-')}</div>
                            <div class="order-card-details">
                                <b>Załadunek:</b> {row.get('DataZal', '-')}<br>
                                <b>Stawka:</b> {row.get('Stawka', '-')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # --- PRZYCISKI Z LOGIKĄ COFANIA I ANULOWANIA ---
                    if title == "DRAFT (NOWE)":
                        a1, a2 = st.columns(2)
                        if a1.button("✅ AKCEPT", key=f"akc_{o_id}"):
                            update_order_status(o_id, "ZAAKCEPTOWANE")
                            st.rerun()
                        if a2.button("📦 STACK", key=f"stk_{o_id}"):
                            try:
                                order_items = json.loads(row.get('Sprzet', '[]'))
                                new_manifest = []
                                for item in order_items:
                                    for p in products_data:
                                        if p['name'] == item['SKU']:
                                            p_copy = p.copy()
                                            p_copy['p_act'] = int(item['ILOSC'])
                                            new_manifest.append(p_copy)
                                            break
                                st.session_state.v_manifest = new_manifest
                                st.session_state.active_module = "PLANER 3D (STACK)"
                                st.rerun()
                            except Exception as e: st.error(f"Błąd ładunku: {e}")
                            
                        if st.button("❌ ANULUJ", key=f"anl_{o_id}"):
                            update_order_status(o_id, "ANULOWANE")
                            st.rerun()
                                    
                    elif title == "ZAAKCEPTOWANE":
                        a1, a2 = st.columns(2)
                        if a1.button("🚚 W DROGĘ", key=f"drg_{o_id}"):
                            update_order_status(o_id, "W TRASIE")
                            st.rerun()
                        if a2.button("💸 FLOW", key=f"flw_{o_id}"):
                            try:
                                order_items = json.loads(row.get('Sprzet', '[]'))
                                new_manifest = []
                                for item in order_items:
                                    for p in products_data:
                                        if p['name'] == item['SKU']:
                                            p_copy = p.copy()
                                            p_copy['p_act'] = int(item['ILOSC'])
                                            new_manifest.append(p_copy)
                                            break
                                st.session_state.v_manifest = new_manifest
                                st.session_state.flow_origin = row.get('Start', '')
                                st.session_state.flow_dest = row.get('Koniec', '')
                                st.session_state.flow_rate = row.get('Stawka', '')
                                st.session_state.active_module = "FINANSE (FLOW)"
                                st.rerun()
                            except Exception as e: st.error(f"Błąd ładunku: {e}")
                            
                        b1, b2 = st.columns(2)
                        if b1.button("↩️ COFNIJ", key=f"cof_{o_id}"):
                            update_order_status(o_id, "DRAFT (NOWE)")
                            st.rerun()
                        if b2.button("❌ ANULUJ", key=f"anl2_{o_id}"):
                            update_order_status(o_id, "ANULOWANE")
                            st.rerun()
                            
                    elif title == "W TRASIE":
                        a1, a2 = st.columns(2)
                        if a1.button("🏁 KONIEC", key=f"kon_{o_id}"):
                            update_order_status(o_id, "ZAKOŃCZONE")
                            st.rerun()
                        if a2.button("↩️ COFNIJ", key=f"cof_{o_id}"):
                            update_order_status(o_id, "ZAAKCEPTOWANE")
                            st.rerun()
                            
                    elif title == "ZAKOŃCZONE":
                        if st.button("↩️ COFNIJ DO TRASY", key=f"cof_{o_id}"):
                            update_order_status(o_id, "W TRASIE")
                            st.rerun()

    elif mode == "➕ NOWE ZLECENIE":
        st.markdown("### KREATOR ZLECENIA")
        c_left, c_right = st.columns([2, 1])
        
        with c_left:
            with st.container(border=True):
                st.markdown("#### 1. LOGISTYKA")
                col1, col2 = st.columns(2)
                klient = col1.text_input("KLIENT / ZLECENIODAWCA")
                stawka = col2.text_input("STAWKA (np. 4500 PLN / 1200 EUR)")
                
                miasta_start = list(config_data.get("DISTANCES_AND_MYTO", {}).keys()) if config_data else ["Poznań", "Warszawa"]
                
                col3, col4 = st.columns(2)
                start = col3.selectbox("MIEJSCE ZAŁADUNKU", miasta_start)
                
                miasta_cel = list(config_data.get("DISTANCES_AND_MYTO", {}).get(start, {}).keys()) if config_data else []
                koniec = col4.selectbox("MIEJSCE ROZŁADUNKU", miasta_cel)
                
                col5, col6, col7 = st.columns(3)
                data_z = col5.date_input("DATA ZAŁADUNKU")
                data_r = col6.date_input("DATA ROZŁADUNKU")
                postoj = col7.number_input("DNI POSTOJU (EXPO)", min_value=0, value=0)
                
                uwagi = st.text_area("UWAGI OPERACYJNE (np. awizacja, kontakt)")

        with c_right:
            with st.container(border=True):
                st.markdown("#### 2. ŁADUNEK (SKU)")
                lista_sku = [p['name'] for p in products_data] if products_data else []
                wybrane_sku = st.selectbox("WYBIERZ SPRZĘT", lista_sku)
                ilosc_sku = st.number_input("ILOŚĆ (SZTUKI/CASE)", min_value=1, value=1)
                
                if st.button("➕ DODAJ DO LISTY ZLECENIA"):
                    st.session_state.core_cart.append({"SKU": wybrane_sku, "ILOSC": ilosc_sku})
                
                st.markdown("---")
                if st.session_state.core_cart:
                    for i, item in enumerate(st.session_state.core_cart):
                        st.markdown(f"- **{item['ILOSC']}x** {item['SKU']}")
                    if st.button("🗑️ WYCZYŚĆ ŁADUNEK"):
                        st.session_state.core_cart = []
                        st.rerun()
                else:
                    st.info("Lista sprzętu jest pusta.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 ZAPISZ I UTWÓRZ ZLECENIE", use_container_width=True):
            if not klient:
                st.error("Podaj nazwę klienta!")
            else:
                now = datetime.now()
                order_id = f"VC-{now.strftime('%y')}-{now.strftime('%H%M%S')}"
                sprzet_json = json.dumps(st.session_state.core_cart, ensure_ascii=False)
                
                row = [
                    order_id, "DRAFT (NOWE)", klient, current_user, start, koniec, 
                    str(data_z), str(data_r), postoj, stawka, sprzet_json, uwagi
                ]
                
                if save_new_order(row):
                    st.session_state.core_cart = [] 
                    st.success(f"Zlecenie {order_id} zostało pomyślnie utworzone!")
                    st.balloons()
                else:
                    st.error("Błąd zapisu. Upewnij się, że masz zakładkę 'Zlecenia' w Google Sheets.")

    # --- NOWY WIDOK: BAZA / ARCHIWUM ---
    elif mode == "🗄️ BAZA / ARCHIWUM":
        st.markdown("### 🗄️ REJESTR WSZYSTKICH ZLECEŃ")
        if df.empty:
            st.info("Baza zleceń jest pusta.")
        else:
            # Formatujemy wyświetlanie JSONa ze sprzętem, by nie zaciemniał tabeli
            display_df = df.copy()
            
            # Liczniki
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Wszystkich Zleceń", len(display_df))
            col2.metric("W Trasie", len(display_df[display_df['Status'] == 'W TRASIE']))
            col3.metric("Zakończone", len(display_df[display_df['Status'] == 'ZAKOŃCZONE']))
            col4.metric("Anulowane", len(display_df[display_df['Status'] == 'ANULOWANE']))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    run_core()
