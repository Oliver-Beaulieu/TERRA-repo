from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

# Variable name includes the domain (ngo_bp) so it stays readable when
# imported alongside other blueprints (e.g. `from ... import ngo_bp, donor_bp`).
ngo_bp = Blueprint("ngos", __name__)


# Get all NGOs with optional filtering by country, focus area, and founding year
# Example: /ngo/ngos?country=United%20States&focus_area=Environmental%20Conservation
@ngo_bp.route("/ngos", methods=["GET"])
def get_all_ngos():
    current_app.logger.info('GET /ngo/ngos')
    try:
        # Query parameters are added after the main part of the URL.
        # Example: http://localhost:4000/ngo/ngos?founding_year=1971
        country = request.args.get("country")
        focus_area = request.args.get("focus_area")
        founding_year = request.args.get("founding_year")

        # WHERE 1=1 lets us append AND clauses cleanly without special-casing the first filter
        query = "SELECT * FROM WorldNGOs WHERE 1=1"
        params = []

        if country:
            query += " AND Country = %s"
            params.append(country)
        if focus_area:
            query += " AND Focus_Area = %s"
            params.append(focus_area)
        if founding_year:
            query += " AND Founding_Year = %s"
            params.append(founding_year)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            ngo_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(ngo_list)} NGOs')
        return jsonify(ngo_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_ngos: {e}')
        return error_response(str(e))


# Get detailed information about a specific NGO including its projects and donors
# Example: /ngo/ngos/1
@ngo_bp.route("/ngos/<int:ngo_id>", methods=["GET"])
def get_ngo(ngo_id):
    current_app.logger.info(f'GET /ngo/ngos/{ngo_id}')
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM WorldNGOs WHERE NGO_ID = %s", (ngo_id,))
            ngo = cursor.fetchone()

            if not ngo:
                return error_response("NGO not found", 404)

            # Reuse the same cursor for the follow-up queries
            cursor.execute("SELECT * FROM Projects WHERE NGO_ID = %s", (ngo_id,))
            ngo["projects"] = cursor.fetchall()

            cursor.execute("SELECT * FROM Donors WHERE NGO_ID = %s", (ngo_id,))
            ngo["donors"] = cursor.fetchall()

        return jsonify(ngo), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_ngo: {e}')
        return error_response(str(e))


# Create a new NGO
# Required fields: Name, Country, Founding_Year, Focus_Area, Website
# Example: POST /ngo/ngos with JSON body
@ngo_bp.route("/ngos", methods=["POST"])
def create_ngo():
    current_app.logger.info('POST /ngo/ngos')
    try:
        data = request.get_json()

        required_fields = ["Name", "Country", "Founding_Year", "Focus_Area", "Website"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        query = """
            INSERT INTO WorldNGOs (Name, Country, Founding_Year, Focus_Area, Website, Notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (
                data["Name"],
                data["Country"],
                data["Founding_Year"],
                data["Focus_Area"],
                data["Website"],
                data.get("Notes", ""),
            ))
            new_id = cursor.lastrowid

        get_db().commit()
        current_app.logger.info(f'Created NGO with id={new_id}')
        return jsonify({"message": "NGO created successfully", "ngo_id": new_id}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_ngo: {e}')
        return error_response(str(e))


# Update an existing NGO's information
# Can update any field except NGO_ID
# Example: PUT /ngo/ngos/1 with JSON body containing fields to update
@ngo_bp.route("/ngos/<int:ngo_id>", methods=["PUT"])
def update_ngo(ngo_id):
    current_app.logger.info(f'PUT /ngo/ngos/{ngo_id}')
    try:
        data = request.get_json()

        # Build update query dynamically based on provided fields
        allowed_fields = ["Name", "Country", "Founding_Year", "Focus_Area", "Website", "Notes"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return error_response("No valid fields to update", 400)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT NGO_ID FROM WorldNGOs WHERE NGO_ID = %s", (ngo_id,))
            if not cursor.fetchone():
                return error_response("NGO not found", 404)

            params.append(ngo_id)
            query = f"UPDATE WorldNGOs SET {', '.join(update_fields)} WHERE NGO_ID = %s"
            cursor.execute(query, params)

        get_db().commit()
        return jsonify({"message": "NGO updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_ngo: {e}')
        return error_response(str(e))


# Delete an NGO
# Example: DELETE /ngo/ngos/1
@ngo_bp.route("/ngos/<int:ngo_id>", methods=["DELETE"])
def delete_ngo(ngo_id):
    current_app.logger.info(f'DELETE /ngo/ngos/{ngo_id}')
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT NGO_ID FROM WorldNGOs WHERE NGO_ID = %s", (ngo_id,))
            if not cursor.fetchone():
                return error_response("NGO not found", 404)

            cursor.execute("DELETE FROM WorldNGOs WHERE NGO_ID = %s", (ngo_id,))

        get_db().commit()
        current_app.logger.info(f'Deleted NGO id={ngo_id}')
        return jsonify({"message": "NGO deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_ngo: {e}')
        return error_response(str(e))
