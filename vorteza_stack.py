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
# 0. KONFIGURACJA ŚCIEŻEK I ZASOBÓW
# ==============================================================================
PATH_DATA = os.path.join("data", "products.json")
PATH_BG = os.path.join("assets", "bg_vorteza.png")

LANGUAGES = {
    "PL": {
        "title": "VORTEZA STACK PRO V25", "fleet": "KONSOLA FLOTY", "unit": "JEDNOSTKA",
        "offset": "OFFSET (cm)", "cargo": "WEJŚCIE ŁADUNKU", "sku_sel": "WYBÓR SKU",
        "qty": "SZTUKI", "add": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ DANE",
        "manifest": "MANIFEST ZAŁADUNKOWY", "edit_m": "EDYCJA MANIFESTU", "cases": "OPAKOWANIA",
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "WAGA BRUTTO", "util": "UTYLIZACJA",
        "ldm_occ": "LDM ZAJĘTE", "ldm_free": "LDM WOLNE", "vol": "OBJĘTOŚĆ",
        "no_data": "STATUS: OCZEKIWANIE NA DANE", "inventory": "BAZA SKU", 
        "save_db": "ZAPISZ BAZĘ", "sync": "SYNCHRONIZACJA OK", "update": "AKTUALIZUJ MANIFEST"
    }
}

FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "axles": 3, "cab_l": 250, "total_ldm": 13.6},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "axles": 3, "cab_l": 250, "total_ldm": 13.6},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "axles": 2, "cab_l": 200, "total_ldm": 9.2}
}

