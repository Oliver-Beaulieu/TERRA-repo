import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

USER_ID = 1 

STATUSES = ["Draft", "Under Review", "Active", "Archived"]

st.title("Policy Notes")
st.write(
    "Write and manage policy notes tied to specific countries. "
    "Use this to keep track of observations and recommendations as you analyze climate and asylum trends."
)

st.divider()

# countries
try:
    r = requests.get("http://web-api:4000/countries", timeout=5)
    countries = r.json() if r.status_code == 200 else []
except Exception:
    countries = []

if not countries:
    st.error("Could not load countries. Make sure the backend is running.")
    st.stop()

name_to_country = {c["country_name"]: c for c in countries}

#  Add policy note 

st.subheader("Add a Policy Note")

col1, col2 = st.columns(2)

with col1:
    selected_country = st.selectbox("Country", sorted(name_to_country.keys()))
    note_name = st.text_input("Note Title")
    policy_type = st.selectbox("Type", ["Climate Risk", "Asylum Policy", "Humanitarian", "Economic", "Other"])

with col2:
    status = st.selectbox("Status", STATUSES)
    description = st.text_area("Notes / Description", height=138)

if st.button("Save Note", type="primary", use_container_width=True):
    if not note_name or not description:
        st.warning("Please fill in a title and description.")
    else:
        payload = {
            "country_id":  name_to_country[selected_country]["country_id"],
            "name":        note_name,
            "policy_type": policy_type,
            "status":      status,
            "description": description,
            "created_by":  USER_ID,
        }
        try:
            r = requests.post("http://web-api:4000/policies", json=payload)
            if r.status_code == 201:
                st.success("Note saved.")
                st.rerun()
            else:
                st.error("Could not save note.")
        except requests.exceptions.RequestException as e:
            st.error("Could not connect to the API.")
            st.write(e)

st.divider()

#  Existing  notes 
try:
    r = requests.get("http://web-api:4000/policies", timeout=5)
    policies = r.json() if r.status_code == 200 else []
except Exception:
    policies = []

col_title, col_export = st.columns([3, 1])
col_title.subheader("Saved Policy Notes")

if policies:
    df_export = pd.DataFrame(policies)[["name", "country_name", "policy_type", "status", "description", "created_at"]]
    col_export.download_button(
        "📥 Export as CSV",
        df_export.to_csv(index=False).encode(),
        "policy_notes.csv",
        use_container_width=True,
    )

if not policies:
    st.info("No policy notes yet. Add one above.")
else:
    for p in policies:
        with st.expander(f"{p['name']} — {p['country_name']} ({p['status']})"):
            st.caption(f"Type: {p['policy_type']}  |  Created: {p['created_at']}")
            st.write(p["description"])

            update_col, delete_col = st.columns([2, 1])

            new_status = update_col.selectbox(
                "Update status",
                STATUSES,
                index=STATUSES.index(p["status"]) if p["status"] in STATUSES else 0,
                key=f"status_{p['policy_id']}"
            )

            if update_col.button("Update Status", key=f"upd_{p['policy_id']}"):
                try:
                    r = requests.put(
                        f"http://web-api:4000/policies/{p['policy_id']}",
                        json={"status": new_status}
                    )
                    if r.status_code == 200:
                        st.success("Status updated.")
                        st.rerun()
                    else:
                        st.error("Could not update status.")
                except requests.exceptions.RequestException as e:
                    st.error("Could not connect to the API.")
                    st.write(e)

            if delete_col.button("🗑 Delete", key=f"del_{p['policy_id']}"):
                try:
                    r = requests.delete(f"http://web-api:4000/policies/{p['policy_id']}")
                    if r.status_code == 200:
                        st.success("Note deleted.")
                        st.rerun()
                    else:
                        st.error("Could not delete note.")
                except requests.exceptions.RequestException as e:
                    st.error("Could not connect to the API.")
                    st.write(e)
