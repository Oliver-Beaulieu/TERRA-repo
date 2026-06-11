import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title("Asylum Applications Prediction")
st.write(
    "Given a country's economic and climate conditions, this model estimates "
    "how many asylum applications that country is likely to receive. "
    "Use this to understand which conditions drive displacement pressure."
)

st.divider()

st.subheader("Enter country information")
st.caption(
    "The model predicts from a country's economic and climate indicators. "
)

col1, col2, col3 = st.columns(3)

# Load countries from DB; fall back to hardcoded list on error
try:
    _country_resp = requests.get("http://web-api:4000/countries", timeout=5)
    _country_data = _country_resp.json() if _country_resp.status_code == 200 else []
except Exception:
    _country_data = []

if _country_data:
    _country_options = [
        f"{c['country_name']} ({c['country_code']})" for c in _country_data
    ]
else:
    _FALLBACK = {
        "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CY": "Cyprus",
        "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "EE": "Estonia",
        "ES": "Spain", "FI": "Finland", "FR": "France", "GR": "Greece",
        "HR": "Croatia", "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
        "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "MT": "Malta",
        "NL": "Netherlands", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
        "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
    }
    _country_options = [f"{name} ({code})" for code, name in _FALLBACK.items()]

with col1:
    _country_label = st.selectbox("Country", _country_options)
    country_code = _country_label.split("(")[-1].rstrip(")")

    gdp_per_capita = st.number_input(
        "GDP per Capita (USD $)",
        min_value=0.0,
        value=55000.0,
        step=1000.0,
        format="%g",
        help="Values in current US dollars (USD), sourced from the World Bank. Max reasonable value: $200,000."
    )

    unemployment_rate = st.number_input(
        "Unemployment Rate (%)",
        min_value=0.0,
        value=5.5,
        step=2.0,
        format="%g",
        help="Enter as a percentage (0–100). Steps ±2%; you can type a decimal if needed."
    )

with col2:
    temp_mean = st.number_input(
        "Average Temperature (°C)",
        value=12.0,
        step=2.0,
        format="%g",
        help="Range: −89 °C to 57 °C (Earth's recorded extremes). Steps ±2 °C; can type a decimal if needed."
    )

    heatwave_days = st.number_input(
        "Heatwave Days",
        min_value=0,
        value=0,
        step=10,
    )

with col3:
    precip_days_heavy = st.number_input(
        "Heavy Precipitation Days",
        min_value=0,
        value=3,
        step=10,
    )

    dry_days = st.number_input(
        "Dry Days",
        min_value=0,
        value=220,
        step=10,
    )

st.divider()

if st.button("Predict Asylum Applications", type="primary", use_container_width=True):

    # ── Input validation ────────────────────────────────────────────────────
    _errors = []
    if not (-89.0 <= temp_mean <= 57.0):
        _errors.append(f"Average Temperature must be between −89 °C and 57 °C (you entered {temp_mean} °C).")
    if not (0.0 <= unemployment_rate <= 100.0):
        _errors.append(f"Unemployment Rate must be between 0% and 100% (you entered {unemployment_rate}%).")
    if gdp_per_capita > 200_000:
        _errors.append(f"GDP per Capita seems unrealistically high — max is $200,000 USD (you entered ${gdp_per_capita:,.0f}).")
    if heatwave_days > 366:
        _errors.append(f"Heatwave Days cannot exceed 366 (you entered {heatwave_days}).")
    if precip_days_heavy > 366:
        _errors.append(f"Heavy Precipitation Days cannot exceed 366 (you entered {precip_days_heavy}).")
    if dry_days > 366:
        _errors.append(f"Dry Days cannot exceed 366 (you entered {dry_days}).")

    if _errors:
        for _e in _errors:
            st.error(_e)
        st.stop()
    # ────────────────────────────────────────────────────────────────────────

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
    api_url = "http://web-api:4000/models/1/predict/asylum"

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

            # Average temperature highlight
            temp_f = temp_mean * 9 / 5 + 32
            if temp_mean >= 30:
                _temp_color = "#d73027"   # hot — red
                _temp_label = "High"
            elif temp_mean <= 0:
                _temp_color = "#4575b4"   # cold — blue
                _temp_label = "Low"
            else:
                _temp_color = "#1a9850"   # moderate — green
                _temp_label = "Moderate"
            st.markdown(
                f'<div style="background:{_temp_color};color:#fff;padding:12px 18px;'
                f'border-radius:8px;display:inline-block;font-size:1.1rem;font-weight:600;margin:8px 0">'
                f'🌡 Avg Temperature: {temp_mean:.1f} °C / {temp_f:.1f} °F '
                f'<span style="font-size:0.85rem;opacity:0.9">({_temp_label})</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


        else:
            st.error("The prediction API returned an error.")
            st.write(response.json())

    except requests.exceptions.RequestException as e:
        st.error("Could not connect to the prediction API.")
        st.write(e)