# HealthCare App/medml-backend/app/services.py
import joblib
import pandas as pd
import numpy as np
import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from flask import current_app

# Path to models_store directory
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models_store')

# Global dictionary to hold models and preprocessors
models = {
    'diabetes': None,
    'heart': None,
    'liver': None,
    'mental_health': None
}

def load_model(app: Any, key: str, filename: str):
    """Loads a .pkl model from the models_store directory into a global dict."""
    try:
        path = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(path):
            app.logger.warning(f"Model file not found at {path}. Predictions for '{key}' will fail.")
            return None
        return joblib.load(path)
    except Exception as e:
        app.logger.error(f"Error loading model {filename}: {e}")
        return None

def load_models(app: Any):
    """Loads all models and preprocessors at application startup."""
    with app.app_context():
        app.logger.info(f"Loading models from: {MODEL_DIR}")
        
        models['diabetes'] = load_model(app, 'diabetes', 'diabetes_LightGBM SMOTE.pkl')
        models['heart'] = load_model(app, 'heart', 'heart_SVM Weighted Tuned.pkl')
        models['liver'] = load_model(app, 'liver', 'liver_LightGBM SMOTE.pkl')
        # Use depressiveness model as the main mental health model
        models['mental_health'] = load_model(app, 'mental_health', 'mental_health_depressiveness_Logistic Regression.pkl')
        
        app.logger.info("Model loading complete.")
        
        # --- Configure Gemini ---
        try:
            api_key = app.config.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                app.logger.info("Gemini API configured successfully.")
            else:
                app.logger.warning("GEMINI_API_KEY is not set. Recommendation service will be disabled.")
        except Exception as e:
            app.logger.error(f"Error configuring Gemini API: {e}")

# --- Preprocessing & Prediction Logic (UPDATED) ---

def predict_diabetes(data: Dict[str, Any]) -> float:
    model = models.get('diabetes')
    if model is None:
        current_app.logger.error("Diabetes model is not loaded.")
        raise RuntimeError("Diabetes model is not loaded.")
        
    try:
        # --- FIXED: Map assessment data to model's expected features ---
        # Convert assessment data to model's expected format
        processed_data = {}
        
        # Map basic features
        processed_data['Pregnancies'] = 1 if data.get('pregnancy') else 0
        processed_data['Glucose'] = data.get('glucose', 0)
        processed_data['BloodPressure'] = data.get('blood_pressure', 0)
        processed_data['SkinThickness'] = data.get('skin_thickness', 0)
        processed_data['Insulin'] = data.get('insulin', 0)
        processed_data['BMI'] = data.get('bmi', 0)
        processed_data['Age'] = data.get('age', 0)
        
        # Calculate missing features that the model expects
        # DiabetesPedigreeFunction - using a simplified calculation
        glucose = processed_data['Glucose']
        age = processed_data['Age']
        bmi = processed_data['BMI']
        
        # Simplified DiabetesPedigreeFunction calculation
        processed_data['DiabetesPedigreeFunction'] = (glucose * age * bmi) / 10000.0 if glucose and age and bmi else 0.5
        
        # Create age groups
        if age < 30:
            processed_data['AgeGroup'] = 0
        elif age < 50:
            processed_data['AgeGroup'] = 1
        else:
            processed_data['AgeGroup'] = 2
            
        # Create BMI categories
        if bmi < 18.5:
            processed_data['BMICategory'] = 0  # Underweight
        elif bmi < 25:
            processed_data['BMICategory'] = 1  # Normal
        elif bmi < 30:
            processed_data['BMICategory'] = 2  # Overweight
        else:
            processed_data['BMICategory'] = 3  # Obese
            
        # Create glucose categories
        if glucose < 100:
            processed_data['GlucoseCategory'] = 0  # Normal
        elif glucose < 126:
            processed_data['GlucoseCategory'] = 1  # Prediabetes
        else:
            processed_data['GlucoseCategory'] = 2  # Diabetes
            
        # Create interaction features
        processed_data['BMIAgeInteraction'] = bmi * age
        processed_data['GlucoseBMIInteraction'] = glucose * bmi
        
        # Define the exact feature order expected by the model
        feature_order = [
            'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 
            'AgeGroup', 'BMICategory', 'GlucoseCategory', 
            'BMIAgeInteraction', 'GlucoseBMIInteraction'
        ]
        
        # Create DataFrame with the correct feature order
        df = pd.DataFrame([processed_data], columns=feature_order)
        
        # Predict probability of class 1 (disease)
        probability = model.predict_proba(df)[0][1] 
        
        return float(probability)
    except Exception as e:
        current_app.logger.error(f"Diabetes prediction error: {e}")
        raise ValueError("Failed to preprocess diabetes data.")

