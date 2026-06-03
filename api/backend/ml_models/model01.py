"""
model01.py demonstrates how to store model parameters in the database
and retrieve them at prediction time via a REST route.
"""
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


def predict(var01, var02):
    """
    Retrieves model parameters from the database and uses them for
    real-time prediction. Parameters are stored as a comma-separated
    string and parsed into a numpy array here.

    Raises ValueError if inputs cannot be converted to float, or if
    no model parameters exist in the database yet.
    """
    # Input validation belongs here at the boundary between the route and the model.
    # If conversion fails, ValueError propagates up to the route handler.
    x1 = float(var01)
    x2 = float(var02)

    with get_db().cursor(dictionary=True) as cursor:
        query = 'SELECT beta_vals FROM model1_params ORDER BY sequence_number DESC LIMIT 1'
        cursor.execute(query)
        row = cursor.fetchone()

    if row is None:
        raise ValueError("No model parameters found in the database")

    # Parse the stored parameter string (e.g. "[1.2,3.4,5.6]") into a numpy array
    params_array = np.array(list(map(float, row['beta_vals'][1:-1].split(','))))
    current_app.logger.info(f'params_array = {params_array}')

    # Prepend 1.0 as the intercept term, then dot with the parameter vector
    input_array = np.array([1.0, x1, x2])
    return float(params_array.T @ input_array)
