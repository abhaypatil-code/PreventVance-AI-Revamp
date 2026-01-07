# HealthCare App/medml-backend/app/api/predict.py
from flask import jsonify, current_app
from . import api_bp
from app.models import Patient, RiskPrediction
from app.extensions import db
from app.services import run_prediction
from app.api.decorators import admin_required, get_current_admin_id
from flask_jwt_extended import jwt_required
from .responses import ok, forbidden, not_found, bad_request

def _run_and_save_prediction(patient_id):
    """
    Internal helper to run all predictions for a patient (based on latest
    assessments) and save a new prediction record.
    Allows partial predictions if some assessments are missing.
    """
    patient = Patient.query.get_or_404(patient_id)
    if not patient:
        raise Exception("Patient not found")

    # --- UPDATED: Get features independently ---
    diabetes_data = None
    liver_data = None
    heart_data = None
    mental_health_data = None
    
    has_any_data = False

    try:
        diabetes_data = patient.get_latest_diabetes_features()
        has_any_data = True
    except ValueError:
        pass # Skip diabetes
        
    try:
        liver_data = patient.get_latest_liver_features()
        has_any_data = True
    except ValueError:
        pass # Skip liver

    try:
        heart_data = patient.get_latest_heart_features()
        has_any_data = True
    except ValueError:
        pass # Skip heart

    try:
        mental_health_data = patient.get_latest_mental_health_features()
        has_any_data = True
    except ValueError:
        pass # Skip mental health
        
    if not has_any_data:
        raise Exception("Cannot run prediction: No assessments found for this patient. Please complete at least one.")

    current_app.logger.info(f"Running partial predictions for patient {patient_id}...")

    # --- 1. Run Predictions (if data exists) ---
    diabetes_score = None
    liver_score = None
    heart_score = None
    mental_health_score = None

    if diabetes_data:
        try:
            diabetes_score = run_prediction('diabetes', diabetes_data)
        except Exception as e:
            current_app.logger.error(f"Diabetes prediction failed: {e}")

    if liver_data:
        try:
            liver_score = run_prediction('liver', liver_data)
        except Exception as e:
            current_app.logger.error(f"Liver prediction failed: {e}")

    if heart_data:
        try:
            heart_score = run_prediction('heart', heart_data)
        except Exception as e:
            current_app.logger.warning(f"Heart prediction failed: {e}")
            
    if mental_health_data:
        try:
            mental_health_score = run_prediction('mental_health', mental_health_data)
        except Exception as e:
            current_app.logger.warning(f"Mental health prediction failed: {e}")

    # --- 2. Create New Prediction Record ---
    prediction = RiskPrediction(patient_id=patient_id)
    db.session.add(prediction)
    
    # --- 3. Save Available Scores ---
    if diabetes_score is not None:
        prediction.update_risk('diabetes', diabetes_score, '1.0')
        
    if liver_score is not None:
        prediction.update_risk('liver', liver_score, '1.0')
        
    if heart_score is not None:
        prediction.update_risk('heart', heart_score, '1.0')
        
    if mental_health_score is not None:
        prediction.update_risk('mental_health', mental_health_score, '1.0')

    try:
        db.session.commit()
        current_app.logger.info(f"Successfully saved new prediction {prediction.id} for patient {patient_id}")
        return prediction
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving predictions for patient {patient_id}: {e}")
        raise Exception(f"Database error saving predictions: {e}")


@api_bp.route('/patients/<int:patient_id>/predict', methods=['POST'])
@jwt_required()
@admin_required
def trigger_all_predictions(patient_id):
    """
    [Admin Only] Triggers risk assessment for available data.
    """
    try:
        prediction = _run_and_save_prediction(patient_id)
        return ok({
            "message": "Risk prediction completed successfully.",
            "predictions": prediction.to_dict(),
        })
    except Exception as e:
        current_app.logger.error(f"Prediction trigger failed for patient {patient_id}: {e}")
        return bad_request(str(e))

# --- ADDED: Endpoint for frontend client ---
@api_bp.route('/patients/<int:patient_id>/predictions/latest', methods=['GET'])
@jwt_required()
def get_latest_prediction(patient_id):
    """
    [Admin/Patient] Gets the single *most recent* risk prediction.
    This is required by the frontend's api_client.
    """
    # Check permissions
    from .decorators import parse_jwt_identity
    jwt_identity = parse_jwt_identity()
    user_role = jwt_identity.get('role')
    user_id = jwt_identity.get('id')
    
    if user_role == 'patient' and user_id != patient_id:
        return forbidden("Patients can only access their own data")

    patient = Patient.query.get_or_404(patient_id)
    
    # Get the first item from the ordered 1:N relationship
    latest_prediction = patient.risk_predictions.first()
    
    if not latest_prediction:
        return not_found("No predictions found for this patient")
    
    return ok(latest_prediction.to_dict())