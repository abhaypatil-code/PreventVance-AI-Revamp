# HealthCare App/medml-backend/app/models.py
from app.extensions import db, bcrypt
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from sqlalchemy import CheckConstraint
from flask import current_app

class User(db.Model):
    """
    Represents an Admin user (Healthcare Worker)
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    
    # Fields from SRD 'Admin' table
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) # Used for login
    username = db.Column(db.String(80), unique=True, nullable=True) # Added from SRD
    password_hash = db.Column(db.String(256), nullable=False)
    designation = db.Column(db.String(100), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    facility_name = db.Column(db.String(150), nullable=True) # Added from SRD
    
    role = db.Column(db.String(20), nullable=False, default='admin')
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    # 1:N relationship (Admin -> Patients)
    patients = db.relationship('Patient', back_populates='created_by_admin', passive_deletes=True)
    
    # 1:N relationship (Admin -> Consultations)
    booked_consultations = db.relationship('Consultation', back_populates='booked_by_admin')
    
    # 1:N relationship (Admin -> ConsultationNotes)
    consultation_notes = db.relationship('ConsultationNote', back_populates='admin')


    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "admin_id": self.id,
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "role": self.role,
            "designation": self.designation,
            "contact_number": self.contact_number,
            "facility_name": self.facility_name
        }

class Patient(db.Model):
    """
    Represents a Patient
    """
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    
    # SRD Fields
    name = db.Column(db.String(150), nullable=False) # Renamed from full_name
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    height = db.Column(db.Float, nullable=False) # Renamed from height_cm
    weight = db.Column(db.Float, nullable=False) # Renamed from weight_kg
    abha_id = db.Column(db.String(14), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # For patient login
    state_name = db.Column(db.String(100), nullable=True)
    
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_by_admin = db.relationship('User', back_populates='patients')
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # --- UPDATED: 1:N Relationships as per SRD ---
    diabetes_assessments = db.relationship('DiabetesAssessment', back_populates='patient', lazy='dynamic', cascade="all, delete-orphan", order_by="DiabetesAssessment.assessed_at.desc()")
    liver_assessments = db.relationship('LiverAssessment', back_populates='patient', lazy='dynamic', cascade="all, delete-orphan", order_by="LiverAssessment.assessed_at.desc()")
    heart_assessments = db.relationship('HeartAssessment', back_populates='patient', lazy='dynamic', cascade="all, delete-orphan", order_by="HeartAssessment.assessed_at.desc()")
    mental_health_assessments = db.relationship('MentalHealthAssessment', back_populates='patient', lazy='dynamic', cascade="all, delete-orphan", order_by="MentalHealthAssessment.assessed_at.desc()")
    risk_predictions = db.relationship('RiskPrediction', back_populates='patient', lazy='dynamic', cascade="all, delete-orphan", order_by="RiskPrediction.predicted_at.desc()")
    
    # 1:N relationship (Patient -> Consultations)
    consultations = db.relationship('Consultation', back_populates='patient', lazy='dynamic')
    
    # --- ADDED: 1:N relationship for Notes ---
    consultation_notes = db.relationship('ConsultationNote', back_populates='patient', lazy='dynamic', cascade="all, delete-orphan", order_by="ConsultationNote.created_at.desc()")


    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @hybrid_property
    def bmi(self):
        """ Auto-calculates BMI as required by SRD """
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100.0
            return round(self.weight / (height_m ** 2), 2)
        return None

    def to_dict(self, include_admin=True, include_history=False, include_latest_prediction=False, include_notes=False):
        data = {
            "patient_id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "abha_id": self.abha_id,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,
            "state_name": self.state_name,
            "created_by_admin_id": self.created_by_admin_id,
            "created_at": self.created_at.isoformat(),
        }
        if include_admin and self.created_by_admin:
            data['created_by_admin'] = self.created_by_admin.to_dict()
            
        if include_history:
            data['diabetes_assessments'] = [a.to_dict() for a in self.diabetes_assessments]
            data['liver_assessments'] = [a.to_dict() for a in self.liver_assessments]
            data['heart_assessments'] = [a.to_dict() for a in self.heart_assessments]
            data['mental_health_assessments'] = [a.to_dict() for a in self.mental_health_assessments]
            data['risk_predictions'] = [p.to_dict() for p in self.risk_predictions]
        
        if include_latest_prediction:
             data['latest_prediction'] = self.risk_predictions.first().to_dict() if self.risk_predictions.first() else None

        if include_notes:
            data['consultation_notes'] = [n.to_dict() for n in self.consultation_notes]
            
        return data

    # --- ADDED: Helper methods to get features for ML models ---
    def _get_common_features(self):
        return {
            "age": self.age,
            "gender": self.gender,
            "bmi": self.bmi
        }

    def get_latest_diabetes_features(self):
        latest_assessment = self.diabetes_assessments.first()
        if not latest_assessment:
            raise ValueError("No diabetes assessment found for patient")
        
        features = latest_assessment.to_dict(include_patient_data=True)
        features.update(self._get_common_features())
        return features

    def get_latest_liver_features(self):
        latest_assessment = self.liver_assessments.first()
        if not latest_assessment:
            raise ValueError("No liver assessment found for patient")
        
        features = latest_assessment.to_dict(include_patient_data=True)
        features.update(self._get_common_features())
        return features

    def get_latest_heart_features(self):
        latest_assessment = self.heart_assessments.first()
        if not latest_assessment:
            raise ValueError("No heart assessment found for patient")
        
        features = latest_assessment.to_dict(include_patient_data=True)
        features.update(self._get_common_features())
        return features

    def get_latest_mental_health_features(self):
        latest_assessment = self.mental_health_assessments.first()
        if not latest_assessment:
            raise ValueError("No mental health assessment found for patient")
        
        features = latest_assessment.to_dict(include_patient_data=True)
        features.update(self._get_common_features())
        return features


# --- Assessment Tables (as per SRD) ---

class BaseAssessment(db.Model):
    """ Abstract base for common assessment fields """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    # UPDATED: Removed unique=True for 1:N
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False) 
    assessed_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    # Renamed from updated_by_user_id
    assessed_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

class DiabetesAssessment(BaseAssessment):
    __tablename__ = 'diabetes_assessments'
    patient = db.relationship('Patient', back_populates='diabetes_assessments')
    
    # --- UPDATED FIELDS from SRD ---
    pregnancy = db.Column(db.Boolean, nullable=False, default=False)
    glucose = db.Column(db.Float, nullable=False)
    blood_pressure = db.Column(db.Float, nullable=False)
    skin_thickness = db.Column(db.Float, nullable=False)
    insulin = db.Column(db.Float, nullable=False)
    diabetes_history = db.Column(db.Boolean, nullable=False, default=False)
    
    def to_dict(self, include_patient_data=False):
        data = {
            "assessment_id": self.id,
            "patient_id": self.patient_id,
            "pregnancy": self.pregnancy,
            "glucose": self.glucose,
            "blood_pressure": self.blood_pressure,
            "skin_thickness": self.skin_thickness,
            "insulin": self.insulin,
            "diabetes_history": self.diabetes_history,
            "assessed_at": self.assessed_at.isoformat()
        }
        if include_patient_data and self.patient:
             data.update(self.patient._get_common_features())
        return data


class LiverAssessment(BaseAssessment):
    __tablename__ = 'liver_assessments'
    patient = db.relationship('Patient', back_populates='liver_assessments')
    
    # --- UPDATED FIELDS from SRD ---
    total_bilirubin = db.Column(db.Float, nullable=False)
    direct_bilirubin = db.Column(db.Float, nullable=False)
    alkaline_phosphatase = db.Column(db.Float, nullable=False) # Renamed
    sgpt_alamine_aminotransferase = db.Column(db.Float, nullable=False) # Renamed
    sgot_aspartate_aminotransferase = db.Column(db.Float, nullable=False) # Renamed
    total_protein = db.Column(db.Float, nullable=False) # Renamed
    albumin = db.Column(db.Float, nullable=False)
    # Removed globulin
    
    @hybrid_property
    def ag_ratio(self):
        """ Auto-calculates A/G Ratio as required from SRD """
        if self.albumin and self.total_protein and self.total_protein > self.albumin:
            globulin = self.total_protein - self.albumin
            if globulin > 0:
                return round(self.albumin / globulin, 2)
        return None

    def to_dict(self, include_patient_data=False):
        data = {
            "assessment_id": self.id,
            "patient_id": self.patient_id,
            "total_bilirubin": self.total_bilirubin,
            "direct_bilirubin": self.direct_bilirubin,
            "alkaline_phosphatase": self.alkaline_phosphatase,
            "sgpt_alamine_aminotransferase": self.sgpt_alamine_aminotransferase,
            "sgot_aspartate_aminotransferase": self.sgot_aspartate_aminotransferase,
            "total_protein": self.total_protein,
            "albumin": self.albumin,
            "ag_ratio": self.ag_ratio, # Add the computed ratio
            "assessed_at": self.assessed_at.isoformat()
        }
        if include_patient_data and self.patient:
             data.update(self.patient._get_common_features())
        return data


class HeartAssessment(BaseAssessment):
    __tablename__ = 'heart_assessments'
    patient = db.relationship('Patient', back_populates='heart_assessments')
    
    # --- COMPLETELY REPLACED FIELDS from SRD ---
    diabetes = db.Column(db.Boolean, nullable=False, default=False)
    hypertension = db.Column(db.Boolean, nullable=False, default=False)
    obesity = db.Column(db.Boolean, nullable=False, default=False)
    smoking = db.Column(db.Boolean, nullable=False, default=False)
    alcohol_consumption = db.Column(db.Boolean, nullable=False, default=False)
    physical_activity = db.Column(db.Boolean, nullable=False, default=False)
    diet_score = db.Column(db.Integer, nullable=True) # 1-10
    cholesterol_level = db.Column(db.Float, nullable=False)
    triglyceride_level = db.Column(db.Float, nullable=True)
    ldl_level = db.Column(db.Float, nullable=True)
    hdl_level = db.Column(db.Float, nullable=True)
    systolic_bp = db.Column(db.Integer, nullable=False)
    diastolic_bp = db.Column(db.Integer, nullable=False)
    air_pollution_exposure = db.Column(db.Float, nullable=True)
    family_history = db.Column(db.Boolean, nullable=False, default=False)
    stress_level = db.Column(db.Integer, nullable=True) # 1-10
    heart_attack_history = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self, include_patient_data=False):
        data = {
            "assessment_id": self.id,
            "patient_id": self.patient_id,
            "diabetes": self.diabetes,
            "hypertension": self.hypertension,
            "obesity": self.obesity,
            "smoking": self.smoking,
            "alcohol_consumption": self.alcohol_consumption,
            "physical_activity": self.physical_activity,
            "diet_score": self.diet_score,
            "cholesterol_level": self.cholesterol_level,
            "triglyceride_level": self.triglyceride_level,
            "ldl_level": self.ldl_level,
            "hdl_level": self.hdl_level,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "air_pollution_exposure": self.air_pollution_exposure,
            "family_history": self.family_history,
            "stress_level": self.stress_level,
            "heart_attack_history": self.heart_attack_history,
            "assessed_at": self.assessed_at.isoformat()
        }
        if include_patient_data and self.patient:
             data.update(self.patient._get_common_features())
        return data

class MentalHealthAssessment(BaseAssessment):
    __tablename__ = 'mental_health_assessments'
    patient = db.relationship('Patient', back_populates='mental_health_assessments')
    
    # --- UPDATED FIELDS from SRD ---
    phq_score = db.Column(db.Integer, nullable=False)
    gad_score = db.Column(db.Integer, nullable=False)
    depressiveness = db.Column(db.Boolean, nullable=False, default=False)
    suicidal = db.Column(db.Boolean, nullable=False, default=False)
    anxiousness = db.Column(db.Boolean, nullable=False, default=False)
    sleepiness = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self, include_patient_data=False):
        data = {
            "assessment_id": self.id,
            "patient_id": self.patient_id,
            "phq_score": self.phq_score,
            "gad_score": self.gad_score,
            "depressiveness": self.depressiveness,
            "suicidal": self.suicidal,
            "anxiousness": self.anxiousness,
            "sleepiness": self.sleepiness,
            "assessed_at": self.assessed_at.isoformat()
        }
        if include_patient_data and self.patient:
             data.update(self.patient._get_common_features())
        return data


# --- Prediction and Recommendation Tables ---

class RiskPrediction(db.Model):
    __tablename__ = 'risk_predictions'
    id = db.Column(db.Integer, primary_key=True)
    # UPDATED: Removed unique=True for 1:N
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False) 
    patient = db.relationship('Patient', back_populates='risk_predictions')
    
    diabetes_risk_score = db.Column(db.Float, nullable=True) # Renamed
    diabetes_risk_level = db.Column(db.String(20), nullable=True) # Renamed
    liver_risk_score = db.Column(db.Float, nullable=True) # Renamed
    liver_risk_level = db.Column(db.String(20), nullable=True) # Renamed
    heart_risk_score = db.Column(db.Float, nullable=True) # Renamed
    heart_risk_level = db.Column(db.String(20), nullable=True) # Renamed
    mental_health_risk_score = db.Column(db.Float, nullable=True) # Renamed
    mental_health_risk_level = db.Column(db.String(20), nullable=True) # Renamed
    
    model_version = db.Column(db.String(50), nullable=True, default='1.0')
    predicted_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    def _get_level(self, score):
        """Categorizes score based on config thresholds."""
        thresholds = current_app.config.get('RISK_THRESHOLDS', {'medium': 0.35, 'high': 0.7})
        if score >= thresholds['high']:
            return 'High'
        if score >= thresholds['medium']:
            return 'Medium'
        return 'Low'

    def update_risk(self, model_key: str, score: float, model_version: str):
        """Helper to update a specific risk and its level."""
        level = self._get_level(score)
        setattr(self, f"{model_key}_risk_score", score)
        setattr(self, f"{model_key}_risk_level", level)
        # Potentially update model version per-disease, or use a general one
        self.model_version = model_version

    def to_dict(self):
        return {
            "prediction_id": self.id,
            "patient_id": self.patient_id,
            "diabetes_risk_score": self.diabetes_risk_score,
            "diabetes_risk_level": self.diabetes_risk_level,
            "liver_risk_score": self.liver_risk_score,
            "liver_risk_level": self.liver_risk_level,
            "heart_risk_score": self.heart_risk_score,
            "heart_risk_level": self.heart_risk_level,
            "mental_health_risk_score": self.mental_health_risk_score,
            "mental_health_risk_level": self.mental_health_risk_level,
            "model_version": self.model_version,
            "predicted_at": self.predicted_at.isoformat()
        }

class LifestyleRecommendation(db.Model):
    """
    Personalized health guidance based on risk levels.
    Stores recommendations persistently for consistent display across UI and PDF.
    """
    __tablename__ = 'lifestyle_recommendations'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey('risk_predictions.id', ondelete='CASCADE'), nullable=True)
    disease_type = db.Column(db.String(50), nullable=False) # Diabetes/Liver/Heart/MentalHealth/General
    risk_level = db.Column(db.String(20), nullable=False) # Low/Medium/High
    category = db.Column(db.String(50), nullable=False) # Diet/Exercise/Sleep/Lifestyle
    recommendation_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=True, default='Hindi') # Language of the recommendation
    priority = db.Column(db.Integer, nullable=True) # for ordering display
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    patient = db.relationship('Patient', backref='lifestyle_recommendations')
    prediction = db.relationship('RiskPrediction', backref='recommendations')
    
    def to_dict(self):
        return {
            "recommendation_id": self.id,
            "patient_id": self.patient_id,
            "prediction_id": self.prediction_id,
            "disease_type": self.disease_type,
            "risk_level": self.risk_level,
            "category": self.category,
            "recommendation_text": self.recommendation_text,
            "language": self.language,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }

class Consultation(db.Model):
    """
    Represents a (dummy) consultation booking.
    """
    __tablename__ = 'consultations'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    disease = db.Column(db.String(50), nullable=True) # ADDED
    consultation_type = db.Column(db.String(50), nullable=False) # 'teleconsultation', 'in_person'
    consultation_datetime = db.Column(db.DateTime, nullable=False) # Dummy datetime
    notes = db.Column(db.Text, nullable=True) # Note from admin at booking time
    status = db.Column(db.String(20), nullable=False, default='Booked') # e.g., 'Booked', 'Completed'
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    patient = db.relationship('Patient', back_populates='consultations')
    booked_by_admin = db.relationship('User', back_populates='booked_consultations')

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "admin_id": self.admin_id,
            "disease": self.disease,
            "consultation_type": self.consultation_type,
            "consultation_datetime": self.consultation_datetime.isoformat(),
            "notes": self.notes,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

# --- ADDED: ConsultationNote Table ---
class ConsultationNote(db.Model):
    """
    Represents notes added by an Admin for a Patient ("Notes for Doctor").
    """
    __tablename__ = 'consultation_notes'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    notes = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    patient = db.relationship('Patient', back_populates='consultation_notes')
    admin = db.relationship('User', back_populates='consultation_notes')
    
    def to_dict(self):
        return {
            "note_id": self.id,
            "patient_id": self.patient_id,
            "admin_id": self.admin_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }

# --- Token Blocklist for JWT revocation ---
class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), index=True, nullable=False, unique=True)
    token_type = db.Column(db.String(10), nullable=False) # 'access' or 'refresh'
    user_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)