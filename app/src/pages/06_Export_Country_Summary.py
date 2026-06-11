import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
import pandas as pd
from modules.nav import SideBarLinks

API_BASE = "http://web-api:4000"

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Export Country Summary")
st.write("### Generate a country-level humanitarian summary using TERRA Model 1")
st.write(
    "Select a country and year to pull its climate and economic data, "
    "run it through the asylum applications prediction model, and export a summary."
)

st.divider()


# Load all countries from DB
try:
    countries_resp = requests.get(f"{API_BASE}/countries")
    if countries_resp.status_code == 200:
        countries = countries_resp.json()
    else:
        st.error("Could not load countries from the API.")
        st.stop()
except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the API: {e}")
    st.stop()

country_names = [c["country_name"] for c in countries]
country_map = {c["country_name"]: c for c in countries}

col1, col2 = st.columns(2)

with col1:
    selected_name = st.selectbox("Select a Country", country_names)

with col2:
    selected_year = st.number_input("Select a Year", min_value=2010, max_value=2023, value=2019)

if st.button("Generate Summary", type="primary", use_container_width=True):

    country = country_map[selected_name]
    country_id = country["country_id"]
    country_code = country["country_code"]

    # Fetch year data for the selected country
    try:
        year_resp = requests.get(f"{API_BASE}/countries/{country_id}/year-data")
        if year_resp.status_code != 200:
            st.error("Could not load year data for this country.")
            st.stop()
        year_data = year_resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the API: {e}")
        st.stop()

    # Find the row matching the selected year
    year_row = next((r for r in year_data if r["year"] == selected_year), None)

    if year_row is None:
        st.warning(f"No data found for {selected_name} in {selected_year}. Try a different year.")
        st.stop()

    # Build prediction payload
    prediction_payload = {
        "country_code": country_code,
        "year": year_row["year"],
        "gdp_per_capita": year_row.get("gdp_per_capita", 0),
        "unemployment_rate": year_row.get("unemployment_rate", 0),
        "population": year_row.get("population", 0),
        "urban_pct": year_row.get("urban_pct", 0),
        "temp_mean": year_row.get("temp_mean", 0),
        "heatwave_days": year_row.get("heatwave_days", 0),
        "precip_total": year_row.get("precip_total", 0),
        "precip_days_heavy": year_row.get("precip_days_heavy", 0),
        "dry_days": year_row.get("dry_days", 0),
        "evapotrans_total": year_row.get("evapotrans_total", 0),
    }

    # Use real asylum data for past years, model prediction for future years
    actual_asylum = year_row.get("asylum_applications")
    is_future = selected_year > 2023

    if is_future or actual_asylum is None:
        try:
            pred_resp = requests.post(f"{API_BASE}/models/1/predict/asylum", json=prediction_payload)
            if pred_resp.status_code == 200:
                asylum_value = pred_resp.json()["prediction"]
                asylum_label = "🔮 Predicted Asylum Applications"
            else:
                st.error(f"Prediction failed: {pred_resp.json().get('message', 'Unknown error')}")
                st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach prediction API: {e}")
            st.stop()
    else:
        asylum_value = float(actual_asylum)
        asylum_label = "📊 Asylum Applications (Actual)"

    # Cast all numeric values safely
    def to_float(val, default=0):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    gdp         = to_float(year_row.get("gdp_per_capita"))
    unemp       = to_float(year_row.get("unemployment_rate"))
    pop         = to_float(year_row.get("population"))
    urban       = to_float(year_row.get("urban_pct"))
    temp        = to_float(year_row.get("temp_mean"))
    heatwave    = to_float(year_row.get("heatwave_days"))
    precip      = to_float(year_row.get("precip_total"))
    precip_h    = to_float(year_row.get("precip_days_heavy"))
    dry         = to_float(year_row.get("dry_days"))
    evapotrans  = to_float(year_row.get("evapotrans_total"))

    # Display summary
    st.divider()
    st.subheader(f"📋 {selected_name} — {selected_year} Summary")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(asylum_label, f"{asylum_value:,.0f}")
    with m2:
        st.metric("💰 GDP per Capita", f"${gdp:,.0f}")
    with m3:
        st.metric("📉 Unemployment Rate", f"{unemp:.1f}%")
    with m4:
        st.metric("👥 Population", f"{pop:,.0f}")

    m5, m6, m7, m8 = st.columns(4)
    with m5:
        st.metric("🏙 Urban Population", f"{urban:.1f}%")
    with m6:
        st.metric("🌡 Avg Temperature", f"{temp:.1f} °C")
    with m7:
        st.metric("☀️ Dry Days", f"{dry:.0f}")
    with m8:
        st.metric("🔥 Heatwave Days", f"{heatwave:.0f}")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.write("#### 🌡 Climate Indicators")
        st.write(f"**Avg Temperature:** {temp:.1f} °C")
        st.write(f"**Heatwave Days:** {heatwave:.0f}")
        st.write(f"**Total Precipitation:** {precip:.1f} mm")
        st.write(f"**Heavy Precipitation Days:** {precip_h:.0f}")
        st.write(f"**Dry Days:** {dry:.0f}")
        st.write(f"**Evapotranspiration:** {evapotrans:.1f}")

    with col_b:
        st.write("#### 💼 Economic Indicators")
        st.write(f"**GDP per Capita:** ${gdp:,.2f}")
        st.write(f"**Unemployment Rate:** {unemp:.1f}%")
        st.write(f"**Population:** {pop:,.0f}")
        st.write(f"**Urban Population %:** {urban:.1f}%")

    st.divider()

    # Build export dataframe
    export_data = {
        "Country": [selected_name],
        "Country Code": [country_code],
        "Year": [selected_year],
        "Asylum Applications": [round(asylum_value)],
        "Asylum Data Type": ["Predicted" if is_future or actual_asylum is None else "Actual"],
        "GDP per Capita": [gdp],
        "Unemployment Rate (%)": [unemp],
        "Population": [pop],
        "Urban Population (%)": [urban],
        "Avg Temperature (°C)": [temp],
        "Heatwave Days": [heatwave],
        "Total Precipitation (mm)": [precip],
        "Heavy Precipitation Days": [precip_h],
        "Dry Days": [dry],
        "Evapotranspiration": [evapotrans],
    }

    df_export = pd.DataFrame(export_data)

    csv = df_export.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download CSV Summary",
        data=csv,
        file_name=f"{selected_name}_{selected_year}_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Save the report to the database for this user
    user_id = st.session_state.get("user_id")
    if user_id:
        report_payload = {
            "country_id": country_id,
            "user_id": user_id,
            "report_title": f"{selected_name} — {selected_year}",
            "report_text": df_export.to_csv(index=False),
            "export_format": "CSV",
        }
        try:
            save_resp = requests.post(f"{API_BASE}/reports", json=report_payload)
            if save_resp.status_code == 201:
                st.success("Report saved to your history.")
            else:
                st.warning("Summary generated but could not save to history.")
        except requests.exceptions.RequestException:
            st.warning("Summary generated but could not reach API to save history.")

st.divider()

# ── Saved report history ─────────────────────────────────────────────────────

user_id = st.session_state.get("user_id")

if user_id:
    st.subheader("Saved Report History")

    try:
        history_resp = requests.get(f"{API_BASE}/reports", params={"user_id": user_id})
        if history_resp.status_code == 200:
            history = history_resp.json()
        else:
            history = []
    except requests.exceptions.RequestException:
        history = []

    if not history:
        st.write("No saved reports yet. Generate a summary above to create one.")
    else:
        for report in history:
            col_title, col_del = st.columns([5, 1])

            with col_title:
                st.write(f"**{report['report_title']}**")
                st.caption(f"Generated {report['generated_at']}  ·  Format: {report['export_format']}")

            with col_del:
                if st.button("Delete", key=f"del_report_{report['report_id']}"):
                    try:
                        del_resp = requests.delete(f"{API_BASE}/reports/{report['report_id']}")
                        if del_resp.status_code == 200:
                            st.success("Report deleted.")
                            st.rerun()
                        else:
                            st.error("Could not delete report.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Could not connect to the API: {e}")

            st.markdown("---")
