import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Initialize sidebar
SideBarLinks()

st.title("NGO Profile")

# Get NGO ID from session state
ngo_id = st.session_state.get("selected_ngo_id")

if ngo_id is None:
    st.info("Please select an NGO from the directory first.")
    if st.button("Go to NGO Directory", key="no_ngo_return"):
        st.switch_page("pages/14_NGO_Directory.py")
else:
    # API endpoint
    API_URL = f"http://web-api:4000/ngo/ngos/{ngo_id}"

    try:
        # Fetch NGO details
        response = requests.get(API_URL)

        if response.status_code == 200:
            ngo = response.json()

            # Display basic information
            st.header(ngo["Name"])

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Basic Information")
                st.write(f"**Country:** {ngo['Country']}")
                st.write(f"**Founded:** {ngo['Founding_Year']}")
                st.write(f"**Focus Area:** {ngo['Focus_Area']}")
                st.write(f"**Website:** [{ngo['Website']}]({ngo['Website']})")
                if ngo.get("Notes"):
                    st.write(f"**Notes:** {ngo['Notes']}")

            with col2:
                st.subheader("Actions")
                if st.button("🗑 Remove This NGO", type="primary", use_container_width=True):
                    delete_response = requests.delete(API_URL)
                    if delete_response.status_code == 200:
                        st.success(f"{ngo['Name']} has been removed.")
                        del st.session_state["selected_ngo_id"]
                        st.switch_page("pages/14_NGO_Directory.py")
                    else:
                        st.error("Failed to remove NGO.")


        elif response.status_code == 404:
            st.error("NGO not found")
        else:
            st.error(
                f"Error fetching NGO data: {response.json().get('error', 'Unknown error')}"
            )

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")
        st.info("Please ensure the API server is running")

# Add a button to return to the NGO Directory
if st.button("Return to NGO Directory", key="bottom_return"):
    if "selected_ngo_id" in st.session_state:
        del st.session_state["selected_ngo_id"]
    st.switch_page("pages/14_NGO_Directory.py")
