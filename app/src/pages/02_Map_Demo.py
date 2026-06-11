import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

st.title("Predictive Risk Map")
st.write(
    "Enter scenario conditions below. TERRA **Model 1** (Linear Regression) "
    "predicts asylum applications for every EU country — dots on the map are "
    "sized by predicted volume and colored by risk level."
)

API_BASE = "http://web-api:4000"

# EU country — lat/lon used by st.map
EU_COUNTRIES = {
    "AT": {"name": "Austria",      "lat": 47.52,  "lon": 14.55},
    "BE": {"name": "Belgium",      "lat": 50.50,  "lon": 4.47},
    "BG": {"name": "Bulgaria",     "lat": 42.73,  "lon": 25.49},
    "CY": {"name": "Cyprus",       "lat": 35.13,  "lon": 33.43},
    "CZ": {"name": "Czechia",      "lat": 49.82,  "lon": 15.47},
    "DE": {"name": "Germany",      "lat": 51.17,  "lon": 10.45},
    "DK": {"name": "Denmark",      "lat": 56.26,  "lon": 9.50},
    "EE": {"name": "Estonia",      "lat": 58.60,  "lon": 25.01},
    "ES": {"name": "Spain",        "lat": 40.46,  "lon": -3.75},
    "FI": {"name": "Finland",      "lat": 61.92,  "lon": 25.75},
    "FR": {"name": "France",       "lat": 46.23,  "lon": 2.21},
    "GR": {"name": "Greece",       "lat": 39.07,  "lon": 21.82},
    "HR": {"name": "Croatia",      "lat": 45.10,  "lon": 15.20},
    "HU": {"name": "Hungary",      "lat": 47.16,  "lon": 19.50},
    "IE": {"name": "Ireland",      "lat": 53.41,  "lon": -8.24},
    "IT": {"name": "Italy",        "lat": 41.87,  "lon": 12.57},
    "LT": {"name": "Lithuania",    "lat": 55.17,  "lon": 23.88},
    "LU": {"name": "Luxembourg",   "lat": 49.82,  "lon": 6.13},
    "LV": {"name": "Latvia",       "lat": 56.88,  "lon": 24.60},
    "MT": {"name": "Malta",        "lat": 35.94,  "lon": 14.38},
    "NL": {"name": "Netherlands",  "lat": 52.13,  "lon": 5.29},
    "PL": {"name": "Poland",       "lat": 51.92,  "lon": 19.15},
    "PT": {"name": "Portugal",     "lat": 39.40,  "lon": -8.22},
    "RO": {"name": "Romania",      "lat": 45.94,  "lon": 24.97},
    "SE": {"name": "Sweden",       "lat": 60.13,  "lon": 18.64},
    "SI": {"name": "Slovenia",     "lat": 46.15,  "lon": 14.99},
    "SK": {"name": "Slovakia",     "lat": 48.67,  "lon": 19.70},
}

# Color per risk level — used by st.map's color parameter
RISK_COLORS = {
    "Low":      [26,  152, 80,  180],   # green
    "Medium":   [254, 224, 139, 200],   # yellow
    "High":     [252, 141, 89,  200],   # orange
    "Critical": [215, 48,  39,  220],   # red
}

st.divider()
st.subheader("Enter scenario conditions")
st.caption(
    "Values are applied to every EU country. Country identity is encoded "
    "automatically so each country still produces a distinct prediction."
)

# ── Input form — same layout as 11_Prediction.py ────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
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
        help="Steps ±2 °C; you can type a decimal if needed."
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

if st.button("Run Risk Map", type="primary", use_container_width=True):

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

    scenario = {
        "gdp_per_capita": gdp_per_capita,
        "unemployment_rate": unemployment_rate,
        "temp_mean": temp_mean,
        "heatwave_days": heatwave_days,
        "precip_days_heavy": precip_days_heavy,
        "dry_days": dry_days,
    }

    rows = []
    errors = []

    with st.spinner("Running Model 1 for all 27 EU countries…"):
        progress = st.progress(0)
        total = len(EU_COUNTRIES)

        for i, (code2, info) in enumerate(EU_COUNTRIES.items()):
            payload = {"country_code": code2, **scenario}
            try:
                r = requests.post(f"{API_BASE}/models/1/predict/asylum", json=payload, timeout=15)
                pred = r.json()["prediction"] if r.status_code == 200 else 0
            except requests.exceptions.RequestException:
                pred = 0
                errors.append(info["name"])

            if pred < 1000:
                risk = "Low"
            elif pred < 10000:
                risk = "Medium"
            elif pred < 50000:
                risk = "High"
            else:
                risk = "Critical"

            rows.append({
                "country": info["name"],
                "code": code2,
                "lat": info["lat"],
                "lon": info["lon"],
                "predicted_asylum": float(pred),
                "risk_level": risk,
                "color": RISK_COLORS[risk],
                # st.map size column — scale dot to prediction volume
                "size": max(500, min(int(pred / 10), 80000)),
            })
            progress.progress((i + 1) / total)

    progress.empty()

    if errors:
        st.warning(f"Could not get predictions for: {', '.join(errors)}")

    st.session_state["map_df"] = pd.DataFrame(rows)

# ── Render results ───────────────────────────────────────────────────────────
if "map_df" in st.session_state:
    df = st.session_state["map_df"]

    # KPI cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("EU Countries Mapped", len(df))
    m2.metric("Highest Predicted Asylum", f"{df['predicted_asylum'].max():,.0f}")
    m3.metric("Average Predicted Asylum", f"{df['predicted_asylum'].mean():,.0f}")
    m4.metric("Critical Risk Countries", int((df["risk_level"] == "Critical").sum()))

    st.divider()

    # Legend
    leg_cols = st.columns(4)
    for col, (level, rgba) in zip(leg_cols, RISK_COLORS.items()):
        r, g, b, _ = rgba
        col.markdown(
            f'<span style="background:rgb({r},{g},{b});padding:4px 10px;'
            f'border-radius:4px;color:#111;font-weight:600">{level}</span>',
            unsafe_allow_html=True,
        )

    st.write("")

    # st.map — native Streamlit map using lat/lon columns.
    # color= accepts an RGBA list column; size= scales each dot.
    # Streamlit feature used: st.map
    st.map(
        df,
        latitude="lat",
        longitude="lon",
        color="color",
        size="size",
        zoom=3,
        use_container_width=True,
    )

    # Country rankings table
    st.divider()
    df_sorted = df.sort_values("predicted_asylum", ascending=False).reset_index(drop=True)
    df_sorted.index += 1

    st.subheader("Country Rankings")
    st.dataframe(
        df_sorted[["country", "code", "predicted_asylum", "risk_level"]].rename(columns={
            "country": "Country",
            "code": "Code",
            "predicted_asylum": "Predicted Asylum Apps",
            "risk_level": "Risk Level",
        }),
        use_container_width=True,
        height=400,
    )
