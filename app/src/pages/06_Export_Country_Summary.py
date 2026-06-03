import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Export Country Summary")
st.write("### Generate a country-level humanitarian summary")

st.write(
    "This page allows you to view a specific countries infoormation and dive deep into it. "
)

st.divider()

selected_country = st.selectbox(
    "Select a country",
    ["Greece", "Italy", "Spain", "Germany", "France"]
)

st.subheader(f"{selected_country} Humanitarian Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Risk Level", "TBD")

with col2:
    st.metric("Asylum Applications", "TBD")

with col3:
    st.metric("Active NGOs", "TBD")

st.write("#### Summary Notes")

st.write(
    f"{selected_country} will have a short summary here showing climate stressors, "
    "displacement pressure, NGO coverage, and recommended humanitarian action."
)

st.divider()

if st.button("Generate PDF Summary", type="primary", use_container_width=True):
    st.info("*PLACEHOLDER - YADIEL WILL FIX")