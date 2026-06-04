from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

country_bp = Blueprint("countries", __name__)


# Get all countries
@country_bp.route("", methods=["GET"])
def get_all_countries():
    current_app.logger.info("GET /countries")
    try:
        query = """
            SELECT country_id, country_name, country_code, region, population
            FROM country
            ORDER BY country_name
        """

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query)
            countries = cursor.fetchall()

        return jsonify(countries), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_all_countries: {e}")
        return error_response(str(e))


# Get one country profile
@country_bp.route("/<int:country_id>", methods=["GET"])
def get_country(country_id):
    current_app.logger.info(f"GET /countries/{country_id}")
    try:
        query = """
            SELECT country_id, country_name, country_code, region, population
            FROM country
            WHERE country_id = %s
        """

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (country_id,))
            country = cursor.fetchone()

        if not country:
            return error_response("Country not found", 404)

        return jsonify(country), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_country: {e}")
        return error_response(str(e))


# Get yearly data for one country
@country_bp.route("/<int:country_id>/year-data", methods=["GET"])
def get_country_year_data(country_id):
    current_app.logger.info(f"GET /countries/{country_id}/year-data")
    try:
        query = """
            SELECT *
            FROM country_year_data
            WHERE country_id = %s
            ORDER BY year
        """

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (country_id,))
            year_data = cursor.fetchall()

        return jsonify(year_data), 200

    except Error as e:
        current_app.logger.error(f"Database error in get_country_year_data: {e}")
        return error_response(str(e))