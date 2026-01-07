# HealthCare App/medml-backend/app/api/patients.py
from flask import request, jsonify, current_app
from . import api_bp
from app.models import Patient, User, RiskPrediction
from app.extensions import limiter, db
from app.schemas import PatientCreateSchema, PatientUpdateSchema
from app.api.decorators import admin_required, get_current_admin_id, parse_jwt_identity
from pydantic import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
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

@api_bp.route('/patients', methods=['POST'])
@jwt_required()
@admin_required
def create_patient():
    """
    [Admin Only] Creates a new patient record.
    """
    try:
        current_app.logger.info(f"Received patient data: {request.json}")
        data = PatientCreateSchema(**request.json)
        current_app.logger.info(f"Validated patient data: {data}")
    except ValidationError as e:
        current_app.logger.error(f"Validation error: {e.errors()}")
        return unprocessable_entity(messages=e.errors())
    
    admin_id = get_current_admin_id()
    if not admin_id:
        return unauthorized("Admin ID not found")
    
    if Patient.query.filter_by(abha_id=data.abha_id).first():
        return conflict("Patient with this ABHA ID already exists")

    new_patient = Patient(
        name=data.name, # Updated from full_name
        age=data.age,
        gender=data.gender,
        height=data.height, # Updated from height_cm
        weight=data.weight, # Updated from weight_kg
        abha_id=data.abha_id,
        state_name=data.state_name,
        created_by_admin_id=admin_id # Updated from created_by_user_id
    )
    new_patient.set_password(data.password) 

    try:
        db.session.add(new_patient)
        db.session.commit()
        current_app.logger.info(f"Admin {admin_id} created patient {new_patient.id} with ABHA ID {new_patient.abha_id}")
        
        return created({
            "message": "Patient created successfully",
            "patient": new_patient.to_dict(),
            "patient_id": new_patient.id,
            "name": new_patient.name,
        })
    
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"IntegrityError creating patient: {e}")
        return conflict("Could not create patient. ABHA ID may be taken.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating patient: {e}")
        return server_error("An unexpected error occurred.")

@api_bp.route('/patients', methods=['GET'])
@jwt_required()
@admin_required
@limiter.limit("100 per minute")  # More permissive limit for patient listing
def get_patients():
    """
    [Admin Only] Gets a list of all patients, with filtering and sorting
    matching the frontend api_client.
    """
    try:
        query = Patient.query
        
        # Filter by disease category (e.g., 'diabetes')
        disease = request.args.get('disease')
        
        # Sort by 'recently_added', 'high_risk', 'medium_risk'
        sort = request.args.get('sort', 'recently_added')
        
        if disease:
            query = query.join(RiskPrediction, Patient.id == RiskPrediction.patient_id)
            if disease == 'diabetes':
                disease_filter = RiskPrediction.diabetes_risk_level
            elif disease == 'liver':
                disease_filter = RiskPrediction.liver_risk_level
            elif disease == 'heart':
                disease_filter = RiskPrediction.heart_risk_level
            elif disease == 'mental_health':
                disease_filter = RiskPrediction.mental_health_risk_level
            else:
                disease_filter = None

            if disease_filter is not None:
                if sort == 'high_risk':
                    query = query.filter(disease_filter == 'High').order_by(Patient.created_at.desc())
                elif sort == 'medium_risk':
                    query = query.filter(disease_filter == 'Medium').order_by(Patient.created_at.desc())
                elif sort == 'low_risk':
                    query = query.filter(disease_filter == 'Low').order_by(Patient.created_at.desc())
                else: # 'recently_added' or default
                    # Show all for that disease, sorted by recency
                    query = query.filter(or_(disease_filter == 'High', disease_filter == 'Medium', disease_filter == 'Low')).order_by(Patient.created_at.desc())
            
        else: # 'All Users' tab
            if sort == 'high_risk':
                query = query.join(RiskPrediction).filter(or_(
                    RiskPrediction.diabetes_risk_level == 'High',
                    RiskPrediction.liver_risk_level == 'High',
                    RiskPrediction.heart_risk_level == 'High',
                    RiskPrediction.mental_health_risk_level == 'High'
                )).order_by(Patient.created_at.desc())
            elif sort == 'medium_risk':
                 query = query.join(RiskPrediction).filter(or_(
                    RiskPrediction.diabetes_risk_level == 'Medium',
                    RiskPrediction.liver_risk_level == 'Medium',
                    RiskPrediction.heart_risk_level == 'Medium',
                    RiskPrediction.mental_health_risk_level == 'Medium'
                )).order_by(Patient.created_at.desc())
            elif sort == 'low_risk':
                query = query.join(RiskPrediction).filter(or_(
                    RiskPrediction.diabetes_risk_level == 'Low',
                    RiskPrediction.liver_risk_level == 'Low',
                    RiskPrediction.heart_risk_level == 'Low',
                    RiskPrediction.mental_health_risk_level == 'Low'
                )).order_by(Patient.created_at.desc())
            else: # 'recently_added'
                query = query.order_by(Patient.created_at.desc())

        patients = query.all()
        
        # Return list, including latest prediction data for the dashboard view
        patients_data = [p.to_dict(include_latest_prediction=True) for p in patients]
        
        return ok(patients_data)
    
    except Exception as e:
        current_app.logger.error(f"Error fetching patients: {e}")
        return server_error(str(e))


@api_bp.route('/patients/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    """
    [Admin/Patient] Gets detailed info for a single patient.
    Patient can only access their own.
    """
    # Check permissions
    jwt_identity = parse_jwt_identity()
    user_role = jwt_identity.get('role')
    user_id = jwt_identity.get('id')
    
    if user_role == 'patient' and user_id != patient_id:
        return forbidden("Patients can only access their own data")

    patient = Patient.query.get_or_404(patient_id)
    
    # Return full details including all history and notes for Admin view
    return ok(patient.to_dict(
        include_admin=True,
        include_history=True, 
        include_latest_prediction=True,
        include_notes=True
    ))


@api_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_patient(patient_id):
    """
    [Admin Only] Updates a patient's basic info.
    """
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        data = PatientUpdateSchema(**request.json)
    except ValidationError as e:
        return unprocessable_entity(messages=e.errors())

    # Check for ABHA ID conflict if it's being changed
    if data.abha_id != patient.abha_id:
        if Patient.query.filter_by(abha_id=data.abha_id).first():
            return conflict("Patient with this ABHA ID already exists")
    
    try:
        # Update mutable fields
        patient.name = data.name
        patient.age = data.age
        patient.gender = data.gender
        patient.state_name = data.state_name
        patient.height = data.height
        patient.weight = data.weight
        patient.abha_id = data.abha_id # Allow ABHA ID update

        db.session.commit()
        current_app.logger.info(f"Patient {patient_id} updated by admin {get_current_admin_id()}")
        
        return ok({"message": "Patient updated successfully", "patient": patient.to_dict()})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating patient {patient_id}: {e}")
        return server_error()