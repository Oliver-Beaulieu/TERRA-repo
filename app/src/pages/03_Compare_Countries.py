import logging
logger = logging.getLogger(__name__)

import random
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("Compare countries")

REGIONS = {
    "Northern": ["Denmark", "Estonia", "Finland", "Ireland", "Latvia",
                 "Lithuania", "Sweden"],
    "Western":  ["Austria", "Belgium", "France", "Germany", "Luxembourg",
                 "Netherlands"],
    "Southern": ["Croatia", "Cyprus", "Greece", "Italy", "Malta",
                 "Portugal", "Slovenia", "Spain"],
    "Eastern":  ["Bulgaria", "Czechia", "Hungary", "Poland", "Romania",
                 "Slovakia"],
}
COUNTRY_REGION = {c: r for r, cs in REGIONS.items() for c in cs}
ALL_COUNTRIES = sorted(COUNTRY_REGION.keys())
YEARS_ALL = list(range(2018, 2024))

REGION_COLORS = {
    "Northern": "#3498db", "Western": "#9b59b6",
    "Southern": "#f1c40f", "Eastern": "#e74c3c",
}

@st.cache_data
def get_mock():
    data = {}
    for c in ALL_COUNTRIES:
        rng = random.Random(c)              # seed by name -> stable values
        base = rng.randint(8000, 120000)
        series = {}
        v = base
        for y in YEARS_ALL:
            v = max(2000, int(v * rng.uniform(0.85, 1.35)))
            series[y] = v
        data[c] = series
    return data

MOCK = get_mock()

default_countries = st.session_state.pop("load_countries", ["Germany", "France", "Greece", "Spain"])
default_range = st.session_state.pop("load_range", (2018, 2023))

selected = st.multiselect(
    "Countries (EU member states)",
    options=ALL_COUNTRIES,
    default=default_countries,
)

col_a, col_b = st.columns([1, 2])
mode = col_a.radio("Breakdown", ["By country", "By region"], horizontal=True)
yr = col_b.slider("Year range", 2018, 2023, default_range)

years = list(range(yr[0], yr[1] + 1))
n_years = len(years)

if not selected:
    st.info("Pick at least one country to compare.")
    st.stop()

rows = []
if mode == "By region":
    regions_in_play = sorted({COUNTRY_REGION[c] for c in selected})
    for reg in regions_in_play:
        members = [c for c in selected if COUNTRY_REGION[c] == reg]
        for y in years:
            rows.append({"Series": f"{reg} EU", "Year": y,
                         "Asylum apps": sum(MOCK[c][y] for c in members)})
    color_map = {f"{r} EU": REGION_COLORS[r] for r in REGIONS}
else:
    for c in selected:
        for y in years:
            rows.append({"Series": c, "Year": y, "Asylum apps": MOCK[c][y]})
    color_map = None  # let Plotly assign per-country colors

df = pd.DataFrame(rows)

st.write(f"### Asylum apps {yr[0]} → {yr[1]}")

if n_years == 2:
    st.caption("Showing a stacked bar chart (2-year view).")
    fig = px.bar(df, x="Year", y="Asylum apps", color="Series",
                 color_discrete_map=color_map, barmode="stack")
else:
    fig = px.line(df, x="Year", y="Asylum apps", color="Series",
                  color_discrete_map=color_map, markers=True)

fig.update_xaxes(dtick=1)
fig.update_layout(legend_title_text="", height=450,
                  margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig, use_container_width=True)

def summarize(df):
    out = {}
    for s in df["Series"].unique():
        sub = df[df["Series"] == s].sort_values("Year")
        lines, prev = [], None
        for _, r in sub.iterrows():
            v, y = int(r["Asylum apps"]), int(r["Year"])
            if prev is None:
                lines.append(f"In {y}, {s} recorded {v:,} asylum applications.")
            else:
                diff = v - prev
                pct = (diff / prev * 100) if prev else 0
                word = "rose" if diff > 0 else "fell" if diff < 0 else "held steady"
                lines.append(f"In {y}, {s} recorded {v:,} asylum applications, "
                             f"which {word} {abs(pct):.0f}% from {y-1}.")
            prev = v
        out[s] = lines
    return out

summaries = summarize(df)
st.write("### Summary")
tabs = st.tabs(list(summaries.keys()))
for tab, s in zip(tabs, summaries.keys()):
    with tab:
        for line in summaries[s]:
            st.write("• " + line)

export_df = df.pivot(index="Year", columns="Series", values="Asylum apps")
c1, c2, c3, c4 = st.columns(4)

if c1.button("Save", use_container_width=True):
    st.session_state.setdefault("saved_views", []).append({
        "name": " / ".join(selected),
        "countries": " ".join(selected),
        "range": f"{yr[0]}-{yr[1]}",
    })
    st.toast("Saved to your views.")

c2.download_button("CSV", export_df.to_csv().encode(),
                   "compare.csv", use_container_width=True)

if c3.button("PNG", use_container_width=True):
    st.info("Use the 📷 icon at the top-right of the chart to download a PNG.")

summary_text = f"TERRA — Compare countries summary ({yr[0]}-{yr[1]})\n\n"
for s, lines in summaries.items():
    summary_text += f"{s}\n" + "\n".join("  - " + l for l in lines) + "\n\n"
c4.download_button("PDF Summary", summary_text.encode(),
                   "summary.txt", use_container_width=True)