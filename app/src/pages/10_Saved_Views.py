import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

API_BASE = "http://web-api:4000"
USER_ID = 1  # Gabriel's seeded user_id


# ── helpers ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_all_countries():
    try:
        r = requests.get(f"{API_BASE}/countries", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def fetch_views():
    try:
        r = requests.get(f"{API_BASE}/saved-views", params={"user_id": USER_ID}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def fetch_view_detail(view_id):
    try:
        r = requests.get(f"{API_BASE}/saved-views/{view_id}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# ── page ──────────────────────────────────────────────────────────────────────

st.title("My Saved Views")

all_countries_data = fetch_all_countries()
name_to_id   = {c["country_name"]: c["country_id"] for c in all_countries_data}
all_names    = sorted(name_to_id.keys())

views = fetch_views()

if not views:
    st.info("No saved views yet — build a comparison on the Compare page and hit **Save View**, or create one below.")
else:
    for i, view in enumerate(views):
        detail       = fetch_view_detail(view["view_id"])
        countries_in = [c["country_name"] for c in (detail or {}).get("countries", [])]
        year_from    = view.get("year_from") or 2018
        year_to      = view.get("year_to")   or 2023

        with st.container(border=True):
            head_col, open_col, del_col = st.columns([5, 2, 1])

            head_col.subheader(view["view_name"])
            head_col.caption(
                f"{', '.join(countries_in) if countries_in else '—'}  ·  {year_from}–{year_to}"
            )

            if open_col.button("Open in Compare", key=f"open_{i}", use_container_width=True):
                st.session_state["load_countries"] = countries_in
                st.session_state["load_range"]     = (year_from, year_to)
                st.switch_page("pages/03_Compare_Countries.py")

            if del_col.button("✕", key=f"del_{i}", use_container_width=True):
                try:
                    requests.delete(f"{API_BASE}/saved-views/{view['view_id']}", timeout=5)
                except Exception:
                    pass
                st.rerun()

            # ── swap / update controls ──────────────────────────────────────
            if countries_in:
                s1, arrow_col, s2, upd_col = st.columns([4, 1, 4, 2])

                swap_out = s1.selectbox(
                    "Swap out", countries_in,
                    key=f"out_{i}", label_visibility="collapsed"
                )
                arrow_col.markdown(
                    "<div style='text-align:center;padding-top:8px'>→</div>",
                    unsafe_allow_html=True
                )
                remaining = [c for c in all_names if c not in countries_in]
                swap_in   = s2.selectbox(
                    "Swap in", remaining,
                    key=f"in_{i}", label_visibility="collapsed"
                )

                new_range = st.slider(
                    "Year range", 2010, 2023, (year_from, year_to),
                    key=f"range_{i}"
                )

                if upd_col.button("Update", key=f"upd_{i}", use_container_width=True):
                    new_countries = [swap_in if c == swap_out else c for c in countries_in]
                    new_ids       = [name_to_id[c] for c in new_countries if c in name_to_id]
                    payload       = {
                        "view_name":   view["view_name"],
                        "year_from":   new_range[0],
                        "year_to":     new_range[1],
                        "country_ids": new_ids,
                    }
                    try:
                        resp = requests.put(
                            f"{API_BASE}/saved-views/{view['view_id']}",
                            json=payload, timeout=5
                        )
                        if resp.status_code == 200:
                            st.toast(f"Updated \"{view['view_name']}\".")
                            fetch_all_countries.clear()
                        else:
                            st.error(f"Update failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                    st.rerun()
            else:
                new_range = st.slider(
                    "Year range", 2010, 2023, (year_from, year_to),
                    key=f"range_{i}"
                )

st.divider()

# ── create new view ───────────────────────────────────────────────────────────

st.subheader("➕  Create a new saved view")

with st.form("new_view_form", clear_on_submit=True):
    view_name_input  = st.text_input("View name", placeholder="e.g. Southern Frontline")
    chosen_countries = st.multiselect("Countries", all_names)
    yr_range         = st.slider("Year range", 2010, 2023, (2018, 2023))
    submitted        = st.form_submit_button("Save View", use_container_width=True)

    if submitted:
        if not view_name_input.strip():
            st.error("Please enter a view name.")
        elif not chosen_countries:
            st.error("Please select at least one country.")
        else:
            country_ids = [name_to_id[c] for c in chosen_countries if c in name_to_id]
            payload = {
                "user_id":     USER_ID,
                "view_name":   view_name_input.strip(),
                "year_from":   yr_range[0],
                "year_to":     yr_range[1],
                "country_ids": country_ids,
            }
            try:
                resp = requests.post(f"{API_BASE}/saved-views", json=payload, timeout=5)
                if resp.status_code == 201:
                    st.success(f"View \"{view_name_input.strip()}\" saved!")
                    st.rerun()
                else:
                    st.error(f"Failed to save view: {resp.text}")
            except Exception as e:
                st.error(f"Could not connect to API: {e}")
