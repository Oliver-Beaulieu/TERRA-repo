import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("Displacement Timeline")
st.write("Pick a country to see how displacement has changed over the years alongside key climate indicators.")

st.divider()

API_BASE = "http://web-api:4000"

@st.cache_data(ttl=300)
def fetch_countries():
    try:
        r = requests.get(f"{API_BASE}/countries", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

@st.cache_data(ttl=300)
def fetch_year_data(country_id):
    try:
        r = requests.get(f"{API_BASE}/countries/{country_id}/year-data", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

countries = fetch_countries()
if not countries:
    st.error("Could not load countries. Make sure the backend is running.")
    st.stop()

country_names = sorted([c["country_name"] for c in countries])
name_to_country = {c["country_name"]: c for c in countries}

country = st.selectbox("Select a country", country_names)

rows = fetch_year_data(name_to_country[country]["country_id"])
if not rows:
    st.error("No data available for this country.")
    st.stop()

df = pd.DataFrame(rows).sort_values("year")

st.divider()

# ── Highlights ────────────────────────────────────────────────────────────────
peak = df.loc[df["asylum_applications"].idxmax()]
latest = df.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Peak displacement year", int(peak["year"]), f"{int(peak['asylum_applications']):,} applications")
col2.metric("Most recent year", int(latest["year"]), f"{int(latest['asylum_applications']):,} applications")
col3.metric("Years of data", len(df))

st.divider()

# ── Asylum applications chart ─────────────────────────────────────────────────
st.subheader("Asylum applications over time")
fig = px.line(df, x="year", y="asylum_applications", markers=True,
              color_discrete_sequence=["#3dba7e"],
              labels={"year": "Year", "asylum_applications": "Asylum Applications"})
fig.update_layout(height=300, margin=dict(l=5, r=5, t=10, b=5))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Year by year table ────────────────────────────────────────────────────────
st.subheader("Year by year breakdown")

table = df[["year", "asylum_applications"]].copy()
table = table.sort_values("year", ascending=False)
table.columns = ["Year", "Asylum Applications"]
table["Asylum Applications"] = table["Asylum Applications"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")

st.dataframe(table, use_container_width=True, hide_index=True)
