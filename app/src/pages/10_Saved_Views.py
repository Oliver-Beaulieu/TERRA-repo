import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("My saved views")

ALL_COUNTRIES = sorted([
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
    "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
    "Slovenia", "Spain", "Sweden",
])

if "saved_views" not in st.session_state:
    st.session_state["saved_views"] = [
        {"name": "Southern frontline",
         "countries": "Greece Italy Spain Malta Cyprus", "range": "2019-2023"},
        {"name": "Central Europe",
         "countries": "Germany Austria Czechia Poland Hungary", "range": "2018-2023"},
        {"name": "Baltic States",
         "countries": "Estonia Latvia Lithuania", "range": "2020-2023"},
    ]

views = st.session_state["saved_views"]

if not views:
    st.info("No saved views yet. Build a comparison on the Compare page and hit Save.")
    st.stop()

for i, view in enumerate(views):
    with st.container(border=True):
        countries = view["countries"].split()
        yr_start, yr_end = (view["range"].split("-") + ["2018", "2023"])[:2]

        head, open_btn, delete = st.columns([5, 2, 1])
        head.subheader(view["name"])
        head.caption(f"{view['countries']}  ·  {view['range']}")

        if open_btn.button("Open in Compare", key=f"open_{i}",
                            use_container_width=True):
            st.session_state["load_countries"] = countries
            st.session_state["load_range"] = (int(yr_start), int(yr_end))
            st.switch_page("pages/03_Compare_Countries.py")

        if delete.button("✕", key=f"del_{i}", use_container_width=True):
            views.pop(i)
            st.rerun()

        s1, arrow, s2, upd = st.columns([4, 1, 4, 2])
        swap_out = s1.selectbox("Swap out", countries,
                                key=f"out_{i}", label_visibility="collapsed")
        arrow.markdown("<div style='text-align:center;padding-top:8px'>→</div>",
                       unsafe_allow_html=True)
        swap_in = s2.selectbox("Swap in",
                               [c for c in ALL_COUNTRIES if c not in countries],
                               key=f"in_{i}", label_visibility="collapsed")

        new_range = st.slider("Year range", 2018, 2023,
                              (int(yr_start), int(yr_end)),
                              key=f"range_{i}")

        if upd.button("Update", key=f"upd_{i}", use_container_width=True):
            new_countries = [swap_in if c == swap_out else c for c in countries]
            view["countries"] = " ".join(new_countries)
            view["range"] = f"{new_range[0]}-{new_range[1]}"
            st.toast(f"Updated “{view['name']}”.")
            st.rerun()