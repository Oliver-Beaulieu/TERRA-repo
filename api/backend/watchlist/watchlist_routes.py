from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

watchlist_bp = Blueprint("watchlist", __name__)


# Get all watchlist entries for a user
@watchlist_bp.route("/", methods=["GET"])
def get_watchlist():
    current_app.logger.info("GET /watchlist")
    try:
        user_id = request.args.get("user_id")

        if not user_id:
            return error_response("Missing required query param: user_id", 400)

        query = """
            SELECT w.watchlist_id, w.user_id, w.added_at,
                   c.country_id, c.country_name, c.country_code, c.region
            FROM watchlist w
            JOIN country c ON w.country_id = c.country_id
            WHERE w.user_id = %s
            ORDER BY w.added_at DESC
        """

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id,))
            entries = cursor.fetchall()

        return jsonify(entries), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_watchlist: {e}")
        return error_response(str(e))


# Add a country to a user's watchlist
@watchlist_bp.route("/", methods=["POST"])
def add_to_watchlist():
    current_app.logger.info("POST /watchlist")
    try:
        data = request.get_json()

        required_fields = ["user_id", "country_id"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("""
                INSERT INTO watchlist (user_id, country_id)
                VALUES (%s, %s)
            """, (data["user_id"], data["country_id"]))
            new_id = cursor.lastrowid

        get_db().commit()

        return jsonify({
            "message": "Country added to watchlist",
            "watchlist_id": new_id
        }), 201

    except Error as e:
        current_app.logger.error(f"Database error in add_to_watchlist: {e}")
        return error_response(str(e))


# Remove a country from a user's watchlist
@watchlist_bp.route("/<int:watchlist_id>", methods=["DELETE"])
def remove_from_watchlist(watchlist_id):
    current_app.logger.info(f"DELETE /watchlist/{watchlist_id}")
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT watchlist_id FROM watchlist WHERE watchlist_id = %s",
                (watchlist_id,)
            )
            if not cursor.fetchone():
                return error_response("Watchlist entry not found", 404)

            cursor.execute(
                "DELETE FROM watchlist WHERE watchlist_id = %s",
                (watchlist_id,)
            )

        get_db().commit()

        return jsonify({"message": "Country removed from watchlist"}), 200

    except Error as e:
        current_app.logger.error(f"Database error in remove_from_watchlist: {e}")
        return error_response(str(e))
