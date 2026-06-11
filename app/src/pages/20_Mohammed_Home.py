import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}.")
st.write("### Climate & Displacement Explorer")

st.write(
    "This dashboard is designed to help you explore climate-driven displacement trends across Europe. "
)

st.divider()

st.subheader("Main Focus Areas")

col1, col2 = st.columns(2)

with col1:
    st.metric("Countries Tracked", "27")
    st.write("Explore EU countries and their climate risk and displacement data.")

with col2:
    st.metric("Displacement Data", "Timeline View")
    st.write("Track how asylum and displacement numbers have shifted over time.")

st.divider()

st.subheader("Quick Actions")

button_col1, button_col2 = st.columns(2)

with button_col1:
    if st.button("Explore Risk Map",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/02_Map_Demo.py")

    if st.button("Climate Events",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/07_Climate_Events.py")

with button_col2:
    if st.button("Displacement Timeline",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/08_Displacement_Timeline.py")

    if st.button("Similar Countries",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/09_Similar_Countries.py")

    if st.button("My Watchlist",
                 type="primary",
                 use_container_width=True):
        st.switch_page("pages/21_My_Watchlist.py")
