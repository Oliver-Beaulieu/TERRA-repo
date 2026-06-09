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
        position: relative;
        display: inline-block;
        animation: glitch-main 7s infinite;
    }
    .terra-title::before,
    .terra-title::after {
        content: attr(data-text);
        position: absolute;
        top: 0; left: 0;
        width: 100%;
        font-size: 96px;
        font-weight: 900;
        letter-spacing: 16px;
        overflow: hidden;
    }
    .terra-title::before {
        color: #3dba7e;
        animation: glitch-top 7s infinite;
        clip-path: polygon(0 0, 100% 0, 100% 40%, 0 40%);
    }
    .terra-title::after {
        color: #00cfff;
        animation: glitch-bot 7s infinite;
        clip-path: polygon(0 55%, 100% 55%, 100% 75%, 0 75%);
    }
    @keyframes glitch-main {
        0%, 90%, 100%  { transform: none; filter: none; }
        91%            { transform: skewX(-4deg) translateX(6px); filter: brightness(1.3); }
        92%            { transform: skewX(4deg) translateX(-8px); }
        93%            { transform: skewX(-2deg) translateX(4px); filter: none; }
        94%            { transform: none; }
        96%            { transform: translateX(-5px) skewX(2deg); filter: brightness(1.2); }
        97%            { transform: translateX(5px); }
        98%            { transform: none; filter: none; }
    }
    @keyframes glitch-top {
        0%, 89%, 100%  { opacity: 0; transform: translateX(0); }
        90%            { opacity: 1; transform: translateX(-12px) skewX(-5deg); }
        91%            { transform: translateX(10px) skewX(3deg); }
        92%            { transform: translateX(-6px); }
        93%            { transform: translateX(8px) skewX(-2deg); }
        94%            { transform: translateX(0); }
        95%            { opacity: 1; transform: translateX(-10px); }
        96%            { transform: translateX(6px); }
        97%            { opacity: 0; }
    }
    @keyframes glitch-bot {
        0%, 89%, 100%  { opacity: 0; transform: translateX(0); }
        90%            { opacity: 1; transform: translateX(12px) skewX(5deg); }
        91%            { transform: translateX(-10px) skewX(-3deg); }
        92%            { transform: translateX(6px); }
        93%            { transform: translateX(-8px) skewX(2deg); }
        94%            { transform: translateX(0); }
        95%            { opacity: 1; transform: translateX(10px); }
        96%            { transform: translateX(-6px); }
        97%            { opacity: 0; }
    }
    .terra-subtitle-wrap {
        display: block;
        width: 100%;
        margin-top: 20px;
        text-align: center;
    }
    .terra-subtitle {
        font-size: 18px;
        color: #7dd9b0;
        letter-spacing: 3px;
        font-weight: 400;
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        border-right: 2px solid #3dba7e;
        max-width: 0px;
        animation: typewriter 6s steps(47, end) 1s infinite,
                   blink-cursor 0.75s step-end infinite;
    }
    @keyframes typewriter {
        0%   { max-width: 0px; }
        50%  { max-width: 900px; }
        75%  { max-width: 900px; }
        95%  { max-width: 0px; }
        100% { max-width: 0px; }
    }
    @keyframes blink-cursor {
        from, to { border-color: transparent; }
        50%      { border-color: #3dba7e; }
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
    <div class="terra-title" data-text="T.E.R.R.A">T.E.R.R.A</div>
    <div class="terra-subtitle-wrap">
        <span class="terra-subtitle">Tracking European Climate Risk &amp; Refugee Asylum</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

st.markdown('<div class="section-header">TERRA at a Glance</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="snapshot-card">
        <div class="snapshot-number">2</div>
        <div class="snapshot-label">Predictive ML Models</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="snapshot-card">
        <div class="snapshot-number">20+</div>
        <div class="snapshot-label">Years of Historical Data</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="snapshot-card">
        <div class="snapshot-number">3</div>
        <div class="snapshot-label">Data Sources</div>
    </div>
    """, unsafe_allow_html=True)

st.caption("Powered by Open-Meteo, Eurostat, and World Bank datasets")

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