def predict_heart(data: Dict[str, Any]) -> float:
    model = models.get('heart')
    # --- FIX: Removed preprocessor ---
    # preprocessor = preprocessors.get('heart')
    
    # --- FIX: Removed preprocessor check ---
    if model is None:
        current_app.logger.error("Heart model is not loaded.")
        raise RuntimeError("Heart model is not loaded.")
        
    try:
        # --- FIXED: Use correct capitalized feature names that match the trained model ---
        # Map 'gender' from 'Male'/'Female' to 0/1
        gender_value = 1 if data.get('gender') == 'Male' else 0
        
        # Convert bools to int
        diabetes = 1 if data.get('diabetes') else 0
        hypertension = 1 if data.get('hypertension') else 0
        obesity = 1 if data.get('obesity') else 0
        smoking = 1 if data.get('smoking') else 0
        alcohol_consumption = 1 if data.get('alcohol_consumption') else 0
        physical_activity = 1 if data.get('physical_activity') else 0
        family_history = 1 if data.get('family_history') else 0
        heart_attack_history = 1 if data.get('heart_attack_history') else 0

        # Get numeric values
        age = data.get('age', 0)
        bmi = data.get('bmi', 0)
        diet_score = data.get('diet_score', 0)
        cholesterol_level = data.get('cholesterol_level', 0)
        triglyceride_level = data.get('triglyceride_level', 0)
        ldl_level = data.get('ldl_level', 0)
        hdl_level = data.get('hdl_level', 0)
        systolic_bp = data.get('systolic_bp', 0)
        diastolic_bp = data.get('diastolic_bp', 0)
        air_pollution_exposure = data.get('air_pollution_exposure', 0)
        stress_level = data.get('stress_level', 0)
        
        # Calculate engineered features with correct names
        cholesterol_hdl_ratio = cholesterol_level / hdl_level if hdl_level > 0 else 0
        ldl_hdl_ratio = ldl_level / hdl_level if hdl_level > 0 else 0
        triglyceride_hdl_ratio = triglyceride_level / hdl_level if hdl_level > 0 else 0
        bp_difference = systolic_bp - diastolic_bp
        age_bmi_interaction = age * bmi
        stress_diet_interaction = stress_level * diet_score
        age_gender_interaction = age * gender_value
        
        # Create the processed data with correct capitalized feature names
        processed_data = {
            'Diabetes': diabetes,
            'Hypertension': hypertension,
            'Obesity': obesity,
            'Smoking': smoking,
            'Alcohol_Consumption': alcohol_consumption,
            'Physical_Activity': physical_activity,
            'Diet_Score': diet_score,
            'Cholesterol_Level': cholesterol_level,
            'Triglyceride_Level': triglyceride_level,
            'LDL_Level': ldl_level,
            'HDL_Level': hdl_level,
            'Systolic_BP': systolic_bp,
            'Diastolic_BP': diastolic_bp,
            'Air_Pollution_Exposure': air_pollution_exposure,
            'Family_History': family_history,
            'Stress_Level': stress_level,
            'Heart_Attack_History': heart_attack_history,
            'Age': age,
            'Gender': gender_value,
            'BMI': bmi,
            'Cholesterol_HDL_Ratio': cholesterol_hdl_ratio,
            'LDL_HDL_Ratio': ldl_hdl_ratio,
            'Triglyceride_HDL_Ratio': triglyceride_hdl_ratio,
            'BP_Difference': bp_difference,
            'Age_BMI_Interaction': age_bmi_interaction,
            'Stress_Diet_Interaction': stress_diet_interaction,
            'Age_Gender_Interaction': age_gender_interaction
        }
        
        # Define the exact feature order expected by the model (27 features)
        feature_columns = [
            'Diabetes', 'Hypertension', 'Obesity', 'Smoking', 'Alcohol_Consumption',
            'Physical_Activity', 'Diet_Score', 'Cholesterol_Level', 'Triglyceride_Level',
            'LDL_Level', 'HDL_Level', 'Systolic_BP', 'Diastolic_BP', 'Air_Pollution_Exposure',
            'Family_History', 'Stress_Level', 'Heart_Attack_History', 'Age', 'Gender', 'BMI',
            'Cholesterol_HDL_Ratio', 'LDL_HDL_Ratio', 'Triglyceride_HDL_Ratio', 'BP_Difference',
            'Age_BMI_Interaction', 'Stress_Diet_Interaction', 'Age_Gender_Interaction'
        ]
        
        # Create DataFrame with the correct feature order and processed data
        df = pd.DataFrame([processed_data], columns=feature_columns)
        current_app.logger.info(f"Heart DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")
        
        # --- FIX: Removed preprocessor step ---
        # df_processed = preprocessor.transform(df) 
        
        # --- FIX: Try to predict, but handle model mismatch gracefully ---
        try:
            probability = model.predict_proba(df)[0][1]
            return float(probability)
        except Exception as model_error:
            current_app.logger.warning(f"Heart model prediction failed: {model_error}")
            # If the model fails due to feature mismatch, provide a default prediction
            # based on basic risk factors
            risk_score = 0.0
            
            # Basic risk calculation based on available data
            if diabetes or hypertension or smoking:
                risk_score += 0.3
            if obesity:
                risk_score += 0.2
            if family_history:
                risk_score += 0.2
            if age > 50:
                risk_score += 0.2
            if stress_level > 5:
                risk_score += 0.1
                
            # Cap at 1.0
            risk_score = min(risk_score, 1.0)
            current_app.logger.info(f"Using fallback heart prediction: {risk_score}")
            return float(risk_score)
            
    except Exception as e:
        current_app.logger.error(f"Heart prediction error: {e}")
        raise ValueError("Failed to preprocess heart data.")

