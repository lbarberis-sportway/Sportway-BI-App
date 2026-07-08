import pandas as pd
import os
import streamlit as st

DEFAULT_FILE_PATH = "data/Dati Excel/Analisi Fitness Adidas Taglie.xlsx"

def list_excel_files(directory="data/Dati Excel"):
    if not os.path.exists(directory):
        return []
    return sorted(f for f in os.listdir(directory) if f.endswith('.xlsx'))

SIZE_ORDER = [
    '0/3M', '3/6M', '6/9M', '9/12M', '12/18M', '18/24M',
    '2/3A', '3/4A', '4/5A', '5/6A', '6/7A', '7/8A', '9/10A',
    '11/12A', '13/14A', '14/15A', '15/16A',
    'KXXL', 'KXL',
    'XXS', 'XS', 'S', 'SAB', 'M', 'MAB', 'L', 'LAB', 'XL', 'XXL',
    'UNICA'
]

def sort_sizes(sizes):
    ordered = [s for s in SIZE_ORDER if s in sizes]
    remaining = sorted(s for s in sizes if s not in SIZE_ORDER)
    return ordered + remaining

def _taglia_cat_dtype(taglie_values=None):
    if taglie_values is not None:
        all_sizes = set(taglie_values)
        categories = [s for s in SIZE_ORDER if s in all_sizes] + sorted(s for s in all_sizes if s not in SIZE_ORDER)
        return pd.CategoricalDtype(categories=categories, ordered=True)
    return pd.CategoricalDtype(categories=SIZE_ORDER, ordered=True)

@st.cache_data(ttl=600)
def load_data(file_source=None):
    """Carica i dati dai due fogli Excel e standardizza i nomi delle colonne."""
    if file_source is None:
        file_source = DEFAULT_FILE_PATH
    
    if isinstance(file_source, str) and not os.path.exists(file_source):
        raise FileNotFoundError(f"File {file_source} non trovato.")
    
    # Carica fogli (pd.read_excel accetta sia stringhe che BytesIO)
    df_vend = pd.read_excel(file_source, sheet_name='VEND')
    df_acq = pd.read_excel(file_source, sheet_name='ACQ')
    
    # Rinomina colonne per evitare problemi con caratteri speciali
    df_vend.rename(columns=lambda x: x.strip(), inplace=True)
    df_acq.rename(columns=lambda x: x.strip(), inplace=True)
    
    # Unifica Deposito (ACQ) in Negozio per filtrare uniformemente
    if 'Deposito' in df_acq.columns:
        df_acq.rename(columns={'Deposito': 'Negozio'}, inplace=True)
    
    # Mappa manuale per le colonne di quantità
    for col in df_vend.columns:
        if "Quantit" in col and "Venduta" in col:
            df_vend.rename(columns={col: "Qta_Venduta"}, inplace=True)
            
    for col in df_acq.columns:
        if "Quantit" in col and "acquistata" in col.lower():
            df_acq.rename(columns={col: "Qta_Acquistata"}, inplace=True)
            
    # Gestione delle date
    if 'Data Vendita' in df_vend.columns:
        df_vend['Data'] = pd.to_datetime(df_vend['Data Vendita'], errors='coerce')
    if 'Data Acquisto' in df_acq.columns:
        df_acq['Data'] = pd.to_datetime(df_acq['Data Acquisto'], errors='coerce')

    # Convertiamo tutte le colonne categoriche in stringhe gestendo valori nulli e decimali
    cat_cols = ['Linea', 'Stagione', 'Taglia', 'Categoria', 'Produttore', 'Negozio']
    for col in cat_cols:
        if col in df_vend.columns:
            df_vend[col] = df_vend[col].fillna('N.D. / Unica').astype(str).str.replace(r'\.0$', '', regex=True)
            df_vend[col] = df_vend[col].replace('nan', 'N.D. / Unica')
        if col in df_acq.columns:
            df_acq[col] = df_acq[col].fillna('N.D. / Unica').astype(str).str.replace(r'\.0$', '', regex=True)
            df_acq[col] = df_acq[col].replace('nan', 'N.D. / Unica')

    return df_vend, df_acq

