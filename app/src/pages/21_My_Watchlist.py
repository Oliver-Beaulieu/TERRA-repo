import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

API_BASE = "http://web-api:4000"

st.set_page_config(layout="wide")

SideBarLinks()

st.title("My Watchlist")
st.write("### Countries you're following — live snapshots")

st.divider()

user_id = st.session_state.get("user_id")

if not user_id:
    st.error("You must be logged in to view your watchlist.")
    st.stop()


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_watchlist():
    try:
        resp = requests.get(f"{API_BASE}/watchlist", params={"user_id": user_id})
        return resp.json() if resp.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []


def load_all_countries():
    try:
        resp = requests.get(f"{API_BASE}/countries")
        return resp.json() if resp.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []


def load_risk_map():
    """Return {country_id: latest risk row}."""
    try:
        resp = requests.get(f"{API_BASE}/risk/classifications")
        if resp.status_code != 200:
            return {}
        risk_map = {}
        for row in resp.json():
            cid = row["country_id"]
            if cid not in risk_map or row["year"] > risk_map[cid]["year"]:
                risk_map[cid] = row
        return risk_map
    except requests.exceptions.RequestException:
        return {}


def load_year_data(country_id):
    try:
        resp = requests.get(f"{API_BASE}/countries/{country_id}/year-data")
        return resp.json() if resp.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []


def load_climate_events(country_id):
    try:
        resp = requests.get(f"{API_BASE}/climate/{country_id}/events")
        return resp.json() if resp.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []


RISK_COLORS = {
    "Low":    "#2ecc71",
    "Medium": "#f39c12",
    "High":   "#e74c3c",
}


def risk_badge(level):
    color = RISK_COLORS.get(level, "#888888")
    return f'<span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:13px;font-weight:600;">{level or "N/A"}</span>'


# ── Load data ────────────────────────────────────────────────────────────────

watchlist    = load_watchlist()
all_countries = load_all_countries()
risk_map     = load_risk_map()

# ── Add a country ────────────────────────────────────────────────────────────

watched_ids = {entry["country_id"] for entry in watchlist}
available   = [c for c in all_countries if c["country_id"] not in watched_ids]

if available:
    country_names = [c["country_name"] for c in available]
    country_map   = {c["country_name"]: c for c in available}

    col_select, col_btn = st.columns([3, 1])
    with col_select:
        selected_name = st.selectbox("Add a country to your watchlist", country_names)
    with col_btn:
        st.write("")
        st.write("")
        if st.button("Add", type="primary", use_container_width=True):
            country = country_map[selected_name]
            try:
                resp = requests.post(f"{API_BASE}/watchlist", json={
                    "user_id": user_id,
                    "country_id": country["country_id"],
                })
                if resp.status_code == 201:
                    st.success(f"{selected_name} added to your watchlist.")
                    st.rerun()
                else:
                    st.error(resp.json().get("error", "Failed to add country."))
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the API: {e}")
else:
    st.info("You are already watching all available countries.")

st.divider()

# ── Watchlist cards ──────────────────────────────────────────────────────────

if not watchlist:
    st.write("Your watchlist is empty. Add a country above to get started.")
    st.stop()

st.subheader(f"Watching {len(watchlist)} {'country' if len(watchlist) == 1 else 'countries'}")

for entry in watchlist:
    country_id   = entry["country_id"]
    country_name = entry["country_name"]
    country_code = entry["country_code"]
    region       = entry["region"]

    risk_row  = risk_map.get(country_id, {})
    risk_level = risk_row.get("risk_level")
    risk_score = risk_row.get("risk_score")
    risk_year  = risk_row.get("year")

    year_data = load_year_data(country_id)
    latest_yr = max(year_data, key=lambda r: r["year"]) if year_data else None

    climate_events = load_climate_events(country_id)
    recent_events  = climate_events[:3]

    # ── Card header ──
    col_name, col_remove = st.columns([6, 1])
    with col_name:
        st.markdown(
            f"### {country_name} &nbsp; {risk_badge(risk_level)}",
            unsafe_allow_html=True,
        )
        added_date = str(entry['added_at']).split(" ")[0]
        st.caption(f"{country_code} · Added {added_date}")
    with col_remove:
        st.write("")
        if st.button("Remove", key=f"remove_{entry['watchlist_id']}"):
            try:
                resp = requests.delete(f"{API_BASE}/watchlist/{entry['watchlist_id']}")
                if resp.status_code == 200:
                    st.rerun()
                else:
                    st.error("Failed to remove.")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the API: {e}")

    # ── Stats row ──
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        if risk_score is not None:
            st.metric("Risk Score", f"{float(risk_score):.2f}", help=f"As of {risk_year}")
        else:
            st.metric("Risk Score", "N/A")

    with m2:
        if latest_yr:
            asylum = latest_yr.get("asylum_applications")
            st.metric(f"Asylum Apps ({latest_yr['year']})", f"{int(asylum):,}" if asylum else "N/A")
        else:
            st.metric("Asylum Apps", "N/A")

    with m3:
        if latest_yr:
            temp = latest_yr.get("temp_mean")
            st.metric(f"Avg Temp ({latest_yr['year']})", f"{float(temp):.1f} °C" if temp else "N/A")
        else:
            st.metric("Avg Temp", "N/A")

    with m4:
        if latest_yr:
            gdp = latest_yr.get("gdp_per_capita")
            st.metric(f"GDP/Capita ({latest_yr['year']})", f"${float(gdp):,.0f}" if gdp else "N/A")
        else:
            st.metric("GDP/Capita", "N/A")

    with m5:
        st.metric("Climate Events", len(climate_events))

    # ── Recent climate events ──
    if recent_events:
        with st.expander(f"Recent climate events ({len(climate_events)} total)"):
            for ev in recent_events:
                severity = ev.get("severity", "")
                sev_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(severity, "⚪")
                st.write(
                    f"{sev_color} **{ev.get('event_type', 'Event')}** — "
                    f"{ev.get('event_date', '')}  |  Severity: {severity}"
                )
                if ev.get("description"):
                    st.caption(ev["description"])
    else:
        st.caption("No climate events on record for this country.")

    # ── Quick actions ──
    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("View on Risk Map", key=f"map_{country_id}", use_container_width=True):
            st.switch_page("pages/02_Map_Demo.py")
    with btn2:
        if st.button("Displacement Timeline", key=f"timeline_{country_id}", use_container_width=True):
            st.switch_page("pages/08_Displacement_Timeline.py")
    with btn3:
        if st.button("Find Similar Countries", key=f"similar_{country_id}", use_container_width=True):
            st.switch_page("pages/09_Similar_Countries.py")

    st.markdown("---")
