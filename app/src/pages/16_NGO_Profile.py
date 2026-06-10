import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("NGO Profile")

ngo_id = st.session_state.get("selected_ngo_id")

if ngo_id is None:
    st.info("Please select an NGO from the directory first.")
    if st.button("Go to NGO Directory"):
        st.switch_page("pages/14_NGO_Directory.py")
    st.stop()

# Load NGO
try:
    response = requests.get(f"http://web-api:4000/ngo/ngos/{ngo_id}")
    ngo = response.json() if response.status_code == 200 else None
except requests.exceptions.RequestException as e:
    st.error("Could not connect to the API.")
    st.write(e)
    st.stop()

if not ngo:
    st.error("NGO not found.")
    st.stop()

# ── Basic info ────────────────────────────────────────────────────────────────

st.header(ngo["Name"])
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Organisation Information")
    st.write(f"**Country:** {ngo['Country']}")
    st.write(f"**Founded:** {ngo['Founding_Year']}")
    st.write(f"**Focus Area:** {ngo['Focus_Area']}")
    st.write(f"**Website:** [{ngo['Website']}]({ngo['Website']})")
    if ngo.get("Notes"):
        st.write(f"**Notes:** {ngo['Notes']}")

with col2:
    st.subheader("Actions")
    if st.button("🗑 Remove This NGO", type="primary", use_container_width=True):
        try:
            r = requests.delete(f"http://web-api:4000/ngo/ngos/{ngo_id}")
            if r.status_code == 200:
                st.success(f"{ngo['Name']} has been removed.")
                del st.session_state["selected_ngo_id"]
                st.switch_page("pages/14_NGO_Directory.py")
            else:
                st.error("Failed to remove NGO.")
        except requests.exceptions.RequestException as e:
            st.error("Could not connect to the API.")
            st.write(e)

# ── Climate context ───────────────────────────────────────────────────────────

st.divider()
st.subheader("Climate Context")
st.write(
    "Select an EU country this NGO operates in to see its climate indicators. "
    "Use this to understand the conditions on the ground where this organisation is active."
)

try:
    r = requests.get("http://web-api:4000/countries", timeout=5)
    countries = r.json() if r.status_code == 200 else []
except Exception:
    countries = []

if not countries:
    st.warning("Could not load country climate data.")
else:
    name_to_country = {c["country_name"]: c for c in countries}
    selected = st.selectbox("Select EU country", sorted(name_to_country.keys()))

    try:
        r = requests.get(f"http://web-api:4000/countries/{name_to_country[selected]['country_id']}/year-data", timeout=5)
        rows = r.json() if r.status_code == 200 else []
    except Exception:
        rows = []

    if rows:
        df = pd.DataFrame(rows).sort_values("year")
        latest = df.iloc[-1]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Avg Heatwave Days",     f"{df['heatwave_days'].mean():.1f} /yr")
        m2.metric("Avg Heavy Rainfall Days", f"{df['precip_days_heavy'].mean():.1f} /yr")
        m3.metric("Avg Dry Days",          f"{df['dry_days'].mean():.0f} /yr")
        m4.metric("Avg Temp",              f"{pd.to_numeric(df['temp_mean'], errors='coerce').mean():.1f} °C")

        st.caption(f"Based on {int(df['year'].min())}–{int(df['year'].max())} data.")
    else:
        st.warning(f"No climate data available for {selected}.")

st.divider()

if st.button("Return to NGO Directory", use_container_width=True):
    if "selected_ngo_id" in st.session_state:
        del st.session_state["selected_ngo_id"]
    st.switch_page("pages/14_NGO_Directory.py")
