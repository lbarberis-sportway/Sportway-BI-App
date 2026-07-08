import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="Sportway BI",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Caricamento Configurazione Login ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- Login ---
try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state["authentication_status"]:
    # L'utente è loggato
    authenticator.logout("Logout", "sidebar")
    
    # Recupera i ruoli dell'utente (è una lista, prendiamo il primo)
    roles = st.session_state.get("roles", [])
    user_role = roles[0] if roles else "user"
    
    st.sidebar.markdown(f"**Utente:** {st.session_state['name']}")
    st.sidebar.markdown(f"**Ruolo:** {user_role}")
    
    # --- Configurazione Pagine in base al ruolo ---
    
    # Pagine disponibili
    home_page = st.Page("views/home.py", title="Home", icon="🏠")
    incassi_page = st.Page("views/1_Incassi.py", title="Incassi", icon="💰")
    taglie_page = st.Page("views/2_Taglie.py", title="Taglie", icon="📏")
    magazzino_page = st.Page("views/3_Magazzino.py", title="Magazzino", icon="📦")
    
    if user_role == "admin":
        pages = {
            "Principale": [home_page],
            "Dashboard": [incassi_page, taglie_page, magazzino_page]
        }
    elif user_role == "venditore":
        # Il venditore vede solo le Taglie. Aggiungiamo anche la Home così ha un punto di partenza.
        pages = {
            "Dashboard": [taglie_page]
        }
    else:
        # Default per ruoli sconosciuti (non dovrebbe succedere se il yaml è configurato bene)
        pages = {
            "Principale": [home_page]
        }
        
    pg = st.navigation(pages)
    pg.run()
    
elif st.session_state["authentication_status"] is False:
    st.error('Username o password non corretti')
elif st.session_state["authentication_status"] is None:
    st.warning('Inserisci username e password')
