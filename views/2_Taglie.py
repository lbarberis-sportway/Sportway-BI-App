import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys
import os

# Aggiungiamo la root dell'app al path per trovare utils/
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_engine import load_data, get_filtered_options, filter_dataframe, merge_and_aggregate, get_date_reference, get_date_options, filter_by_date, merge_period_comparison, list_excel_files

# --- CSS condiviso ---
_css_path = Path(__file__).parent.parent / "assets" / "style.css"
if _css_path.exists():
    with open(_css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- CARICAMENTO FILE (Upload o Stato) ---
if 'df_vend_raw' not in st.session_state:
    st.session_state.df_vend_raw = None
    st.session_state.df_acq_raw = None
    st.session_state.file_name = None

def reset_filters():
    st.session_state.filter_linea = []
    st.session_state.filter_categoria = []
    st.session_state.filter_stagione = []
    st.session_state.filter_taglia = []
    st.session_state.filter_produttore = []
    st.session_state.filter_negozio = []

if st.session_state.df_vend_raw is None:
    st.title("Sportway Analisi Dati")
    st.markdown("Carica un file Excel per iniziare l'analisi.")

    col_up1, col_up2 = st.columns(2)

    with col_up1:
        st.markdown("**File dalla cartella Dati Excel**")
        files_disponibili = list_excel_files()
        if files_disponibili:
            sel_file = st.selectbox("", files_disponibili, label_visibility="collapsed", key="file_select")
            if st.button("Analizza file selezionato", type="primary", use_container_width=True):
                try:
                    df_vend_raw, df_acq_raw = load_data(f"data/Dati Excel/{sel_file}")
                    st.session_state.df_vend_raw = df_vend_raw
                    st.session_state.df_acq_raw = df_acq_raw
                    st.session_state.file_name = sel_file
                    st.success(f"Caricato: {sel_file}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore nel caricamento del file: {e}")
        else:
            st.info("Nessun file .xlsx trovato nella cartella Dati Excel.")

    with col_up2:
        st.markdown("**Oppure carica un file dal computer**")
        uploaded_file = st.file_uploader("", type=['xlsx'], label_visibility="collapsed")

        if uploaded_file is not None:
            try:
                df_vend_raw, df_acq_raw = load_data(uploaded_file)
                st.session_state.df_vend_raw = df_vend_raw
                st.session_state.df_acq_raw = df_acq_raw
                st.session_state.file_name = uploaded_file.name
                st.rerun()
            except Exception as e:
                st.error(f"Errore nel caricamento del file: {e}")

    st.caption("Formato richiesto: file **.xlsx** con fogli **VEND** (Vendite) e **ACQ** (Acquisti).")
    st.stop()

df_vend_raw = st.session_state.df_vend_raw
df_acq_raw = st.session_state.df_acq_raw

# ==========================================
# LAYOUT PRINCIPALE
# ==========================================
st.title("Esplorazione Dati Taglie")
col_title, col_reset, col_new = st.columns([6, 1, 1])
with col_title:
    st.markdown("Analisi incrociata di Acquisti e Vendite per ottimizzare lo stock.")
    st.caption(f"File: {st.session_state.file_name}")
with col_reset:
    st.button("↺ Reset Filtri", on_click=reset_filters, use_container_width=True)
with col_new:
    if st.button("← Nuova Analisi", use_container_width=True):
        st.session_state.df_vend_raw = None
        st.session_state.df_acq_raw = None
        st.session_state.file_name = None
        st.rerun()

# Filtri Fissi Superiori (Cascading bidirezionale)
st.markdown("### Filtri Ricerca")
_FILTRI_COLS = ['Linea', 'Categoria', 'Stagione', 'Taglia', 'Produttore', 'Negozio']

def _other_filters(exclude_col):
    filters = {}
    for col in _FILTRI_COLS:
        if col != exclude_col:
            val = st.session_state.get(f"filter_{col.lower()}", [])
            if val:
                filters[col] = val
    return filters

f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
with f_col1:
    selected_linee = st.multiselect("Linea",
        get_filtered_options(df_vend_raw, df_acq_raw, 'Linea', _other_filters('Linea')),
        placeholder="Tutte le Linee", key="filter_linea")
with f_col2:
    selected_cat = st.multiselect("Categoria",
        get_filtered_options(df_vend_raw, df_acq_raw, 'Categoria', _other_filters('Categoria')),
        placeholder="Tutte le Categorie", key="filter_categoria")
with f_col3:
    selected_stag = st.multiselect("Stagione",
        get_filtered_options(df_vend_raw, df_acq_raw, 'Stagione', _other_filters('Stagione')),
        placeholder="Tutte le Stagioni", key="filter_stagione")
with f_col4:
    selected_taglie = st.multiselect("Taglia",
        get_filtered_options(df_vend_raw, df_acq_raw, 'Taglia', _other_filters('Taglia')),
        placeholder="Tutte le Taglie", key="filter_taglia")
with f_col5:
    selected_prod = st.multiselect("Produttore",
        get_filtered_options(df_vend_raw, df_acq_raw, 'Produttore', _other_filters('Produttore')),
        placeholder="Tutti i Produttori", key="filter_produttore")

f_col6, f_col7, f_col8 = st.columns(3)
with f_col6:
    selected_negozio = st.multiselect("Negozio",
        get_filtered_options(df_vend_raw, df_acq_raw, 'Negozio', _other_filters('Negozio')),
        placeholder="Tutti i Negozi", key="filter_negozio")

st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)

