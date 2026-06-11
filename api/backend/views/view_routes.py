from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

view_bp = Blueprint("views", __name__)


# Get all saved views for a user
@view_bp.route("/", methods=["GET"])
def get_saved_views():
    current_app.logger.info("GET /saved-views")
    try:
        user_id = request.args.get("user_id")

        query = """
            SELECT view_id, user_id, view_name, year_from, year_to, created_at, updated_at
            FROM saved_views
            WHERE 1=1
        """
        params = []

        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)

        query += " ORDER BY updated_at DESC"

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            saved_views = cursor.fetchall()

        return jsonify(saved_views), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_saved_views: {e}")
        return error_response(str(e))


# Get one saved view and its countries
@view_bp.route("/<int:view_id>", methods=["GET"])
def get_saved_view(view_id):
    current_app.logger.info(f"GET /saved-views/{view_id}")
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT view_id, user_id, view_name, year_from, year_to, created_at, updated_at
                FROM saved_views
                WHERE view_id = %s
            """, (view_id,))
            saved_view = cursor.fetchone()

            if not saved_view:
                return error_response("Saved view not found", 404)

            cursor.execute("""
                SELECT c.country_id, c.country_name, c.country_code, c.region
                FROM saved_view_country svc
                JOIN country c ON svc.country_id = c.country_id
                WHERE svc.view_id = %s
                ORDER BY c.country_name
            """, (view_id,))
            saved_view["countries"] = cursor.fetchall()

        return jsonify(saved_view), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_saved_view: {e}")
        return error_response(str(e))


# Create a new saved view
@view_bp.route("/", methods=["POST"])
def create_saved_view():
    current_app.logger.info("POST /saved-views")
    try:
        data = request.get_json()

        required_fields = ["user_id", "view_name"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("""
                INSERT INTO saved_views (user_id, view_name, year_from, year_to)
                VALUES (%s, %s, %s, %s)
            """, (
                data["user_id"],
                data["view_name"],
                data.get("year_from"),
                data.get("year_to")
            ))

            new_id = cursor.lastrowid

            country_ids = data.get("country_ids", [])
            for country_id in country_ids:
                cursor.execute("""
                    INSERT INTO saved_view_country (view_id, country_id)
                    VALUES (%s, %s)
                """, (new_id, country_id))

        get_db().commit()

        return jsonify({
            "message": "Saved view created successfully",
            "view_id": new_id
        }), 201

    except Error as e:
        current_app.logger.error(f"Database error in create_saved_view: {e}")
        return error_response(str(e))


# Update a saved view
@view_bp.route("/<int:view_id>", methods=["PUT"])
def update_saved_view(view_id):
    current_app.logger.info(f"PUT /saved-views/{view_id}")
    try:
        data = request.get_json()

        allowed_fields = ["view_name", "year_from", "year_to"]
        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT view_id FROM saved_views WHERE view_id = %s", (view_id,))
            if not cursor.fetchone():
                return error_response("Saved view not found", 404)

            if update_fields:
                params.append(view_id)
                query = f"""
                    UPDATE saved_views
                    SET {", ".join(update_fields)}
                    WHERE view_id = %s
                """
                cursor.execute(query, params)

            if "country_ids" in data:
                cursor.execute("DELETE FROM saved_view_country WHERE view_id = %s", (view_id,))

                for country_id in data["country_ids"]:
                    cursor.execute("""
                        INSERT INTO saved_view_country (view_id, country_id)
                        VALUES (%s, %s)
                    """, (view_id, country_id))

        get_db().commit()

        return jsonify({"message": "Saved view updated successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Database error in update_saved_view: {e}")
        return error_response(str(e))


# Delete a saved view
@view_bp.route("/<int:view_id>", methods=["DELETE"])
def delete_saved_view(view_id):
    current_app.logger.info(f"DELETE /saved-views/{view_id}")
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT view_id FROM saved_views WHERE view_id = %s", (view_id,))
            if not cursor.fetchone():
                return error_response("Saved view not found", 404)

            cursor.execute("DELETE FROM saved_view_country WHERE view_id = %s", (view_id,))
            cursor.execute("DELETE FROM saved_views WHERE view_id = %s", (view_id,))

        get_db().commit()

        return jsonify({"message": "Saved view deleted successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Database error in delete_saved_view: {e}")
        return error_response(str(e))