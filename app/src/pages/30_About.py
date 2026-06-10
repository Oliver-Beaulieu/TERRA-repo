import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks(show_home=True)

st.title("About TERRA")

st.write(
    "**TERRA — Tracking European Climate Risk & Refugee Asylum** is an application "
    "which helps explore how climate change and human displacement are connected "
    "by looking at the 27 member states of the European Union. Climate change is a real and "
    "is a present threat, from rising sea levels and high temperatures to wildfires and "
    "flooding, it's forcing people to move from their homes. Yet no tool brings together "
    "climate disasters and the displacement data they drive. TERRA was built to fill this gap. "
)

st.divider()
st.subheader("What the App Does")
st.write(
    "TERRA combines climate indicators, disaster records, and asylum "
    "statistics from public international datasets. Users can explore maps, "
    "compare countries, look into individual nations, and track how displacement trends "
    "have evolved over time. Machine learning models help classify climate displacement "
    "risk levels and surface countries facing similar pressures."
)

st.subheader("Our Goals")
st.write(
    "- Makes it easier to understand the relationship between climate events and displacement\n"
    "- Supports better decisions about where humanitarian attention and resources are needed\n"
)

st.subheader("Who It's For")
st.write(
    "TERRA is built around three users, a policy analyst reviewing country trends to "
    "inform EU policy, a humanitarian coordinator that determines where to give support, "
    "and a climate-displaced student looking to understand regions affected like their own."
)

st.divider()
st.subheader("The Team")
st.write("TERRA was built by four Computer Science students at Northeastern University:")

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Yadiel Cruz**")
    st.caption("Hi, I’m Yadiel, a Computer Science and Economics student at Northeastern University. I hope TERRA helps make climate and displacement data easier to understand by showing how climate risks can significantly shape movement across Europe.")
    st.image("assets/Yadiel_Cruz.jpg", width=450)
    st.markdown("**Hamza Chakir**")
    st.caption("Second-year CS student.")
with c2:
    st.markdown("**Oliver Beaulieu**")
    st.caption("I'm a 4th year Computer Science and Cognitive Pyschology student at Northeastern University. I hope that TERRA is used to help create actionable plans to combat climate challanges that we see today.")
    st.image("assets/oliver_photo.jpg", width=450)
    st.markdown("**James Chan**")
    st.caption("Computer Science.")

st.divider()
st.caption("Summer 2026 · Data and Software in International Government and Politics Dialogue of Civilizations · Northeastern University")