# HealthCare App/medml-backend/app/api/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from . import (
    auth, 
    patients, 
    assessments, 
    predict, 
    recommendations, 
    dashboard, 
    consultations,
    reports,
    # errors # <-- This module can be added for global API error handling
)