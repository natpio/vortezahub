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
# 0. KONFIGURACJA I ZASOBY [cite: 4, 13]
# ==============================================================================
PATH_DATA = os.path.join("data", "products.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")

LANGUAGES = {
    "PL": {
        "title": "VORTEZA STACK", "fleet": "KONSOLA FLOTY", "unit": "JEDNOSTKA TRANSPORTOWA",
        "offset": "OFFSET OD ŚCIANY (cm)", "cargo": "WEJŚCIE ŁADUNKU", "sku_sel": "WYBÓR SKU",
        "qty": "ILOŚĆ (SZTUKI)", "add": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ DANE",
        "manifest": "MANIFEST ZAŁADUNKOWY", "edit_m": "EDYCJA MANIFESTU", "cases": "OPAKOWANIA",
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "WAGA BRUTTO", "util": "WYKORZYSTANIE",
        "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI", "no_data": "STATUS: OCZEKIWANIE NA DANE",
        "inventory": "BAZA SKU", "save_db": "ZAPISZ BAZĘ SKU", "sync": "SYNCHRONIZACJA OK",
        "update": "AKTUALIZUJ MANIFEST", "sku_ident": "IDENTYFIKATOR SKU"
    },
    "ENG": {
        "title": "VORTEZA STACK", "fleet": "FLEET CONSOLE", "unit": "TRANSPORT UNIT",
        "offset": "WALL OFFSET (cm)", "cargo": "CARGO ENTRY", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY (PCS)", "add": "ADD TO MANIFEST", "purge": "PURGE DATA",
        "manifest": "LOAD MANIFEST", "edit_m": "EDIT MANIFEST", "cases": "CASES",
        "pcs": "TOTAL PCS", "weight": "GROSS WEIGHT", "util": "UTILIZATION",
        "cog": "CENTER OF GRAVITY", "no_data": "STATUS: WAITING FOR DATA",
        "inventory": "MASTER INVENTORY", "save_db": "SAVE DATABASE", "sync": "SYNC OK",
        "update": "UPDATE MANIFEST", "sku_ident": "SKU IDENTIFIER"
    }
}

FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "axles": 3, "cab_l": 250},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "axles": 3, "cab_l": 250},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "axles": 2, "cab_l": 200},
    "BUS XL Express": {"max_w": 1300, "L": 485, "W": 175, "H": 220, "axles": 2, "cab_l": 150}
} [cite: 13, 14, 15]

