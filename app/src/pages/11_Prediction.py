import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title("Asylum Applications Prediction Model")
st.write(
    "This page uses TERRA's first machine learning model to predict asylum "
    "applications based on climate and economic indicators."
)

st.divider()

st.subheader("Enter country information")
st.caption(
    "The model predicts from a country's economic and climate indicators. "
    "It does not use calendar year, population, urbanization, total "
    "precipitation, or evapotranspiration — those were removed during model "
    "tuning (multicollinearity / out-of-range extrapolation)."
)

col1, col2, col3 = st.columns(3)

with col1:
    country_code = st.selectbox(
        "Country Code",
        ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR",
         "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL",
         "PT", "RO", "SE", "SI", "SK"]
    )

    gdp_per_capita = st.number_input(
        "GDP per Capita",
        min_value=0.0,
        value=55000.0
    )

    unemployment_rate = st.number_input(
        "Unemployment Rate",
        min_value=0.0,
        max_value=100.0,
        value=5.5
    )

with col2:
    temp_mean = st.number_input(
        "Average Temperature",
        value=12.0
    )

    heatwave_days = st.number_input(
        "Heatwave Days",
        min_value=0,
        value=0
    )

with col3:
    precip_days_heavy = st.number_input(
        "Heavy Precipitation Days",
        min_value=0,
        value=3
    )

    dry_days = st.number_input(
        "Dry Days",
        min_value=0,
        value=220
    )

st.divider()

if st.button("Predict Asylum Applications", type="primary", use_container_width=True):

    user_inputs = {
        "country_code": country_code,
        "gdp_per_capita": gdp_per_capita,
        "unemployment_rate": unemployment_rate,
        "temp_mean": temp_mean,
        "heatwave_days": heatwave_days,
        "precip_days_heavy": precip_days_heavy,
        "dry_days": dry_days,
    }

    # Use web-api when running in Docker.
    # If running Streamlit locally outside Docker, use localhost instead.
    api_url = "http://web-api:4000/predict/asylum"

    try:
        response = requests.post(api_url, json=user_inputs)

        if response.status_code == 200:
            result = response.json()
            prediction = result["prediction"]

            st.success("Prediction complete.")
            st.metric(
                "Predicted Asylum Applications",
                f"{prediction:,.0f}"
            )

            st.write("### Model Inputs Used")
            st.json(user_inputs)

        else:
            st.error("The prediction API returned an error.")
            st.write(response.json())

    except requests.exceptions.RequestException as e:
        st.error("Could not connect to the prediction API.")
        st.write(e)