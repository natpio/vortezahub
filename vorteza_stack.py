# -*- coding: utf-8 -*-
import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random
import base64
import os
from datetime import datetime

# --- 1. KONFIGURACJA ŚCIEŻEK ---
PATH_DATA = os.path.join("data", "products.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")
PATH_LOGO = os.path.join("assets", "logo_vorteza.png")

# --- 2. MULTILINGUAL ENGINE (V-LANG) ---
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
        "mission_data": "OCZEKIWANIE NA DANE MISJI", "pos": "POZYCJONOWANIE"
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
        "mission_data": "WAITING FOR MISSION DATA", "pos": "DYNAMIC POSITIONING"
    }
}

FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 230},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 230},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ldm_max": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "cab_l": 200},
    "BUS XL Express": {"max_w": 1300, "L": 485, "W": 175, "H": 220, "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140}
}

# --- 3. POMOCNICZE ---
def load_vorteza_asset_b64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f: return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def get_vorteza_sku_hex(sku_name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#16A085", "#27AE60", "#2980B9", "#E67E22", "#C0392B"]
    random.seed(sum(ord(c) for c in str(sku_name)))
    return random.choice(palette)

def db_core_load():
    if os.path.exists(PATH_DATA):
        try:
            with open(PATH_DATA, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def db_core_save(data):
    with open(PATH_DATA, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

# --- 4. SILNIK GRAFICZNY CAD-3D ---
def build_box_cad_geometry(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    i_map, j_map, k_map = [7,0,0,0,4,4,6,6,4,0,3,2], [3,4,1,2,5,6,5,2,0,1,6,3], [0,7,2,3,6,7,1,1,5,5,7,6]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i_map, j=j_map, k=k_map, color=color, opacity=0.9, name=name, flatshading=True)
    lx = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    ly = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    lz = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=2), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']
    # Podłoga
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-5, -5, -5, -5], color='#111', opacity=1))
    # Rama kabiny i paki
    skeleton = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]), ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])]
    for lx, ly, lz in skeleton: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=4), hoverinfo='skip'))
    # Ładunek
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            parts = build_box_cad_geometry(cluster['x'], cluster['y'], unit['z'], unit['w_fit'], unit['l_fit'], unit['height'], get_vorteza_sku_hex(unit['name']), unit['name'])
            for p in parts: fig.add_trace(p)
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor='rgba(0,0,0,0)'), margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# --- 5. SILNIK PAKOWANIA ---
class V24SupremeEngine:
    @staticmethod
    def solve(cargo_list, vehicle, x_offset=0):
        items_sorted = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        placed_stacks, failed_units, total_weight = [], [], 0
        cx, cy, current_row_max_w = x_offset, 0, 0
        for unit in items_sorted:
            if total_weight + unit['weight'] > vehicle['max_w']: failed_units.append(unit); continue
            is_stacked = False
            for s in placed_stacks:
                if unit.get('canStack', True) and unit['width'] <= s['w'] and unit['length'] <= s['l'] and (s['curH'] + unit['height'] <= vehicle['H']):
                    u_c = unit.copy(); u_c['z'] = s['curH']; u_c['w_fit'], u_c['l_fit'] = s['w'], s['l']
                    s['items'].append(u_c); s['curH'] += unit['height']; total_weight += unit['weight']; is_stacked = True; break
            if is_stacked: continue
            fw, fl = unit['width'], unit['length']
            if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                cy += fl; current_row_max_w = max(current_row_max_w, fw); total_weight += unit['weight']
            elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                cx += current_row_max_w; cy = 0; current_row_max_w = fw
                u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                cy += fl; total_weight += unit['weight']
            else: failed_units.append(unit)
        return placed_stacks, total_weight, failed_units

# --- 6. FUNKCJA URUCHOMIENIOWA (DLA HUB) ---
def run_stack():
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    L = LANGUAGES[st.session_state.lang]
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_core_load()

    # Sidebar operacyjny
    with st.sidebar:
        st.markdown(f"### 📡 {L['fleet']}")
        v_key = st.selectbox(L['unit'], list(FLEET_MASTER_DATA.keys()))
        veh = FLEET_MASTER_DATA[v_key]
        x_shift = st.slider(L['offset'], 0, veh['L']-200, 0)
        st.divider()
        sel_sku = st.selectbox(L['sku_sel'], [p['name'] for p in inventory], index=None)
        if sel_sku:
            p_ref = next(p for p in inventory if p['name'] == sel_sku)
            p_qty = st.number_input(L['qty'], min_value=1, value=int(p_ref.get('itemsPerCase', 1)))
            if st.button(L['add']):
                found = False
                for item in st.session_state.v_manifest:
                    if item['name'] == sel_sku: item['p_act'] += p_qty; found = True; break
                if not found:
                    u_entry = p_ref.copy(); u_entry['p_act'] = p_qty; st.session_state.v_manifest.append(u_entry)
                st.rerun()
        if st.button(L['purge']): st.session_state.v_manifest = []; st.rerun()

    tab_planner, tab_db = st.tabs([f"📊 {L['title']}", f"📦 {L['inventory']}"])

    with tab_planner:
        if st.session_state.v_manifest:
            engine_in = []
            for e in st.session_state.v_manifest:
                for _ in range(math.ceil(e['p_act'] / e.get('itemsPerCase', 1))): engine_in.append(e.copy())
            stacks, weight, failed = V24SupremeEngine.solve(engine_in, veh, x_shift)
            
            k1, k2, k3 = st.columns(3)
            k1.metric(L['pcs'], sum(it['p_act'] for it in st.session_state.v_manifest))
            k2.metric(L['weight'], f"{weight} KG")
            k3.metric(L['util'], f"{(weight/veh['max_w'])*100:.1f}%")

            st.plotly_chart(render_vorteza_cad_3d(veh, stacks), use_container_width=True)
        else: st.info(L['no_data'])

    with tab_db:
        new_db = st.data_editor(pd.DataFrame(inventory), use_container_width=True, num_rows="dynamic")
        if st.button(L['save_db']): db_core_save(new_db.to_dict('records')); st.success(L['sync'])
