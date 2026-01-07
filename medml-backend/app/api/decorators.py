# HealthCare App/medml-backend/app/api/decorators.py
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

def parse_jwt_identity():
    """
    Parse the JWT identity string back to a dictionary.
    This handles the conversion from string format back to dictionary.
    """
    identity = get_jwt_identity()
    if isinstance(identity, str) and ":" in identity:
        # Parse the string back to dictionary
        parts = identity.split(":", 2)
        if len(parts) >= 2:
            return {
                "id": int(parts[0]) if parts[0].isdigit() else parts[0],
                "role": parts[1],
                "name": parts[2] if len(parts) > 2 else ""
            }
    # Fallback for non-string or malformed identities
    return {"id": identity, "role": "unknown", "name": ""}

def admin_required(fn):
    """
    Decorator to ensure the user is an admin.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        jwt_identity = parse_jwt_identity()
        if jwt_identity.get('role') != 'admin':
            return jsonify(error="Forbidden", message="Admin access required"), 403
        return fn(*args, **kwargs)
    return wrapper

def get_current_admin_id():
    """
    Helper function to get the ID of the currently logged-in admin.
    Assumes this is called from within an @admin_required route.
    """
    try:
        jwt_identity = parse_jwt_identity()
        if jwt_identity.get('role') == 'admin':
            return jwt_identity.get('id')
    except Exception:
        pass # Will return None
    return None