from flask import Blueprint, jsonify, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

climate_bp = Blueprint("climate", __name__)


# Get climate events for one country
@climate_bp.route("/countries/<int:country_id>/climate-events", methods=["GET"])
def get_country_climate_events(country_id):
    current_app.logger.info(f"GET /countries/{country_id}/climate-events")
    try:
        query = """
            SELECT *
            FROM climate_event
            WHERE country_id = %s
            ORDER BY event_date DESC
        """

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (country_id,))
            events = cursor.fetchall()

        return jsonify(events), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_country_climate_events: {e}")
        return error_response(str(e))
