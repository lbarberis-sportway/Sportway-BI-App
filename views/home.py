import streamlit as st

# --- CSS Home Page ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .hero-header {
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e40af, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #64748b;
        font-weight: 400;
        margin-bottom: 2.5rem;
    }
    .dash-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: pointer;
        height: 100%;
    }
    .dash-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.15);
        border-color: #93c5fd;
    }
    .dash-card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    .dash-card-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .dash-card-desc {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.5;
    }
    .dash-card-badge {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.3rem 0.8rem;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #1d4ed8;
        background: #dbeafe;
    }
    .section-divider {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 2.5rem 0;
    }
    .footer-note {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        padding: 1rem 0 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("assets/logo.png", width=80)
    except Exception:
        st.write("Logo")
with col_title:
    st.markdown("<div style='padding-top: 16px;'><span class='hero-title'>Sportway BI</span></div>", unsafe_allow_html=True)

st.markdown("<p class='hero-subtitle'>Piattaforma di Business Intelligence per l'analisi delle performance dei negozi Sportway.</p>", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# --- CARD DASHBOARD ---
st.markdown("### Seleziona una Dashboard")
st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-title">Analisi Incassi</div>
        <div class="dash-card-desc">
            Confronta le performance di incasso settimana per settimana, analizza il YTD, 
            i periodi personalizzati e le matrici mensili per negozio.
        </div>
        <span class="dash-card-badge">Anno su Anno · YTD · Saldi</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # Using switch_page as we don't have implicit st.page_link if it relies on "pages/" being present.
    # But wait, with st.navigation, st.page_link requires the Page object or the file path used in st.navigation.
    if st.button("Apri Dashboard Incassi →", use_container_width=True):
        st.switch_page("views/1_Incassi.py")

with c2:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-title">Analisi Taglie</div>
        <div class="dash-card-desc">
            Esplora acquisti vs vendite per taglia, categoria, stagione e produttore. 
            Calcola il Sell-Through rate e confronta le stagioni tra loro.
        </div>
        <span class="dash-card-badge">Sell-Through · Stagioni · Filtri Avanzati</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Apri Dashboard Taglie →", use_container_width=True):
        st.switch_page("views/2_Taglie.py")

with c3:
    st.markdown("""
    <div class="dash-card">
        <div class="dash-card-title">Tempo di Stock Magazzino</div>
        <div class="dash-card-desc">
            Analizza il ciclo di vita degli articoli: dal magazzino al negozio alla vendita. 
            Calcola il Lead Time totale con algoritmo FIFO.
        </div>
        <span class="dash-card-badge">FIFO · Lead Time · Scaffale</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Apri Dashboard Magazzino →", use_container_width=True):
        st.switch_page("views/3_Magazzino.py")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer-note">
    Sportway BI &nbsp;·&nbsp; Piattaforma interna di analisi dati
</div>
""", unsafe_allow_html=True)
