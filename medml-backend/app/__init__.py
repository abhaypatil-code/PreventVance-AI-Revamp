# HealthCare App/medml-backend/app/__init__.py
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()

from app.config import config
from .extensions import db, jwt, bcrypt, cors, limiter
from .api import api_bp
from . import services

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extension initializations
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    # Configure CORS
    origins = os.environ.get('CORS_ORIGINS', '*')
    if isinstance(origins, str) and origins != '*':
        origins = [o.strip() for o in origins.split(',') if o.strip()]
    cors.init_app(app, resources={r"/api/*": {"origins": origins}})
    limiter.init_app(app)
    
    # Create DB tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # --- Load ML Models ---
    with app.app_context():
        # Enable SQLite foreign key enforcement
        try:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                try:
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
                except Exception:
                    pass
        except Exception:
            pass

        services.load_models(app)
    
    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Import models to ensure they are registered
    from . import models

    # --- Add Logging ---
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/medml.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('MedML backend startup')

    # Global error handler for 500
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Internal Server Error: {e}", exc_info=True)
        return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500
    
    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify(error="Not Found", message=str(e).replace("404 Not Found: ", "")), 404

    # --- JWT Callbacks ---
    from app.models import TokenBlocklist
    from flask_jwt_extended import JWTManager

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        try:
            jti = jwt_payload.get('jti')
            if not jti:
                return False
            return db.session.query(TokenBlocklist.id).filter(TokenBlocklist.jti == jti).first() is not None
        except Exception:
            return True

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, dict):
            return f"{user.get('id')}:{user.get('role')}:{user.get('name', '')}"
        return str(user)

    return app