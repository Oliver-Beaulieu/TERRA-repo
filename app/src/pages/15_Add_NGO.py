import logging
logger = logging.getLogger(__name__)

import datetime
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("Add New NGO")

EU_COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
    "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
    "Slovenia", "Spain", "Sweden", "Other (specify)"
]

CLIMATE_FOCUS_OPTIONS = [
    "Climate Displacement", "Flood Response", "Drought Relief",
    "Heatwave Response", "Refugee Resettlement", "General Humanitarian",
    "Environmental Conservation", "Medical Relief", "Other"
]

# Success modal
if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False
if "success_ngo_name" not in st.session_state:
    st.session_state.success_ngo_name = ""
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0

@st.dialog("Success")
def show_success_dialog(ngo_name):
    st.markdown(f"### {ngo_name} has been successfully added!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Return to NGO Directory", use_container_width=True):
            st.session_state.show_success_modal = False
            st.session_state.success_ngo_name = ""
            st.switch_page("pages/14_NGO_Directory.py")
    with col2:
        if st.button("Add Another NGO", use_container_width=True):
            st.session_state.show_success_modal = False
            st.session_state.success_ngo_name = ""
            st.session_state.reset_form = True
            st.rerun()

if st.session_state.reset_form:
    st.session_state.form_key_counter += 1
    st.session_state.reset_form = False

# Load EU country climate data for snapshot
try:
    r = requests.get("http://web-api:4000/countries", timeout=5)
    eu_countries_data = r.json() if r.status_code == 200 else []
except Exception:
    eu_countries_data = []

name_to_country = {c["country_name"]: c for c in eu_countries_data}

st.divider()

# Country picker outside the form so climate snapshot reacts live
st.subheader("Where is this NGO based?")
country_choice = st.selectbox("Country", EU_COUNTRIES, key=f"country_{st.session_state.form_key_counter}")

if country_choice == "Other (specify)":
    country_value = st.text_input("Enter country name", key=f"country_text_{st.session_state.form_key_counter}")
else:
    country_value = country_choice

# Climate snapshot
if country_choice != "Other (specify)" and country_choice in name_to_country:
    try:
        r = requests.get(f"http://web-api:4000/countries/{name_to_country[country_choice]['country_id']}/year-data", timeout=5)
        rows = r.json() if r.status_code == 200 else []
    except Exception:
        rows = []

    if rows:
        df = pd.DataFrame(rows)
        st.caption(f"📍 Climate snapshot for {country_choice}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Heatwave Days",      f"{df['heatwave_days'].mean():.1f} /yr")
        m2.metric("Avg Heavy Rainfall Days", f"{pd.to_numeric(df['precip_days_heavy'], errors='coerce').mean():.1f} /yr")
        m3.metric("Avg Dry Days",           f"{df['dry_days'].mean():.0f} /yr")

st.divider()

# Rest of the form
with st.form(f"add_ngo_form_{st.session_state.form_key_counter}"):
    st.subheader("NGO Information")

    name = st.text_input("Organisation Name *")
    current_year = datetime.date.today().year
    founding_year = st.number_input("Founding Year *", min_value=1800, max_value=current_year, value=current_year)

    focus_col, custom_col = st.columns(2)
    with focus_col:
        focus_choice = st.selectbox("Climate Focus Area *", CLIMATE_FOCUS_OPTIONS)
    with custom_col:
        custom_focus = st.text_input("Or type a custom focus area", placeholder="Leave blank to use dropdown selection")

    focus_area = custom_focus.strip() if custom_focus.strip() else focus_choice

    website = st.text_input("Website URL *")
    notes = st.text_area("Notes", placeholder="Any additional notes about this NGO (optional)")

    submitted = st.form_submit_button("Add NGO", use_container_width=True)

    if submitted:
        if not name or not website or not country_value:
            st.error("Please fill in organisation name, country, and website.")
        else:
            payload = {
                "Name":         name,
                "Country":      country_value,
                "Founding_Year": int(founding_year),
                "Focus_Area":   focus_area,
                "Website":      website,
                "Notes":        notes,
            }
            try:
                r = requests.post("http://web-api:4000/ngo/ngos", json=payload)
                if r.status_code == 201:
                    st.session_state.show_success_modal = True
                    st.session_state.success_ngo_name = name
                    st.rerun()
                else:
                    st.error("Failed to add NGO.")
            except requests.exceptions.RequestException as e:
                st.error("Could not connect to the API.")
                st.write(e)

if st.session_state.show_success_modal:
    show_success_dialog(st.session_state.success_ngo_name)

if st.button("Return to NGO Directory"):
    st.switch_page("pages/14_NGO_Directory.py")
