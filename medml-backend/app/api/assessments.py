# HealthCare App/medml-backend/app/api/assessments.py
from flask import request, jsonify, current_app
from . import api_bp
from app.models import Patient
from app.extensions import db
from app.models import DiabetesAssessment, LiverAssessment, HeartAssessment, MentalHealthAssessment
from app.schemas import (
    DiabetesAssessmentSchema, LiverAssessmentSchema, 
    HeartAssessmentSchema, MentalHealthAssessmentSchema
)
from app.api.decorators import admin_required, get_current_admin_id
from pydantic import ValidationError
from flask_jwt_extended import jwt_required
from .responses import created, unprocessable_entity, server_error, ok

def _create_assessment(patient_id, AssessmentModel, SchemaModel):
    """
    Internal helper function to CREATE a new assessment for a patient.
    This supports the 1:N history requirement from the SRD.
    """
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        # Validate incoming JSON data
        data = SchemaModel(**request.json)
    except ValidationError as e:
        return unprocessable_entity(messages=e.errors())

    # --- UPDATED: Always create a new assessment ---
    assessment = AssessmentModel(patient_id=patient_id, **data.model_dump())
    
    # Audit: set assessor to current admin
    updater_id = get_current_admin_id()
    if hasattr(assessment, 'assessed_by_admin_id'):
        assessment.assessed_by_admin_id = updater_id
        
    db.session.add(assessment)
    message = f"{AssessmentModel.__name__} created successfully"

    try:
        db.session.commit()
        current_app.logger.info(f"{message} for patient {patient_id} by admin {get_current_admin_id()}")
        
        # Prediction is now handled by a separate call
        
        # Return the newly created assessment
        return created({
            "message": message,
            "assessment": assessment.to_dict(),
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving {AssessmentModel.__name__} for patient {patient_id}: {e}")
        return server_error()

# --- Public API Endpoints ---

@api_bp.route('/patients/<int:patient_id>/assessments/diabetes', methods=['POST'])
@jwt_required()
@admin_required
def submit_diabetes_assessment(patient_id):
    """
    [Admin Only] Creates a new diabetes assessment for a patient.
    """
    return _create_assessment(patient_id, DiabetesAssessment, DiabetesAssessmentSchema)

@api_bp.route('/patients/<int:patient_id>/assessments/liver', methods=['POST'])
@jwt_required()
@admin_required
def submit_liver_assessment(patient_id):
    """
    [Admin Only] Creates a new liver assessment for a patient.
    """
    return _create_assessment(patient_id, LiverAssessment, LiverAssessmentSchema)

@api_bp.route('/patients/<int:patient_id>/assessments/heart', methods=['POST'])
@jwt_required()
@admin_required
def submit_heart_assessment(patient_id):
    """
    [Admin Only] Creates a new heart assessment for a patient.
    """
    return _create_assessment(patient_id, HeartAssessment, HeartAssessmentSchema)

@api_bp.route('/patients/<int:patient_id>/assessments/mental_health', methods=['POST'])
@jwt_required()
@admin_required
def submit_mental_health_assessment(patient_id):
    """
    [Admin Only] Creates a new mental health assessment for a patient.
    """
    return _create_assessment(patient_id, MentalHealthAssessment, MentalHealthAssessmentSchema)

@api_bp.route('/patients/<int:patient_id>/assessments', methods=['GET'])
@jwt_required()
@admin_required
def get_all_assessments(patient_id):
    """
    [Admin Only] Gets all historical assessments for a single patient.
    """
    patient = Patient.query.get_or_404(patient_id)
    
    assessments_data = {
        "diabetes": [a.to_dict() for a in patient.diabetes_assessments],
        "liver": [a.to_dict() for a in patient.liver_assessments],
        "heart": [a.to_dict() for a in patient.heart_assessments],
        "mental_health": [a.to_dict() for a in patient.mental_health_assessments],
    }
    
    return ok({"patient_id": patient_id, "assessments": assessments_data})