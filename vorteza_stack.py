# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 24.0 | APEX ULTIMATE PLUS
MODUŁ: ZINTEGROWANY Z HUBEM (vorteza_hub)
================================================================================
"""

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
# KONFIGURACJA ŚCIEŻEK (ZGODNIE Z NOWĄ STRUKTURĄ)
# ==============================================================================
PATH_DATA = os.path.join("data", "products.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")
PATH_LOGO = os.path.join("assets", "logo_vorteza.png")

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
    },
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
    }
}

FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 230},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 230},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ldm_max": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "cab_l": 200},
    "Solo 7m Medium": {"max_w": 7000, "L": 720, "W": 245, "H": 260, "ldm_max": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200, "cab_l": 180},
    "BUS XL Express": {"max_w": 1300, "L": 485, "W": 175, "H": 220, "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140}
}

# ==============================================================================
# 2. BRANDING VORTEZA & UI ENGINE
# ==============================================================================
def load_vorteza_asset_b64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def inject_vorteza_stack_ui():
    bg_data = load_vorteza_asset_b64(PATH_BG)
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            :root {{
                --v-copper: #B58863;
                --v-panel-bg: rgba(6, 6, 6, 0.98);
                --v-border: rgba(181, 136, 99, 0.2);
            }}
            .stApp {{ background-image: url("data:image/png;base64,{bg_data}"); background-size: cover; background-attachment: fixed; color: #FFFFFF; font-family: 'Montserrat', sans-serif; }}
            .v-tile-apex {{ background: var(--v-panel-bg); padding: 3rem; border: 1px solid var(--v-border); border-left: 15px solid var(--v-copper); box-shadow: 0 50px 120px rgba(0,0,0,1); margin-bottom: 3.5rem; backdrop-filter: blur(50px); }}
            .v-table-tactical {{ width: 100%; border-collapse: collapse; margin-top: 40px; border: 1px solid #111; }}
            .v-table-tactical th {{ background: #000; color: var(--v-copper); padding: 25px; border-bottom: 3px solid #333; letter-spacing: 3px; }}
            .v-table-tactical td {{ padding: 20px 25px; border-bottom: 1px solid #111; color: #CCC; }}
            .v-rail-track {{ width: 100%; height: 35px; background: #050505; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0; }}
            .v-cog-pointer {{ position: absolute; width: 10px; height: 70px; top: -17.5px; background: #00FF41; border-radius: 5px; }}
            .v-badge-unit {{ background: rgba(181,136,99,0.1); border: 1px solid var(--v-copper); padding: 20px; font-family: 'JetBrains Mono', monospace; color: var(--v-copper); }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. SILNIK GRAFICZNY I ANALITYKA
# ==============================================================================
def get_vorteza_sku_hex(sku_name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#16A085", "#27AE60", "#2980B9", "#E67E22", "#C0392B"]
    random.seed(sum(ord(c) for c in str(sku_name)))
    return random.choice(palette)

def build_box_cad_geometry(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    i_map, j_map, k_map = [7,0,0,0,4,4,6,6,4,0,3,2], [3,4,1,2,5,6,5,2,0,1,6,3], [0,7,2,3,6,7,1,1,5,5,7,6]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i_map, j=j_map, k=k_map, color=color, opacity=0.99, name=name, flatshading=True)
    lx, ly, lz = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x], [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y], [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#151515', opacity=1, hoverinfo='skip'))
    for a in range(vehicle_specs.get('axles', 3)):
        ax_x = (L - 450 if L > 800 else L - 180) + (a * 145)
        if ax_x < L:
            for side in [-40, W+25]:
                fig.add_trace(go.Mesh3d(x=[ax_x-60, ax_x+60, ax_x+60, ax_x-60], y=[side, side, side+18, side+18], z=[-85, -85, -15, -15], color='#000', opacity=1, hoverinfo='skip'))
    for cluster in cargo_stacks:
        for u in cluster['items']:
            parts = build_box_cad_geometry(cluster['x'], cluster['y'], u['z'], u['w_fit'], u['l_fit'], u['height'], get_vorteza_sku_hex(u['name']), u['name'])
            for p in parts: fig.add_trace(p)
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# ==============================================================================
# 5. SILNIK PAKOWANIA V24
# ==============================================================================
class V24SupremeEngine:
    @staticmethod
    def solve(cargo_list, vehicle, x_offset=0):
        items_sorted = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        placed_stacks, failed_units, total_weight = [], [], 0
        cx, cy, row_max_w = x_offset, 0, 0
        for unit in items_sorted:
            if total_weight + unit['weight'] > vehicle['max_w']: failed_units.append(unit); continue
            is_placed = False
            for s in placed_stacks:
                if unit.get('canStack', True) and unit['width'] <= s['w'] and unit['length'] <= s['l'] and (s['curH'] + unit['height'] <= vehicle['H']):
                    u_c = unit.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = s['curH'], s['w'], s['l']
                    s['items'].append(u_c); s['curH'] += unit['height']; total_weight += unit['weight']; is_placed = True; break
            if not is_placed:
                fw, fl = unit['width'], unit['length']
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = 0, fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; row_max_w = max(row_max_w, fw); total_weight += unit['weight']; is_placed = True
                elif cx + row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += row_max_w; cy = 0; row_max_w = fw
                    u_c = unit.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = 0, fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; total_weight += unit['weight']; is_placed = True
            if not is_placed: failed_units.append(unit)
        ldm = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, total_weight, failed_units, ldm

def db_core_load():
    if os.path.exists(PATH_DATA):
        try:
            with open(PATH_DATA, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def db_core_save(data):
    with open(PATH_DATA, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 7. FUNKCJA URUCHOMIENIOWA (MODUŁ HUB)
# ==============================================================================
def run_stack():
    inject_vorteza_stack_ui()
    
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    L = LANGUAGES[st.session_state.lang]
    
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_core_load()

    # HEADER
    hc1, hc2 = st.columns([1, 4])
    with hc1:
        logo_b64 = load_vorteza_asset_b64(PATH_LOGO)
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="180">', unsafe_allow_html=True)
    with hc2:
        st.markdown(f"<h1>{L['title']}</h1>", unsafe_allow_html=True)

    with st.sidebar:
        st.session_state.lang = st.selectbox("🌐 LANGUAGE", ["PL", "ENG"], index=0 if st.session_state.lang=="PL" else 1)
        L = LANGUAGES[st.session_state.lang]
        
        st.markdown(f"### 📡 {L['fleet']}")
        v_key = st.selectbox(L['unit'], list(FLEET_MASTER_DATA.keys()))
        veh = FLEET_MASTER_DATA[v_key]
        
        st.divider()
        x_shift = st.slider(L['offset'], 0, veh['L']-200, 0)
        
        st.divider()
        sel_sku_name = st.selectbox(L['sku_sel'], [p['name'] for p in inventory], index=None)
        if sel_sku_name:
            p_ref = next(p for p in inventory if p['name'] == sel_sku_name)
            p_qty = st.number_input(L['qty'], min_value=1, value=int(p_ref.get('itemsPerCase', 1)))
            if st.button(L['add']):
                found = False
                for item in st.session_state.v_manifest:
                    if item['name'] == sel_sku_name: item['p_act'] += p_qty; found = True; break
                if not found:
                    u_e = p_ref.copy(); u_e['p_act'] = p_qty; st.session_state.v_manifest.append(u_e)
                st.rerun()

        if st.session_state.v_manifest:
            if st.button(L['purge']): st.session_state.v_manifest = []; st.rerun()

    # TABS
    tab_planner, tab_db = st.tabs([f"📊 {L['title']}", f"📦 {L['inventory']}"])

    with tab_planner:
        if st.session_state.v_manifest:
            engine_input = []
            for entry in st.session_state.v_manifest:
                for _ in range(math.ceil(entry['p_act'] / entry.get('itemsPerCase', 1))): engine_input.append(entry.copy())
            
            stacks, weight, failed, ldm = V24SupremeEngine.solve(engine_input, veh, x_shift)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric(L['cases'], len(engine_input)); k2.metric(L['pcs'], sum(it['p_act'] for it in st.session_state.v_manifest))
            k3.metric(L['weight'], f"{weight} KG"); k4.metric(L['util'], f"{(weight/veh['max_w'])*100:.1f}%")

            st.markdown('<div class="v-tile-apex">', unsafe_allow_html=True)
            st.plotly_chart(render_vorteza_cad_3d(veh, stacks), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.info(L['no_data'])

    with tab_db:
        st.markdown(f"### 📦 {L['inventory']}")
        new_db = st.data_editor(pd.DataFrame(inventory), use_container_width=True, num_rows="dynamic")
        if st.button(L['save_db']): db_core_save(new_db.to_dict('records')); st.success(L['sync'])

if __name__ == "__main__":
    run_stack()