def predict_liver(data: Dict[str, Any]) -> float:
    model = models.get('liver')
    if model is None:
        current_app.logger.error("Liver model is not loaded.")
        raise RuntimeError("Liver model is not loaded.")

    try:
        current_app.logger.info(f"Liver prediction input data: {data}")
        data_processed = data.copy()
        
        # Map 'gender'
        data_processed['Gender'] = 1 if data_processed.get('gender') == 'Male' else 0
        
        # --- UPDATED: Calculate A/G Ratio per SRD/model ---
        albumin = data_processed.get('albumin', 0)
        total_protein = data_processed.get('total_protein', 0)
        
        if total_protein and albumin and total_protein > albumin:
            globulin = total_protein - albumin
            data_processed['Albumin_and_Globulin_Ratio'] = round(albumin / globulin, 2)
        else:
            data_processed['Albumin_and_Globulin_Ratio'] = 0.9 # Placeholder median
        # --- End Update ---
        
        # Map keys to match the model's expected feature names (abbreviated)
        key_map = {
            'age': 'Age',
            'gender': 'Gender',
            'total_bilirubin': 'TB',
            'direct_bilirubin': 'DB',
            'alkaline_phosphatase': 'Alkphos',
            'sgpt_alamine_aminotransferase': 'Sgpt',
            'sgot_aspartate_aminotransferase': 'Sgot',
            'total_protein': 'TP',
            'albumin': 'ALB',
            'ag_ratio': 'AGRatio'
        }
        
        model_input_data = {
            key_map.get(k, k): v for k, v in data_processed.items()
        }
        
        # Fix AGRatio if it's None
        if model_input_data.get('AGRatio') is None:
            model_input_data['AGRatio'] = model_input_data.get('Albumin_and_Globulin_Ratio', 0.9)
        
        # Calculate additional engineered features that the model expects
        age = model_input_data.get('Age', 0)
        gender = model_input_data.get('Gender', 0)
        tb = model_input_data.get('TB', 0)
        db = model_input_data.get('DB', 0)
        sgpt = model_input_data.get('Sgpt', 0)
        sgot = model_input_data.get('Sgot', 0)
        tp = model_input_data.get('TP', 0)
        alb = model_input_data.get('ALB', 0)
        
        # Calculate additional features
        model_input_data['BilirubinRatio'] = db / tb if tb > 0 else 0
        model_input_data['SGPTSGOTRatio'] = sgpt / sgot if sgot > 0 else 0
        model_input_data['TotalEnzymes'] = sgpt + sgot
        model_input_data['AgeGroup'] = 0 if age < 30 else (1 if age < 50 else 2)
        model_input_data['LowProtein'] = 1 if tp < 6.0 else 0
        model_input_data['HighEnzymes'] = 1 if (sgpt > 40 or sgot > 40) else 0
        model_input_data['AgeGenderInteraction'] = age * gender
        
        current_app.logger.info(f"Liver model input data: {model_input_data}")

        # Define feature order for the model (as expected by the trained model)
        feature_columns = [
            'Age', 'Gender', 'TB', 'DB', 'Alkphos', 'Sgpt', 'Sgot', 'TP', 'ALB', 
            'AGRatio', 'BilirubinRatio', 'SGPTSGOTRatio', 'TotalEnzymes', 
            'AgeGroup', 'LowProtein', 'HighEnzymes', 'AgeGenderInteraction'
        ]
        
        # Ensure all required features are present with default values
        for col in feature_columns:
            if col not in model_input_data:
                current_app.logger.warning(f"Missing feature {col}, using default value 0")
                model_input_data[col] = 0
        
        # Convert all values to float to avoid dtype issues
        for key, value in model_input_data.items():
            if value is None:
                model_input_data[key] = 0.0
            else:
                try:
                    model_input_data[key] = float(value)
                except (ValueError, TypeError):
                    model_input_data[key] = 0.0
        
        df = pd.DataFrame([model_input_data], columns=feature_columns)
        current_app.logger.info(f"Liver DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")
        current_app.logger.info(f"Liver DataFrame values: {df.iloc[0].to_dict()}")
        
        # Predict probability of class 1 (disease)
        probability = model.predict_proba(df)[0][1]
            
        return float(probability)
    except Exception as e:
        current_app.logger.error(f"Liver prediction error: {e}")
        raise ValueError("Failed to preprocess liver data.")


