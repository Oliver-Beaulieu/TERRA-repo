from flask import Blueprint, jsonify, request, current_app

from backend.ml_models.terra_model_1 import predict

terra_model_bp = Blueprint("terra_model", __name__)


# Predict asylum applications using TERRA Model 1
# Example: POST /predict/asylum
@terra_model_bp.route("/predict/asylum", methods=["POST"])
def predict_asylum_applications():
    current_app.logger.info("POST /predict/asylum")

    try:
        data = request.get_json()

        required_fields = [
            "country_code",
            "year",
            "gdp_per_capita",
            "unemployment_rate",
            "population",
            "urban_pct",
            "temp_mean",
            "heatwave_days",
            "precip_total",
            "precip_days_heavy",
            "dry_days",
            "evapotrans_total",
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