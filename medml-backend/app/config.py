# HealthCare App/medml-backend/app/config.py
import os
from datetime import timedelta

# This is the 'app' directory
basedir = os.path.abspath(os.path.dirname(__file__))
# This is the project's root directory (medml-backend)
BASE_DIR = os.path.abspath(os.path.join(basedir, '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        print("Warning: SECRET_KEY is not set. Using a temporary dev key.")
        SECRET_KEY = 'dev-secret-key' # Allow in dev

    # Database configuration with robust path handling
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        # Try multiple possible database locations
        possible_paths = [
            os.path.join(basedir, 'medml.db'),  # In app directory
            os.path.join(os.path.dirname(basedir), 'medml.db'),  # In backend directory
            os.path.join(os.path.dirname(os.path.dirname(basedir)), 'medml.db'),  # In project root
        ]
        
        db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            # Create database in app directory if none exists
            db_path = os.path.join(basedir, 'medml.db')
        
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(db_path).replace('\\', '/')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Base directory for the application
    BASE_DIR = BASE_DIR
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        print("Warning: JWT_SECRET_KEY is not set. Using a temporary dev key.")
        JWT_SECRET_KEY = 'dev-jwt-secret-key' # Allow in dev
        
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MIN', 15)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)))
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Recommendation API will fail.")
        
    # --- ADDED: Risk Thresholds from SRD ---
    RISK_THRESHOLDS = {
        'low': 0.0,  # Example: 0.0 to 0.34
        'medium': 0.35, # Example: 0.35 to 0.69
        'high': 0.70  # Example: 0.70+
    }
    
    # --- State to Language Mapping (extensible) ---
    # Maps Indian states to their regional languages for localized recommendations
    STATE_LANGUAGE_MAP = {
        # South Indian States - Regional Languages
        "Karnataka": "Kannada",
        "Tamil Nadu": "Tamil",
        "Kerala": "Malayalam",
        "Andhra Pradesh": "Telugu",
        "Telangana": "Telugu",
        
        # North Indian States - Hindi
        "Uttar Pradesh": "Hindi",
        "Madhya Pradesh": "Hindi",
        "Bihar": "Hindi",
        "Rajasthan": "Hindi",
        "Haryana": "Hindi",
        "Jharkhand": "Hindi",
        "Uttarakhand": "Hindi",
        "Chhattisgarh": "Hindi",
        "Himachal Pradesh": "Hindi",
        "Delhi": "Hindi",
        "Punjab": "Hindi",
        
        # West Indian States
        "Maharashtra": "English",
        "Gujarat": "Hindi",  # Can be changed to Gujarati if needed
        "Goa": "Hindi",
        
        # East Indian States
        "West Bengal": "Hindi",  # Can be changed to Bengali if needed
        "Odisha": "Hindi",  # Can be changed to Odia if needed
        "Assam": "Hindi",  # Can be changed to Assamese if needed
        
        # Northeast States
        "Arunachal Pradesh": "Hindi",
        "Manipur": "Hindi",
        "Meghalaya": "Hindi",
        "Mizoram": "Hindi",
        "Nagaland": "Hindi",
        "Sikkim": "Hindi",
        "Tripura": "Hindi",
        
        # Union Territories
        "Jammu and Kashmir": "Hindi",
        "Ladakh": "Hindi",
        "Chandigarh": "Hindi",
        "Puducherry": "Tamil",
        
        # Default fallback
        "default": "Hindi"
    }


# --- Helper function for language lookup ---
def get_language_for_state(state_name: str) -> str:
    """
    Returns the appropriate language for a given Indian state.
    Falls back to Hindi if state is not found.
    """
    if not state_name:
        return Config.STATE_LANGUAGE_MAP.get("default", "Hindi")
    return Config.STATE_LANGUAGE_MAP.get(state_name, Config.STATE_LANGUAGE_MAP.get("default", "Hindi"))

class DevelopmentConfig(Config):
    DEBUG = True
    # Database URI is inherited from Config class
    # Disable rate limiting in development
    RATELIMIT_ENABLED = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret'
    JWT_SECRET_KEY = 'test-jwt-secret'
    GEMINI_API_KEY = 'test-gemini-key' # Use a dummy key for testing

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # In production, SECRET_KEY and JWT_SECRET_KEY *must* be set
    def __init__(self):
        super().__init__()
        if not os.environ.get('SECRET_KEY'):
             raise ValueError("No SECRET_KEY set for Flask application in production")
        if not os.environ.get('JWT_SECRET_KEY'):
            raise ValueError("No JWT_SECRET_KEY set for Flask application in production")
        
        # --- ADDED: Enforce Gemini Key in Prod ---
        if not os.environ.get('GEMINI_API_KEY'):
            raise ValueError("No GEMINI_API_KEY set for Flask application in production")

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}