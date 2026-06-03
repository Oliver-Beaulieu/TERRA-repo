import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Priority Countries")
st.write("### Countries that may need humanitarian attention first")

st.write(
    "This page ranks countries by risk level, displacement pressure, and NGO coverage. "
    "*PLACEHOLDER DATA - GROUP WILL REVIST"
)

st.divider()

priority_data = [
    {
        "Country": "Greece",
        "Risk Level": "Critical",
        "Displacement Pressure": "High",
        "Main Climate Stressor": "Wildfire + Heat",
        "NGO Coverage": "Medium",
        "Recommended Action": "Review resources"
    },
    {
        "Country": "Italy",
        "Risk Level": "Critical",
        "Displacement Pressure": "High",
        "Main Climate Stressor": "Flooding + Heat",
        "NGO Coverage": "Medium",
        "Recommended Action": "Coordinate NGO support"
    },
    {
        "Country": "Spain",
        "Risk Level": "High",
        "Displacement Pressure": "Moderate",
        "Main Climate Stressor": "Drought + Heat",
        "NGO Coverage": "Low",
        "Recommended Action": "Monitor closely"
    },
    {
        "Country": "Germany",
        "Risk Level": "Moderate",
        "Displacement Pressure": "Moderate",
        "Main Climate Stressor": "Flooding",
        "NGO Coverage": "High",
        "Recommended Action": "Continue monitoring"
    }
]

st.dataframe(priority_data, use_container_width=True)
