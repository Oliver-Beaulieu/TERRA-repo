from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

report_bp = Blueprint("reports", __name__)


# Get all saved reports for a user
@report_bp.route("/", methods=["GET"])
def get_reports():
    current_app.logger.info("GET /reports")
    try:
        user_id = request.args.get("user_id")

        if not user_id:
            return error_response("Missing required query param: user_id", 400)

        query = """
            SELECT r.report_id, r.user_id, r.report_title,
                   r.report_text, r.export_format, r.generated_at,
                   c.country_id, c.country_name, c.country_code
            FROM country_summary_report r
            JOIN country c ON r.country_id = c.country_id
            WHERE r.user_id = %s
            ORDER BY r.generated_at DESC
        """

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id,))
            reports = cursor.fetchall()

        return jsonify(reports), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_reports: {e}")
        return error_response(str(e))


# Save a new report
@report_bp.route("/", methods=["POST"])
def create_report():
    current_app.logger.info("POST /reports")
    try:
        data = request.get_json()

        required_fields = ["country_id", "user_id", "report_title"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("""
                INSERT INTO country_summary_report
                    (country_id, user_id, report_title, report_text, export_format)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                data["country_id"],
                data["user_id"],
                data["report_title"],
                data.get("report_text"),
                data.get("export_format", "CSV"),
            ))
            new_id = cursor.lastrowid

        get_db().commit()

        return jsonify({
            "message": "Report saved successfully",
            "report_id": new_id
        }), 201

    except Error as e:
        current_app.logger.error(f"Database error in create_report: {e}")
        return error_response(str(e))


# Delete a saved report
@report_bp.route("/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    current_app.logger.info(f"DELETE /reports/{report_id}")
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT report_id FROM country_summary_report WHERE report_id = %s",
                (report_id,)
            )
            if not cursor.fetchone():
                return error_response("Report not found", 404)

            cursor.execute(
                "DELETE FROM country_summary_report WHERE report_id = %s",
                (report_id,)
            )

        get_db().commit()

        return jsonify({"message": "Report deleted successfully"}), 200

    except Error as e:
        current_app.logger.error(f"Database error in delete_report: {e}")
        return error_response(str(e))
