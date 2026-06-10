import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("Climate Overview")
st.write(
    "Compare climate conditions of EU countries and see what each country "
    "has been experiencing and what that could mean for the people there."
)

st.divider()

# Countries
try:
    response = requests.get("http://web-api:4000/countries", timeout=5)
    countries = response.json() if response.status_code == 200 else []
except Exception:
    countries = []

if not countries:
    st.error("Could not load countries. Make sure the backend is running.")
    st.stop()

country_names = sorted([c["country_name"] for c in countries])
name_to_country = {c["country_name"]: c for c in countries}

col_a, col_b = st.columns(2)
with col_a:
    country1_name = st.selectbox("Your country (N/A if not in EU)", ["N/A"] + country_names)
with col_b:
    country2_name = st.selectbox("Country to explore", country_names, index=country_names.index("Germany"))

# N/A for comparison
selected = [c for c in [country1_name, country2_name] if c != "N/A"]

if len(selected) == 0:
    st.info("Select at least one country to explore.")
    st.stop()

st.divider()

# Data for each country
country_data = {}
for name in selected:
    country = name_to_country[name]
    try:
        r = requests.get(f"http://web-api:4000/countries/{country['country_id']}/year-data", timeout=5)
        rows = r.json() if r.status_code == 200 else []
    except Exception:
        rows = []
    if rows:
        country_data[name] = {"info": country, "df": pd.DataFrame(rows).sort_values("year")}

# charts
st.subheader("How is climate risk changing?")

for name, data in country_data.items():
    st.write(f"**{name}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.bar(data["df"], x="year", y="heatwave_days", title="Heatwave Days per Year",
                     color_discrete_sequence=["#e74c3c"])
        fig.update_layout(height=250, margin=dict(l=5, r=5, t=40, b=5))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(data["df"], x="year", y="precip_days_heavy", title="Heavy Rainfall Days per Year",
                     color_discrete_sequence=["#3498db"])
        fig.update_layout(height=250, margin=dict(l=5, r=5, t=40, b=5))
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        fig = px.bar(data["df"], x="year", y="dry_days", title="Dry Days per Year",
                     color_discrete_sequence=["#f39c12"])
        fig.update_layout(height=250, margin=dict(l=5, r=5, t=40, b=5))
        st.plotly_chart(fig, use_container_width=True)

# Estimate
st.divider()
st.subheader("What could this mean for people living there?")
st.write(
    "The model estimates what conditions people are likely to keep experiencing. "
    "More heatwave days tends to mean higher health risks and displacement pressure. "
    "More dry days could lead to water stress and food insecurity."
)

if st.button("Show Climate Estimates", type="primary", use_container_width=True):

    est_cols = st.columns(len(country_data))
    for col, (name, data) in zip(est_cols, country_data.items()):
        latest = data["df"].iloc[-1]
        user_inputs = {
            "country_code":        data["info"]["country_code"],
            "gdp_per_capita":      float(latest.get("gdp_per_capita") or 0),
            "unemployment_rate":   float(latest.get("unemployment_rate") or 0),
            "population":          float(latest.get("population") or 0),
            "urban_pct":           float(latest.get("urban_pct") or 0),
            "asylum_applications": float(latest.get("asylum_applications") or 0),
        }

        try:
            r = requests.post("http://web-api:4000/predict/climate", json=user_inputs)
            if r.status_code == 200:
                preds = r.json().get("predictions")
                with col:
                    st.success(name)
                    st.metric("Estimated Heatwave Days",       f"{preds['heatwave_days_pred']:.1f}")
                    st.metric("Estimated Heavy Rainfall Days", f"{preds['precip_days_heavy_pred']:.1f}")
                    st.metric("Estimated Dry Days",            f"{preds['dry_days_pred']:.1f}")
            else:
                with col:
                    st.error(f"Could not get estimate for {name}.")
        except requests.exceptions.RequestException as e:
            with col:
                st.error("Could not connect to the prediction API.")
                st.write(e)