# Crea dizionario filtri
filters = {
    'Linea': selected_linee,
    'Categoria': selected_cat,
    'Stagione': selected_stag,
    'Taglia': selected_taglie,
    'Produttore': selected_prod,
    'Negozio': selected_negozio
}

# Applica Filtri
df_vend = filter_dataframe(df_vend_raw, filters)
df_acq = filter_dataframe(df_acq_raw, filters)
df_vend_cat = df_vend.copy()
df_acq_cat = df_acq.copy()

# Init filtri temporali
date_ref = get_date_reference(df_vend_raw, df_acq_raw)
_ref_min = date_ref['Data'].min().date()
_ref_max = date_ref['Data'].max().date()

if 'range_slider' not in st.session_state:
    st.session_state.range_slider = (_ref_min, _ref_max)
if 'temp_start' not in st.session_state:
    st.session_state.temp_start = _ref_min
if 'temp_end' not in st.session_state:
    st.session_state.temp_end = _ref_max

def _sync_slider_dates():
    st.session_state.temp_start = st.session_state.range_slider[0]
    st.session_state.temp_end = st.session_state.range_slider[1]

def _sync_dates_slider():
    st.session_state.range_slider = (st.session_state.temp_start, st.session_state.temp_end)

COLOR_ACQ = "#3b82f6"
COLOR_VEND = "#f59e0b"
COLOR_ACQ_LIGHT = "#93c5fd"
COLOR_VEND_LIGHT = "#fcd34d"

def _c_str(val):
    if pd.isna(val):
        return 'color: #d1d5db'
    if val < 30:
        return 'color: #dc2626; font-weight: 600'
    if val < 70:
        return 'color: #d97706; font-weight: 600'
    return 'color: #16a34a; font-weight: 600'

def _c_str_delta(val):
    if pd.isna(val) or val == 0:
        return 'color: #94a3b8'
    if val > 0:
        return 'color: #16a34a; font-weight: 600'
    return 'color: #dc2626; font-weight: 600'

def _fmt_delta(val):
    if pd.isna(val) or val == 0:
        return '0'
    if val > 0:
        return f'+{val:,.0f}'.replace(',', '.')
    return f'{val:,.0f}'.replace(',', '.')

def _fmt_delta_pct(val):
    if pd.isna(val) or abs(val) < 0.01:
        return '0.0%'
    if val > 0:
        return f'+{val:.1f}%'
    return f'{val:.1f}%'

tab1, tab2 = st.tabs(["Analisi Completa", "Confronto Stagionale"])

