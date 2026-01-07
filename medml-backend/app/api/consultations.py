# HealthCare App/medml-backend/app/api/consultations.py
from flask import request, jsonify, current_app
from . import api_bp
from app.models import Patient, Consultation, ConsultationNote, User
from app.extensions import db
from app.api.decorators import admin_required, get_current_admin_id
from pydantic import BaseModel, constr
from pydantic.error_wrappers import ValidationError
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from .responses import created, bad_request, not_found, server_error, ok

# --- UPDDATED: Schema removed, using direct JSON ---

@api_bp.route('/consultations', methods=['POST'])
@jwt_required()
@admin_required
def book_consultation():
    """
    [Admin Only] Books a dummy consultation for a patient.
    Matches frontend api_client call.
    """
    data = request.json
    admin_id = get_current_admin_id()

    patient_id = data.get('patient_id')
    disease = data.get('disease')
    consultation_type = data.get('consultation_type') # 'teleconsultation' or 'in_person'

    if not all([patient_id, disease, consultation_type]):
        return bad_request("Missing patient_id, disease, or consultation_type")

    patient = Patient.query.get(patient_id)
    if not patient:
        return not_found("Patient not found")

    # Create dummy data as per SRD
    dummy_datetime = datetime.now() + timedelta(days=7)
    dummy_notes = f"Booking for {disease} ({consultation_type})"

    new_consultation = Consultation(
        patient_id=patient_id,
        admin_id=admin_id,
        disease=disease,
        consultation_type=consultation_type,
        consultation_datetime=dummy_datetime,
        notes=dummy_notes,
        status='Booked'
    )
    
    try:
        db.session.add(new_consultation)
        db.session.commit()
        current_app.logger.info(f"Admin {admin_id} booked {consultation_type} for patient {patient_id}")
        
        return created({
            "message": "Consultation booked successfully",
            "consultation": new_consultation.to_dict(),
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error booking consultation: {e}")
        return server_error("Could not book consultation.")

@api_bp.route('/consultations/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_patient_consultations(patient_id):
    """
    [Admin Only] Gets all consultations for a specific patient.
    """
    patient = Patient.query.get_or_404(patient_id)
    consultations = [c.to_dict() for c in patient.consultations]
    return ok({"consultations": consultations})

# --- ADDED: Endpoint for saving doctor notes ---

class NoteSchema(BaseModel):
    patient_id: int
    notes: constr(min_length=1)

@api_bp.route('/consultations/notes', methods=['POST'])
@jwt_required()
@admin_required
def add_consultation_note():
    """
    [Admin Only] Adds a new note for a patient ("Notes for Doctor").
    """
    try:
        data = NoteSchema(**request.json)
    except ValidationError as e:
        from .responses import unprocessable_entity
        return unprocessable_entity(messages=e.errors())
    
    admin_id = get_current_admin_id()
    
    patient = Patient.query.get(data.patient_id)
    if not patient:
        return not_found("Patient not found")
        
    new_note = ConsultationNote(
        patient_id=data.patient_id,
        admin_id=admin_id,
        notes=data.notes
    )
    
    try:
        db.session.add(new_note)
        db.session.commit()
        current_app.logger.info(f"Admin {admin_id} added note for patient {data.patient_id}")
        
        return created({
            "message": "Note added successfully",
            "note": new_note.to_dict(),
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding note: {e}")
        return server_error("Could not add note.")