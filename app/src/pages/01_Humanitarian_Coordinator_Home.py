import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Humanitarian Coordinator, {st.session_state['first_name']}.")
st.write("### Humanitarian Support Dashboard")

st.write(
    "This is designed to help identify where humanitarian support may be needed. "
    "It focuses on country risk levels, displacement trends, and NGO activity across Europe."
)

st.divider()

st.subheader("Main Focus Areas")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Countries Tracked", "27")
    st.write("Monitor EU countries for climate risk and displacement pressure.")

with col2:
    st.metric("Risk Priority", "Low → Critical")
    st.write("Use risk levels to decide which countries may need attention first.")

with col3:
    st.metric("NGO Support", "Directory")
    st.write("Track organizations working in each country and update support records.")

st.divider()

st.subheader("Quick Actions")

button_col1, button_col2 = st.columns(2)

with button_col1:
    if st.button("View Risk Map",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/02_Map_Demo.py")

    if st.button("View Priority Countries",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/05_Priority_Countries.py")

    if st.button("Export Country Summary",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/06_Export_Country_Summary.py")

with button_col2:
    if st.button("View NGO Directory",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/14_NGO_Directory.py")

    if st.button("Add New NGO",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/15_Add_NGO.py")

    if st.button("View NGO Profile",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/16_NGO_Profile.py")