# ===================== TAB 1: ANALISI COMPLETA =====================
with tab1:
    st.markdown("### Filtri Temporali")
    st.caption(f"Periodo disponibile: {_ref_min.strftime('%d/%m/%Y')} → {_ref_max.strftime('%d/%m/%Y')}")

    st.slider("Intervallo Date", min_value=_ref_min, max_value=_ref_max,
              format="DD/MM/YYYY", key="range_slider", on_change=_sync_slider_dates)

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.date_input("Data Inizio", key="temp_start", format="DD/MM/YYYY", on_change=_sync_dates_slider)
    with d_col2:
        st.date_input("Data Fine", key="temp_end", format="DD/MM/YYYY", on_change=_sync_dates_slider)

    df_vend = df_vend[(df_vend['Data'] >= pd.Timestamp(st.session_state.temp_start)) &
                      (df_vend['Data'] <= pd.Timestamp(st.session_state.temp_end))]
    df_acq = df_acq[(df_acq['Data'] >= pd.Timestamp(st.session_state.temp_start)) &
                    (df_acq['Data'] <= pd.Timestamp(st.session_state.temp_end))]

    st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)

    df_stag, df_tot = merge_and_aggregate(df_vend, df_acq)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        tot_acq = df_tot['Qta_Acquistata'].sum()
        st.metric("Totale Acquistato", f"{int(tot_acq):,}".replace(",", "."))
    with col2:
        tot_vend = df_tot['Qta_Venduta'].sum()
        st.metric("Totale Venduto", f"{int(tot_vend):,}".replace(",", "."))
    with col3:
        sell_through = (tot_vend / tot_acq * 100) if tot_acq > 0 else 0
        st.metric("Sell-Through %", f"{sell_through:.1f}%")
    with col4:
        taglie_attive = df_tot[df_tot['Qta_Acquistata'] > 0]['Taglia'].nunique()
        st.metric("Taglie Analizzate", f"{taglie_attive}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)

    cat_vend = df_vend.groupby('Categoria')['Qta_Venduta'].sum().reset_index()
    cat_acq = df_acq.groupby('Categoria')['Qta_Acquistata'].sum().reset_index()
    cat_agg = pd.merge(cat_acq, cat_vend, on='Categoria', how='outer').fillna(0)
    cat_agg = cat_agg.sort_values('Qta_Venduta', ascending=False)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Andamento per Taglia")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df_tot['Taglia'], y=df_tot['Qta_Acquistata'], name='Acquistato', marker_color=COLOR_ACQ))
        fig_bar.add_trace(go.Bar(x=df_tot['Taglia'], y=df_tot['Qta_Venduta'], name='Venduto', marker_color=COLOR_VEND))
        fig_bar.update_layout(
            barmode='group', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(family="Inter, sans-serif", color="#475569")
        )
        fig_bar.update_yaxes(gridcolor='#f1f5f9')
        fig_bar.update_xaxes(type='category', title_text='')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("Andamento per Categoria")
        fig_cat_bar = go.Figure()
        fig_cat_bar.add_trace(go.Bar(x=cat_agg['Categoria'], y=cat_agg['Qta_Acquistata'], name='Acquistato', marker_color=COLOR_ACQ))
        fig_cat_bar.add_trace(go.Bar(x=cat_agg['Categoria'], y=cat_agg['Qta_Venduta'], name='Venduto', marker_color=COLOR_VEND))
        fig_cat_bar.update_layout(
            barmode='group', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(family="Inter, sans-serif", color="#475569")
        )
        fig_cat_bar.update_yaxes(gridcolor='#f1f5f9', title='Quantità')
        fig_cat_bar.update_xaxes(type='category', title_text='')
        st.plotly_chart(fig_cat_bar, use_container_width=True)

    st.subheader("Trend Sell-Through per Taglie")
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_tot['Taglia'], y=df_tot['Qta_Acquistata'], mode='lines+markers', name='Acquistato', line=dict(color=COLOR_ACQ, width=2)))
    fig_line.add_trace(go.Scatter(x=df_tot['Taglia'], y=df_tot['Qta_Venduta'], mode='lines+markers', name='Venduto', line=dict(color=COLOR_VEND, width=3)))
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif", color="#475569")
    )
    fig_line.update_yaxes(gridcolor='#f1f5f9')
    fig_line.update_xaxes(type='category', title_text='')
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    st.subheader("Vendite per Negozio")

    negozi_agg = df_vend.groupby('Negozio')['Qta_Venduta'].sum().reset_index()
    negozi_agg = negozi_agg.sort_values('Qta_Venduta', ascending=True)

    fig_negozi = go.Figure()
    fig_negozi.add_trace(go.Bar(x=negozi_agg['Qta_Venduta'], y=negozi_agg['Negozio'], orientation='h', marker_color=COLOR_VEND, name='Venduto'))
    fig_negozi.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Inter, sans-serif", color="#475569")
    )
    fig_negozi.update_yaxes(gridcolor='#f1f5f9')
    fig_negozi.update_xaxes(title='Quantità Venduta', gridcolor='#f1f5f9')
    st.plotly_chart(fig_negozi, use_container_width=True)

    st.subheader("Matrice Taglie")
    st.markdown("Esplora i dati per Stagione e Taglia. Clicca sulle intestazioni per ordinare.")

    display_df = df_stag.copy()
    display_df = display_df[['Taglia', 'Stagione', 'Qta_Acquistata', 'Qta_Venduta', 'Sell_Through_%']]
    display_df.rename(columns={'Qta_Acquistata': 'Somma Q.tà Acquistata', 'Qta_Venduta': 'Somma Q.tà Venduta'}, inplace=True)

    styled = (
        display_df.style
        .map(_c_str, subset=['Sell_Through_%'])
        .format({'Somma Q.tà Acquistata': '{:.0f}', 'Somma Q.tà Venduta': '{:.0f}', 'Sell_Through_%': '{:.1f}%'})
    )
    st.dataframe(styled, use_container_width=True, height=400)

    st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    st.subheader("Matrice Produttori")
    st.markdown("Esplora i dati per Produttore.")

    agg_acq_prod = df_acq.groupby('Produttore')['Qta_Acquistata'].sum().reset_index()
    agg_vend_prod = df_vend.groupby('Produttore')['Qta_Venduta'].sum().reset_index()
    prod_merged = pd.merge(agg_acq_prod, agg_vend_prod, on='Produttore', how='outer').fillna(0)
    prod_merged['Sell_Through_%'] = (prod_merged['Qta_Venduta'] / prod_merged['Qta_Acquistata']) * 100
    prod_merged['Sell_Through_%'] = prod_merged['Sell_Through_%'].replace([float('inf'), -float('inf')], 0).fillna(0)
    prod_merged = prod_merged.sort_values('Qta_Acquistata', ascending=False).reset_index(drop=True)

    prod_display = prod_merged.rename(columns={'Qta_Acquistata': 'Somma Q.tà Acquistata', 'Qta_Venduta': 'Somma Q.tà Venduta'})
    prod_styled = (
        prod_display.style
        .map(_c_str, subset=['Sell_Through_%'])
        .format({'Somma Q.tà Acquistata': '{:.0f}', 'Somma Q.tà Venduta': '{:.0f}', 'Sell_Through_%': '{:.1f}%'})
    )
    st.dataframe(prod_styled, use_container_width=True, height=400)

    st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    st.subheader("Matrice Categoria")
    st.markdown("Esplora i dati per Categoria.")

    agg_acq_cat = df_acq.groupby('Categoria')['Qta_Acquistata'].sum().reset_index()
    agg_vend_cat = df_vend.groupby('Categoria')['Qta_Venduta'].sum().reset_index()
    cat_merged = pd.merge(agg_acq_cat, agg_vend_cat, on='Categoria', how='outer').fillna(0)
    cat_merged['Sell_Through_%'] = (cat_merged['Qta_Venduta'] / cat_merged['Qta_Acquistata']) * 100
    cat_merged['Sell_Through_%'] = cat_merged['Sell_Through_%'].replace([float('inf'), -float('inf')], 0).fillna(0)
    cat_merged = cat_merged.sort_values('Qta_Acquistata', ascending=False).reset_index(drop=True)

    cat_display = cat_merged.rename(columns={'Qta_Acquistata': 'Somma Q.tà Acquistata', 'Qta_Venduta': 'Somma Q.tà Venduta'})
    cat_styled = (
        cat_display.style
        .map(_c_str, subset=['Sell_Through_%'])
        .format({'Somma Q.tà Acquistata': '{:.0f}', 'Somma Q.tà Venduta': '{:.0f}', 'Sell_Through_%': '{:.1f}%'})
    )
    st.dataframe(cat_styled, use_container_width=True, height=400)

    st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    st.subheader("Matrice Linea")
    st.markdown("Esplora i dati per Linea.")

    agg_acq_linea = df_acq.groupby('Linea')['Qta_Acquistata'].sum().reset_index()
    agg_vend_linea = df_vend.groupby('Linea')['Qta_Venduta'].sum().reset_index()
    linea_merged = pd.merge(agg_acq_linea, agg_vend_linea, on='Linea', how='outer').fillna(0)
    linea_merged['Sell_Through_%'] = (linea_merged['Qta_Venduta'] / linea_merged['Qta_Acquistata']) * 100
    linea_merged['Sell_Through_%'] = linea_merged['Sell_Through_%'].replace([float('inf'), -float('inf')], 0).fillna(0)
    linea_merged = linea_merged.sort_values('Qta_Acquistata', ascending=False).reset_index(drop=True)

    linea_display = linea_merged.rename(columns={'Qta_Acquistata': 'Somma Q.tà Acquistata', 'Qta_Venduta': 'Somma Q.tà Venduta'})
    linea_styled = (
        linea_display.style
        .map(_c_str, subset=['Sell_Through_%'])
        .format({'Somma Q.tà Acquistata': '{:.0f}', 'Somma Q.tà Venduta': '{:.0f}', 'Sell_Through_%': '{:.1f}%'})
    )
    st.dataframe(linea_styled, use_container_width=True, height=400)

