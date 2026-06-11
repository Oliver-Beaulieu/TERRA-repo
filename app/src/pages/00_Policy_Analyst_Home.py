import logging
logger = logging.getLogger(__name__)

import requests
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

API_BASE = "http://web-api:4000"

# fetch active policy notes count
try:
    r = requests.get(f"{API_BASE}/policy", timeout=5)
    policies = r.json() if r.status_code == 200 else []
    active_notes = sum(1 for p in policies if p.get("status") == "Active")
except Exception:
    active_notes = "—"

# fetch count of Critical countries from risk classifications
try:
    r = requests.get(f"{API_BASE}/risk/classifications", timeout=5)
    risks = r.json() if r.status_code == 200 else []
    # get the latest year per country then count Critical ones
    seen = {}
    for row in risks:
        cid = row["country_id"]
        if cid not in seen or row["year"] > seen[cid]["year"]:
            seen[cid] = row
    critical_count = sum(1 for row in seen.values() if row.get("risk_level") == "Critical")
except Exception:
    critical_count = "—"

st.divider()

st.subheader("Main Focus")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Countries Tracked", "27")
    st.write("Compare EU countries using climate and displacement data.")

with col2:
    st.metric("Active Policy Notes", active_notes)
    st.write("Policy notes flagged across EU countries currently marked active.")

with col3:
    st.metric("Critical Countries", critical_count)
    st.write("Countries currently at the highest risk level across all three indicators.")
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

    if st.button('Saved views — your stored comparisons',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/10_Saved_Views.py')
