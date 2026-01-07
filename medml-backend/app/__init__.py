# HealthCare App/medml-backend/app/__init__.py
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from app.config import config
from .extensions import db, jwt, bcrypt, cors, limiter # <-- ADDED limiter
from .api import api_bp
from . import services
# from .db_seeder import seed_static_recommendations # <-- REMOVED

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extension initializations
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    # Configure CORS origins from env (comma-separated), default to "*" in dev
    origins = os.environ.get('CORS_ORIGINS', '*')
    if isinstance(origins, str) and origins != '*':
        origins = [o.strip() for o in origins.split(',') if o.strip()]
    cors.init_app(app, resources={r"/api/*": {"origins": origins}})
    limiter.init_app(app) # <-- ADDED limiter init
    Migrate(app, db)
    
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
        # seed_static_recommendations() # <-- REMOVED
    # --- End ---

    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1') # Updated to v1

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
    # --- End Logging ---

    # Global error handler for 500
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Internal Server Error: {e}", exc_info=True)
        return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500
    
    @app.errorhandler(404)
    def not_found_error(e):
        # Use str(e) to get the default "Not Found" message or a custom one
        return jsonify(error="Not Found", message=str(e).replace("404 Not Found: ", "")), 404

    # --- JWT Blocklist callback (DB-backed) ---
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
            # Fail closed: if error occurs, treat as revoked
            return True

    # --- JWT Identity Callbacks for Dictionary Identities ---
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """
        Convert dictionary identity to string for JWT subject.
        This allows us to use dictionary identities while maintaining JWT compatibility.
        """
        if isinstance(user, dict):
            # Convert dict to a string representation that can be parsed back
            return f"{user.get('id')}:{user.get('role')}:{user.get('name', '')}"
        return str(user)


    return app