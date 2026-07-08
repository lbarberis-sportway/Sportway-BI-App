# Sportway BI

Piattaforma di Business Intelligence per l'analisi delle performance dei negozi Sportway.

## Architettura del progetto

```mermaid
graph TD
    subgraph Avvio
        A[app.py] --> B[config.yaml<br/>Login]
        B --> C{Ruolo?}
        C -->|admin| D[Home, Incassi,<br/>Taglie, Magazzino]
        C -->|venditore| E[Taglie]
    end

    subgraph assets
        F[style.css]
        G[logo.png]
    end

    subgraph views
        H[home.py] --> I[Dashboard cards]
        J[1_Incassi.py] --> K[Excel: Incassi Negozio]
        L[2_Taglie.py] --> M[Excel: Dati Excel/*.xlsx]
        N[3_Magazzino.py] --> O[Excel: Entrate,<br/>Uscite, Vendite]
    end

    subgraph utils
        P[data_engine.py] --> L
        Q[data_loader.py] --> N
    end

    style A fill:#3b82f6,color:#fff
    style J fill:#10b981,color:#fff
    style L fill:#f59e0b,color:#fff
    style N fill:#8b5cf6,color:#fff
```

```mermaid
mindmap
  root((Sportway-BI-App))
    app.py
    config.yaml
    requirements.txt
    .streamlit
      config.toml
    assets
      style.css
      logo.png
    data
      INCASSI_NEGOZI_ANALISI.xlsx
      VENDITE.xlsx
      Dati Excel
    utils
      data_engine.py
      data_loader.py
      generate_hash.py
    views
      home.py
      1_Incassi.py
      2_Taglie.py
      3_Magazzino.py
```

## Requisiti

- Python 3.11+
- Dipendenze in `requirements.txt`

## Installazione

```bash
pip install -r requirements.txt
```

## Avvio

```bash
streamlit run app.py
```

## Dati

I file Excel nella cartella `data/` contengono i dati di vendita, incassi e magazzino.

## Autenticazione

Due ruoli disponibili in `config.yaml`:
- **admin** — accesso a tutte le dashboard
- **venditore** — accesso solo alla dashboard Taglie
