import pandas as pd
import streamlit as st

@st.cache_data
def load_and_process_data(entrate_path, uscite_path, vendite_path=None):
    # FASE 1: ENTRATE -> USCITE (Tempo di Giacenza Magazzino)
    df_entrate = pd.read_excel(entrate_path)
    df_uscite = pd.read_excel(uscite_path)
    
    df_entrate.columns = df_entrate.columns.str.strip()
    df_uscite.columns = df_uscite.columns.str.strip()
    
    for df in [df_entrate, df_uscite]:
        for col in df.columns:
            if 'Quantit' in col:
                df.rename(columns={col: 'Quantita'}, inplace=True)
                break
                
    df_entrate['Data'] = pd.to_datetime(df_entrate['Data'])
    df_uscite['Data'] = pd.to_datetime(df_uscite['Data'])
    
    df_entrate = df_entrate.sort_values(by='Data').reset_index(drop=True)
    df_uscite = df_uscite.sort_values(by='Data').reset_index(drop=True)
    
    df_entrate = df_entrate.dropna(subset=['Barcode', 'Quantita'])
    df_uscite = df_uscite.dropna(subset=['Barcode', 'Quantita'])
    
    entrate_dict = {}
    for idx, row in df_entrate.iterrows():
        barcode = row['Barcode']
        if barcode not in entrate_dict:
            entrate_dict[barcode] = []
        entrate_dict[barcode].append({
            'Data_Entrata': row['Data'],
            'Quantita_Disponibile': row['Quantita'],
            'Categoria': row.get('Categoria', 'N/D'),
            'Linea': row.get('Linea', 'N/D'),
            'Stagione': row.get('Stagione', 'N/D'),
            'Produttore': row.get('Produttore', 'N/D'),
            'Articolo': row.get('Articolo / Prodotto', 'N/D')
        })
        
    matched_records = []
    
    for idx, row in df_uscite.iterrows():
        barcode = row['Barcode']
        qta_uscita = row['Quantita']
        data_uscita = row['Data']
        negozio_uscita = row.get('Negozio', 'N/D')
        
        if barcode in entrate_dict:
            queue = entrate_dict[barcode]
            while qta_uscita > 0 and queue:
                entrata = queue[0]
                
                qta_da_scalare = min(qta_uscita, entrata['Quantita_Disponibile'])
                
                matched_records.append({
                    'Barcode': barcode,
                    'Articolo': entrata['Articolo'],
                    'Categoria': entrata['Categoria'],
                    'Linea': entrata['Linea'],
                    'Stagione': entrata['Stagione'],
                    'Produttore': entrata['Produttore'],
                    'Data_Entrata': entrata['Data_Entrata'],
                    'Data_Uscita': data_uscita,
                    'Negozio_Uscita': negozio_uscita,
                    'Quantita': qta_da_scalare,
                    'Tempo_di_Stock_Giorni': max((data_uscita - entrata['Data_Entrata']).days, 0)
                })
                
                qta_uscita -= qta_da_scalare
                entrata['Quantita_Disponibile'] -= qta_da_scalare
                
                if entrata['Quantita_Disponibile'] <= 0:
                    queue.pop(0)
                    
    df_matched = pd.DataFrame(matched_records)
    
    # FASE 2: USCITE -> VENDITE (Tempo di Scaffale e Lead Time Totale)
    df_vendite = None
    if vendite_path:
        df_vendite = pd.read_excel(vendite_path)
        df_vendite.columns = df_vendite.columns.str.strip()
        
        for col in df_vendite.columns:
            if 'Quantit' in col:
                df_vendite.rename(columns={col: 'Quantita_Venduta'}, inplace=True)
                break
                
        df_vendite['Data Vendita'] = pd.to_datetime(df_vendite['Data Vendita'])
        df_vendite.rename(columns={'Data Vendita': 'Data_Vendita'}, inplace=True)
        df_vendite = df_vendite.sort_values(by='Data_Vendita').reset_index(drop=True)
        df_vendite = df_vendite.dropna(subset=['Barcode', 'Quantita_Venduta'])
        
        # Coda delle uscite per Barcode
        uscite_dict = {}
        for idx, row in df_matched.iterrows():
            barcode = row['Barcode']
            if barcode not in uscite_dict:
                uscite_dict[barcode] = []
            uscite_dict[barcode].append({
                'Data_Entrata': row['Data_Entrata'],
                'Data_Uscita': row['Data_Uscita'],
                'Quantita_Disponibile': row['Quantita'],
                'Tempo_di_Stock_Giorni': row['Tempo_di_Stock_Giorni'],
                'Categoria': row['Categoria'],
                'Linea': row['Linea'],
                'Stagione': row['Stagione'],
                'Produttore': row['Produttore'],
                'Articolo': row['Articolo']
            })
            
        full_lifecycle_records = []
        
        for idx, row in df_vendite.iterrows():
            barcode = row['Barcode']
            qta_vendita = row['Quantita_Venduta']
            data_vendita = row['Data_Vendita']
            negozio_vendita = row.get('Negozio', 'N/D')
            
            if barcode in uscite_dict:
                queue = uscite_dict[barcode]
                
                if qta_vendita > 0:
                    while qta_vendita > 0 and queue:
                        uscita = queue[0]
                        
                        qta_da_scalare = min(qta_vendita, uscita['Quantita_Disponibile'])
                        
                        tempo_scaffale = max((data_vendita - uscita['Data_Uscita']).days, 0)
                        tempo_totale = uscita['Tempo_di_Stock_Giorni'] + tempo_scaffale
                        
                        full_lifecycle_records.append({
                            'Barcode': barcode,
                            'Articolo': uscita['Articolo'],
                            'Categoria': uscita['Categoria'],
                            'Linea': uscita['Linea'],
                            'Stagione': uscita['Stagione'],
                            'Produttore': uscita['Produttore'],
                            'Data_Entrata': uscita['Data_Entrata'],
                            'Data_Uscita': uscita['Data_Uscita'],
                            'Data_Vendita': data_vendita,
                            'Negozio': negozio_vendita,
                            'Quantita': qta_da_scalare,
                            'Tempo_di_Stock_Giorni': uscita['Tempo_di_Stock_Giorni'],
                            'Tempo_di_Scaffale_Giorni': tempo_scaffale,
                            'Lead_Time_Totale_Giorni': tempo_totale
                        })
                        
                        qta_vendita -= qta_da_scalare
                        uscita['Quantita_Disponibile'] -= qta_da_scalare
                        
                        if uscita['Quantita_Disponibile'] <= 0:
                            queue.pop(0)
                elif qta_vendita < 0 and queue:
                    qta_reso = -qta_vendita
                    queue[-1]['Quantita_Disponibile'] += qta_reso
                        
        df_matched = pd.DataFrame(full_lifecycle_records)
        
    return df_entrate, df_uscite, df_matched, df_vendite
