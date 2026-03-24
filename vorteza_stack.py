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
# 0. KONFIGURACJA ŚCIEŻEK
# ==============================================================================
PATH_DATA = os.path.join("data", "products.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")

# ==============================================================================
# 1. MULTILINGUAL ENGINE (V-LANG)
# ==============================================================================
LANGUAGES = {
    "PL": {
        "title": "VORTEZA STACK", "fleet": "KONSOLA FLOTY", "unit": "JEDNOSTKA TRANSPORTOWA",
        "offset": "OFFSET OD ŚCIANY (cm)", "cargo": "WEJŚCIE ŁADUNKU", "sku_sel": "WYBÓR SKU",
        "qty": "ILOŚĆ (SZTUKI)", "add": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ DANE",
        "manifest": "MANIFEST ZAŁADUNKOWY", "pcs": "SZTUKI ŁĄCZNIE", "weight": "WAGA BRUTTO", 
        "util": "WYKORZYSTANIE", "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI", "no_data": "STATUS: OCZEKIWANIE NA DANE",
        "inventory": "BAZA SKU", "save_db": "ZAPISZ BAZĘ SKU", "sync": "SYNCHRONIZACJA OK",
        "cases": "OPAKOWANIA", "sku_ident": "IDENTYFIKATOR SKU"
    },
    "ENG": {
        "title": "VORTEZA STACK", "fleet": "FLEET CONSOLE", "unit": "TRANSPORT UNIT",
        "offset": "WALL OFFSET (cm)", "cargo": "CARGO ENTRY", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY (PCS)", "add": "ADD TO MANIFEST", "purge": "PURGE DATA",
        "manifest": "LOAD MANIFEST", "pcs": "TOTAL PCS", "weight": "GROSS WEIGHT", 
        "util": "UTILIZATION", "cog": "CENTER OF GRAVITY", "no_data": "STATUS: WAITING FOR DATA",
        "inventory": "MASTER INVENTORY", "save_db": "SAVE DATABASE", "sync": "SYNC OK",
        "cases": "CASES", "sku_ident": "SKU IDENTIFIER"
    }
}

FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "axles": 3, "cab_l": 250},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "axles": 3, "cab_l": 250},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "axles": 2, "cab_l": 200},
    "BUS XL Express": {"max_w": 1300, "L": 485, "W": 175, "H": 220, "axles": 2, "cab_l": 150}
}

# ==============================================================================
# 2. BRANDING & UI ENGINE
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
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=JetBrains+Mono&display=swap');
            .stApp {{
                background-image: url("data:image/png;base64,{bg_data}");
                background-size: cover; background-attachment: fixed;
            }}
            .v-tile-apex {{ 
                background: rgba(6, 6, 6, 0.98); padding: 2rem; border-left: 10px solid #B58863; 
                box-shadow: 0 20px 50px rgba(0,0,0,0.5); margin-bottom: 2rem; 
            }}
            .v-table-tactical {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .v-table-tactical th {{ background: #000; color: #B58863; padding: 15px; text-align: left; border-bottom: 2px solid #333; }}
            .v-table-tactical td {{ padding: 12px 15px; border-bottom: 1px solid #111; color: #CCC; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. SILNIK GRAFICZNY I PAKOWANIA
# ==============================================================================
def get_vorteza_sku_hex(sku_name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#16A085", "#27AE60", "#2980B9", "#E67E22", "#C0392B"]
    random.seed(sum(ord(c) for c in str(sku_name)))
    return random.choice(palette)

def build_box_cad_geometry(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    i, j, k = [7,0,0,0,4,4,6,6,4,0,3,2], [3,4,1,2,5,6,5,2,0,1,6,3], [0,7,2,3,6,7,1,1,5,5,7,6]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, color=color, opacity=0.9, name=name, flatshading=True)
    lx = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    ly = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    lz = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=2), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']
    cab_l = vehicle_specs.get('cab_l', 200)
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-2, -2, -2, -2], color='#111', opacity=1, hoverinfo='skip'))
    fig.add_trace(go.Mesh3d(x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l], y=[-10, -10, W+10, W+10, -10, -10, W+10, W+10], z=[0, 0, 0, 0, H*0.8, H*0.8, H*0.8, H*0.8], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#050505', opacity=1))
    skel = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]), ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])]
    for lx, ly, lz in skel: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=5), hoverinfo='skip'))
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            parts = build_box_cad_geometry(cluster['x'], cluster['y'], unit['z'], unit['w_fit'], unit['l_fit'], unit['height'], get_vorteza_sku_hex(unit['name']), unit['name'])
            for p in parts: fig.add_trace(p)
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor='rgba(0,0,0,0)'), margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

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
                u_c = unit.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = 0, fw, fl
                placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; row_max_w = max(row_max_w, fw); total_weight += unit['weight']
            elif cx + row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                cx += row_max_w; cy = 0; row_max_w = fw; u_c = unit.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = 0, fw, fl
                placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; total_weight += unit['weight']
            else: failed_units.append(unit)
        return placed_stacks, total_weight, failed_units