# ==============================================================================
# 1. UI ENGINE [cite: 16, 17]
# ==============================================================================
def inject_vorteza_stack_ui():
    bg_data = ""
    if os.path.exists(PATH_BG):
        with open(PATH_BG, 'rb') as f: bg_data = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=JetBrains+Mono&display=swap');
            .stApp {{ background-image: url("data:image/png;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }}
            .v-tile-apex {{ background: rgba(6, 6, 6, 0.98); padding: 2rem; border-left: 10px solid #B58863; margin-bottom: 2rem; border: 1px solid rgba(181,136,99,0.2); }}
            .v-table-tactical {{ width: 100%; border-collapse: collapse; margin-top: 20px; border: 1px solid #111; }}
            .v-table-tactical th {{ background: #000; color: #B58863; padding: 15px; border-bottom: 2px solid #333; }}
            .v-table-tactical td {{ padding: 12px; border-bottom: 1px solid #111; color: #CCC; }}
        </style>
    """, unsafe_allow_html=True) [cite: 16, 17, 18, 19, 20, 21]

# ==============================================================================
# 2. SILNIK GRAFICZNY I CAD-3D [cite: 37, 38, 39]
# ==============================================================================
def get_vorteza_sku_hex(sku_name):
    random.seed(sum(ord(c) for c in str(sku_name)))
    return random.choice(["#B58863", "#D4AF37", "#8E6A4D", "#16A085", "#2980B9", "#E67E22"]) [cite: 36, 37]

def build_box_cad_geometry(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=color, opacity=0.9, name=name, flatshading=True)
    lx = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    ly = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    lz = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=2), hoverinfo='skip')
    return [mesh, lines] [cite: 37, 38]

def render_vorteza_cad_3d(veh, stacks):
    fig = go.Figure()
    L, W, H, cab = veh['L'], veh['W'], veh['H'], veh.get('cab_l', 200)
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-2, -2, -2, -2], color='#111', opacity=1))
    fig.add_trace(go.Mesh3d(x=[-cab, 0, 0, -cab, -cab, 0, 0, -cab], y=[-10, -10, W+10, W+10, -10, -10, W+10, W+10], z=[0, 0, 0, 0, H*0.8, H*0.8, H*0.8, H*0.8], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#050505', opacity=1))
    skel = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]), ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])]
    for lx, ly, lz in skel: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=5), hoverinfo='skip'))
    for s in stacks:
        for u in s['items']:
            for p in build_box_cad_geometry(s['x'], s['y'], u['z'], u['w_fit'], u['l_fit'], u['height'], get_vorteza_sku_hex(u['name']), u['name']): fig.add_trace(p)
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor='rgba(0,0,0,0)'), margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig [cite: 39, 40, 41, 42]

# ==============================================================================
# 3. SILNIK PAKOWANIA [cite: 43]
# ==============================================================================
class V24SupremeEngine:
    @staticmethod
    def solve(cargo, veh, x_off=0):
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        stacks, weight = [], 0
        cx, cy, r_max_w = x_off, 0, 0
        for u in items:
            if weight + u['weight'] > veh['max_w']: continue
            placed = False
            for s in stacks:
                if u.get('canStack', True) and u['width'] <= s['w'] and u['length'] <= s['l'] and (s['curH'] + u['height'] <= veh['H']):
                    u_c = u.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = s['curH'], s['w'], s['l']
                    s['items'].append(u_c); s['curH'] += u['height']; weight += u['weight']; placed = True; break
            if placed: continue
            if cy + u['length'] <= veh['W'] and cx + u['width'] <= veh['L']:
                u_c = u.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = 0, u['width'], u['length']
                stacks.append({'x':cx, 'y':cy, 'w':u['width'], 'l':u['length'], 'curH':u['height'], 'items':[u_c]})
                cy += u['length']; r_max_w = max(r_max_w, u['width']); weight += u['weight']
            elif cx + r_max_w + u['width'] <= veh['L'] and u['length'] <= veh['W']:
                cx += r_max_w; cy, r_max_w = 0, u['width']
                u_c = u.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = 0, u['width'], u['length']
                stacks.append({'x':cx, 'y':cy, 'w':u['width'], 'l':u['length'], 'curH':u['height'], 'items':[u_c]})
                cy += u['length']; weight += u['weight']
        return stacks, weight [cite: 43, 44, 45, 46, 47, 48, 49, 50, 51, 52]

# ==============================================================================
# 4. GŁÓWNA FUNKCJA URUCHOMIENIOWA (MODUŁ HUB) [cite: 57]
# ==============================================================================
def run_stack():
    inject_vorteza_stack_ui()
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    L = LANGUAGES[st.session_state.lang]
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []

    if os.path.exists(PATH_DATA):
        with open(PATH_DATA, 'r', encoding='utf-8') as f: inventory = json.load(f)
    else: inventory = []

    # --- SIDEBAR: OPERACJE I EDYTOR ---
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
                    u_e = p_ref.copy(); u_e['p_act'] = p_qty; st.session_state.v_manifest.append(u_e) [cite: 60, 61, 62, 63]
                st.rerun()

        # --- SEKCOJA EDYCJI MANIFESTU (TUTAJ JEST TWOJA LISTA!) ---
        if st.session_state.v_manifest:
            st.divider()
            st.markdown(f"### 📝 {L['edit_m']}")
            df_m = pd.DataFrame(st.session_state.v_manifest)
            # Edytor pozwalający na zmianę ilości 
            res_edit = st.data_editor(df_m[['name', 'p_act']], column_config={"p_act": st.column_config.NumberColumn(L['qty'], min_value=0)}, use_container_width=True, num_rows="dynamic")
            
            if st.button(L['update']):
                new_list = []
                for _, row in res_edit.iterrows():
                    # Jeśli ilość > 0, zostawiamy. Jeśli 0 - usuwamy. [cite: 65]
                    if row['p_act'] > 0:
                        orig = next((p for p in inventory if p['name'] == row['name']), None)
                        if orig:
                            u_entry = orig.copy(); u_entry['p_act'] = row['p_act']
                            new_list.append(u_entry) [cite: 66, 67]
                st.session_state.v_manifest = new_list
                st.rerun()

        if st.button(L['purge']): st.session_state.v_manifest = []; st.rerun() [cite: 68]

    # --- OKNO GŁÓWNE ---
    st.markdown(f"<h2 style='color:#B58863;'>{L['title']}</h2>", unsafe_allow_html=True)
    tab_planner, tab_db = st.tabs([f"📊 {L['manifest']}", f"📦 {L['inventory']}"])

    with tab_planner:
        if st.session_state.v_manifest:
            eng_in = []
            for e in st.session_state.v_manifest:
                for _ in range(math.ceil(e['p_act'] / e.get('itemsPerCase', 1))): eng_in.append(e.copy()) [cite: 69]
            
            stacks, weight = V24SupremeEngine.solve(eng_in, veh, x_shift)
            k1, k2, k3 = st.columns(3)
            k1.metric(L['pcs'], sum(it['p_act'] for it in st.session_state.v_manifest))
            k2.metric(L['weight'], f"{weight} KG")
            k3.metric(L['util'], f"{(weight/veh['max_w'])*100:.1f}%") [cite: 70]
            
            st.markdown('<div class="v-tile-apex">', unsafe_allow_html=True)
            st.plotly_chart(render_vorteza_cad_3d(veh, stacks), use_container_width=True)
            
            # Tabela podglądu (Tactical Table)
            sku_agg = pd.Series([it['name'] for s in stacks for it in s['items']]).value_counts().reset_index()
            sku_agg.columns = [L['sku_ident'], 'CASES'] [cite: 71]
            h_table = f'<table class="v-table-tactical"><tr><th>SKU</th><th>{L["cases"]}</th></tr>'
            for _, r in sku_agg.iterrows():
                h_table += f'<tr><td><span style="color:{get_vorteza_sku_hex(r[L["sku_ident"]])}">■</span> {r[L["sku_ident"]]}</td><td>{r["CASES"]}</td></tr>'
            st.markdown(h_table + '</table>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.info(L['no_data'])

    with tab_db:
        st.markdown(f"### 📦 {L['inventory']}")
        new_db = st.data_editor(pd.DataFrame(inventory), use_container_width=True, num_rows="dynamic")
        if st.button(L['save_db']):
            with open(PATH_DATA, 'w', encoding='utf-8') as f: json.dump(new_db.to_dict('records'), f, indent=4, ensure_ascii=False)
            st.success(L['sync']) [cite: 72, 73]

if __name__ == "__main__": run_stack()
