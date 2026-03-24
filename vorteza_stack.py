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
# 0. KONFIGURACJA ŚCIEŻEK (ZGODNIE Z HUBEM)
# ==============================================================================
PATH_DATA = os.path.join("data", "products.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")
PATH_LOGO = os.path.join("assets", "logo_vorteza.png")

# ==============================================================================
# 1. MULTILINGUAL ENGINE (V-LANG) - 4 JĘZYKI [cite: 75, 84]
# ==============================================================================
LANGUAGES = {
    "PL": {
        "title": "VORTEZA STACK", "fleet": "KONSOLA FLOTY", "unit": "JEDNOSTKA TRANSPORTOWA",
        "offset": "OFFSET OD ŚCIANY (cm)", "cargo": "WEJŚCIE ŁADUNKU", "sku_sel": "WYBÓR SKU",
        "qty": "ILOŚĆ (SZTUKI)", "add": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ DANE",
        "manifest": "MANIFEST ZAŁADUNKOWY", "edit_m": "EDYCJA MANIFESTU", "cases": "OPAKOWANIA",
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "WAGA BRUTTO", "util": "WYKORZYSTANIE",
        "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI", "no_data": "STATUS: OCZEKIWANIE NA DANE",
        "inventory": "BAZA SKU", "sync": "SYNCHRONIZACJA ZAKOŃCZONA", "save_db": "ZAPISZ BAZĘ",
        "pos": "POZYCJONOWANIE", "sku_ident": "IDENTYFIKATOR SKU"
    },
    "ENG": {
        "title": "VORTEZA STACK", "fleet": "FLEET CONSOLE", "unit": "TRANSPORT UNIT",
        "offset": "WALL OFFSET (cm)", "cargo": "CARGO ENTRY", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY (TOTAL PCS)", "add": "APPEND TO MANIFEST", "purge": "PURGE ALL DATA",
        "manifest": "LOAD MANIFEST", "edit_m": "EDIT MANIFEST", "cases": "CASES",
        "pcs": "TOTAL PCS", "weight": "GROSS WEIGHT", "util": "UTILIZATION",
        "cog": "CENTER OF GRAVITY ANALYSIS", "no_data": "STATUS: WAITING FOR DATA",
        "inventory": "MASTER INVENTORY", "sync": "SYNC COMPLETE", "save_db": "SAVE DATABASE",
        "pos": "DYNAMIC POSITIONING", "sku_ident": "SKU IDENTIFIER"
    },
    "ES": {
        "title": "VORTEZA STACK", "fleet": "CONSOLA DE FLOTA", "unit": "UNIDAD DE TRANSPORTE",
        "offset": "DESPLAZAMIENTO (cm)", "cargo": "ENTRADA DE CARGA", "sku_sel": "SELECTOR DE SKU",
        "qty": "CANTIDAD (PIEZAS)", "add": "AÑADIR AL MANIFIESTO", "purge": "LIMPIAR DATOS",
        "manifest": "MANIFIESTO DE CARGA", "edit_m": "EDITAR MANIFIESTO", "cases": "CAJAS",
        "pcs": "PIEZAS TOTALES", "weight": "PESO BRUTO", "util": "UTILIZACIÓN",
        "cog": "ANÁLISIS DEL CENTRO DE GRAVEDAD", "no_data": "ESTADO: ESPERANDO DATOS",
        "inventory": "INVENTARIO", "sync": "SINCRONIZACIÓN OK", "save_db": "GUARDAR BASE",
        "pos": "POSICIONAMIENTO", "sku_ident": "IDENTIFICADOR SKU"
    },
    "DE": {
        "title": "VORTEZA STACK", "fleet": "FLOTTENKONSOLE", "unit": "TRANSPORTEINHEIT",
        "offset": "WANDABSTAND (cm)", "cargo": "LADUNGSEINGABE", "sku_sel": "SKU-AUSWAHL",
        "qty": "MENGE (STÜCK)", "add": "ZUM MANIFEST HINZUFÜGEN", "purge": "DATEN LÖSCHEN",
        "manifest": "LADEMANIFEST", "edit_m": "MANIFEST BEARBEITEN", "cases": "KARTONS",
        "pcs": "STÜCK GESAMT", "weight": "BRUTTOGEWICHT", "util": "AUSLASTUNG",
        "cog": "SCHWERPUNKTSANALYSE", "no_data": "STATUS: WARTE AUF DATEN",
        "inventory": "INVENTAR", "sync": "SYNC ABGESCHLOSSEN", "save_db": "SPEICHERN",
        "pos": "POSITIONIERUNG", "sku_ident": "SKU-IDENTIFIKATOR"
    }
}

FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "axles": 3, "cab_l": 230},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "axles": 3, "cab_l": 230},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "axles": 2, "cab_l": 200},
    "BUS XL Express": {"max_w": 1300, "L": 485, "W": 175, "H": 220, "axles": 2, "cab_l": 140}
}

# ==============================================================================
# 2. BRANDING VORTEZA & UI ENGINE (NAPRAWIONA SKŁADNIA CSS) [cite: 88, 105]
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
                --v-neon-green: #00FF41;
            }}
            .v-tile-apex {{ background: var(--v-panel-bg); padding: 2rem; border-left: 10px solid var(--v-copper); margin-bottom: 2rem; border: 1px solid var(--v-border); }}
            .v-rail-track {{ width: 100%; height: 35px; background: #050505; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0; }}
            .v-cog-pointer {{ position: absolute; width: 10px; height: 70px; top: -17.5px; background: var(--v-neon-green); box-shadow: 0 0 30px var(--v-neon-green); border-radius: 5px; }}
            .v-table-tactical {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .v-table-tactical th {{ background: #000; color: var(--v-copper); padding: 15px; border-bottom: 2px solid #333; }}
            .v-table-tactical td {{ padding: 12px; border-bottom: 1px solid #111; color: #CCC; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. SILNIK GRAFICZNY I CAD-3D RENDERER [cite: 108, 113]
# ==============================================================================
def get_vorteza_sku_hex(sku_name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#16A085", "#27AE60", "#2980B9", "#E67E22", "#C0392B"]
    random.seed(sum(ord(c) for c in str(sku_name)))
    return random.choice(palette)

def build_box_cad_geometry(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    i_map, j_map, k_map = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i_map, j=j_map, k=k_map, color=color, opacity=0.99, name=name, flatshading=True)
    lx = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    ly = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    lz = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#151515', opacity=1, hoverinfo='skip'))
    axles = vehicle_specs.get('axles', 3)
    rear_base_x = L - 450 if L > 800 else L - 180
    for a in range(axles):
        ax_x = rear_base_x + (a * 145)
        if ax_x < L:
            for side in [-40, W+25]:
                fig.add_trace(go.Mesh3d(x=[ax_x-60, ax_x+60, ax_x+60, ax_x-60], y=[side, side, side+18, side+18], z=[-85, -85, -15, -15], color='#000', opacity=1))
    cab_l = vehicle_specs.get('cab_l', 230)
    fig.add_trace(go.Mesh3d(x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l], y=[-45, -45, W+45, W+45, -45, -45, W+45, W+45], z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#050505', opacity=1))
    skeleton_lines = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]), ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]), ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])]
    for lx, ly, lz in skeleton_lines: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            parts = build_box_cad_geometry(cluster['x'], cluster['y'], unit['z'], unit['w_fit'], unit['l_fit'], unit['height'], get_vorteza_sku_hex(unit['name']), unit['name'])
            for p in parts: fig.add_trace(p)
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0)), bgcolor='rgba(0,0,0,0)'), margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# ==============================================================================
# 4. SILNIK PAKOWANIA V24 SUPREME [cite: 114, 124]
# ==============================================================================
class V24SupremeEngine:
    @staticmethod
    def solve(cargo_list, vehicle, x_offset=0):
        items_sorted = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        placed_stacks, failed_units, total_weight = [], [], 0
        cx, cy, current_row_max_w = x_offset, 0, 0
        for unit in items_sorted:
            if total_weight + unit['weight'] > vehicle['max_w']:
                failed_units.append(unit)
                continue
            is_stacked = False
            if unit.get('canStack', True):
                for s in placed_stacks:
                    orient = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
                    if any(fw <= s['w'] and fl <= s['l'] for fw, fl in orient) and (s['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy()
                        u_copy['z'] = s['curH']
                        u_copy['w_fit'], u_copy['l_fit'] = s['w'], s['l']
                        s['items'].append(u_copy)
                        s['curH'] += unit['height']
                        total_weight += unit['weight']
                        is_stacked = True
                        break
            if is_stacked: continue
            is_placed, orientations = False, [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl; placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; current_row_max_w = max(current_row_max_w, fw); total_weight += unit['weight']; is_placed = True; break
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw; u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl; placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]}); cy += fl; total_weight += unit['weight']; is_placed = True; break
            if not is_placed: failed_units.append(unit)
        ldm_res = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, total_weight, failed_units, ldm_res

