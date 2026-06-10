import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_BASE = "http://web-api:4000"
USER_ID  = st.session_state.get('user_id', 1)

LEVEL_COLOR = {
    "Low":      "🟢",
    "Moderate": "🟡",
    "High":     "🟠",
    "Critical": "🔴",
}

POLICY_TYPES = ["Emergency", "Preventive Measure", "Monitoring", "Funding Allocation", "Other"]
STATUSES     = ["Draft", "Under Review", "Active", "Archived"]

st.title("Risk Classification")
st.write(
    "Review climate-displacement risk levels across EU countries. "
    "Filter by risk level and flag countries that need policy attention."
)

st.divider()

#data 
try:
    r = requests.get(f"{API_BASE}/risk-classifications", timeout=5)
    risks = r.json() if r.status_code == 200 else []
except Exception:
    risks = []

try:
    r = requests.get(f"{API_BASE}/countries", timeout=5)
    countries = r.json() if r.status_code == 200 else []
except Exception:
    countries = []

if not risks:
    st.warning("No risk data available. Make sure the backend is running.")
    st.stop()

df = pd.DataFrame(risks)

#latest year per country
df = df.sort_values("year", ascending=False).drop_duplicates(subset="country_id")

st.subheader("Filter by Risk Level")
all_levels   = ["Low", "Moderate", "High", "Critical"]
active_levels = st.multiselect(
    "Show risk levels",
    options=all_levels,
    default=all_levels,
    label_visibility="collapsed",
)

filtered = df[df["risk_level"].isin(active_levels)].sort_values("risk_score", ascending=False)

st.caption(f"Showing {len(filtered)} of {len(df)} countries")
st.divider()

# Risk table
st.subheader("Country Risk Overview")

if filtered.empty:
    st.info("No countries in the filter.")
else:
    name_to_id = {c["country_name"]: c["country_id"] for c in countries}

    for _, row in filtered.iterrows():
        icon  = LEVEL_COLOR.get(row["risk_level"], "⚪")
        label = f"{icon} {row['risk_level']}"

        col_name, col_score, col_level, col_year, col_flag = st.columns([3, 1.5, 1.5, 1, 2])

        col_name.markdown(f"**{row['country_name']}**")
        col_score.metric("Risk Score", f"{float(row['risk_score']):.1f}")
        col_level.markdown(f"<div style='padding-top:8px'>{label}</div>", unsafe_allow_html=True)
        col_year.markdown(f"<div style='padding-top:8px; color:#888'>{int(row['year'])}</div>", unsafe_allow_html=True)

        flag_key = f"flag_{row['country_id']}"
        if col_flag.button("🚩 Flag for Policy", key=flag_key, use_container_width=True):
            st.session_state[f"show_flag_{row['country_id']}"] = True

        if st.session_state.get(f"show_flag_{row['country_id']}"):
            with st.form(key=f"form_{row['country_id']}"):
                st.markdown(f"**Flag: {row['country_name']}** — add a policy note")
                note_title  = st.text_input("Note title", placeholder="e.g. Urgent review needed")
                policy_type = st.selectbox("Type", POLICY_TYPES)
                status      = st.selectbox("Status", STATUSES)
                description = st.text_area("Description", placeholder="What action or observation prompted this flag?")
                c1, c2      = st.columns(2)
                submitted   = c1.form_submit_button("Save Note", use_container_width=True)
                cancelled   = c2.form_submit_button("Cancel",    use_container_width=True)

            if submitted:
                if not note_title.strip() or not description.strip():
                    st.error("Please fill in a title and description.")
                else:
                    country_id = name_to_id.get(row["country_name"])
                    payload = {
                        "country_id":  country_id,
                        "name":        note_title.strip(),
                        "policy_type": policy_type,
                        "status":      status,
                        "description": description.strip(),
                        "created_by":  USER_ID,
                    }
                    try:
                        resp = requests.post(f"{API_BASE}/policies", json=payload, timeout=5)
                        if resp.status_code == 201:
                            st.success(f"Policy note saved for {row['country_name']}.")
                            st.session_state[f"show_flag_{row['country_id']}"] = False
                            st.rerun()
                        else:
                            st.error("Failed to save note.")
                    except Exception as e:
                        st.error(f"Could not connect to API: {e}")

            if cancelled:
                st.session_state[f"show_flag_{row['country_id']}"] = False
                st.rerun()

        st.divider()
