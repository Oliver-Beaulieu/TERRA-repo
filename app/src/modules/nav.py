# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st
from pathlib import Path


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About TERRA", icon="🧠")


# ---- Role: pol_analyst ------------------------------------------------

def policy_analyst_home_nav():
    name = st.session_state.get('display_name', st.session_state.get('first_name', 'Home'))
    st.sidebar.page_link(
        "pages/00_Policy_Analyst_Home.py", label=f"{name} — Home", icon="🏠"
    )


def compare_countries_nav():
    st.sidebar.page_link(
        "pages/03_Compare_Countries.py", label="Compare Countries", icon="📊"
    )


def classification_nav():
    st.sidebar.page_link(
        "pages/13_Classification.py", label="Risk Classification", icon="🗺️"
    )


def prediction_nav():
    st.sidebar.page_link(
        "pages/11_Prediction.py", label="Prediction Model", icon="📈"
    )


def export_reports_nav():
    st.sidebar.page_link(
        "pages/04_Export_Reports.py", label="Export / Reports", icon="⬇"
    )

def saved_views_nav():
    st.sidebar.page_link(
        "pages/10_Saved_Views.py", label="Saved Views", icon="💾"
    )



# ---- Role: humanitarian_coordinator -----------------------------------------------------

def humanitarian_coordinator_home_nav():
    name = st.session_state.get('display_name', st.session_state.get('first_name', 'Home'))
    st.sidebar.page_link(
        "pages/01_Humanitarian_Coordinator_Home.py", label=f"{name} — Home", icon="🏠"
    )


def risk_map_nav():
    st.sidebar.page_link("pages/02_Map_Demo.py", label="Predictive Risk Map", icon="🗺️")


def priority_countries_nav():
    st.sidebar.page_link(
        "pages/05_Priority_Countries.py", label="Priority Risk Countries", icon="🚨"
    )


def ngo_directory_nav():
    st.sidebar.page_link("pages/14_NGO_Directory.py", label="NGO Directory", icon="🏢")


def add_ngo_nav():
    st.sidebar.page_link("pages/15_Add_NGO.py", label="Add NGO", icon="➕")


def ngo_profile_nav():
    st.sidebar.page_link("pages/16_NGO_Profile.py", label="NGO Profile", icon="👥")


def export_country_summary_nav():
    st.sidebar.page_link(
        "pages/06_Export_Country_Summary.py", label="Export Country Summary", icon="⬇"
    )

# ---- Role: student_user ------------------------------------------------------

def student_home_nav():
    name = st.session_state.get('display_name', st.session_state.get('first_name', 'Home'))
    st.sidebar.page_link(
        "pages/20_Mohammed_Home.py", label=f"{name} — Home", icon="🏠"
    )


def explore_risk_map_nav():
    st.sidebar.page_link("pages/02_Map_Demo.py", label="Predictive Risk Map", icon="🗺️")


def climate_events_nav():
    st.sidebar.page_link(
        "pages/07_Climate_Events.py", label="Climate Events", icon="🌡️"
    )


def displacement_timeline_nav():
    st.sidebar.page_link(
        "pages/08_Displacement_Timeline.py", label="Displacement Timeline", icon="📈"
    )


def similar_countries_nav():
    st.sidebar.page_link(
        "pages/09_Similar_Countries.py", label="Similar Countries", icon="🔍"
    )


def my_watchlist_nav():
    st.sidebar.page_link(
        "pages/21_My_Watchlist.py", label="My Watchlist", icon="⭐"
    )

# ---- Role: administrator ----------------------------------------------------

def admin_home_nav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="System Admin", icon="🖥️")


def ml_model_mgmt_nav():
    st.sidebar.page_link(
        "pages/21_ML_Model_Mgmt.py", label="ML Model Management", icon="🏢"
    )

def new_ml_model_nav():
    st.sidebar.page_link(
        "pages/22_Prettier_ML.py", label="New ML Model", icon="📈"
    )

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    st.markdown("""
    <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebar"] > div:first-child,
        section[data-testid="stSidebar"] {
            background-color: #0d1f3c !important;
            border-right: 1px solid #25415F !important;
            box-shadow: 4px 0 16px rgba(0,0,0,0.4) !important;
        }
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarContent"] > div {
            background-color: #0d1f3c !important;
        }
        [data-testid="stSidebarNavLink"] {
            background-color: transparent !important;
        }
        [data-testid="stSidebarNavLink"]:hover {
            background-color: rgba(126,217,166,0.1) !important;
        }
        [data-testid="stSidebarNavLink"][aria-selected="true"],
        [data-testid="stSidebarNavLink"].active {
            background-color: rgba(126,217,166,0.12) !important;
        }
        [data-testid="stSidebar"] img {
            width: 100% !important;
            max-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

    logo_path = Path(__file__).parent.parent / "assets" / "TERRALogo.png"
    st.sidebar.image(str(logo_path), use_container_width=True)

    # Decorative gradient divider below logo
    st.sidebar.markdown("""
    <div style="margin: 4px 0 12px 0;">
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #3dba7e, transparent); border-radius: 2px;"></div>
        <div style="text-align: center; font-size: 16px; margin: 8px 0 2px 0; letter-spacing: 8px; opacity: 0.5;">🌍 🌿 🌊</div>
        <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(61,186,126,0.4), transparent); border-radius: 1px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "policy_analyst":
            policy_analyst_home_nav()
            compare_countries_nav()
            classification_nav()
            prediction_nav()
            saved_views_nav()
            export_reports_nav()

        if st.session_state["role"] == "humanitarian_coordinator":
            humanitarian_coordinator_home_nav()
            risk_map_nav()
            priority_countries_nav()
            ngo_directory_nav()
            add_ngo_nav()
            ngo_profile_nav()
            export_country_summary_nav()

        if st.session_state["role"] == "student_user":
            student_home_nav()
            explore_risk_map_nav()
            climate_events_nav()
            displacement_timeline_nav()
            similar_countries_nav()
            my_watchlist_nav()

        if st.session_state["role"] == "administrator":
            admin_home_nav()
            ml_model_mgmt_nav()
            new_ml_model_nav()
            
    # Decorative footer divider
    st.sidebar.markdown("""
    <div style="margin: 12px 0 4px 0;">
        <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(61,186,126,0.4), transparent);"></div>
        <div style="text-align: center; font-size: 10px; color: rgba(61,186,126,0.45); letter-spacing: 3px; text-transform: uppercase; margin: 8px 0 4px 0;">Track · Protect · Act</div>
        <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(61,186,126,0.4), transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
