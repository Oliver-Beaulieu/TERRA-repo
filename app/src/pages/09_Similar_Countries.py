import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("Similar Countries")
st.write("Pick a country and find the 5 EU countries with the most similar climate and displacement conditions.")

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

ref_country = st.selectbox("Select a country", country_names)

if st.button("Find Similar Countries", type="primary", use_container_width=True):

    COLS = ["heatwave_days", "dry_days", "precip_days_heavy", "asylum_applications"]

    # Get reference averages
    ref_rows = fetch_year_data(name_to_country[ref_country]["country_id"])
    if not ref_rows:
        st.error("Could not load data for the selected country.")
        st.stop()

    ref_df = pd.DataFrame(ref_rows)
    ref_df = ref_df[ref_df["year"] >= 2018]
    ref_avgs = {c: ref_df[c].mean() for c in COLS if c in ref_df.columns}

    # Compare all other countries
    results = []
    with st.spinner("Comparing countries…"):
        for c in countries:
            if c["country_name"] == ref_country:
                continue
            rows = fetch_year_data(c["country_id"])
            if not rows:
                continue
            df = pd.DataFrame(rows)
            df = df[df["year"] >= 2018]
            if df.empty:
                continue

            avgs = {col: df[col].mean() for col in COLS if col in df.columns}

            diffs = []
            for col in COLS:
                if col not in avgs or col not in ref_avgs:
                    continue
                denom = max(abs(ref_avgs[col]), abs(avgs[col]), 1)
                diffs.append(abs(ref_avgs[col] - avgs[col]) / denom)

            if not diffs:
                continue

            similarity = max(0.0, 1.0 - (sum(diffs) / len(diffs))) * 100
            results.append({
                "Country":                  c["country_name"],
                "Similarity %":             round(similarity, 1),
                "Avg Heatwave Days":        round(avgs.get("heatwave_days", 0), 1),
                "Avg Dry Days":             round(avgs.get("dry_days", 0), 1),
                "Avg Heavy Rain Days":      round(avgs.get("precip_days_heavy", 0), 1),
                "Avg Asylum Applications":  int(avgs.get("asylum_applications", 0)),
            })

    if not results:
        st.warning("Not enough data to compare.")
        st.stop()

    top5 = (
        pd.DataFrame(results)
        .sort_values("Similarity %", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )
    top5.index += 1
    top5.index.name = "Rank"

    st.subheader(f"Top 5 countries most similar to {ref_country}")
    st.dataframe(
        top5.style.format({
            "Similarity %":            "{:.2f}%",
            "Avg Heatwave Days":       "{:.2f}",
            "Avg Dry Days":            "{:.2f}",
            "Avg Heavy Rain Days":     "{:.2f}",
            "Avg Asylum Applications": "{:,}",
        }),
        use_container_width=True,
    )
