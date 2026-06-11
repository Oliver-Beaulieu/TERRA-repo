from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

risk_bp = Blueprint("risk", __name__)


# GET all risk classifications
@risk_bp.route("/classifications", methods=["GET"])
def get_all_risk_classifications():
    current_app.logger.info("GET /classifications")
    try:
        query = """
            SELECT r.risk_id, r.country_id, c.country_name, c.country_code,
                   r.year, r.risk_score, r.risk_level, r.label_method, r.notes
            FROM risk_assessment r
            JOIN country c ON r.country_id = c.country_id
            ORDER BY r.year DESC, r.risk_score DESC
        """
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query)
            risks = cursor.fetchall()
        return jsonify(risks), 200
    except Error as e:
        current_app.logger.error(f"DB error in get_all_risk_classifications: {e}")
        return error_response(str(e))


#Update a country's risk classification for a specific year
@risk_bp.route("/classifications/<int:country_id>", methods=["PUT"])
def update_country_risk_classification(country_id):
    current_app.logger.info(f"PUT /classifications/{country_id}")
    try:
        data = request.get_json()

        for field in ["year", "risk_score", "risk_level"]:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        query = """
            UPDATE risk_assessment
            SET risk_score = %s, risk_level = %s, label_method = %s, notes = %s
            WHERE country_id = %s AND year = %s
        """
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (
                data["risk_score"],
                data["risk_level"],
                data.get("label_method"),
                data.get("notes"),
                country_id,
                data["year"],
            ))
            get_db().commit()
        return jsonify({"message": "Risk classification updated"}), 200
    except Error as e:
        current_app.logger.error(f"DB error in update_country_risk_classification: {e}")
        return error_response(str(e))