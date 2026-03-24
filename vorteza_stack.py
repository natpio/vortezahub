# -*- coding: utf-8 -*-
import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
import math
import pandas as pd
import random
import base64
from datetime import datetime
import io
import os
from PIL import Image

# ==============================================================================
# 0. MULTILINGUAL ENGINE (V-LANG)
# ==============================================================================
LANGUAGES = {
    "PL": {
        "title": "VORTEZA STACK", "fleet": "KONSOLA FLOTY", "unit": "JEDNOSTKA TRANSPORTOWA",
        "offset": "OFFSET OD ŚCIANY (cm)", "cargo": "WEJŚCIE ŁADUNKU", "sku_sel": "WYBÓR SKU",
        "qty": "ILOŚĆ (SZTUKI)", "add": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ DANE",
        "manifest": "MANIFEST ZAŁADUNKOWY", "edit_m": "EDYCJA MANIFESTU", "cases": "OPAKOWANIA",
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "WAGA BRUTTO", "util": "WYKORZYSTANIE",
        "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI", "mission": "JEDNOSTKA MISJI", "l_auth": "OBRÓT: AUTORYZOWANY",
        "l_lock": "OBRÓT: ZABLOKOWANY", "no_data": "STATUS: OCZEKIWANIE NA DANE",
        "update": "AKTUALIZUJ MANIFEST", "terminate": "WYLOGUJ", "inventory": "BAZA SKU",
        "logs": "LOGI SYSTEMOWE", "kpi": "WSKAŹNIKI KPI", "bal_front": "ALARM: PRZECIĄŻENIE PRZODU",
        "bal_rear": "ALARM: ODCIĄŻENIE OSI SKRĘTNEJ", "bal_ok": "STATUS NOMINALNY: Balans optymalny",
        "save_db": "ZAPISZ BAZĘ SKU", "sync": "SYNCHRONIZACJA ZAKOŃCZONA", "sku_ident": "IDENTYFIKATOR SKU",
        "mission_data": "OCZEKIWANIE NA DANE MISJI", "pos": "POZYCJONOWANIE", "auth_label": "KLUCZ BEZPIECZEŃSTWA GOLIATH",
        "auth_title": "VORTEZA LOGIN"
    }, [cite: 5, 6, 7]
    "ENG": {
        "title": "VORTEZA STACK", "fleet": "FLEET CONSOLE", "unit": "TRANSPORT UNIT",
        "offset": "WALL OFFSET (cm)", "cargo": "CARGO ENTRY", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY (TOTAL PCS)", "add": "APPEND TO MANIFEST", "purge": "PURGE ALL DATA",
        "manifest": "LOAD MANIFEST", "edit_m": "EDIT MANIFEST", "cases": "CASES",
        "pcs": "TOTAL PCS", "weight": "GROSS WEIGHT", "util": "UTILIZATION",
        "cog": "CENTER OF GRAVITY ANALYSIS", "mission": "MISSION UNIT", "l_auth": "ROTATION: AUTHORIZED",
        "l_lock": "ROTATION: LOCKED", "no_data": "STATUS: WAITING FOR MISSION DATA",
        "update": "UPDATE MANIFEST", "terminate": "TERMINATE", "inventory": "MASTER INVENTORY",
        "logs": "SYSTEM LOGS", "kpi": "OPERATIONAL KPI", "bal_front": "ALARM: FRONT OVERLOAD",
        "bal_rear": "ALARM: STEERING AXLE UNLOADED", "bal_ok": "NOMINAL STATUS: Optimal Balance",
        "save_db": "SAVE SKU DATABASE", "sync": "SYNC COMPLETE", "sku_ident": "SKU IDENTIFIER",
        "mission_data": "WAITING FOR MISSION DATA", "pos": "DYNAMIC POSITIONING", "auth_label": "GOLIATH CORE SECURITY KEY",
        "auth_title": "VORTEZA LOGIN"
    }, [cite: 7, 8, 9]
    "ES": {
        "title": "VORTEZA STACK", "fleet": "CONSOLA DE FLOTA", "unit": "UNIDAD DE TRANSPORTE",
        "offset": "DESPLAZAMIENTO (cm)", "cargo": "ENTRADA DE CARGA", "sku_sel": "SELECTOR DE SKU",
        "qty": "CANTIDAD (PIEZAS)", "add": "AÑADIR AL MANIFIESTO", "purge": "LIMPIAR DATOS",
        "manifest": "MANIFIESTO DE CARGA", "edit_m": "EDITAR MANIFIESTO", "cases": "CAJAS",
        "pcs": "PIEZAS TOTALES", "weight": "PESO BRUTO", "util": "UTILIZACIÓN",
        "cog": "ANÁLISIS DEL CENTRO DE GRAVEDAD", "mission": "UNIDAD DE MISIÓN", "l_auth": "GIRO: AUTORIZADO",
        "l_lock": "GIRO: BLOQUEADO", "no_data": "ESTADO: ESPERANDO DATOS",
        "update": "ACTUALIZAR MANIFIESTO", "terminate": "SALIR", "inventory": "INVENTARIO",
        "logs": "REGISTROS", "kpi": "KPI OPERATIVO", "bal_front": "ALARMA: SOBRECARGA DELANTERA",
        "bal_rear": "ALARMA: EJE DE DIRECCIÓN DESCARGADO", "bal_ok": "ESTADO NOMINAL: Balance óptimo",
        "save_db": "GUARDAR BASE DE DATOS", "sync": "SINCRONIZACIÓN OK", "sku_ident": "IDENTIFICADOR SKU",
        "mission_data": "ESPERANDO DATOS", "pos": "POSICIONAMIENTO", "auth_label": "CLAVE DE SEGURIDAD GOLIATH",
        "auth_title": "VORTEZA INICIAR"
    }, [cite: 10, 11, 12]
    "DE": {
        "title": "VORTEZA STACK", "fleet": "FLOTTENKONSOLE", "unit": "TRANSPORTEINHEIT",
        "offset": "WANDABSTAND (cm)", "cargo": "LADUNGSEINGABE", "sku_sel": "SKU-AUSWAHL",
        "qty": "MENGE (STÜCK)", "add": "ZUM MANIFEST HINZUFÜGEN", "purge": "DATEN LÖSCHEN",
        "manifest": "LADEMANIFEST", "edit_m": "MANIFEST BEARBEITEN", "cases": "KARTONS",
        "pcs": "STÜCK GESAMT", "weight": "BRUTTOGEWICHT", "util": "AUSLASTUNG",
        "cog": "SCHWERPUNKTSANALYSE", "mission": "MISSIONSEINHEIT", "l_auth": "ROTATION: ERLAUBT",
        "l_lock": "ROTATION: GESPERRT", "no_data": "STATUS: WARTE AUF DATEN",
        "update": "MANIFEST AKTUALISIEREN", "terminate": "BEENDEN", "inventory": "INVENTAR",
        "logs": "SYSTEMPROTOKOLLE", "kpi": "BETRIEBS-KPI", "bal_front": "ALARM: FRONTÜBERLASTUNG",
        "bal_rear": "ALARM: LENKACHSE ENTLASTET", "bal_ok": "NOMINALER STATUS: Optimale Balance",
        "save_db": "SKU-DATENBANK SPEICHERN", "sync": "SYNC ABGESCHLOSSEN", "sku_ident": "SKU-IDENTIFIKATOR",
        "mission_data": "WARTE AUF MISSIONSDATEN", "pos": "POSITIONIERUNG", "auth_label": "GOLIATH SICHERHEITSSCHLÜSSEL",
        "auth_title": "VORTEZA ANMELDUNG"
    } [cite: 12, 13, 14]
}

