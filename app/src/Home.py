##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

st.session_state['authenticated'] = False

SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the Home page of the app")

st.markdown("""
<style>
    .terra-hero {
        background: linear-gradient(135deg, #050c1a 0%, #0d1f3c 55%, #102b4a 100%);
        border-radius: 16px;
        padding: 48px 32px 40px 32px;
        text-align: center;
        margin-bottom: 8px;
        border: 1px solid #1a3a5c;
    }
    .terra-title {
        font-size: 96px;
        font-weight: 900;
        letter-spacing: 16px;
        color: #ffffff;
        margin: 0;
        text-shadow: 0 4px 32px rgba(61,186,126,0.4);
    }
    .terra-subtitle {
        font-size: 18px;
        color: #7dd9b0;
        letter-spacing: 3px;
        margin-top: 12px;
        font-weight: 400;
    }
    .snapshot-card {
        background: #0d1530;
        border-left: 5px solid #3dba7e;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 8px;
    }
    .snapshot-number {
        font-size: 48px;
        font-weight: 800;
        color: #3dba7e;
        line-height: 1;
    }
    .snapshot-label {
        font-size: 13px;
        color: #8ab8a8;
        margin-top: 4px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #7dd9b0;
        margin-bottom: 12px;
    }
</style>

<div class="terra-hero">
    <div class="terra-title">T.E.R.R.A</div>
    <div class="terra-subtitle">Tracking European Climate Risk &amp; Refugee Asylum</div>
</div>
""", unsafe_allow_html=True)

st.divider()

st.markdown('<div class="section-header">Project Snapshot</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="snapshot-card">
        <div class="snapshot-number">27</div>
        <div class="snapshot-label">EU Member States</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="snapshot-card">
        <div class="snapshot-number">3+</div>
        <div class="snapshot-label">Data Sources</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="snapshot-card">
        <div class="snapshot-number">3</div>
        <div class="snapshot-label">User Personas</div>
    </div>
    """, unsafe_allow_html=True)

st.caption("Data from Open-Meteo, Eurostat, and World Bank")

st.divider()

st.markdown('<div class="section-header">Choose a user persona to enter the app</div>', unsafe_allow_html=True)

if st.button("Act as Gabriel, a Political Analyst",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'policy_analyst'
    st.session_state['first_name'] = 'Gabriel'
    logger.info("Logging in as Gabriel Policy Analyst Persona")
    st.switch_page('pages/00_Policy_Analyst_Home.py')

if st.button('Act as Diana, a Humanitarian Coordinator',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'humanitarian_coordinator'
    st.session_state['first_name'] = 'Diana'
    logger.info("Logging in as Diana Humanitarian Coordinator Persona")
    st.switch_page('pages/01_Humanitarian_Coordinator_Home.py')

if st.button('Act as Mohammed, a Climate-Displaced Student',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'student_user'
    st.session_state['first_name'] = 'Mohammed'
    logger.info("Logging in as Mohammed Student Persona")
    st.switch_page('pages/20_Mohammed_Home.py')






