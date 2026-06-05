from flask import Blueprint, jsonify, request, current_app

from backend.ml_models.terra_model_1 import predict, train_test_model, store_params_in_db

terra_model_bp = Blueprint("terra_model", __name__)


# Retrain TERRA Model 1 and store the new parameters in the database.
# Example: POST /model1/train  (admin "Train Model 1" action)
@terra_model_bp.route("/model1/train", methods=["POST"])
def train_model1():
    current_app.logger.info("POST /model1/train")
    try:
        artifacts = train_test_model()
        seq = store_params_in_db(artifacts)
        return jsonify({
            "model": "TERRA Model 1 Linear Regression",
            "message": "Model retrained and parameters stored in the database.",
            "version": seq,
            "metrics": artifacts["metrics"],
        }), 200
    except Exception as e:
        current_app.logger.error(f"Training error: {e}")
        return jsonify({"error": "Training failed", "message": str(e)}), 500


# Predict asylum applications using TERRA Model 1
# Example: POST /predict/asylum
@terra_model_bp.route("/predict/asylum", methods=["POST"])
def predict_asylum_applications():
    current_app.logger.info("POST /predict/asylum")

    try:
        data = request.get_json()

        # Must match terra_model_1.NUMERIC_FEATURES (+ country_code). `year`,
        # population, urban_pct, precip_total, evapotrans_total were dropped
        # during model tuning and are intentionally no longer required.
        required_fields = [
            "country_code",
            "gdp_per_capita",
            "unemployment_rate",
            "temp_mean",
            "heatwave_days",
            "precip_days_heavy",
            "dry_days",
        ]

        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        prediction = predict(data)

        return jsonify({
            "model": "TERRA Model 1 Linear Regression",
            "prediction": round(prediction, 2),
            "input_data": data
        }), 200

    except Exception as e:
        current_app.logger.error(f"Prediction error: {e}")
        return jsonify({
            "error": "Prediction failed",
            "message": str(e)
        }), 500