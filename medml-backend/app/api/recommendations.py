# HealthCare App/medml-backend/app/api/recommendations.py
from flask import jsonify, current_app, request
from . import api_bp
from app.models import db, Patient
from app.api.decorators import admin_required
from flask_jwt_extended import jwt_required
from app.services import get_gemini_recommendations, save_recommendations_to_db, get_stored_recommendations
from app.config import get_language_for_state
from .responses import ok, forbidden, server_error

@api_bp.route('/patients/<int:patient_id>/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations(patient_id):
    """
    [Admin/Patient] Fetches lifestyle recommendations based on *latest* risk.
    Patient can only access their own.
    
    Returns stored recommendations if available, otherwise generates new ones
    using Gemini API and stores them for future use.
    """
    try:
        # 1. Check permissions
        from .decorators import parse_jwt_identity
        jwt_identity = parse_jwt_identity()
        user_role = jwt_identity.get('role')
        user_id = jwt_identity.get('id')
        
        if user_role == 'patient' and user_id != patient_id:
            return forbidden("Patients can only access their own report")
        
        patient = Patient.query.get_or_404(patient_id)

        # --- Get latest prediction ---
        risk_prediction = patient.risk_predictions.first()
        
        if not risk_prediction:
            # No predictions yet, return empty
            return ok({"diet": [], "exercise": [], "sleep": [], "lifestyle": []})

        # --- Check for stored recommendations first ---
        stored_recs = get_stored_recommendations(patient_id, risk_prediction.id)
        
        if stored_recs:
            current_app.logger.info(f"Returning stored recommendations for patient {patient_id}")
            return ok(stored_recs)
        
        # --- No stored recommendations, generate new ones ---
        current_app.logger.info(f"Generating new recommendations for patient {patient_id}")
        
        risk_map = {
            'diabetes': risk_prediction.diabetes_risk_level,
            'liver': risk_prediction.liver_risk_level,
            'heart': risk_prediction.heart_risk_level,
            'mental_health': risk_prediction.mental_health_risk_level
        }
        
        # Generate recommendations with localization
        recommendations_data = get_gemini_recommendations(
            risk_map, 
            patient_state=patient.state_name, 
            patient_id=patient_id
        )
        
        # Save to database for persistence
        target_language = get_language_for_state(patient.state_name)
        save_recommendations_to_db(
            patient_id=patient_id,
            prediction_id=risk_prediction.id,
            recommendations=recommendations_data,
            language=target_language
        )
        
        # Return the grouped-by-category dictionary
        return ok(recommendations_data)

    except Exception as e:
        current_app.logger.error(f"Error fetching recommendations: {e}")
        return server_error(str(e))


@api_bp.route('/patients/<int:patient_id>/recommendations/regenerate', methods=['POST'])
@jwt_required()
def regenerate_recommendations(patient_id):
    """
    [Admin/Patient] Forces regeneration of recommendations.
    Useful when patient's state changes or new predictions are made.
    """
    try:
        # 1. Check permissions
        from .decorators import parse_jwt_identity
        jwt_identity = parse_jwt_identity()
        user_role = jwt_identity.get('role')
        user_id = jwt_identity.get('id')
        
        if user_role == 'patient' and user_id != patient_id:
            return forbidden("Patients can only access their own recommendations")
        
        patient = Patient.query.get_or_404(patient_id)
        risk_prediction = patient.risk_predictions.first()
        
        if not risk_prediction:
            return ok({"diet": [], "exercise": [], "sleep": [], "lifestyle": []})

        risk_map = {
            'diabetes': risk_prediction.diabetes_risk_level,
            'liver': risk_prediction.liver_risk_level,
            'heart': risk_prediction.heart_risk_level,
            'mental_health': risk_prediction.mental_health_risk_level
        }
        
        # Generate fresh recommendations
        recommendations_data = get_gemini_recommendations(
            risk_map, 
            patient_state=patient.state_name, 
            patient_id=patient_id
        )
        
        # Save to database (this will deactivate old ones)
        target_language = get_language_for_state(patient.state_name)
        save_recommendations_to_db(
            patient_id=patient_id,
            prediction_id=risk_prediction.id,
            recommendations=recommendations_data,
            language=target_language
        )
        
        return ok(recommendations_data)

    except Exception as e:
        current_app.logger.error(f"Error regenerating recommendations: {e}")
        return server_error(str(e))