def get_date_reference(df_vend, df_acq):
    dates = pd.concat([
        df_vend[['Data']].dropna(),
        df_acq[['Data']].dropna()
    ]).drop_duplicates().sort_values('Data')
    return dates

def get_date_options(dates, year=None, quarter=None, month=None):
    df = dates.copy()
    years = sorted(df['Data'].dt.year.unique())
    if year is not None:
        df = df[df['Data'].dt.year == year]
    quarters = sorted(df['Data'].dt.quarter.unique())
    if quarter is not None:
        df = df[df['Data'].dt.quarter == quarter]
    months = sorted(df['Data'].dt.month.unique())
    if month is not None:
        df = df[df['Data'].dt.month == month]
    days = sorted(df['Data'].dt.day.unique())
    return years, quarters, months, days

def filter_by_date(df, year=None, quarter=None, month=None, day=None):
    df_filtered = df.copy()
    if year is not None:
        df_filtered = df_filtered[df_filtered['Data'].dt.year == year]
    if quarter is not None:
        df_filtered = df_filtered[df_filtered['Data'].dt.quarter == quarter]
    if month is not None:
        df_filtered = df_filtered[df_filtered['Data'].dt.month == month]
    if day is not None:
        df_filtered = df_filtered[df_filtered['Data'].dt.day == day]
    return df_filtered

def get_filtered_options(df_vend, df_acq, column, filters):
    """Estrae le opzioni uniche per una colonna applicando i filtri correnti (cascading)."""
    vend_f = filter_dataframe(df_vend, filters)
    acq_f = filter_dataframe(df_acq, filters)
    v_opts = set(vend_f[column].dropna().unique()) if column in vend_f.columns else set()
    a_opts = set(acq_f[column].dropna().unique()) if column in acq_f.columns else set()
    combined = list(v_opts.union(a_opts))
    if column == 'Taglia':
        return sort_sizes(combined)
    return sorted(combined)

def filter_dataframe(df, filters):
    """Applica i filtri al dataframe."""
    df_filtered = df.copy()
    for col, values in filters.items():
        if values and len(values) > 0 and col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[col].isin(values)]
    return df_filtered

def filter_by_date_range(df, year, end_month):
    """Filtra i dati dal 1 Gennaio alla fine del mese specificato."""
    df_filtered = df.copy()
    df_filtered = df_filtered[df_filtered['Data'].dt.year == year]
    df_filtered = df_filtered[df_filtered['Data'].dt.month <= end_month]
    return df_filtered

def filter_by_iso_week_range(df, iso_year, end_week):
    """Filtra i dati per anno ISO e settimana ISO (settimana 1 a end_week)."""
    df_filtered = df.copy()
    iso = df_filtered['Data'].dt.isocalendar()
    df_filtered = df_filtered[(iso['year'] == iso_year) & (iso['week'] <= end_week)]
    return df_filtered

