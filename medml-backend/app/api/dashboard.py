# HealthCare App/medml-backend/app/api/dashboard.py
from flask import jsonify, current_app
from . import api_bp
from app.models import Patient, RiskPrediction
from app.extensions import db
from app.extensions import limiter
from app.api.decorators import admin_required
from flask_jwt_extended import jwt_required
from sqlalchemy import func, cast, Date
from datetime import date
from .responses import ok, server_error

@api_bp.route('/dashboard/stats', methods=['GET']) # Renamed route
@jwt_required()
@admin_required
@limiter.limit("100 per minute")  # More permissive limit for dashboard stats
def get_dashboard_stats(): # Renamed function
    """
    [Admin Only] Provides analytics for the admin dashboard.
    Returns counts as per frontend api_client.
    """
    try:
        # 1. Today's Registrations - Fixed timezone handling
        today = date.today()
        todays_registrations_count = db.session.query(func.count(Patient.id)).filter(
            func.date(Patient.created_at) == today
        ).scalar()

        # 2. Count by disease risk (Medium OR High)
        diabetes_risk_count = db.session.query(func.count(RiskPrediction.id)).filter(
            RiskPrediction.diabetes_risk_level.in_(['Medium', 'High'])
        ).scalar()
        
        liver_risk_count = db.session.query(func.count(RiskPrediction.id)).filter(
            RiskPrediction.liver_risk_level.in_(['Medium', 'High'])
        ).scalar()
        
        heart_risk_count = db.session.query(func.count(RiskPrediction.id)).filter(
            RiskPrediction.heart_risk_level.in_(['Medium', 'High'])
        ).scalar()
        
        mental_health_risk_count = db.session.query(func.count(RiskPrediction.id)).filter(
            RiskPrediction.mental_health_risk_level.in_(['Medium', 'High'])
        ).scalar()
        
        # Total registered patients
        total_patients_count = db.session.query(func.count(Patient.id)).scalar()
        
        # Additional stats for better analytics
        # This week's registrations (last 7 days)
        from datetime import timedelta
        week_ago = today - timedelta(days=7)
        this_week_registrations = db.session.query(func.count(Patient.id)).filter(
            func.date(Patient.created_at) >= week_ago
        ).scalar()
        
        # This month's registrations
        month_start = today.replace(day=1)
        this_month_registrations = db.session.query(func.count(Patient.id)).filter(
            func.date(Patient.created_at) >= month_start
        ).scalar()
        
        # Total assessments count
        total_assessments = db.session.query(func.count(RiskPrediction.id)).scalar()

        # --- UPDATED: Enhanced response with more analytics ---
        stats_data = {
            "today_registrations": todays_registrations_count,
            "this_week_registrations": this_week_registrations,
            "this_month_registrations": this_month_registrations,
            "total_patients": total_patients_count,
            "total_assessments": total_assessments,
            "diabetes_risk_count": diabetes_risk_count,
            "liver_risk_count": liver_risk_count,
            "heart_risk_count": heart_risk_count,
            "mental_health_risk_count": mental_health_risk_count
        }
        
        return ok(stats_data) # Return flat JSON

    except Exception as e:
        current_app.logger.error(f"Error fetching dashboard stats: {e}")
        return server_error()