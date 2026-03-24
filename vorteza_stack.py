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

# ==============================================================================
# 0. KONFIGURACJA ŚCIEŻEK (ZGODNIE Z NOWĄ STRUKTURĄ)
# ==============================================================================
PATH_DATA = os.path.join("data", "products.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")
PATH_LOGO = os.path.join("assets", "logo_vorteza.png")

# ==============================================================================
# 1. REJESTR INŻYNIERYJNY FLOTY
# ==============================================================================
FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 230
    },
    "TIR FTL Standard 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 230
    },
    "Solo 9m Heavy Duty": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_max": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "cab_l": 200
    },
    "Solo 7m Medium": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_max": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200, "cab_l": 180
    },
    "BUS XL Express": {
        "max_w": 1300, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140
    }
}

LANGUAGES = {
    "PL": {
        "title": "VORTEZA STACK", "fleet": "KONSOLA FLOTY", "unit": "JEDNOSTKA TRANSPORTOWA",
        "offset": "OFFSET OD ŚCIANY (cm)", "cargo": "WEJŚCIE ŁADUNKU", "sku_sel": "WYBÓR SKU",
        "qty": "ILOŚĆ (SZTUKI)", "add": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ DANE",
        "manifest": "MANIFEST ZAŁADUNKOWY", "edit_m": "EDYCJA MANIFESTU", "cases": "OPAKOWANIA",
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "WAGA BRUTTO", "util": "WYKORZYSTANIE",
        "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI", "bal_front": "ALARM: PRZECIĄŻENIE PRZODU",
        "bal_rear": "ALARM: ODCIĄŻENIE OSI SKRĘTNEJ", "bal_ok": "STATUS NOMINALNY: Balans optymalny",
        "no_data": "STATUS: OCZEKIWANIE NA DANE", "inventory": "BAZA SKU", "pos": "POZYCJONOWANIE",
        "save_db": "ZAPISZ BAZĘ SKU", "sync": "SYNCHRONIZACJA ZAKOŃCZONA", "update": "AKTUALIZUJ"
    },
    "ENG": {
        "title": "VORTEZA STACK", "fleet": "FLEET CONSOLE", "unit": "TRANSPORT UNIT",
        "offset": "WALL OFFSET (cm)", "cargo": "CARGO ENTRY", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY (TOTAL PCS)", "add": "APPEND TO MANIFEST", "purge": "PURGE ALL DATA",
        "manifest": "LOAD MANIFEST", "edit_m": "EDIT MANIFEST", "cases": "CASES",
        "pcs": "TOTAL PCS", "weight": "GROSS WEIGHT", "util": "UTILIZATION",
        "cog": "CENTER OF GRAVITY ANALYSIS", "bal_front": "ALARM: FRONT OVERLOAD",
        "bal_rear": "ALARM: STEERING AXLE UNLOADED", "bal_ok": "NOMINAL STATUS: Optimal Balance",
        "no_data": "STATUS: WAITING FOR DATA", "inventory": "MASTER INVENTORY", "pos": "DYNAMIC POSITIONING",
        "save_db": "SAVE SKU DATABASE", "sync": "SYNC COMPLETE", "update": "UPDATE"
    }
}