# ==============================================================================
# 5. DATA I/O LOKALNE [cite: 125, 127]
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
# 6. FUNKCJA URUCHOMIENIOWA (MODUŁ HUB) [cite: 128, 144]
# ==============================================================================
def run_stack():
    inject_vorteza_stack_ui()
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    L = LANGUAGES[st.session_state.lang]
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_core_load()

    with st.sidebar:
        st.session_state.lang = st.selectbox("🌐 LANGUAGE", ["PL", "ENG", "ES", "DE"], index=["PL", "ENG", "ES", "DE"].index(st.session_state.lang))
        L = LANGUAGES[st.session_state.lang]
        st.markdown(f"### 📡 {{L['fleet']}}")
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
                    if item['name'] == sel_sku:
                        item['p_act'] += p_qty
                        found = True; break
                if not found:
                    u_entry = p_ref.copy(); u_entry['p_act'] = p_qty; st.session_state.v_manifest.append(u_entry)
                st.rerun()
        if st.button(L['purge']): st.session_state.v_manifest = []; st.rerun()

    tab_planner, tab_db = st.tabs([f"📊 {{L['title']}}", f"📦 {{L['inventory']}}"])

    with tab_planner:
        if st.session_state.v_manifest:
            engine_input = []
            for entry in st.session_state.v_manifest:
                n_cases = math.ceil(entry['p_act'] / entry.get('itemsPerCase', 1))
                for _ in range(n_cases): engine_input.append(entry.copy())
            stacks, weight, failed, ldm = V24SupremeEngine.solve(engine_input, veh, x_shift)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric(L['cases'], len(engine_input)); k2.metric(L['pcs'], sum(it['p_act'] for it in st.session_state.v_manifest))
            k3.metric(L['weight'], f"{{weight}} KG"); k4.metric(L['util'], f"{{(weight/veh['max_w'])*100:.1f}}%")
            
            st.markdown('<div class="v-tile-apex">', unsafe_allow_html=True)
            st.plotly_chart(render_vorteza_cad_3d(veh, stacks), use_container_width=True)
            # Analiza środka ciężkości (CoG)
            if weight > 0:
                cog_p = (sum(((s['x'] + it['w_fit']/2) * it['weight']) for s in stacks for it in s['items']) / weight / veh['L']) * 100
                marker_clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
                st.markdown(f'<div class="v-rail-track"><div class="v-cog-pointer" style="left: {{cog_p}}%; background: {{marker_clr}};"></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.info(L['no_data'])

    with tab_db:
        st.markdown(f"### 📦 {{L['inventory']}}")
        new_db = st.data_editor(pd.DataFrame(inventory), use_container_width=True, num_rows="dynamic")
        if st.button(L['save_db']): db_core_save(new_db.to_dict('records')); st.success(L['sync'])

if __name__ == "__main__":
    run_stack()
