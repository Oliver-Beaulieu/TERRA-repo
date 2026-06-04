from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

policy_bp = Blueprint("policy", __name__)


# Create a policy flag
@policy_bp.route("/policy-flags", methods=["POST"])
def create_policy_flag():
    current_app.logger.info("POST /policy-flags")
    try:
        data = request.get_json()

        required_fields = ["country_id", "user_id", "flag_status"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        query = """
            INSERT INTO policy_flag (country_id, user_id, flag_status, flag_note)
            VALUES (%s, %s, %s, %s)
        """

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (
                data["country_id"],
                data["user_id"],
                data["flag_status"],
                data.get("flag_note")
            ))
            new_id = cursor.lastrowid

        get_db().commit()
        return jsonify({"message": "Policy flag created", "flag_id": new_id}), 201

    except Error as e:
        current_app.logger.error(f"Database error in create_policy_flag: {e}")
        return error_response(str(e))


# Update a policy flag
@policy_bp.route("/policy-flags/<int:flag_id>", methods=["PUT"])
def update_policy_flag(flag_id):
    current_app.logger.info(f"PUT /policy-flags/{flag_id}")
    try:
        data = request.get_json()

        allowed_fields = ["flag_status", "flag_note"]
        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        if not update_fields:
            return error_response("No valid fields to update", 400)

        params.append(flag_id)

        query = f"""
            UPDATE policy_flag
            SET {", ".join(update_fields)}
            WHERE flag_id = %s
        """

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)

        get_db().commit()
        return jsonify({"message": "Policy flag updated"}), 200

    except Error as e:
        current_app.logger.error(f"Database error in update_policy_flag: {e}")
        return error_response(str(e))


# Delete a policy flag
@policy_bp.route("/policy-flags/<int:flag_id>", methods=["DELETE"])
def delete_policy_flag(flag_id):
    current_app.logger.info(f"DELETE /policy-flags/{flag_id}")
    try:
        query = "DELETE FROM policy_flag WHERE flag_id = %s"

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (flag_id,))

        get_db().commit()
        return jsonify({"message": "Policy flag deleted"}), 200

    except Error as e:
        current_app.logger.error(f"Database error in delete_policy_flag: {e}")
        return error_response(str(e))