# ==============================================================================
# 2. UI ENGINE & ASSETS
# ==============================================================================
def load_vorteza_asset_b64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f: return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def inject_vorteza_stack_ui():
    bg_data = load_vorteza_asset_b64(PATH_BG)
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=JetBrains+Mono&display=swap');
            .v-tile-apex {{ background: rgba(6, 6, 6, 0.98); padding: 2rem; border-left: 10px solid #B58863; box-shadow: 0 20px 50px rgba(0,0,0,0.5); margin-bottom: 2rem; }}
            .v-rail-track {{ width: 100%; height: 25px; background: #050505; border-radius: 12px; position: relative; border: 2px solid #222; margin: 40px 0; }}
            .v-cog-pointer {{ position: absolute; width: 8px; height: 50px; top: -12.5px; border-radius: 4px; transition: left 1s ease-in-out; }}
            .v-table-tactical {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .v-table-tactical th {{ background: #000; color: #B58863; padding: 15px; text-align: left; border-bottom: 2px solid #333; }}
            .v-table-tactical td {{ padding: 12px 15px; border-bottom: 1px solid #111; color: #CCC; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. SILNIK GRAFICZNY CAD-3D
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
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i_map, j=j_map, k=k_map, color=color, opacity=0.9, name=name, flatshading=True)
    lx = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    ly = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    lz = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=2), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']
    # Podłoga i koła
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-10, -10, -10, -10], color='#111', opacity=1, hoverinfo='skip'))
    axles = vehicle_specs.get('axles', 3)
    rear_x = L - 400
    for a in range(axles):
        ax_x = rear_x + (a * 130)
        for side in [-30, W+15]:
            fig.add_trace(go.Mesh3d(x=[ax_x-50, ax_x+50, ax_x+50, ax_x-50], y=[side, side, side+15, side+15], z=[-70, -70, -10, -10], color='#000', opacity=1))
    
    # Kabina
    cab_l = vehicle_specs.get('cab_l', 200)
    fig.add_trace(go.Mesh3d(x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l], y=[-20, -20, W+20, W+20, -20, -20, W+20, W+20], z=[0, 0, 0, 0, H, H, H, H], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#050505', opacity=1))
    
    # Szkielet paki
    skel = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]), ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])]
    for lx, ly, lz in skel: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=6), hoverinfo='skip'))
    
    # Ładunek
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            parts = build_box_cad_geometry(cluster['x'], cluster['y'], unit['z'], unit['w_fit'], unit['l_fit'], unit['height'], get_vorteza_sku_hex(unit['name']), unit['name'])
            for p in parts: fig.add_trace(p)
    
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor='rgba(0,0,0,0)'), margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# ==============================================================================
# 4. SILNIK PAKOWANIA V24 SUPREME
# ==============================================================================
class V24SupremeEngine:
    @staticmethod
    def solve(cargo_list, vehicle, x_offset=0):
        items_sorted = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        placed_stacks, failed_units, total_weight = [], [], 0
        cx, cy, row_max_w = x_offset, 0, 0
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
                u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl; placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; row_max_w = max(row_max_w, fw); total_weight += unit['weight']
            elif cx + row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                cx += row_max_w; cy = 0; row_max_w = fw; u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl; placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; total_weight += unit['weight']
            else: failed_units.append(unit)
        return placed_stacks, total_weight, failed_units

# ==============================================================================
# 5. DATA I/O LOKALNE
# ==============================================================================
def db_core_load():
    if os.path.exists(PATH_DATA):
        try:
            with open(PATH_DATA, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def db_core_save(data):
    with open(PATH_DATA, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 6. GŁÓWNA FUNKCJA URUCHOMIENIOWA (DLA HUB)
# ==============================================================================
def run_stack():
    inject_vorteza_stack_ui()
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    L = LANGUAGES[st.session_state.lang]
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_core_load()

    with st.sidebar:
        st.session_state.lang = st.selectbox("🌐 LANGUAGE", ["PL", "ENG"], index=0 if st.session_state.lang=="PL" else 1)
        L = LANGUAGES[st.session_state.lang]
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
                    u_e = p_ref.copy(); u_e['p_act'] = p_qty; st.session_state.v_manifest.append(u_e)
                st.rerun()
        if st.session_state.v_manifest:
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
            
            st.markdown('<div class="v-tile-apex">', unsafe_allow_html=True)
            st.plotly_chart(render_vorteza_cad_3d(veh, stacks), use_container_width=True)
            # Cog Analysis
            if weight > 0:
                t_mom = sum((s['x'] + it['w_fit']/2) * it['weight'] for s in stacks for it in s['items'])
                cog_p = (t_mom / weight / veh['L']) * 100
                clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
                st.markdown(f'<div class="v-rail-track"><div class="v-cog-pointer" style="left: {cog_p}%; background: {clr}; box-shadow: 0 0 30px {clr};"></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.info(L['no_data'])

    with tab_db:
        st.markdown(f"### 📦 {L['inventory']}")
        new_db = st.data_editor(pd.DataFrame(inventory), use_container_width=True, num_rows="dynamic")
        if st.button(L['save_db']): db_core_save(new_db.to_dict('records')); st.success(L['sync'])

if __name__ == "__main__":
    run_stack()
