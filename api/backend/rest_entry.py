from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import init_app as init_db
from backend.simple.simple_routes import simple_routes
from backend.ml_models.terra_model_routes import terra_model_bp
from backend.ngos.ngo_routes import ngo_bp
from backend.countries.country_routes import country_bp
from backend.climate.climate_routes import climate_bp
from backend.risk.risk_routes import risk_bp
from backend.prediction.prediction_routes import prediction_bp
from backend.views.view_routes import view_bp
from backend.policy.policy_routes import policy_bp


def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    # .strip() removes accidental leading/trailing whitespace from .env values.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY").strip()

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    # simple_routes has no prefix intentionally — it serves root-level demo routes (/, /playlist, etc.)
    app.logger.info("create_app(): registering blueprints")
    app.register_blueprint(simple_routes)
    app.register_blueprint(ngo_bp, url_prefix="/ngo")
    app.register_blueprint(country_bp, url_prefix="/countries")
    app.register_blueprint(climate_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(view_bp)
    app.register_blueprint(terra_model_bp)
    app.register_blueprint(policy_bp)

    return app