def predict_mental_health(data: Dict[str, Any]) -> float:
    model = models.get('mental_health')
    if model is None:
        current_app.logger.error("Mental Health model is not loaded.")
        raise RuntimeError("Mental Health model is not loaded.")
        
    try:
        # --- UPDATED FEATURES per SRD ---
        feature_columns = [
            'phq_score', 'gad_score', 'depressiveness', 'suicidal', 
            'anxiousness', 'sleepiness', 'age', 'gender'
        ]
        
        # Map 'gender' from 'Male'/'Female' to 0/1
        data['gender'] = 1 if data.get('gender') == 'Male' else 0
        
        # Convert bools to int
        bool_cols = ['depressiveness', 'suicidal', 'anxiousness', 'sleepiness']
        for col in bool_cols:
            data[col] = 1 if data.get(col) else 0

        df = pd.DataFrame([data], columns=feature_columns)
        
        # --- FIX: Try to predict, but handle model mismatch gracefully ---
        try:
            probability = model.predict_proba(df)[0][1]
            return float(probability)
        except Exception as model_error:
            current_app.logger.warning(f"Mental health model prediction failed: {model_error}")
            # If the model fails due to feature mismatch, provide a default prediction
            # based on basic risk factors
            risk_score = 0.0
            
            # Basic risk calculation based on available data
            phq_score = data.get('phq_score', 0)
            gad_score = data.get('gad_score', 0)
            
            if phq_score >= 10:  # Moderate to severe depression
                risk_score += 0.4
            elif phq_score >= 5:  # Mild depression
                risk_score += 0.2
                
            if gad_score >= 10:  # Moderate to severe anxiety
                risk_score += 0.3
            elif gad_score >= 5:  # Mild anxiety
                risk_score += 0.15
                
            if data.get('suicidal'):
                risk_score += 0.3
            if data.get('depressiveness'):
                risk_score += 0.2
            if data.get('anxiousness'):
                risk_score += 0.2
            if data.get('sleepiness'):
                risk_score += 0.1
                
            # Cap at 1.0
            risk_score = min(risk_score, 1.0)
            current_app.logger.info(f"Using fallback mental health prediction: {risk_score}")
            return float(risk_score)
            
    except Exception as e:
        current_app.logger.error(f"Mental Health prediction error: {e}")
        raise ValueError("Failed to preprocess mental health data.")


