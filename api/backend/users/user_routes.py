from flask import Blueprint, jsonify
from backend.db_connection import get_db

user_bp = Blueprint('users', __name__)


@user_bp.route('/by-role/<role_name>', methods=['GET'])
def get_users_by_role(role_name):
    """Return all active users for a given role name (e.g. policy_analyst)."""
    try:
        db = get_db()
        with db.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT u.user_id, u.display_name, u.email
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE r.role_name = %s AND u.is_active = TRUE
                ORDER BY u.display_name
            """, (role_name,))
            users = cursor.fetchall()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
