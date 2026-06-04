import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Policy Analyst, {st.session_state['first_name']}.")
st.write("### Policy Analysis Dashboard")

st.write(
    "This is designed to help look at country trends, compare risk patterns, "
    "and support policy decisions related to climate risk and refugee asylum across Europe."
)

st.divider()

st.subheader("Main Focus")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Countries Tracked", "27")
    st.write("Compare EU countries using climate and displacement")

with col2:
    st.metric("Risk Review", "...")
    st.write("Review risk levels to identify countries that may need policy attention.")

with col3:
    st.metric("Model Output", "...")
st.divider()

st.subheader("Quick Actions")

button_col1, button_col2 = st.columns(2)
with button_col1:
    if st.button("Compare Countries",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/03_Compare_Countries.py")

    if st.button("View Risk Classification",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/13_Classification.py")

    if st.button("Export / Reports",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/04_Export_Reports.py")

with button_col2:
    if st.button("View Prediction Model",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/11_Prediction.py")

    if st.button("View Risk Map",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/02_Map_Demo.py")

if st.button('Saved views — your stored comparisons',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/10_Saved_Views.py')
