# HealthCare App/medml-backend/app/api/auth.py
from flask import request, jsonify, abort, current_app
from . import api_bp
from app.models import User, Patient, TokenBlocklist
from app.extensions import db, limiter
from app.schemas import UserRegisterSchema, UserLoginSchema, PatientLoginSchema, PASSWORD_ERROR_MSG
from pydantic import ValidationError
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt,
    get_jti
)
from .decorators import parse_jwt_identity
from datetime import datetime # Added
from .responses import (
    ok,
    created,
    bad_request,
    unauthorized,
    forbidden,
    not_found,
    conflict,
    unprocessable_entity,
    server_error,
)

# Rate limiting to login endpoints
LOGIN_LIMIT = "10 per minute"

@api_bp.route('/auth/admin/register', methods=['POST'])
@limiter.limit("5 per hour") # Stricter limit for registration
def register_admin():
    """
    Registers a new Admin (Healthcare Worker).
    """
    try:
        data = UserRegisterSchema(**request.json)
    except ValidationError as e:
        if any('regex' in err['type'] for err in e.errors()):
            return unprocessable_entity(message=PASSWORD_ERROR_MSG)
        return unprocessable_entity(messages=e.errors())

    if User.query.filter_by(email=data.email).first():
        return conflict("Email already exists")
    
    if data.username and User.query.filter_by(username=data.username).first():
        return conflict("Username already exists")

    new_user = User(
        name=data.name,
        email=data.email,
        username=data.username,
        designation=data.designation,
        contact_number=data.contact_number,
        facility_name=data.facility_name,
        role='admin' # Enforce admin role
    )
    new_user.set_password(data.password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error registering admin: {e}")
        return server_error("Could not register admin.")

    current_app.logger.info(f"New admin registered: {new_user.email}")
    return created({"message": "Admin registered successfully", "user": new_user.to_dict()})

@api_bp.route('/auth/admin/login', methods=['POST'])
@limiter.limit(LOGIN_LIMIT) # Apply rate limit
def login_admin():
    """
    Logs in an Admin (Healthcare Worker) using username or email.
    """
    try:
        data = request.json
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')
        
        if not username_or_email or not password:
            return unprocessable_entity(message="Username/email and password are required")
    except Exception:
        return unprocessable_entity(message="Invalid request format")

    # Try to find user by username first, then by email
    user = User.query.filter_by(username=username_or_email).first()
    if not user:
        user = User.query.filter_by(email=username_or_email).first()

    if user and user.check_password(password):
        # Create token with role identity
        identity = {"id": user.id, "role": user.role, "name": user.name}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        current_app.logger.info(f"Admin login successful: {user.username or user.email}")
        return ok({
            "message": "Admin login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "admin_id": user.id,
            "name": user.name,
        })
    
    current_app.logger.warning(f"Failed admin login attempt for: {username_or_email[:3]}***")
    return unauthorized("Invalid username/email or password.")

@api_bp.route('/auth/patient/login', methods=['POST'])
@limiter.limit(LOGIN_LIMIT) # Apply rate limit
def login_patient():
    """
    Logs in a Patient using ABHA ID only (password-free for simplified access).
    This simplified authentication is designed for rural healthcare settings.
    """
    try:
        data = PatientLoginSchema(**request.json)
    except ValidationError as e:
        return unprocessable_entity(messages=e.errors())

    patient = Patient.query.filter_by(abha_id=data.abha_id).first()

    if patient:
        # Password-free authentication - just verify ABHA ID exists
        # Create token with role identity
        identity = {"id": patient.id, "role": "patient", "name": patient.name}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        current_app.logger.info(f"Patient login successful: {patient.abha_id}")
        return ok({
            "message": "Patient login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "patient_id": patient.id,
            "name": patient.name,
        })
    
    current_app.logger.warning(f"Failed patient login attempt for ABHA ID: {data.abha_id}")
    return unauthorized("Invalid ABHA ID. Patient not found.")


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refreshes an access token.
    """
    try:
        identity = parse_jwt_identity()
        current_jti = get_jwt().get('jti')
        
        # Blocklist the used refresh token
        db.session.add(TokenBlocklist(jti=current_jti, token_type='refresh', user_id=identity.get('id')))
        db.session.commit()

        # Create new tokens
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        return ok({"access_token": access_token, "refresh_token": refresh_token})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error refreshing token: {e}")
        return unauthorized("Token refresh failed")


@api_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logs out a user by blocklisting their token.
    """
    jwt_payload = get_jwt()
    jti = jwt_payload.get("jti")
    token_type = jwt_payload.get("type", "access")
    expires = datetime.fromtimestamp(jwt_payload.get("exp"))
    identity = parse_jwt_identity() or {}
    try:
        db.session.add(TokenBlocklist(jti=jti, token_type=token_type, user_id=identity.get('id'), expires_at=expires))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to revoke token: {e}")
        return server_error("Failed to revoke token")
    return ok({"message": "Token successfully revoked"})


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Returns the profile of the currently authenticated user (Admin or Patient).
    """
    try:
        jwt_identity = parse_jwt_identity()
        user_id = jwt_identity.get('id')
        user_role = jwt_identity.get('role')

        if not user_id or not user_role:
            return unauthorized("Invalid token identity")

        if user_role == 'admin':
            user = User.query.get(user_id)
            if not user:
                return not_found("User not found")
            return ok(user.to_dict())
        elif user_role == 'patient':
            patient = Patient.query.get(user_id)
            if not patient:
                return not_found("Patient not found")
            # Patient dashboard needs history and latest prediction
            return ok(patient.to_dict(
                include_admin=True,
                include_history=True, 
                include_latest_prediction=True,
                include_notes=True
            ))
        
        return unauthorized("Unknown user role")
        
    except Exception as e:
        current_app.logger.error(f"Error in /me endpoint: {e}")
        return server_error()