# ===================== TAB 2: CONFRONTO STAGIONALE =====================
with tab2:
    mesi_nomi_cap = {1:"Gen",2:"Feb",3:"Mar",4:"Apr",5:"Mag",6:"Giu",
                     7:"Lug",8:"Ago",9:"Set",10:"Ott",11:"Nov",12:"Dic"}

    stagioni_disponibili = sorted(df_vend_cat['Stagione'].unique())

    st.markdown("### Confronto Stagionale")
    ytd_col1, ytd_col2, ytd_col3 = st.columns([1, 1, 1])

    with ytd_col1:
        ref_season = st.selectbox("Stagione Riferimento", stagioni_disponibili, index=0, key="ytd_ref_season")
    with ytd_col2:
        comp_opts = [s for s in stagioni_disponibili if s != ref_season]
        comp_season = st.selectbox("Stagione Confronto", comp_opts, index=0 if comp_opts else 0, key="ytd_comp_season")
    with ytd_col3:
        ref_season_data = df_vend_cat[df_vend_cat['Stagione'] == ref_season]
        ref_min = ref_season_data['Data'].min()
        ref_max = ref_season_data['Data'].max()
        sel_date = st.date_input("Data Fine Confronto", value=ref_max.date(),
                                 min_value=ref_min.date(), max_value=ref_max.date(),
                                 format="DD/MM/YYYY", key="ytd_end_date")

    sel_ts = pd.Timestamp(sel_date)
    ref_season_data = df_vend_cat[df_vend_cat['Stagione'] == ref_season]
    comp_season_data = df_vend_cat[df_vend_cat['Stagione'] == comp_season]
    ref_min = ref_season_data['Data'].min()
    ref_end = sel_ts
    comp_year_int = 2000 + int(comp_season[-2:])
    comp_season_max = comp_season_data['Data'].max()
    try:
        comp_end = pd.Timestamp(comp_year_int, sel_ts.month, sel_ts.day)
    except ValueError:
        import calendar
        last_day = calendar.monthrange(comp_year_int, sel_ts.month)[1]
        comp_end = pd.Timestamp(comp_year_int, sel_ts.month, min(sel_ts.day, last_day))
    comp_end = min(comp_end, comp_season_max)
    comp_min = comp_season_data['Data'].min()

    def _fmt_period(s, e):
        return f"{s.day:02d} {mesi_nomi_cap[s.month]} {s.year} → {e.day:02d} {mesi_nomi_cap[e.month]} {e.year}"

    st.caption(
        f"**{ref_season}**: {_fmt_period(ref_min, ref_end)} | "
        f"**{comp_season}**: {_fmt_period(comp_min, comp_end)}"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    vend_p1 = df_vend_cat[(df_vend_cat['Stagione'] == ref_season) & (df_vend_cat['Data'] <= ref_end)]
    acq_p1 = df_acq_cat[(df_acq_cat['Stagione'] == ref_season) & (df_acq_cat['Data'] <= ref_end)]
    vend_p2 = df_vend_cat[(df_vend_cat['Stagione'] == comp_season) & (df_vend_cat['Data'] <= comp_end)]
    acq_p2 = df_acq_cat[(df_acq_cat['Stagione'] == comp_season) & (df_acq_cat['Data'] <= comp_end)]

    tot_acq_p1 = int(acq_p1['Qta_Acquistata'].sum())
    tot_vend_p1 = int(vend_p1['Qta_Venduta'].sum())
    tot_acq_p2 = int(acq_p2['Qta_Acquistata'].sum())
    tot_vend_p2 = int(vend_p2['Qta_Venduta'].sum())
    st_p1 = (tot_vend_p1 / tot_acq_p1 * 100) if tot_acq_p1 > 0 else 0
    st_p2 = (tot_vend_p2 / tot_acq_p2 * 100) if tot_acq_p2 > 0 else 0

    all_p1 = pd.merge(
        acq_p1.groupby('Taglia', observed=True)['Qta_Acquistata'].sum().reset_index(),
        vend_p1.groupby('Taglia', observed=True)['Qta_Venduta'].sum().reset_index(),
        on='Taglia', how='outer'
    ).fillna(0)
    all_p2 = pd.merge(
        acq_p2.groupby('Taglia', observed=True)['Qta_Acquistata'].sum().reset_index(),
        vend_p2.groupby('Taglia', observed=True)['Qta_Venduta'].sum().reset_index(),
        on='Taglia', how='outer'
    ).fillna(0)
    taglie_p1 = int(all_p1[all_p1['Qta_Acquistata'] > 0]['Taglia'].nunique())
    taglie_p2 = int(all_p2[all_p2['Qta_Acquistata'] > 0]['Taglia'].nunique())

    kpi_grid = st.columns(4)
    kpi_data = [
        ("Totale Acquistato", tot_acq_p1, tot_acq_p2, lambda x: f"{x:,}".replace(",", "."), False),
        ("Totale Venduto", tot_vend_p1, tot_vend_p2, lambda x: f"{x:,}".replace(",", "."), False),
        ("Sell-Through %", st_p1, st_p2, None, True),
        ("Taglie Analizzate", taglie_p1, taglie_p2, lambda x: str(x), False),
    ]
    for i, (label, p1, p2, _, is_pct) in enumerate(kpi_data):
        with kpi_grid[i]:
            delta_val = p1 - p2
            if is_pct:
                st.metric(label, f"{p1:.1f}%", delta=f"{delta_val:+.1f}%")
            else:
                p1_fmt = f"{p1:,}".replace(",", ".") if isinstance(p1, int) else str(p1)
                delta_fmt = f"+{delta_val:,}".replace(",", ".") if delta_val > 0 else f"{delta_val:,}".replace(",", ".")
                if isinstance(p1, float):
                    st.metric(label, f"{p1:.1f}%", delta=None)
                else:
                    st.metric(label, p1_fmt, delta=delta_fmt if delta_val != 0 else None)

    st.markdown("<br>", unsafe_allow_html=True)

    comp_taglie = merge_period_comparison(vend_p1, acq_p1, vend_p2, acq_p2, 'Taglia')
    comp_cat = merge_period_comparison(vend_p1, acq_p1, vend_p2, acq_p2, 'Categoria')

    comp_taglie = comp_taglie[(comp_taglie['P1_Acq'] > 0) | (comp_taglie['P2_Acq'] > 0)]
    comp_cat = comp_cat[(comp_cat['P1_Acq'] > 0) | (comp_cat['P2_Acq'] > 0)]

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("Confronto Acquisti per Taglia")
        fig_acq_comp = go.Figure()
        fig_acq_comp.add_trace(go.Bar(x=comp_taglie['Taglia'], y=comp_taglie['P1_Acq'], name=f'Acq {ref_season}', marker_color=COLOR_ACQ))
        fig_acq_comp.add_trace(go.Bar(x=comp_taglie['Taglia'], y=comp_taglie['P2_Acq'], name=f'Acq {comp_season}', marker_color=COLOR_ACQ_LIGHT))
        fig_acq_comp.update_layout(barmode='group', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                    margin=dict(l=20, r=20, t=40, b=20),
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                    font=dict(family="Inter, sans-serif", color="#475569"))
        fig_acq_comp.update_yaxes(gridcolor='#f1f5f9')
        fig_acq_comp.update_xaxes(type='category')
        st.plotly_chart(fig_acq_comp, use_container_width=True)

    with col_c2:
        st.subheader("Confronto Vendite per Taglia")
        fig_vend_comp = go.Figure()
        fig_vend_comp.add_trace(go.Bar(x=comp_taglie['Taglia'], y=comp_taglie['P1_Vend'], name=f'Vend {ref_season}', marker_color=COLOR_VEND))
        fig_vend_comp.add_trace(go.Bar(x=comp_taglie['Taglia'], y=comp_taglie['P2_Vend'], name=f'Vend {comp_season}', marker_color=COLOR_VEND_LIGHT))
        fig_vend_comp.update_layout(barmode='group', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                     margin=dict(l=20, r=20, t=40, b=20),
                                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                     font=dict(family="Inter, sans-serif", color="#475569"))
        fig_vend_comp.update_yaxes(gridcolor='#f1f5f9')
        fig_vend_comp.update_xaxes(type='category')
        st.plotly_chart(fig_vend_comp, use_container_width=True)

    st.subheader("Confronto per Categoria")
    fig_cat_comp = go.Figure()
    fig_cat_comp.add_trace(go.Bar(x=comp_cat['Categoria'], y=comp_cat['P1_Acq'], name=f'Acq {ref_season}', marker_color=COLOR_ACQ))
    fig_cat_comp.add_trace(go.Bar(x=comp_cat['Categoria'], y=comp_cat['P2_Acq'], name=f'Acq {comp_season}', marker_color=COLOR_ACQ_LIGHT))
    fig_cat_comp.add_trace(go.Bar(x=comp_cat['Categoria'], y=comp_cat['P1_Vend'], name=f'Vend {ref_season}', marker_color=COLOR_VEND))
    fig_cat_comp.add_trace(go.Bar(x=comp_cat['Categoria'], y=comp_cat['P2_Vend'], name=f'Vend {comp_season}', marker_color=COLOR_VEND_LIGHT))
    fig_cat_comp.update_layout(barmode='group', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                margin=dict(l=20, r=20, t=40, b=20),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                font=dict(family="Inter, sans-serif", color="#475569"))
    fig_cat_comp.update_yaxes(gridcolor='#f1f5f9')
    fig_cat_comp.update_xaxes(type='category')
    st.plotly_chart(fig_cat_comp, use_container_width=True)

    color_palette = ['#3b82f6','#f59e0b','#10b981','#ef4444','#8b5cf6',
                     '#ec4899','#06b6d4','#f97316','#6366f1','#14b8a6']

    weekly_p1 = df_vend_cat[df_vend_cat['Stagione'] == ref_season].copy()
    iso1 = weekly_p1['Data'].dt.isocalendar()
    weekly_p1['Year'] = iso1['year'].astype(int)
    weekly_p1['Season_Week'] = iso1['week'].astype(int)

    weekly_p2 = df_vend_cat[df_vend_cat['Stagione'] == comp_season].copy()
    iso2 = weekly_p2['Data'].dt.isocalendar()
    weekly_p2['Year'] = iso2['year'].astype(int)
    weekly_p2['Season_Week'] = iso2['week'].astype(int)

    wk_all = pd.concat([weekly_p1, weekly_p2])
    wk_agg = wk_all.groupby(['Stagione', 'Year', 'Season_Week'])['Qta_Venduta'].sum().reset_index()

    min_wk = wk_agg['Season_Week'].min()
    max_wk = wk_agg['Season_Week'].max()
    wk_range = list(range(int(min_wk), int(max_wk) + 1))

    def _stag_year(s):
        return 2000 + int(s[-2:])

    stagioni_uniche = sorted(set([ref_season, comp_season]))
    stag_color = {s: color_palette[i % len(color_palette)] for i, s in enumerate(stagioni_uniche)}

    coppie = wk_agg[['Stagione', 'Year']].drop_duplicates().sort_values(['Year', 'Stagione'])

    st.subheader("Vendite Settimanali per Stagione")
    fig_wk = go.Figure()

    for _, row in coppie.iterrows():
        stag, yr = row['Stagione'], row['Year']
        color = stag_color[stag]
        dash = 'dash' if yr != _stag_year(stag) else 'solid'
        d = wk_agg[(wk_agg['Stagione'] == stag) & (wk_agg['Year'] == yr)]
        d_full = d.set_index('Season_Week')[['Qta_Venduta']].reindex(wk_range, fill_value=0).reset_index()
        fig_wk.add_trace(go.Scatter(
            x=d_full['Season_Week'], y=d_full['Qta_Venduta'],
            mode='lines+markers', name=f'{stag} {yr}',
            line=dict(color=color, width=2, dash=dash),
            marker=dict(size=6)
        ))

    fig_wk.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif", color="#475569"),
        yaxis_title='Quantità Venduta',
        xaxis_title='Settimana Anno Solare (ISO)',
        hovermode='x unified'
    )
    fig_wk.update_yaxes(gridcolor='#f1f5f9')
    fig_wk.update_xaxes(dtick=1)
    st.plotly_chart(fig_wk, use_container_width=True)

    def _show_comp_matrix(df, group_col, title):
        st.markdown("<hr style='margin-top: 2rem; margin-bottom: 1rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
        st.subheader(f"Confronto {title}")

        display = df.rename(columns={
            group_col: title,
            'P1_Acq': f'Acq {ref_season}', 'P1_Vend': f'Vend {ref_season}', 'P1_ST%': f'ST% {ref_season}',
            'P2_Acq': f'Acq {comp_season}', 'P2_Vend': f'Vend {comp_season}', 'P2_ST%': f'ST% {comp_season}',
            'Delta_Acq': 'Δ Acq', 'Delta_Vend': 'Δ Vend', 'Delta_ST': 'Δ ST%'
        })

        st_cols = [title,
                   f'Acq {ref_season}', f'Vend {ref_season}', f'ST% {ref_season}',
                   f'Acq {comp_season}', f'Vend {comp_season}', f'ST% {comp_season}',
                   'Δ Acq', 'Δ Vend', 'Δ ST%']
        display = display[[c for c in st_cols if c in display.columns]]

        styled = (
            display.style
            .map(_c_str, subset=[f'ST% {ref_season}', f'ST% {comp_season}'])
            .map(_c_str_delta, subset=['Δ Acq', 'Δ Vend'])
            .map(_c_str_delta, subset=['Δ ST%'])
            .format({
                f'Acq {ref_season}': '{:.0f}', f'Vend {ref_season}': '{:.0f}', f'ST% {ref_season}': '{:.1f}%',
                f'Acq {comp_season}': '{:.0f}', f'Vend {comp_season}': '{:.0f}', f'ST% {comp_season}': '{:.1f}%',
                'Δ Acq': _fmt_delta, 'Δ Vend': _fmt_delta, 'Δ ST%': _fmt_delta_pct,
            })
        )
        st.dataframe(styled, use_container_width=True, height=400)

    _show_comp_matrix(comp_taglie, 'Taglia', 'Taglie')
    _show_comp_matrix(merge_period_comparison(vend_p1, acq_p1, vend_p2, acq_p2, 'Produttore'), 'Produttore', 'Produttori')
    comp_cat_full = merge_period_comparison(vend_p1, acq_p1, vend_p2, acq_p2, 'Categoria')
    comp_cat_full = comp_cat_full[(comp_cat_full['P1_Acq'] > 0) | (comp_cat_full['P2_Acq'] > 0)]
    _show_comp_matrix(comp_cat_full, 'Categoria', 'Categoria')
    comp_linea = merge_period_comparison(vend_p1, acq_p1, vend_p2, acq_p2, 'Linea')
    comp_linea = comp_linea[(comp_linea['P1_Acq'] > 0) | (comp_linea['P2_Acq'] > 0)]
    _show_comp_matrix(comp_linea, 'Linea', 'Linea')