@st.cache_data(ttl=60)
def merge_period_comparison(df_vend_p1, df_acq_p1, df_vend_p2, df_acq_p2, group_col='Taglia'):
    """Aggrega due periodi in un unico dataframe di confronto con delta."""
    all_vals = set()
    for df in [df_vend_p1, df_acq_p1, df_vend_p2, df_acq_p2]:
        if group_col in df.columns:
            all_vals.update(df[group_col].dropna().unique())

    if group_col == 'Taglia':
        dtype = _taglia_cat_dtype(all_vals)
    else:
        dtype = None

    def _agg(df_v, df_a):
        a = df_a.groupby(group_col, observed=True)['Qta_Acquistata'].sum().reset_index() if group_col in df_a.columns else pd.DataFrame()
        v = df_v.groupby(group_col, observed=True)['Qta_Venduta'].sum().reset_index() if group_col in df_v.columns else pd.DataFrame()
        if not a.empty and not v.empty:
            m = pd.merge(a, v, on=group_col, how='outer').fillna(0)
        elif not a.empty:
            m = a.copy()
            m['Qta_Venduta'] = 0
        elif not v.empty:
            m = v.copy()
            m['Qta_Acquistata'] = 0
        else:
            m = pd.DataFrame(columns=[group_col, 'Qta_Acquistata', 'Qta_Venduta'])
        cols = [c for c in [group_col, 'Qta_Acquistata', 'Qta_Venduta'] if c in m.columns]
        return m[cols]

    p1 = _agg(df_vend_p1, df_acq_p1)
    p2 = _agg(df_vend_p2, df_acq_p2)

    p1 = p1.rename(columns={'Qta_Acquistata': 'P1_Acq', 'Qta_Venduta': 'P1_Vend'})
    p2 = p2.rename(columns={'Qta_Acquistata': 'P2_Acq', 'Qta_Venduta': 'P2_Vend'})

    merged = pd.merge(p1, p2, on=group_col, how='outer').fillna(0)

    for c in ['P1_Acq', 'P1_Vend', 'P2_Acq', 'P2_Vend']:
        if c not in merged.columns:
            merged[c] = 0

    merged['P1_ST%'] = (merged['P1_Vend'] / merged['P1_Acq'] * 100).replace([float('inf'), -float('inf')], 0).fillna(0)
    merged['P2_ST%'] = (merged['P2_Vend'] / merged['P2_Acq'] * 100).replace([float('inf'), -float('inf')], 0).fillna(0)

    merged['Delta_Acq'] = merged['P1_Acq'] - merged['P2_Acq']
    merged['Delta_Vend'] = merged['P1_Vend'] - merged['P2_Vend']
    merged['Delta_ST'] = merged['P1_ST%'] - merged['P2_ST%']

    if dtype is not None:
        merged[group_col] = merged[group_col].astype(dtype)
        merged = merged.sort_values(group_col)
    else:
        merged = merged.sort_values('P1_Acq', ascending=False)

    return merged.reset_index(drop=True)

@st.cache_data(ttl=60)
def merge_and_aggregate(df_vend, df_acq):
    """Aggrega per Taglia e Stagione, e calcola il Sell-Through Rate."""
    all_taglie = set()
    if 'Taglia' in df_vend.columns:
        all_taglie.update(df_vend['Taglia'].dropna().unique())
    if 'Taglia' in df_acq.columns:
        all_taglie.update(df_acq['Taglia'].dropna().unique())
    taglia_dtype = _taglia_cat_dtype(all_taglie)

    # Aggregazione Vendite
    agg_vend = df_vend.groupby('Taglia', observed=True)['Qta_Venduta'].sum().reset_index()
    
    # Aggregazione Acquisti
    agg_acq = df_acq.groupby('Taglia', observed=True)['Qta_Acquistata'].sum().reset_index()
    
    # Merge
    merged = pd.merge(agg_acq, agg_vend, on='Taglia', how='outer').fillna(0)
    merged['Taglia'] = merged['Taglia'].astype(taglia_dtype)
    merged = merged.sort_values('Taglia')
    
    # Raggruppamento per Taglia e Stagione
    agg_vend_stag = df_vend.groupby(['Taglia', 'Stagione'], observed=True)['Qta_Venduta'].sum().reset_index()
    agg_acq_stag = df_acq.groupby(['Taglia', 'Stagione'], observed=True)['Qta_Acquistata'].sum().reset_index()
    merged_stag = pd.merge(agg_acq_stag, agg_vend_stag, on=['Taglia', 'Stagione'], how='outer').fillna(0)
    merged_stag['Taglia'] = merged_stag['Taglia'].astype(taglia_dtype)
    merged_stag = merged_stag.sort_values('Taglia')
    
    # Calcolo Sell-Through Rate
    merged_stag['Sell_Through_%'] = (merged_stag['Qta_Venduta'] / merged_stag['Qta_Acquistata']) * 100
    merged_stag['Sell_Through_%'] = merged_stag['Sell_Through_%'].replace([float('inf'), -float('inf')], 0).fillna(0)
    
    return merged_stag, merged
