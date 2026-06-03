import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('System Admin Home Page')
st.write('### What would you like to do today?')

## When I added a second button to this page, the first stopped working
## Here's a way you might resolve this:
btn1 = st.button('Update ML Models', type='primary', use_container_width=True)
btn2 = st.button('Try Out My Better ML Model', type='primary', use_container_width=True)

if btn1:
    st.switch_page('pages/21_ML_Model_Mgmt.py')
if btn2:
    st.switch_page('pages/22_Prettier_ML.py')