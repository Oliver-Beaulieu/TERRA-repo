import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

API_BASE = "http://web-api:4000"
USER_ID = st.session_state.get('user_id', 1)

st.title("Compare Countries")

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
REGION_COLORS  = {
    "Northern": "#3498db",
    "Western":  "#9b59b6",
    "Southern": "#f1c40f",
    "Eastern":  "#e74c3c",
}


# ── API helpers ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_all_countries():
    try:
        r = requests.get(f"{API_BASE}/countries", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


@st.cache_data(ttl=300)
def fetch_year_data(country_id: int):
    try:
        r = requests.get(f"{API_BASE}/countries/{country_id}/year-data", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


# ── load country list ─────────────────────────────────────────────────────────

all_countries_data = fetch_all_countries()
name_to_country    = {c["country_name"]: c for c in all_countries_data}
all_country_names  = sorted(name_to_country.keys())

if not all_country_names:
    st.error("Could not load countries from the API. Make sure the backend is running.")
    st.stop()

# ── controls ──────────────────────────────────────────────────────────────────

raw_defaults  = st.session_state.pop("load_countries", ["Germany", "France", "Greece", "Spain"])
raw_range     = st.session_state.pop("load_range",     (2018, 2023))

default_countries = [c for c in raw_defaults if c in name_to_country] or all_country_names[:4]

selected = st.multiselect(
    "Countries (EU member states)",
    options=all_country_names,
    default=default_countries,
)

col_a, col_b = st.columns([1, 2])
mode = col_a.radio("Breakdown", ["By country", "By region"], horizontal=True)
yr   = col_b.slider("Year range", 2010, 2023,
                    (int(raw_range[0]), int(raw_range[1])))

if not selected:
    st.info("Pick at least one country to compare.")
    st.stop()

years_filter = list(range(yr[0], yr[1] + 1))

# ── fetch real data ───────────────────────────────────────────────────────────

raw_store: dict[str, list] = {}   # country_name -> list of year-data dicts

with st.spinner("Loading country data…"):
    for cname in selected:
        cid = name_to_country[cname]["country_id"]
        raw_store[cname] = fetch_year_data(cid)

# Build actual-data rows
actual_rows = []
for cname, rows in raw_store.items():
    for row in rows:
        if row["year"] in years_filter and row.get("asylum_applications") is not None:
            actual_rows.append({
                "Country": cname,
                "Region":  COUNTRY_REGION.get(cname, "Other"),
                "Year":    row["year"],
                "Asylum Applications": row["asylum_applications"],
                "Type":    "Actual",
            })

df_actual = pd.DataFrame(actual_rows)

if df_actual.empty:
    st.warning("No data found for the selected countries and year range.")
    st.stop()

# ── aggregate by mode ─────────────────────────────────────────────────────────

if mode == "By region":
    grouped = (
        df_actual.groupby(["Region", "Year"])["Asylum Applications"]
        .sum().reset_index()
    )
    grouped["Series"] = grouped["Region"]
    plot_df = grouped[["Series", "Year", "Asylum Applications"]]
else:
    plot_df = df_actual.copy()
    plot_df["Series"] = plot_df["Country"]
    plot_df = plot_df[["Series", "Year", "Asylum Applications"]]

if plot_df.empty:
    st.warning("Nothing to plot.")
    st.stop()

# ── chart ─────────────────────────────────────────────────────────────────────

st.write(f"### Asylum Applications  {yr[0]} → {yr[1]}")

n_years = yr[1] - yr[0] + 1

if n_years <= 2:
    fig = px.bar(
        plot_df, x="Year", y="Asylum Applications", color="Series",
        barmode="group",
    )
else:
    fig = px.line(
        plot_df, x="Year", y="Asylum Applications", color="Series",
        markers=True,
    )

fig.update_xaxes(dtick=1)
fig.update_layout(
    legend_title_text="",
    height=450,
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig, use_container_width=True)

# ── summary table ─────────────────────────────────────────────────────────────

def build_summary(df: pd.DataFrame) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for series in df["Series"].unique():
        sub  = df[df["Series"] == series].sort_values("Year")
        lines, prev = [], None
        for _, r in sub.iterrows():
            v, y = int(r["Asylum Applications"]), int(r["Year"])
            if prev is None:
                lines.append(f"In {y}: **{v:,}** asylum applications.")
            else:
                diff  = v - prev
                pct   = (diff / prev * 100) if prev else 0
                arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
                lines.append(
                    f"In {y}: **{v:,}**  {arrow} {abs(pct):.0f}% from {y - 1}."
                )
            prev = v
        out[series] = lines
    return out


summaries = build_summary(plot_df)
st.write("### Year-by-Year Summary")
tabs = st.tabs(list(summaries.keys()))
for tab, series in zip(tabs, summaries.keys()):
    with tab:
        for line in summaries[series]:
            st.markdown("• " + line)

# ── export / save ─────────────────────────────────────────────────────────────

export_df = plot_df.pivot_table(
    index="Year", columns="Series",
    values="Asylum Applications", aggfunc="sum"
)

c1, c2, c3, c4 = st.columns(4)

if c1.button("💾  Save View", use_container_width=True):
    name_to_id  = {c["country_name"]: c["country_id"] for c in all_countries_data}
    country_ids = [name_to_id[c] for c in selected if c in name_to_id]
    payload     = {
        "user_id":     USER_ID,
        "view_name":   " / ".join(selected),
        "year_from":   yr[0],
        "year_to":     yr[1],
        "country_ids": country_ids,
    }
    try:
        resp = requests.post(f"{API_BASE}/saved-views", json=payload, timeout=5)
        if resp.status_code == 201:
            st.toast("✅ Saved to your views.")
        else:
            st.error(f"Could not save view: {resp.text}")
    except Exception as e:
        st.error(f"API error: {e}")

c2.download_button(
    "📥  CSV", export_df.to_csv().encode(),
    "compare.csv", use_container_width=True
)

if c3.button("🖼️  PNG", use_container_width=True):
    st.info("Use the 📷 camera icon at the top-right of the chart to download a PNG.")

summary_text  = f"TERRA — Compare countries ({yr[0]}–{yr[1]})\n\n"
for s, lines in summaries.items():
    summary_text += f"{s}\n" + "\n".join("  - " + l for l in lines) + "\n\n"
c4.download_button(
    "📄  Summary", summary_text.encode(),
    "summary.txt", use_container_width=True
)
