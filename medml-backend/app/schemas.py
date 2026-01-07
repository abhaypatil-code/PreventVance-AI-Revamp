# HealthCare App/medml-backend/app/schemas.py
from pydantic import BaseModel, EmailStr, constr, conint, confloat, validator
from typing import List, Optional
import re  # <-- Import the 're' module

# Regex for password
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$"
PASSWORD_ERROR_MSG = "Password must be at least 8 characters long and contain one uppercase letter, one lowercase letter, one number, and one special character."

# --- Auth Schemas ---

class UserRegisterSchema(BaseModel):
    """ Validates admin registration data """
    name: constr(min_length=2, max_length=150)
    email: EmailStr
    username: Optional[constr(min_length=3, max_length=80)] = None
    # --- FIX: Removed complex pattern from constr, only check length ---
    password: constr(min_length=8)
    designation: Optional[constr(max_length=100)] = None
    contact_number: Optional[constr(max_length=20)] = None
    facility_name: Optional[constr(max_length=150)] = None # Added from SRD
    role: str = 'admin'

    # --- FIX: Added custom validator for password complexity ---
    @validator('password')
    def password_complexity(cls, v):
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(PASSWORD_ERROR_MSG)
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Dr. Jane Doe",
                    "email": "jane.doe@med.com",
                    "username": "janedoe",
                    "password": "Password123!",
                    "designation": "Rural Health Worker",
                    "contact_number": "555-1234",
                    "facility_name": "Community Health Center"
                }
            ]
        }


class UserLoginSchema(BaseModel):
    """ Validates admin login """
    email: EmailStr
    password: str

class PatientLoginSchema(BaseModel):
    """ Validates patient login (password-free for simplified access) """
    abha_id: constr(pattern=r'^\d{14}$') # Strict 14-digit ABHA ID
    password: Optional[str] = None  # Password optional for simplified patient login

# --- Patient Schema ---

class PatientCreateSchema(BaseModel):
    """ Validates data for creating a new patient """
    name: constr(min_length=2, max_length=150) # Renamed from full_name
    age: conint(gt=0, le=120)
    gender: constr(min_length=1, max_length=20)
    height: confloat(gt=0) # Renamed from height_cm
    weight: confloat(gt=0) # Renamed from weight_kg
    abha_id: constr(pattern=r'^\d{14}$') # Strict 14-digit validation
    state_name: Optional[constr(max_length=100)] = None
    # --- FIX: Removed complex pattern from constr, only check length ---
    password: constr(min_length=8) # Admin sets initial patient password

    # --- FIX: Added custom validator for password complexity ---
    @validator('password')
    def password_complexity(cls, v):
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(PASSWORD_ERROR_MSG)
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "John Patient",
                    "age": 45,
                    "gender": "Male",
                    "height": 175,
                    "weight": 80,
                    "abha_id": "12345678901234",
                    "state_name": "Karnataka",
                    "password": "Password123!"
                }
            ]
        }

class PatientUpdateSchema(BaseModel):
    """ Validates data for updating a patient """
    name: constr(min_length=2, max_length=150)
    age: conint(gt=0, le=120)
    gender: constr(min_length=1, max_length=20)
    height: confloat(gt=0)
    weight: confloat(gt=0)
    abha_id: constr(pattern=r'^\d{14}$') # Allow updating ABHA ID
    state_name: Optional[constr(max_length=100)] = None

# --- Assessment Schemas (UPDATED as per SRD) ---

class DiabetesAssessmentSchema(BaseModel):
    pregnancy: bool
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    diabetes_history: bool

class LiverAssessmentSchema(BaseModel):
    total_bilirubin: float
    direct_bilirubin: float
    alkaline_phosphatase: float # Renamed
    sgpt_alamine_aminotransferase: float # Renamed
    sgot_aspartate_aminotransferase: float # Renamed
    total_protein: float # Renamed
    albumin: float
    # globulin removed

class HeartAssessmentSchema(BaseModel):
    diabetes: bool
    hypertension: bool
    obesity: bool
    smoking: bool
    alcohol_consumption: bool
    physical_activity: bool
    diet_score: Optional[conint(ge=1, le=10)] = None
    cholesterol_level: float
    triglyceride_level: Optional[float] = None
    ldl_level: Optional[float] = None
    hdl_level: Optional[float] = None
    systolic_bp: int
    diastolic_bp: int
    air_pollution_exposure: Optional[float] = None
    family_history: bool
    stress_level: Optional[conint(ge=1, le=10)] = None
    heart_attack_history: bool

class MentalHealthAssessmentSchema(BaseModel):
    phq_score: conint(ge=0, le=27)
    gad_score: conint(ge=0, le=21)
    depressiveness: bool
    suicidal: bool
    anxiousness: bool
    sleepiness: bool