# ==============================================================================
# 1. ŚRODOWISKO I REJESTR INŻYNIERYJNY FLOTY
# ==============================================================================
FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 230
    }, [cite: 14]
    "TIR FTL Standard 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 230
    }, [cite: 15]
    "Solo 9m Heavy Duty": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_max": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "cab_l": 200
    }, [cite: 15]
    "Solo 7m Medium": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_max": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200, "cab_l": 180
    }, [cite: 16]
    "BUS XL Express": {
        "max_w": 1300, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140
    } [cite: 16]
}

# ==============================================================================
# 2. BRANDING VORTEZA & ADVANCED UI ENGINE
# ==============================================================================
def load_vorteza_asset_b64(file_path):
    try:
        full_path = os.path.join("assets", file_path) if not os.path.exists(file_path) else file_path
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f: [cite: 17]
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def inject_vorteza_stack_ui():
    bg_data = load_vorteza_asset_b64('bg_vorteza.png')
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            :root {{
                --v-copper: #B58863; [cite: 18]
                --v-panel-bg: rgba(6, 6, 6, 0.98); [cite: 19]
                --v-border: rgba(181, 136, 99, 0.2);
                --v-neon-green: #00FF41;
                --v-alert-red: #FF3131; [cite: 19]
            }} [cite: 20]
            .stApp {{ background-image: url("data:image/png;base64,{{bg_data}}"); background-size: cover; background-attachment: fixed; [cite: 20]
                color: #FFFFFF; font-family: 'Montserrat', sans-serif; }} [cite: 21]
            .v-tile-apex {{ background: var(--v-panel-bg); [cite: 21]
                padding: 3rem; border: 1px solid var(--v-border); border-left: 15px solid var(--v-copper); box-shadow: 0 50px 120px rgba(0,0,0,1); margin-bottom: 3.5rem; backdrop-filter: blur(50px); [cite: 22]
            }} [cite: 23]
            section[data-testid="stSidebar"] {{ background-color: rgba(3, 3, 3, 0.99) !important; [cite: 23]
                border-right: 1px solid var(--v-border); width: 480px !important; backdrop-filter: blur(35px); }} [cite: 24]
            h1, h2, h3 {{ color: var(--v-copper) !important; [cite: 24]
                text-transform: uppercase; letter-spacing: 12px !important; font-weight: 700 !important; }} [cite: 25]
            [data-testid="stMetricValue"] {{ color: var(--v-copper) !important; [cite: 25]
                font-family: 'JetBrains Mono', monospace !important; font-size: 3.8rem !important; }} [cite: 26]
            .v-table-tactical {{ width: 100%; [cite: 26]
                border-collapse: collapse; margin-top: 40px; border: 1px solid #111; }} [cite: 27]
            .v-table-tactical th {{ background: #000; [cite: 27]
                color: var(--v-copper); padding: 25px; border-bottom: 3px solid #333; letter-spacing: 3px; [cite: 28]
            }} [cite: 29]
            .v-table-tactical td {{ padding: 20px 25px; [cite: 29]
                border-bottom: 1px solid #111; color: #CCC; }} [cite: 30]
            .v-rail-track {{ width: 100%; [cite: 30]
                height: 35px; background: #050505; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0; [cite: 31]
            }} [cite: 32]
            .v-cog-pointer {{ position: absolute; width: 10px; height: 70px; [cite: 32]
                top: -17.5px; background: var(--v-neon-green); box-shadow: 0 0 40px var(--v-neon-green); border-radius: 5px; transition: left 1.5s cubic-bezier(0.19, 1, 0.22, 1); [cite: 33]
            }} [cite: 34]
            .v-badge-unit {{ background: rgba(181,136,99,0.1); border: 1px solid var(--v-copper); [cite: 34]
                padding: 20px; font-family: 'JetBrains Mono', monospace; color: var(--v-copper); }} [cite: 35]
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. SILNIK GRAFICZNY I CAD-3D RENDERER
# ==============================================================================
def get_vorteza_sku_hex(sku_name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#16A085", "#27AE60", "#2980B9", "#E67E22", "#C0392B"]
    random.seed(sum(ord(c) for c in str(sku_name)))
    return random.choice(palette) [cite: 38]

def build_box_cad_geometry(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    i_map = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j_map = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k_map = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6] [cite: 39]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i_map, j=j_map, k=k_map, color=color, opacity=0.99, name=name, flatshading=True)
    lx = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    ly = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    lz = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    fig = go.Figure() [cite: 40]
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#151515', opacity=1, hoverinfo='skip'))
    axles = vehicle_specs.get('axles', 3)
    rear_base_x = L - 450 if L > 800 else L - 180
    for a in range(axles):
        ax_x = rear_base_x + (a * 145)
        if ax_x < L:
            for side in [-40, W+25]: [cite: 41]
                fig.add_trace(go.Mesh3d(x=[ax_x-60, ax_x+60, ax_x+60, ax_x-60], y=[side, side, side+18, side+18], z=[-85, -85, -15, -15], color='#000', opacity=1, hoverinfo='skip'))
                fig.add_trace(go.Mesh3d(x=[ax_x-25, ax_x+25, ax_x+25, ax_x-25], y=[side-2, side-2, side, side], z=[-60, -60, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'))
    cab_l = vehicle_specs.get('cab_l', 230)
    fig.add_trace(go.Mesh3d(x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l], y=[-45, -45, W+45, W+45, -45, -45, W+45, W+45], z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], [cite: 41]
        j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#050505', opacity=1)) [cite: 42]
    skeleton_lines = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]), ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]), ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])]
    for lx, ly, lz in skeleton_lines: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))
    for cluster in cargo_stacks:
        for unit in cluster['items']: [cite: 43]
            x, y, z, dx, dy, dz = cluster['x'], cluster['y'], unit['z'], unit['w_fit'], unit['l_fit'], unit['height']
            parts = build_box_cad_geometry(x, y, z, dx, dy, dz, get_vorteza_sku_hex(unit['name']), unit['name'])
            for p in parts: fig.add_trace(p)
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0)), bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# ==============================================================================
# 5. SILNIK PAKOWANIA V24 SUPREME
# ==============================================================================
class V24SupremeEngine:
    @staticmethod
    def solve(cargo_list, vehicle, x_offset=0): [cite: 44]
        items_sorted = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        placed_stacks, failed_units, total_weight = [], [], 0
        cx, cy, current_row_max_w = x_offset, 0, 0
        for unit in items_sorted:
            if total_weight + unit['weight'] > vehicle['max_w']: failed_units.append(unit); [cite: 44]
                continue [cite: 45]
            is_stacked = False
            if unit.get('canStack', True):
                for s in placed_stacks:
                    orient = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
                    dim_fit = any(fw <= s['w'] and fl <= s['l'] for fw, fl in orient) [cite: 46]
                    if dim_fit and (s['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy(); [cite: 46]
                        u_copy['z'] = s['curH']; u_copy['w_fit'], u_copy['l_fit'] = s['w'], s['l'] [cite: 47]
                        s['items'].append(u_copy); [cite: 47]
                        s['curH'] += unit['height']; total_weight += unit['weight']; is_stacked = True; break [cite: 48]
            if is_stacked: continue
            is_placed, orientations = False, [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; [cite: 49]
                    u_c['w_fit'], u_c['l_fit'] = fw, fl; placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; current_row_max_w = max(current_row_max_w, fw); [cite: 50]
                    total_weight += unit['weight']; is_placed = True; break [cite: 51]
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; [cite: 51]
                    cy = 0; current_row_max_w = fw; u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl; [cite: 52]
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; total_weight += unit['weight']; is_placed = True; [cite: 53]
                    break [cite: 54]
            if not is_placed: failed_units.append(unit)
        ldm_res = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, total_weight, failed_units, ldm_res

# ==============================================================================
# 6. ANALITYKA I DATA I/O
# ==============================================================================
def process_load_bal_ui(vehicle, stacks, L):
    if not stacks: return
    t_moment, t_weight = 0, 0
    for s in stacks:
        for it in s['items']: t_moment += ((s['x'] + it['w_fit']/2) * it['weight']); [cite: 54]
            t_weight += it['weight'] [cite: 55]
    cog_p = (t_moment / t_weight / vehicle['L']) * 100 if t_weight > 0 else 0
    st.markdown(f"### ⚖️ {{L['cog']}}"); [cite: 55]
    marker_clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131" [cite: 56]
    st.markdown(f'<div class="v-rail-track"><div class="v-cog-pointer" style="left: {{cog_p}}%; background: {{marker_clr}}; box-shadow: 0 0 40px {{marker_clr}};"></div></div>', unsafe_allow_html=True)
    if cog_p < 35: st.warning(L['bal_front'])
    elif cog_p > 65: st.warning(L['bal_rear'])
    else: st.success(L['bal_ok'])

def db_core_load():
    path = os.path.join("data", "products.json")
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def db_core_save(data):
    path = os.path.join("data", "products.json")
    with open(path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False) [cite: 57]

# ==============================================================================
# 7. FUNKCJA URUCHOMIENIOWA (MODUŁ HUB)
# ==============================================================================
def run_stack():
    inject_vorteza_stack_ui()
    
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    L = LANGUAGES[st.session_state.lang]
    
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_core_load()

    hc1, hc2, hc3 = st.columns([1, 4, 1])
    with hc1:
        logo_b64 = load_vorteza_asset_b64('logo_vorteza.png')
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{{logo_b64}}" width="180">', unsafe_allow_html=True) [cite: 58]
        else: st.markdown("### VORTEZA")
    with hc2:
        st.markdown(f"<h1>{{L['title']}}</h1>", unsafe_allow_html=True)
    with hc3:
        pass # Terminacja zarządzana przez Hub

    with st.sidebar:
        st.session_state.lang = st.selectbox("🌐 LANGUAGE", ["PL", "ENG", "ES", "DE"], index=["PL", "ENG", "ES", "DE"].index(st.session_state.lang))
        L = LANGUAGES[st.session_state.lang]
        
        st.markdown(f"### 📡 {{L['fleet']}}")
        v_key = st.selectbox(L['unit'], list(FLEET_MASTER_DATA.keys()))
        veh = FLEET_MASTER_DATA[v_key]
        
        st.divider()
        st.markdown(f"### ⚖️ {{L['pos']}}")
        x_shift = st.slider(L['offset'], 0, veh['L']-200, 0) [cite: 60]
        
        st.divider()
        st.markdown(f"### 📥 {{L['cargo']}}")
        sel_sku_name = st.selectbox(L['sku_sel'], [p['name'] for p in inventory], index=None)
        if sel_sku_name:
            p_ref = next(p for p in inventory if p['name'] == sel_sku_name)
            ipc = p_ref.get('itemsPerCase', 1) [cite: 61]
            st.markdown(f"<div class='v-badge-unit'>SKU: {{sel_sku_name}}<br>STANDARD: {{ipc}} PCS/CASE</div>", unsafe_allow_html=True)
            p_qty = st.number_input(L['qty'], min_value=1, value=int(ipc))
            if st.button(L['add']):
                found = False
                for item in st.session_state.v_manifest: [cite: 62]
                    if item['name'] == sel_sku_name:
                        item['p_act'] += p_qty; [cite: 63]
                        found = True; break
                if not found:
                    u_entry = p_ref.copy(); [cite: 63]
                    u_entry['p_act'] = p_qty; st.session_state.v_manifest.append(u_entry) [cite: 64]
                st.rerun()

        if st.session_state.v_manifest:
            st.divider()
            st.markdown(f"### 📝 {{L['edit_m']}}")
            df_m = pd.DataFrame(st.session_state.v_manifest)
            res_edit = st.data_editor(df_m[['name', 'p_act']], column_config={"p_act": st.column_config.NumberColumn(L['qty'], min_value=0)}, use_container_width=True, num_rows="dynamic") [cite: 65]
            
            if st.button(L['update']):
                new_list = []
                for _, row in res_edit.iterrows():
                    if row['p_act'] > 0: [cite: 66]
                        orig = next((p for p in inventory if p['name'] == row['name']), None)
                        if orig:
                            u_entry = orig.copy(); u_entry['p_act'] = row['p_act']; [cite: 67]
                            new_list.append(u_entry) [cite: 68]
                st.session_state.v_manifest = new_list
                st.rerun()

        if st.button(L['purge']): st.session_state.v_manifest = []; st.rerun() [cite: 69]

    tab_planner, tab_db, tab_terminal = st.tabs([f"📊 {{L['title']}}", f"📦 {{L['inventory']}}", f"⚙️ {{L['logs']}}"])

    with tab_planner:
        if st.session_state.v_manifest:
            engine_input = []
            for entry in st.session_state.v_manifest:
                n_cases = math.ceil(entry['p_act'] / entry.get('itemsPerCase', 1))
                for _ in range(n_cases): engine_input.append(entry.copy()) [cite: 70]
            
            stacks, weight, failed, ldm = V24SupremeEngine.solve(engine_input, veh, x_shift)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric(L['cases'], len(engine_input))
            k2.metric(L['pcs'], sum(it['p_act'] for it in st.session_state.v_manifest))
            k3.metric(L['weight'], f"{{weight}} KG") [cite: 71]
            k4.metric(L['util'], f"{{(weight/veh['max_w'])*100:.1f}}%")

            st.markdown('<div class="v-tile-apex">', unsafe_allow_html=True)
            st.plotly_chart(render_vorteza_cad_3d(veh, stacks), use_container_width=True)
            process_load_bal_ui(veh, stacks, L)
            
            sku_agg = pd.Series([it['name'] for s in stacks for it in s['items']]).value_counts().reset_index()
            sku_agg.columns = [L['sku_ident'], 'CASES'] [cite: 72]
            h_table = f'<table class="v-table-tactical"><tr><th>SKU</th><th>{{L["cases"]}}</th></tr>'
            for _, r in sku_agg.iterrows():
                h_table += f'<tr><td><span style="color:{{get_vorteza_sku_hex(r[L["sku_ident"]])}}">■</span> {{r[L["sku_ident"]]}}</td><td>{{r["CASES"]}}</td></tr>'
            st.markdown(h_table + '</table>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.info(L['no_data'])

    with tab_db: [cite: 73]
        st.markdown(f"### 📦 {{L['inventory']}}")
        new_db = st.data_editor(pd.DataFrame(inventory), use_container_width=True, num_rows="dynamic")
        if st.button(L['save_db']): db_core_save(new_db.to_dict('records')); st.success(L['sync']) [cite: 74]

    with tab_terminal:
        st.code(f"SYSTEM: VORTEZA STACK v24.0\nTIME: {{datetime.now()}}\nLANG: {{st.session_state.lang}}", language="bash")

if __name__ == "__main__":
    run_stack()