# ==============================================================================
# 1. UI ENGINE: APEX DARK & TRANSPARENCY
# ==============================================================================
def inject_vorteza_stack_ui():
    bg_data = ""
    if os.path.exists(PATH_BG):
        with open(PATH_BG, 'rb') as f: bg_data = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700&family=JetBrains+Mono&display=swap');
            .stApp {{ 
                background-image: url("data:image/png;base64,{bg_data}"); 
                background-size: cover; background-attachment: fixed; 
            }}
            .v-kpi-card {{
                background: rgba(10, 10, 10, 0.9);
                border: 1px solid rgba(181, 136, 99, 0.3);
                border-top: 4px solid #B58863;
                padding: 12px;
                text-align: center;
                backdrop-filter: blur(10px);
            }}
            .v-kpi-label {{ color: #B58863; font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; }}
            .v-kpi-value {{ color: #FFFFFF; font-size: 1.4rem; font-family: 'JetBrains Mono', monospace; font-weight: 500; }}
            .v-table-pro {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: rgba(0,0,0,0.7); border: 1px solid #333; }}
            .v-table-pro th {{ background: #B58863; color: black; padding: 12px; text-align: left; text-transform: uppercase; font-size: 0.7rem; }}
            .v-table-pro td {{ padding: 10px 12px; border-bottom: 1px solid #222; color: #DDD; font-family: 'JetBrains Mono', monospace; }}
            .js-plotly-plot .plotly .main-svg {{ background: transparent !important; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. V-COLOR ENGINE
# ==============================================================================
def get_vorteza_sku_hex(sku_name):
    palette = ["#B58863", "#D4AF37", "#16A085", "#27AE60", "#2980B9", "#E67E22", "#C0392B", "#8E44AD", "#F1C40F", "#34495E"]
    random.seed(sum(ord(c) for c in str(sku_name)))
    return random.choice(palette)

# ==============================================================================
# 3. SILNIK GRAFICZNY: TRUCK PRO RENDERER
# ==============================================================================
def build_mesh(vx, vy, vz, color, name, op=1.0):
    return go.Mesh3d(x=vx, y=vy, z=vz, i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=color, opacity=op, name=name, flatshading=True)

def render_vorteza_pro_3d(veh, stacks):
    fig = go.Figure()
    L, W, H, cab = veh['L'], veh['W'], veh['H'], veh['cab_l']
    
    fig.add_trace(build_mesh([0, L, L, 0, 0, L, L, 0], [0, 0, W, W, 0, 0, W, W], [-10, -10, -10, -10, -2, -2, -2, -2], "#B58863", "RAMA"))
    for ax in range(veh['axles']):
        pos_x = L - 380 + (ax * 135)
        for side in [-35, W+15]:
            fig.add_trace(build_mesh([pos_x-50, pos_x+50, pos_x+50, pos_x-50, pos_x-50, pos_x+50, pos_x+50, pos_x-50], [side, side, side+20, side+20, side, side, side+20, side+20], [-80, -80, -80, -80, -5, -5, -5, -5], "#000", "KOŁO"))
    
    fig.add_trace(build_mesh([-cab, 0, 0, -cab, -cab, 0, 0, -cab], [-15, -15, W+15, W+15, -15, -15, W+15, W+15], [0, 0, 0, 0, H*0.95, H*0.95, H*0.95, H*0.95], "#050505", "KABINA"))
    
    for s in stacks:
        for u in s['items']:
            clr = get_vorteza_sku_hex(u['name'])
            vx, vy, vz = [s['x'], s['x']+u['w_fit'], s['x']+u['w_fit'], s['x'], s['x'], s['x']+u['w_fit'], s['x']+u['w_fit'], s['x']], [s['y'], s['y'], s['y']+u['l_fit'], s['y']+u['l_fit'], s['y'], s['y'], s['y']+u['l_fit'], s['y']+u['l_fit']], [u['z'], u['z'], u['z'], u['z'], u['z']+u['height'], u['z']+u['height'], u['z']+u['height'], u['z']+u['height']]
            fig.add_trace(go.Mesh3d(x=vx, y=vy, z=vz, i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=clr, opacity=0.9, name=u['name']))
            
            lx = [vx[0], vx[1], vx[2], vx[3], vx[0], vx[4], vx[5], vx[1], vx[5], vx[6], vx[2], vx[6], vx[7], vx[3], vx[7], vx[4]]
            ly = [vy[0], vy[1], vy[2], vy[3], vy[0], vy[4], vy[5], vy[1], vy[5], vy[6], vy[2], vy[6], vy[7], vy[3], vy[7], vy[4]]
            lz = [vz[0], vz[1], vz[2], vz[3], vz[0], vz[4], vz[5], vz[1], vz[5], vz[6], vz[2], vz[6], vz[7], vz[3], vz[7], vz[4]]
            fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=2), hoverinfo='skip'))

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# ==============================================================================
# 4. SILNIK OPTYMALIZACJI PRZESTRZENNEJ V25 (SPACE-MAXIMIZER)
# ==============================================================================
class V25SpaceMaximizer:
    @staticmethod
    def solve(cargo, veh, x_off=0):
        # Sortowanie: Piętrowalne najpierw, potem wg największej objętości
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width'] * x['length'] * x['height']), reverse=True)
        stacks, weight, volume = [], 0, 0
        
        # Mapa zajętości podłogi (uproszczony algorytm skanowania wolnych luk)
        for u in items:
            if weight + u['weight'] > veh['max_w']: continue
            
            placed = False
            # 1. Próba piętrowania na istniejącym stosie
            for s in stacks:
                if u.get('canStack', True) and u['width'] <= s['w'] and u['length'] <= s['l']:
                    if (s['curH'] + u['height'] <= veh['H']):
                        u_c = u.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = s['curH'], s['w'], s['l']
                        s['items'].append(u_c); s['curH'] += u['height']
                        weight += u['weight']; volume += (u['width']*u['length']*u['height'])/1e6
                        placed = True; break
            if placed: continue
            
            # 2. Poszukiwanie "luki" na podłodze (Algorytm First-Fit na osiach X, Y)
            # Skanujemy wzdłuż naczepy co 5cm dla precyzji, szukając wolnego prostokąta
            for x in range(x_off, veh['L'] - u['width'], 10):
                for y in range(0, veh['W'] - u['length'], 10):
                    # Sprawdzenie kolizji z istniejącymi stosami
                    collision = False
                    for s in stacks:
                        if not (x + u['width'] <= s['x'] or x >= s['x'] + s['w'] or 
                                y + u['length'] <= s['y'] or y >= s['y'] + s['l']):
                            collision = True; break
                    
                    if not collision:
                        u_c = u.copy(); u_c['z'], u_c['w_fit'], u_c['l_fit'] = 0, u['width'], u['length']
                        stacks.append({'x':x, 'y':y, 'w':u['width'], 'l':u['length'], 'curH':u['height'], 'items':[u_c]})
                        weight += u['weight']; volume += (u['width']*u['length']*u['height'])/1e6
                        placed = True; break
                if placed: break
        
        ldm_occ = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
        return stacks, weight, volume, ldm_occ

# ==============================================================================
# 5. GŁÓWNA FUNKCJA URUCHOMIENIOWA
# ==============================================================================
def run_stack():
    inject_vorteza_stack_ui()
    L = LANGUAGES["PL"]
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []

    inventory = []
    if os.path.exists(PATH_DATA):
        with open(PATH_DATA, 'r', encoding='utf-8') as f: inventory = json.load(f)

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
                for it in st.session_state.v_manifest:
                    if it['name'] == sel_sku: it['p_act'] += p_qty; found = True; break
                if not found:
                    u_e = p_ref.copy(); u_e['p_act'] = p_qty; st.session_state.v_manifest.append(u_e)
                st.rerun()

        if st.session_state.v_manifest:
            st.divider()
            st.markdown(f"### 📝 {L['edit_m']}")
            df_m = pd.DataFrame(st.session_state.v_manifest)
            res_edit = st.data_editor(df_m[['name', 'p_act']], column_config={"p_act": st.column_config.NumberColumn(L['qty'], min_value=0)}, use_container_width=True)
            if st.button(L['update']):
                st.session_state.v_manifest = [it for it in [next((orig.copy() for orig in inventory if orig['name'] == r['name']), None) for _, r in res_edit.iterrows()] if it and it.update({'p_act': res_edit.loc[res_edit['name']==it['name'], 'p_act'].values[0]}) is None and it['p_act'] > 0]
                st.rerun()
        
        if st.button(L['purge']): st.session_state.v_manifest = []; st.rerun()

    st.markdown(f"<h2 style='color:#B58863; letter-spacing:10px;'>{L['title']}</h2>", unsafe_allow_html=True)

    if st.session_state.v_manifest:
        eng_in = []
        for e in st.session_state.v_manifest:
            for _ in range(math.ceil(e['p_act'] / e.get('itemsPerCase', 1))): eng_in.append(e.copy())
        
        # WYWOŁANIE NOWEGO SILNIKA V25
        stacks, weight, volume, ldm_occ = V25SpaceMaximizer.solve(eng_in, veh, x_shift)
        
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        stats_list = [
            (L['pcs'], sum(it['p_act'] for it in st.session_state.v_manifest)),
            (L['weight'], f"{weight} KG"),
            (L['vol'], f"{volume:.1f} m³"),
            (L['ldm_occ'], f"{ldm_occ:.2f}"),
            (L['ldm_free'], f"{veh['total_ldm'] - ldm_occ:.2f}"),
            (L['util'], f"{(weight/veh['max_w'])*100:.1f}%")
        ]
        for i, (label, val) in enumerate(stats_list):
            with [c1, c2, c3, c4, c5, c6][i]:
                st.markdown(f'<div class="v-kpi-card"><div class="v-kpi-label">{label}</div><div class="v-kpi-value">{val}</div></div>', unsafe_allow_html=True)

        st.plotly_chart(render_vorteza_pro_3d(veh, stacks), use_container_width=True)
        
        st.markdown(f"### 📋 {L['manifest']}")
        html_table = f'<table class="v-table-pro"><tr><th>KOLOR</th><th>SKU</th><th>{L["cases"]}</th><th>{L["pcs"]}</th></tr>'
        for it in st.session_state.v_manifest:
            clr = get_vorteza_sku_hex(it['name'])
            cases = math.ceil(it['p_act'] / it.get('itemsPerCase', 1))
            html_table += f'<tr><td style="text-align:center;"><span style="color:{clr}; font-size:20px;">■</span></td><td>{it["name"]}</td><td>{cases}</td><td>{it["p_act"]}</td></tr>'
        st.markdown(html_table + '</table>', unsafe_allow_html=True)
    else:
        st.info(L['no_data'])

if __name__ == "__main__": run_stack()