# ==============================================================================
# 4. GŁÓWNA FUNKCJA URUCHOMIENIOWA (MODUŁ HUB)
# ==============================================================================
def run_stack():
    inject_vorteza_stack_ui()
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    L = LANGUAGES[st.session_state.lang]
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []

    if os.path.exists(PATH_DATA):
        with open(PATH_DATA, 'r', encoding='utf-8') as f: inventory = json.load(f)
    else: inventory = []

    with st.sidebar:
        st.markdown(f"### 📡 {L['fleet']}")
        v_key = st.selectbox(L['unit'], list(FLEET_MASTER_DATA.keys()))
        veh = FLEET_MASTER_DATA[v_key]
        x_shift = st.slider(L['offset'], 0, veh['L']-200, 0)
        st.divider()
        st.markdown(f"### 📥 {L['cargo']}")
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
        if st.button(L['purge']): st.session_state.v_manifest = []; st.rerun()

    st.markdown(f"<h2 style='color:#B58863;'>{L['title']}</h2>", unsafe_allow_html=True)
    tab_planner, tab_db = st.tabs([f"📊 {L['manifest']}", f"📦 {L['inventory']}"])

    with tab_planner:
        if st.session_state.v_manifest:
            engine_in = []
            for e in st.session_state.v_manifest:
                n_c = math.ceil(e['p_act'] / e.get('itemsPerCase', 1))
                for _ in range(n_c): engine_in.append(e.copy())
            stacks, weight, failed = V24SupremeEngine.solve(engine_in, veh, x_shift)
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric(L['cases'], len(engine_in))
            k2.metric(L['pcs'], sum(it['p_act'] for it in st.session_state.v_manifest))
            k3.metric(L['weight'], f"{weight} KG")
            util = (weight/veh['max_w'])*100
            k4.metric(L['util'], f"{util:.1f}%")
            
            st.plotly_chart(render_vorteza_cad_3d(veh, stacks), use_container_width=True)
            
            if weight > 0:
                t_mom = sum((s['x'] + it['w_fit']/2) * it['weight'] for s in stacks for it in s['items'])
                cog_p = (t_mom / weight / veh['L']) * 100
                clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
                st.markdown(f'<div style="width:100%; height:20px; background:#111; border-radius:10px; position:relative; margin:20px 0;"><div style="position:absolute; width:10px; height:40px; top:-10px; left:{cog_p}%; background:{clr}; box-shadow:0 0 15px {clr}; border-radius:5px;"></div></div>', unsafe_allow_html=True)
        else: st.info(L['no_data'])

    with tab_db:
        st.markdown(f"### 📦 {L['inventory']}")
        new_db = st.data_editor(pd.DataFrame(inventory), use_container_width=True, num_rows="dynamic")
        if st.button(L['save_db']):
            with open(PATH_DATA, 'w', encoding='utf-8') as f:
                json.dump(new_db.to_dict('records'), f, indent=4, ensure_ascii=False)
            st.success(L['sync'])

if __name__ == "__main__": run_stack()
