import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Asylum Applications Prediction")
st.write(
    "Given a country's economic and climate conditions, this model estimates "
    "how many asylum applications that country is likely to receive. "
    "Use this to understand which conditions drive displacement pressure."
)
st.divider()

# load countries
try:
    r = requests.get(f"{API_BASE}/countries", timeout=5)
    country_data = r.json() if r.status_code == 200 else []
except Exception:
    country_data = []

country_map  = {c["country_name"]: c for c in country_data}
country_names = list(country_map.keys())

st.subheader("Select a country")
st.caption("Inputs are pre-filled from the most recent recorded year. You can adjust them before predicting.")

selected_name = st.selectbox("Country", country_names)
selected      = country_map.get(selected_name, {})
country_code  = selected.get("country_code", "")
country_id    = selected.get("country_id")

# fetch most recent year data for the selected country and use as defaults
defaults = {
    "gdp_per_capita":    55000.0,
    "unemployment_rate": 5.5,
    "temp_mean":         12.0,
    "heatwave_days":     0,
    "precip_days_heavy": 3,
    "dry_days":          220,
    "year":              "N/A",
}

if country_id:
    try:
        r = requests.get(f"{API_BASE}/countries/{country_id}/year-data", timeout=5)
        rows = r.json() if r.status_code == 200 else []
        if rows:
            latest = sorted(rows, key=lambda x: x.get("year", 0))[-1]
            defaults["gdp_per_capita"]    = float(latest.get("gdp_per_capita")    or defaults["gdp_per_capita"])
            defaults["unemployment_rate"] = float(latest.get("unemployment_rate") or defaults["unemployment_rate"])
            defaults["temp_mean"]         = float(latest.get("temp_mean")         or defaults["temp_mean"])
            defaults["heatwave_days"]     = int(latest.get("heatwave_days")       or 0)
            defaults["precip_days_heavy"] = int(latest.get("precip_days_heavy")   or 0)
            defaults["dry_days"]          = int(latest.get("dry_days")            or 0)
            defaults["year"]              = latest.get("year", "N/A")
    except Exception:
        pass

st.caption(f"Showing data from {defaults['year']} — the most recent recorded year for {selected_name}.")
st.divider()

st.subheader("Adjust inputs if needed")

col1, col2, col3 = st.columns(3)

with col1:
    gdp_per_capita = st.number_input(
        "GDP per Capita (USD $)",
        min_value=0.0,
        value=defaults["gdp_per_capita"],
        step=1000.0,
        format="%g",
    )
    unemployment_rate = st.number_input(
        "Unemployment Rate (%)",
        min_value=0.0,
        value=defaults["unemployment_rate"],
        step=0.5,
        format="%g",
    )

with col2:
    temp_mean = st.number_input(
        "Average Temperature (°C)",
        value=defaults["temp_mean"],
        step=1.0,
        format="%g",
    )
    heatwave_days = st.number_input(
        "Heatwave Days",
        min_value=0,
        value=defaults["heatwave_days"],
        step=1,
    )

with col3:
    precip_days_heavy = st.number_input(
        "Heavy Precipitation Days",
        min_value=0,
        value=defaults["precip_days_heavy"],
        step=1,
    )
    dry_days = st.number_input(
        "Dry Days",
        min_value=0,
        value=defaults["dry_days"],
        step=10,
    )

st.divider()

if st.button("Predict Asylum Applications", type="primary", use_container_width=True):

    errors = []
    if not (-89.0 <= temp_mean <= 57.0):
        errors.append(f"Average Temperature must be between −89 °C and 57 °C (you entered {temp_mean} °C).")
    if not (0.0 <= unemployment_rate <= 100.0):
        errors.append(f"Unemployment Rate must be between 0% and 100% (you entered {unemployment_rate}%).")
    if gdp_per_capita > 200_000:
        errors.append(f"GDP per Capita seems unrealistically high — max is $200,000 (you entered ${gdp_per_capita:,.0f}).")
    if heatwave_days > 366:
        errors.append(f"Heatwave Days cannot exceed 366 (you entered {heatwave_days}).")
    if precip_days_heavy > 366:
        errors.append(f"Heavy Precipitation Days cannot exceed 366 (you entered {precip_days_heavy}).")
    if dry_days > 366:
        errors.append(f"Dry Days cannot exceed 366 (you entered {dry_days}).")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    payload = {
        "country_code":      country_code,
        "gdp_per_capita":    gdp_per_capita,
        "unemployment_rate": unemployment_rate,
        "temp_mean":         temp_mean,
        "heatwave_days":     heatwave_days,
        "precip_days_heavy": precip_days_heavy,
        "dry_days":          dry_days,
    }

    try:
        response = requests.post(f"{API_BASE}/models/1/predict/asylum", json=payload)

        if response.status_code == 200:
            prediction = response.json()["prediction"]
            st.success("Prediction complete.")
            st.metric("Predicted Asylum Applications", f"{prediction:,.0f}")

            temp_f = temp_mean * 9 / 5 + 32
            if temp_mean >= 30:
                color, label = "#d73027", "High"
            elif temp_mean <= 0:
                color, label = "#4575b4", "Low"
            else:
                color, label = "#1a9850", "Moderate"

            st.markdown(
                f'<div style="background:{color};color:#fff;padding:12px 18px;'
                f'border-radius:8px;display:inline-block;font-size:1.1rem;font-weight:600;margin:8px 0">'
                f'Avg Temperature: {temp_mean:.1f} °C / {temp_f:.1f} °F '
                f'<span style="font-size:0.85rem;opacity:0.9">({label})</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.error("The prediction API returned an error.")
            st.write(response.json())

    except requests.exceptions.RequestException as e:
        st.error("Could not connect to the prediction API.")
        st.write(e)
