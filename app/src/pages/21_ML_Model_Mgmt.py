import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

st.title('App Administration Page')

st.write('## Model 1 Maintenance')
st.caption(
    "TERRA Model 1 predicts asylum applications. Its parameters are stored in "
    "the database (model1_params / model1_scaler); retraining refits the model "
    "and writes a new parameter version."
)

if st.button("Retrain Model 1", type='primary', use_container_width=True):
    with st.spinner("Retraining and storing parameters in the database..."):
        try:
            resp = requests.post('http://web-api:4000/model1/train')
            resp.raise_for_status()
            result = resp.json()
            st.success(
                f"Model retrained and stored as version {result['version']}."
            )
            m = result["metrics"]
            c1, c2, c3 = st.columns(3)
            c1.metric("R² (log scale)", f"{m['r2_log']:.3f}")
            c2.metric("MSE (log scale)", f"{m['mse_log']:.3f}")
            c3.metric("MAE (applications)", f"{m['mae_orig']:,.0f}")
        except Exception as e:
            st.error(f"Retraining failed: {e}")

st.divider()
st.write("To make a prediction, use the **Asylum Applications Prediction** page.")
