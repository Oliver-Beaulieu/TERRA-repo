"""
model02.py — Belgium GDP regression model (HW2 Part 3.1)

Predicts Belgium GDP (EUR per capita) from:
  - Fossil_Fuels : fossil fuel energy as a % of total energy consumption
  - CO2_Upop     : CO2 emissions (kt) divided by urban population

Model parameters (intercept + two slopes) are stored in the model2_params
table and fetched at prediction time, just like model01.py.

Note: we will need to get scaler parameters from the DB as well to apply
scaling to the raw values the user inputs on the front end

To "retrain" the model, you would create a different function that refits
the regression and then UPDATEs the model2_params table with the new beta_vals.
For simplicity, the train() function below is just a placeholder
"""
import json
import numpy as np
from flask import current_app
from backend.db_connection import get_db


def train():
    """
    Placeholder for a training routine. Could be triggered from an
    admin route to retrain the model and store new parameters in the DB.
    """
    return 'Training the model'


def test():
    return 'Testing the model'


# ------------------------------------------------------------
# Internal helpers — fetch the latest beta vector from the DB.
# Also fetch the scaler parameters that are stored in the DB.
# Kept private (leading underscore) so routes import the public
# functions below rather than the raw DB call.
# ------------------------------------------------------------
def _get_params():
    """
    Fetches the most recent parameter vector from model2_params.

    Returns:
        np.ndarray: 1-D array [intercept, b_Fossil_Fuels, b_CO2_Upop]

    Raises:
        ValueError: if no parameters exist in the database yet.
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT beta_vals FROM model2_params ORDER BY sequence_number DESC LIMIT 1'
        )
        row = cursor.fetchone()

    if row is None:
        raise ValueError("No model2 parameters found in the database.")

    # beta_vals is stored as a JSON-style list string e.g. "[1.2, 3.4, 5.6]"
    params = np.array(json.loads(row['beta_vals']))
    current_app.logger.info(f'model02 params loaded: {params}')
    return params

def _get_scaler_params():
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT feature_means, feature_stds FROM model2_scaler '
            'ORDER BY sequence_number DESC LIMIT 1'
        )
        row = cursor.fetchone()
    if row is None:
        raise ValueError("No model2 scaler parameters found in the database.")
    means = np.array(json.loads(row['feature_means']))
    stds  = np.array(json.loads(row['feature_stds']))
    return means, stds

# ------------------------------------------------------------
# Public functions called by the route handlers
# ------------------------------------------------------------

def predict(fossil_fuels, co2_upop):
    """
    Returns a single GDP prediction given the two input features.

    Args:
        fossil_fuels (str | float): fossil fuel % of total energy
        co2_upop     (str | float): CO2_emit / Urban_pop

    Returns:
        float: predicted GDP per capita (EUR)

    Raises:
        ValueError: if inputs cannot be cast to float, or no params in DB.
    """
    x1 = float(fossil_fuels)
    x2 = float(co2_upop)

    params = _get_params()
    means, stds = _get_scaler_params()

    # apply the same standardization used at training time
    x_scaled = (np.array([x1, x2]) - means) / stds
    
    # [1, x1, x2] . [intercept, b1, b2]
    input_vec = np.array([1.0, x_scaled[0], x_scaled[1]])
    prediction = float(params.T @ input_vec)
    current_app.logger.info(
        f'model02.predict({x1}, {x2}) -> {prediction:.2f}'
    )
    return prediction


def get_observations_with_predictions():
    """
    Fetches the full Belgium dataset from the database and adds a
    column of model predictions, residuals, and the fitted betas.
    Used by the observed-vs-predicted plot on the admin page.

    Returns:
        list[dict]: one dict per year, with keys:
            year, GDP, Fossil_Fuels, CO2_Upop,
            GDP_predicted, residual
    """
    params = _get_params()

    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT year, GDP, Fossil_Fuels, CO2_Upop '
            'FROM belgium_energy ORDER BY year'
        )
        rows = cursor.fetchall()

    means, stds = _get_scaler_params()
    results = []
    for row in rows:
        x1 = row['Fossil_Fuels']
        x2 = row['CO2_Upop']
        x_raw = np.array([x1, x2])
        x_scaled = (x_raw - means) / stds
        y_pred = float(params.T @ np.array([1.0, x_scaled[0], x_scaled[1]]))
        results.append({
            'year':          row['year'],
            'GDP':           round(row['GDP'], 2),
            'Fossil_Fuels':  round(x1, 4),
            'CO2_Upop':      round(x2, 6),
            'GDP_predicted': round(y_pred, 2),
            'residual':      round(row['GDP'] - y_pred, 2),
        })

    return results
