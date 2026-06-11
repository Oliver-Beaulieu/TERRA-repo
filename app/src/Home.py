##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

st.session_state['authenticated'] = False

SideBarLinks(show_home=True)

logger.info("Loading the Home page of the app")

st.markdown("""
<style>
    /* ── Global page background + text ───────────────── */
    [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #0F1E33 !important;
    }
    /* default Streamlit text = white */
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] .stMarkdown p {
        color: #F4F7FB !important;
    }

    .terra-hero {
        background:
            radial-gradient(ellipse at 70% 50%, rgba(93,173,236,0.18) 0%, transparent 60%),
            radial-gradient(ellipse at 20% 80%, rgba(126,217,166,0.10) 0%, transparent 50%),
            linear-gradient(135deg, #060f1e 0%, #0d1f3c 50%, #0f2a45 100%);
        border-radius: 14px;
        padding: 52px 32px 44px 32px;
        text-align: center;
        margin-bottom: 8px;
        border: 1px solid #25415F;
    }
    .terra-title {
        font-size: 96px;
        font-weight: 900;
        letter-spacing: 16px;
        color: #F4F7FB;
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
        color: #7ED9A6;
        animation: glitch-top 7s infinite;
        clip-path: polygon(0 0, 100% 0, 100% 40%, 0 40%);
    }
    .terra-title::after {
        color: #5DADEC;
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
        font-size: 17px;
        color: #7ED9A6 !important;
        letter-spacing: 3px;
        font-weight: 400;
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        border-right: 2px solid #7ED9A6;
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
        50%      { border-color: #7ED9A6; }
    }
    .snapshot-number {
        font-size: 44px;
        font-weight: 800;
        color: #7ED9A6 !important;
        line-height: 1;
        margin-bottom: 6px;
    }
    .snapshot-label {
        font-size: 12px;
        color: #7ED9A6 !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #7ED9A6 !important;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
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
    st.markdown('<div class="snapshot-number">2</div><div class="snapshot-label">Predictive ML Models</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="snapshot-number">20+</div><div class="snapshot-label">Years of Historical Data</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="snapshot-number">3</div><div class="snapshot-label">Data Sources</div>', unsafe_allow_html=True)

st.caption("Powered by Open-Meteo, Eurostat, and World Bank datasets")

st.divider()

st.markdown('<div class="section-header">Choose a user persona to enter the app</div>', unsafe_allow_html=True)

# --- Fetch users from DB ---
def fetch_users(role_name):
    try:
        r = requests.get(f"http://web-api:4000/users/by-role/{role_name}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

analysts     = fetch_users("policy_analyst")
coordinators = fetch_users("humanitarian_coordinator")
students     = fetch_users("student_user")

def names(users):
    return [u["display_name"] for u in users]

def find_user(users, display_name):
    for u in users:
        if u["display_name"] == display_name:
            return u
    return None

def on_analyst_change():
    if st.session_state["analyst_select"] is not None:
        st.session_state["coordinator_select"] = None
        st.session_state["student_select"] = None

def on_coordinator_change():
    if st.session_state["coordinator_select"] is not None:
        st.session_state["analyst_select"] = None
        st.session_state["student_select"] = None

def on_student_change():
    if st.session_state["student_select"] is not None:
        st.session_state["analyst_select"] = None
        st.session_state["coordinator_select"] = None

col1, col2, col3, col4 = st.columns([3, 3, 3, 1.5])

with col1:
    analyst_user = st.selectbox(
        "🏛️ Policy Analyst",
        options=[None] + names(analysts),
        index=0,
        format_func=lambda x: "Select user..." if x is None else x,
        key="analyst_select",
        on_change=on_analyst_change,
    )

with col2:
    coordinator_user = st.selectbox(
        "🤝 Humanitarian Coordinator",
        options=[None] + names(coordinators),
        index=0,
        format_func=lambda x: "Select user..." if x is None else x,
        key="coordinator_select",
        on_change=on_coordinator_change,
    )

with col3:
    student_user = st.selectbox(
        "🎓 Climate-Displaced Student",
        options=[None] + names(students),
        index=0,
        format_func=lambda x: "Select user..." if x is None else x,
        key="student_select",
        on_change=on_student_change,
    )

with col4:
    st.markdown("<div style='margin-top:27px'></div>", unsafe_allow_html=True)
    login_clicked = st.button("Log in →", type="primary", use_container_width=True)

if login_clicked:
    chosen = None
    if analyst_user:
        u = find_user(analysts, analyst_user)
        chosen = (u, "policy_analyst", "pages/00_Policy_Analyst_Home.py")
    elif coordinator_user:
        u = find_user(coordinators, coordinator_user)
        chosen = (u, "humanitarian_coordinator", "pages/01_Humanitarian_Coordinator_Home.py")
    elif student_user:
        u = find_user(students, student_user)
        chosen = (u, "student_user", "pages/20_Mohammed_Home.py")

    if chosen is None:
        st.warning("Please select a user from one of the dropdowns before logging in.")
    else:
        u, role, page = chosen
        st.session_state['authenticated'] = True
        st.session_state['role'] = role
        st.session_state['first_name'] = u["display_name"].split()[0]
        st.session_state['display_name'] = u["display_name"]
        st.session_state['user_id'] = u["user_id"]
        st.session_state['email'] = u["email"]
        logger.info(f"Logging in as {u['display_name']} ({role})")
        st.switch_page(page)
