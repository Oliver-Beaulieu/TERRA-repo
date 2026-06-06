from flask import Blueprint, jsonify, request, current_app
from backend.utils import error_response

import sys
import os

# make ml-src importable so we can reuse model_1.py
sys.path.append("/ml-src")
import model_1

prediction_bp = Blueprint("prediction", __name__)


# POST a single prediction. Body = JSON dict of the model's features.
@prediction_bp.route("/prediction", methods=["POST"])
def make_prediction():
    current_app.logger.info("POST /prediction")
    try:
        user_inputs = request.get_json()
        if not user_inputs:
            return error_response("No input data provided", 400)

        result = model_1.predict(user_inputs)
        return jsonify({"predicted_asylum_applications": round(result)}), 200
    except Exception as e:
        current_app.logger.error(f"Error in make_prediction: {e}")
        return error_response(str(e))