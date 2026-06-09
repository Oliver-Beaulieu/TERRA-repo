from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

from backend.ml_models.terra_model_1 import (
    predict            as model1_predict,
    train_test_model   as model1_train,
    store_params_in_db as model1_store,
)
from backend.ml_models.terra_model_2 import (
    predict            as model2_predict,
    train_test_model   as model2_train,
    store_params_in_db as model2_store,
)

terra_model_bp = Blueprint("terra_model", __name__)


# Retrain TERRA Model 1 and store the new parameters in the database.
# Example: POST /model1/train  (admin "Train Model 1" action)
@terra_model_bp.route("/model1/train", methods=["POST"])
def train_model1():
    current_app.logger.info("POST /model1/train")
    try:
        artifacts = model1_train()
        seq = model1_store(artifacts)
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

        prediction = model1_predict(data)

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


# Bulk asylum risk predictions for all countries — used by the Risk Map.
# Fetches the most recent available year's climate/economic data for every
# country in the DB, runs Model 1 on each, and returns a risk-scored list.
# Example: GET /predict/asylum-map          (uses latest year per country)
#          GET /predict/asylum-map?year=2022 (uses a specific year)
@terra_model_bp.route("/predict/asylum-map", methods=["GET"])
def predict_asylum_map():
    current_app.logger.info("GET /predict/asylum-map")
    try:
        year_filter = request.args.get("year", type=int)

        if year_filter:
            query = """
                SELECT c.country_name, c.country_code,
                       cyd.year,
                       cyd.gdp_per_capita, cyd.unemployment_rate,
                       cyd.temp_mean, cyd.heatwave_days,
                       cyd.precip_days_heavy, cyd.dry_days
                FROM country_year_data cyd
                JOIN country c ON cyd.country_id = c.country_id
                WHERE cyd.year = %s
                  AND cyd.gdp_per_capita IS NOT NULL
                  AND cyd.unemployment_rate IS NOT NULL
                  AND cyd.temp_mean IS NOT NULL
                ORDER BY c.country_name
            """
            params = (year_filter,)
        else:
            # Latest year with complete data per country
            query = """
                SELECT c.country_name, c.country_code,
                       cyd.year,
                       cyd.gdp_per_capita, cyd.unemployment_rate,
                       cyd.temp_mean, cyd.heatwave_days,
                       cyd.precip_days_heavy, cyd.dry_days
                FROM country_year_data cyd
                JOIN country c ON cyd.country_id = c.country_id
                INNER JOIN (
                    SELECT country_id, MAX(year) AS max_year
                    FROM country_year_data
                    WHERE gdp_per_capita IS NOT NULL
                      AND unemployment_rate IS NOT NULL
                      AND temp_mean IS NOT NULL
                    GROUP BY country_id
                ) latest ON cyd.country_id = latest.country_id
                         AND cyd.year = latest.max_year
                ORDER BY c.country_name
            """
            params = ()

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            user_inputs = {
                "country_code": row["country_code"],
                "gdp_per_capita": float(row["gdp_per_capita"] or 0),
                "unemployment_rate": float(row["unemployment_rate"] or 0),
                "temp_mean": float(row["temp_mean"] or 0),
                "heatwave_days": int(row["heatwave_days"] or 0),
                "precip_days_heavy": int(row["precip_days_heavy"] or 0),
                "dry_days": int(row["dry_days"] or 0),
            }
            try:
                predicted = model1_predict(user_inputs)
            except Exception:
                predicted = 0

            if predicted < 1000:
                risk_level = "Low"
            elif predicted < 10000:
                risk_level = "Medium"
            elif predicted < 50000:
                risk_level = "High"
            else:
                risk_level = "Critical"

            results.append({
                "country_name": row["country_name"],
                "country_code": row["country_code"],
                "year": row["year"],
                "predicted_asylum": round(predicted, 0),
                "risk_level": risk_level,
            })

        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"DB error in predict_asylum_map: {e}")
        return jsonify({"error": "Database error", "message": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in predict_asylum_map: {e}")
        return jsonify({"error": "Failed", "message": str(e)}), 500


# ── TERRA Model 2 ─────────────────────────────────────────────────────────────
# Multivariate Linear Regression predicting three climate variables:
#   heatwave_days, precip_days_heavy, dry_days
# Inputs: gdp_per_capita, unemployment_rate, population, urban_pct,
#         asylum_applications, country_code


# Retrain TERRA Model 2 and store the new parameters in the database.
# Example: POST /model2/train
@terra_model_bp.route("/model2/train", methods=["POST"])
def train_model2():
    current_app.logger.info("POST /model2/train")
    try:
        artifacts = model2_train()
        seq = model2_store(artifacts)
        return jsonify({
            "model":   "TERRA Model 2 Multivariate Linear Regression",
            "message": "Model retrained and parameters stored in the database.",
            "version": seq,
            "metrics": artifacts["metrics"],
        }), 200
    except Exception as e:
        current_app.logger.error(f"Model 2 training error: {e}")
        return jsonify({"error": "Training failed", "message": str(e)}), 500


# Predict climate variables (heatwave_days, precip_days_heavy, dry_days)
# for a single country-year using TERRA Model 2.
# Example: POST /predict/climate
# Body (JSON):
#   { "country_code": "DE", "gdp_per_capita": 46000, "unemployment_rate": 3.1,
#     "population": 83000000, "urban_pct": 77.4, "asylum_applications": 12000 }
@terra_model_bp.route("/predict/climate", methods=["POST"])
def predict_climate_variables():
    current_app.logger.info("POST /predict/climate")
    try:
        data = request.get_json()

        required_fields = [
            "country_code",
            "gdp_per_capita",
            "unemployment_rate",
            "population",
            "urban_pct",
            "asylum_applications",
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                "error":          "Missing required fields",
                "missing_fields": missing,
            }), 400

        predictions = model2_predict(data)

        return jsonify({
            "model":       "TERRA Model 2 Multivariate Linear Regression",
            "predictions": predictions,
            "input_data":  data,
        }), 200

    except Exception as e:
        current_app.logger.error(f"Model 2 prediction error: {e}")
        return jsonify({"error": "Prediction failed", "message": str(e)}), 500


# Bulk climate predictions for all countries — uses latest available year's
# economic / asylum data per country from the DB.
# Example: GET /predict/climate-map
#          GET /predict/climate-map?year=2022
@terra_model_bp.route("/predict/climate-map", methods=["GET"])
def predict_climate_map():
    current_app.logger.info("GET /predict/climate-map")
    try:
        year_filter = request.args.get("year", type=int)

        if year_filter:
            query = """
                SELECT c.country_name, c.country_code,
                       cyd.year,
                       cyd.gdp_per_capita, cyd.unemployment_rate,
                       cyd.population, cyd.urban_pct, cyd.asylum_applications
                FROM country_year_data cyd
                JOIN country c ON cyd.country_id = c.country_id
                WHERE cyd.year = %s
                  AND cyd.gdp_per_capita      IS NOT NULL
                  AND cyd.unemployment_rate   IS NOT NULL
                  AND cyd.population          IS NOT NULL
                ORDER BY c.country_name
            """
            params = (year_filter,)
        else:
            query = """
                SELECT c.country_name, c.country_code,
                       cyd.year,
                       cyd.gdp_per_capita, cyd.unemployment_rate,
                       cyd.population, cyd.urban_pct, cyd.asylum_applications
                FROM country_year_data cyd
                JOIN country c ON cyd.country_id = c.country_id
                INNER JOIN (
                    SELECT country_id, MAX(year) AS max_year
                    FROM country_year_data
                    WHERE gdp_per_capita    IS NOT NULL
                      AND unemployment_rate IS NOT NULL
                      AND population        IS NOT NULL
                    GROUP BY country_id
                ) latest ON cyd.country_id = latest.country_id
                         AND cyd.year = latest.max_year
                ORDER BY c.country_name
            """
            params = ()

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            user_inputs = {
                "country_code":       row["country_code"],
                "gdp_per_capita":     float(row["gdp_per_capita"] or 0),
                "unemployment_rate":  float(row["unemployment_rate"] or 0),
                "population":         float(row["population"] or 0),
                "urban_pct":          float(row["urban_pct"] or 0),
                "asylum_applications": float(row["asylum_applications"] or 0),
            }
            try:
                preds = model2_predict(user_inputs)
            except Exception:
                preds = {
                    "heatwave_days_pred":    0,
                    "precip_days_heavy_pred": 0,
                    "dry_days_pred":          0,
                }

            results.append({
                "country_name":          row["country_name"],
                "country_code":          row["country_code"],
                "year":                  row["year"],
                "heatwave_days_pred":    round(preds["heatwave_days_pred"], 1),
                "precip_days_heavy_pred": round(preds["precip_days_heavy_pred"], 1),
                "dry_days_pred":         round(preds["dry_days_pred"], 1),
            })

        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f"DB error in predict_climate_map: {e}")
        return jsonify({"error": "Database error", "message": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Error in predict_climate_map: {e}")
        return jsonify({"error": "Failed", "message": str(e)}), 500