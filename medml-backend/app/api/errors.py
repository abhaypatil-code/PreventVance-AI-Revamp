# HealthCare App/medml-backend/app/api/errors.py
from flask import jsonify
from . import api_bp
from pydantic import ValidationError
from .responses import bad_request, not_found, server_error, unauthorized, forbidden, unprocessable_entity

@api_bp.app_errorhandler(404)
def not_found_error(error):
    return not_found(str(error))

@api_bp.app_errorhandler(500)
def internal_error(error):
    # db.session.rollback() # Rollback in case of DB errors
    return server_error("An unexpected error occurred.")

@api_bp.app_errorhandler(400)
def bad_request_error(error):
    return bad_request(str(error))

@api_bp.app_errorhandler(422)
def validation_error(error):
    # This handler can catch Pydantic's ValidationError if raised
    if isinstance(error.description, ValidationError):
        return unprocessable_entity(messages=error.description.errors())
    return unprocessable_entity(message=str(error))

@api_bp.app_errorhandler(401)
def unauthorized_error(error):
    return unauthorized(str(error))

@api_bp.app_errorhandler(403)
def forbidden_error(error):
    return forbidden(str(error))