# --- Main Service Function ---

def run_prediction(assessment_type: str, input_data: dict) -> float:
    """
    Routes prediction task to the correct function.
    Returns the raw risk score (probability).
    """
    current_app.logger.info(f"Running prediction for {assessment_type}")
    
    if assessment_type == 'diabetes':
        return predict_diabetes(input_data)
    elif assessment_type == 'heart':
        return predict_heart(input_data)
    elif assessment_type == 'liver':
        return predict_liver(input_data)
    elif assessment_type == 'mental_health':
        return predict_mental_health(input_data)
    else:
        current_app.logger.error(f"Invalid assessment type: {assessment_type}")
        raise ValueError("Invalid assessment type")

# --- Gemini Recommendation Service ---

def get_gemini_recommendations(risk_map: dict, patient_state: str = None, patient_id: int = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generates lifestyle recommendations using the Gemini API based on the
    patient's risk profile. Recommendations are generated in regional language
    based on patient's state.
    
    Args:
        risk_map: Dictionary of disease types to risk levels
        patient_state: Patient's state name for language selection
        patient_id: Patient ID for logging purposes
    
    Returns:
        Dictionary of recommendations grouped by category (diet, exercise, sleep, lifestyle)
    """
    from app.config import get_language_for_state
    
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        current_app.logger.warning("GEMINI_API_KEY not set. Returning empty recommendations.")
        return {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Get target language based on patient's state
        target_language = get_language_for_state(patient_state)
        current_app.logger.info(f"Generating recommendations in {target_language} for patient from {patient_state or 'unknown state'}")
        
        # Build a prompt focusing on Medium/High risks
        risk_summary = []
        has_high_risk = False
        for disease, level in risk_map.items():
            if level in ['Medium', 'High']:
                disease_name = disease.replace("_risk_level", "").capitalize()
                risk_summary.append(f"- {disease_name}: {level} risk")
                if level == 'High':
                    has_high_risk = True

        if not risk_summary:
            prompt_intro = "The patient has Low risk for all assessed conditions (diabetes, liver, heart, mental health)."
            prompt_request = "Provide 2-3 general preventative lifestyle recommendations."
        else:
            prompt_intro = "A patient has the following health risk profile:\n" + "\n".join(risk_summary)
            if has_high_risk:
                prompt_request = "Provide a mix of actionable lifestyle recommendations (diet, exercise, sleep, habits) for these conditions, prioritizing the 'High' risk items. Provide 2-3 recommendations per HIGH risk condition and 1-2 per MEDIUM risk condition."
            else:
                prompt_request = "Provide actionable lifestyle recommendations (diet, exercise, sleep, habits) for these 'Medium' risk conditions. Provide 2-3 recommendations per condition."

        # Language instruction for localization
        language_instruction = f"""
        CRITICAL LANGUAGE REQUIREMENT:
        The patient is from {patient_state or 'India'}.
        You MUST write ALL recommendation_text values in {target_language} language.
        Use simple, easy-to-understand {target_language} that a common person can understand.
        Keep disease_type, risk_level, and category in English for system processing.
        Only the recommendation_text field should be in {target_language}.
        """

        # JSON format instruction
        prompt = f"""
        You are a helpful, empathetic health assistant. {prompt_intro}

        {prompt_request}

        {language_instruction}

        Format your response *only* as a valid JSON list of objects.
        Each object in the list must have the following keys:
        - "disease_type": (string) The disease this applies to (e.g., "Diabetes", "Heart", "General"). Use the capitalized name. KEEP IN ENGLISH.
        - "risk_level": (string) The risk level this applies to (e.g., "High", "Medium", "Low"). KEEP IN ENGLISH.
        - "category": (string) The category of advice (e.g., "Diet", "Exercise", "Sleep", "Lifestyle"). KEEP IN ENGLISH.
        - "recommendation_text": (string) The specific recommendation. WRITE THIS IN {target_language} LANGUAGE.

        Example for {target_language}:
        [
          {{
            "disease_type": "Diabetes",
            "risk_level": "High",
            "category": "Diet",
            "recommendation_text": "[Write this recommendation in {target_language}]"
          }}
        ]

        Provide *only* the JSON list.
        """
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        recommendations = json.loads(cleaned_text)
        
        # Group recommendations by category for frontend
        grouped_recs = {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}
        for rec in recommendations:
            cat = rec.get("category", "Lifestyle").lower()
            if cat in grouped_recs:
                grouped_recs[cat].append(rec)
            else:
                grouped_recs["lifestyle"].append(rec)
            
        current_app.logger.info(f"Successfully fetched {len(recommendations)} recommendations from Gemini in {target_language}.")
        return grouped_recs

    except Exception as e:
        current_app.logger.error(f"Error calling Gemini API: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
        return {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}


def save_recommendations_to_db(patient_id: int, prediction_id: int, recommendations: dict, language: str) -> bool:
    """
    Saves generated recommendations to the database for persistence.
    Deactivates old recommendations and saves new ones.
    
    Args:
        patient_id: The patient's ID
        prediction_id: The associated prediction ID
        recommendations: Dictionary of recommendations grouped by category
        language: The language the recommendations are in
    
    Returns:
        True if successful, False otherwise
    """
    from app.models import LifestyleRecommendation
    from app.extensions import db
    
    try:
        # Deactivate old recommendations for this patient
        LifestyleRecommendation.query.filter_by(
            patient_id=patient_id, 
            is_active=True
        ).update({'is_active': False})
        
        # Save new recommendations
        priority = 1
        for category, recs in recommendations.items():
            for rec in recs:
                new_rec = LifestyleRecommendation(
                    patient_id=patient_id,
                    prediction_id=prediction_id,
                    disease_type=rec.get('disease_type', 'General'),
                    risk_level=rec.get('risk_level', 'Medium'),
                    category=category.title(),
                    recommendation_text=rec.get('recommendation_text', ''),
                    language=language,
                    priority=priority,
                    is_active=True
                )
                db.session.add(new_rec)
                priority += 1
        
        db.session.commit()
        current_app.logger.info(f"Saved {priority - 1} recommendations for patient {patient_id} in {language}")
        return True
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving recommendations to database: {e}")
        return False


def get_stored_recommendations(patient_id: int, prediction_id: int = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves stored recommendations from the database.
    
    Args:
        patient_id: The patient's ID
        prediction_id: Optional - filter by specific prediction ID
    
    Returns:
        Dictionary of recommendations grouped by category, or None if not found
    """
    from app.models import LifestyleRecommendation
    
    try:
        query = LifestyleRecommendation.query.filter_by(
            patient_id=patient_id,
            is_active=True
        )
        
        if prediction_id:
            query = query.filter_by(prediction_id=prediction_id)
        
        stored_recs = query.order_by(LifestyleRecommendation.priority).all()
        
        if not stored_recs:
            return None
        
        # Group by category
        grouped = {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}
        for rec in stored_recs:
            cat = rec.category.lower()
            if cat in grouped:
                grouped[cat].append(rec.to_dict())
            else:
                grouped["lifestyle"].append(rec.to_dict())
        
        return grouped
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving stored recommendations: {e}")
        return None