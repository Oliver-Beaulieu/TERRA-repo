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

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the Home page of the app")
st.markdown(
    "<h1 style='text-align: center; font-size: 72px;'> T.E.R.R.A</h1>",
    unsafe_allow_html=True
)

st.write('#### Tracking European Climate Risk & Refugee Asylum')

st.divider()

st.write("#### Project Snapshot")

col1, col2 = st.columns(2)

with col1:
    st.metric("Countries", "27")
    st.write("EU member states included in the project")

with col2:
    st.metric("Sources", "3+")
    st.write("Open-Meteo, Eurostat, and World Bank")

st.divider()

st.write("#### Choose a user persona to enter the app")


# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

if st.button("Act as Gabriel, a Political Analyst",
             type='primary',
             use_container_width=True):
    # when user clicks the button, they are now considered authenticated
    st.session_state['authenticated'] = True
    # we set the role of the current user
    st.session_state['role'] = 'policy_analyst'
    # we add the first name of the user (so it can be displayed on
    # subsequent pages).
    st.session_state['first_name'] = 'Gabriel'
    # finally, we ask streamlit to switch to another page, in this case, the
    # landing page for this particular user type
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






