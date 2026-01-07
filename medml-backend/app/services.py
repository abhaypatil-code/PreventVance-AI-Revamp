# HealthCare App/medml-backend/app/services.py
import joblib
import pandas as pd
import numpy as np
import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from flask import current_app
import random
import time
from google.api_core import exceptions


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
        current_app.logger.info(f"Diabetes input: {data}")
        # Map assessment data to model's expected features
        processed_data = {}
        
        # Map basic features
        processed_data['Pregnancies'] = 1 if data.get('pregnancy') else 0
        processed_data['Glucose'] = data.get('glucose', 0)
        processed_data['BloodPressure'] = data.get('blood_pressure', 0)
        processed_data['SkinThickness'] = data.get('skin_thickness', 0)
        processed_data['Insulin'] = data.get('insulin', 0)
        processed_data['BMI'] = data.get('bmi', 0)
        processed_data['Age'] = data.get('age', 0)
        
        # DiabetesPedigreeFunction calculation
        glucose = processed_data['Glucose']
        age = processed_data['Age']
        bmi = processed_data['BMI']
        
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
        
        feature_order = [
            'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 
            'AgeGroup', 'BMICategory', 'GlucoseCategory', 
            'BMIAgeInteraction', 'GlucoseBMIInteraction'
        ]
        
        df = pd.DataFrame([processed_data], columns=feature_order)
        
        probability = model.predict_proba(df)[0][1] 
        current_app.logger.info(f"Diabetes prediction: {probability}")
        return float(probability)
    except Exception as e:
        current_app.logger.error(f"Diabetes prediction error: {e}")
        raise ValueError(f"Failed to preprocess diabetes data: {e}")

def predict_heart(data: Dict[str, Any]) -> float:
    model = models.get('heart')
    if model is None:
        current_app.logger.error("Heart model is not loaded.")
        raise RuntimeError("Heart model is not loaded.")
        
    try:
        current_app.logger.info(f"Heart input: {data}")
        # Feature Mapping for 'heart_SVM Weighted Tuned.pkl'
        processed_data = {}
        
        # 1. Direct Mappings
        processed_data['Age'] = data.get('age', 0)
        processed_data['Gender'] = 1 if data.get('gender') == 'Male' else 0
        processed_data['Diabetes'] = 1 if data.get('diabetes') else 0
        processed_data['Hypertension'] = 1 if data.get('hypertension') else 0
        processed_data['Obesity'] = 1 if data.get('obesity') else 0
        processed_data['Smoking'] = 1 if data.get('smoking') else 0
        processed_data['Alcohol_Consumption'] = 1 if data.get('alcohol_consumption') else 0
        processed_data['Physical_Activity'] = 1 if data.get('physical_activity') else 0
        processed_data['Diet_Score'] = data.get('diet_score', 5)
        processed_data['Cholesterol_Level'] = data.get('cholesterol_level', 0)
        processed_data['Triglyceride_Level'] = data.get('triglyceride_level', 0)
        processed_data['LDL_Level'] = data.get('ldl_level', 0)
        processed_data['HDL_Level'] = data.get('hdl_level', 0)
        processed_data['Systolic_BP'] = data.get('systolic_bp', 0)
        processed_data['Diastolic_BP'] = data.get('diastolic_bp', 0)
        processed_data['Air_Pollution_Exposure'] = data.get('air_pollution_exposure', 0)
        processed_data['Family_History'] = 1 if data.get('family_history') else 0
        processed_data['Stress_Level'] = data.get('stress_level', 0)
        processed_data['Heart_Attack_History'] = 1 if data.get('heart_attack_history') else 0
        
        # 2. Calculated Features
        sbp = processed_data['Systolic_BP']
        dbp = processed_data['Diastolic_BP']
        processed_data['BP_Difference'] = sbp - dbp
        processed_data['SystolicDiastolicRatio'] = sbp / dbp if dbp > 0 else 0
        
        # 3. Dummy/Default Features for model structure
        processed_data['Patient_ID'] = 1000 
        processed_data['State_Name'] = 0 
        processed_data['Healthcare_Access'] = 0.5 
        processed_data['Emergency_Response_Time'] = 15.0 
        processed_data['Annual_Income'] = 500000 
        processed_data['Health_Insurance'] = 1 
        
        feature_columns = [
            'Patient_ID', 'State_Name', 'Age', 'Gender', 'Diabetes', 'Hypertension', 
            'Obesity', 'Smoking', 'Alcohol_Consumption', 'Physical_Activity', 'Diet_Score', 
            'Cholesterol_Level', 'Triglyceride_Level', 'LDL_Level', 'HDL_Level', 
            'Systolic_BP', 'Diastolic_BP', 'Air_Pollution_Exposure', 'Family_History', 
            'Stress_Level', 'Healthcare_Access', 'Heart_Attack_History', 
            'Emergency_Response_Time', 'Annual_Income', 'Health_Insurance', 
            'SystolicDiastolicRatio', 'BP_Difference'
        ]
        
        df = pd.DataFrame([processed_data], columns=feature_columns)
        
        probability = model.predict_proba(df)[0][1]
        current_app.logger.info(f"Heart prediction: {probability}")
        return float(probability)
            
    except Exception as e:
        current_app.logger.error(f"Heart prediction error: {e}")
        raise ValueError(f"Failed to preprocess heart data: {e}")

def predict_liver(data: Dict[str, Any]) -> float:
    model = models.get('liver')
    if model is None:
        current_app.logger.error("Liver model is not loaded.")
        raise RuntimeError("Liver model is not loaded.")

    try:
        current_app.logger.info(f"Liver input: {data}")
        data_processed = data.copy()
        
        data_processed['Gender'] = 1 if data_processed.get('gender') == 'Male' else 0
        
        albumin = data_processed.get('albumin', 0)
        total_protein = data_processed.get('total_protein', 0)
        
        if total_protein and albumin and total_protein > albumin:
            globulin = total_protein - albumin
            data_processed['Albumin_and_Globulin_Ratio'] = round(albumin / globulin, 2)
        else:
            data_processed['Albumin_and_Globulin_Ratio'] = 0.9 
        
        key_map = {
            'age': 'Age', 'gender': 'Gender', 'total_bilirubin': 'TB',
            'direct_bilirubin': 'DB', 'alkaline_phosphatase': 'Alkphos',
            'sgpt_alamine_aminotransferase': 'Sgpt', 'sgot_aspartate_aminotransferase': 'Sgot',
            'total_protein': 'TP', 'albumin': 'ALB', 'ag_ratio': 'AGRatio'
        }
        
        model_input_data = {
            key_map.get(k, k): v for k, v in data_processed.items()
        }
        
        if model_input_data.get('AGRatio') is None:
            model_input_data['AGRatio'] = model_input_data.get('Albumin_and_Globulin_Ratio', 0.9)
        
        age = model_input_data.get('Age', 0)
        gender = model_input_data.get('Gender', 0)
        tb = model_input_data.get('TB', 0)
        db = model_input_data.get('DB', 0)
        sgpt = model_input_data.get('Sgpt', 0)
        sgot = model_input_data.get('Sgot', 0)
        tp = model_input_data.get('TP', 0)
        
        # Additional features
        model_input_data['BilirubinRatio'] = db / tb if tb > 0 else 0
        model_input_data['SGPTSGOTRatio'] = sgpt / sgot if sgot > 0 else 0
        model_input_data['TotalEnzymes'] = sgpt + sgot
        model_input_data['AgeGroup'] = 0 if age < 30 else (1 if age < 50 else 2)
        model_input_data['LowProtein'] = 1 if tp < 6.0 else 0
        model_input_data['HighEnzymes'] = 1 if (sgpt > 40 or sgot > 40) else 0
        model_input_data['AgeGenderInteraction'] = age * gender
        
        feature_columns = [
            'Age', 'Gender', 'TB', 'DB', 'Alkphos', 'Sgpt', 'Sgot', 'TP', 'ALB', 
            'AGRatio', 'BilirubinRatio', 'SGPTSGOTRatio', 'TotalEnzymes', 
            'AgeGroup', 'LowProtein', 'HighEnzymes', 'AgeGenderInteraction'
        ]
        
        for col in feature_columns:
            if col not in model_input_data:
                model_input_data[col] = 0
        
        for key, value in model_input_data.items():
            if value is None:
                model_input_data[key] = 0.0
            else:
                try:
                    model_input_data[key] = float(value)
                except (ValueError, TypeError):
                    model_input_data[key] = 0.0
        
        df = pd.DataFrame([model_input_data], columns=feature_columns)
        
        probability = model.predict_proba(df)[0][1]
        current_app.logger.info(f"Liver prediction: {probability}")
        return float(probability)
    except Exception as e:
        current_app.logger.error(f"Liver prediction error: {e}")
        raise ValueError(f"Failed to preprocess liver data: {e}")


def predict_mental_health(data: Dict[str, Any]) -> float:
    model = models.get('mental_health')
    if model is None:
        current_app.logger.error("Mental Health model is not loaded.")
        raise RuntimeError("Mental Health model is not loaded.")
        
    try:
        current_app.logger.info(f"Mental Health input: {data}")
        processed_data = {}
        
        age = data.get('age', 25)
        phq = data.get('phq_score', 0)
        gad = data.get('gad_score', 0)
        
        processed_data['age'] = age
        processed_data['gender'] = 1 if data.get('gender') == 'Male' else 0
        processed_data['phq_score'] = phq
        processed_data['gad_score'] = gad
        processed_data['suicidal'] = 1 if data.get('suicidal') else 0
        
        processed_data['school_year'] = 0 
        processed_data['bmi'] = 22.0
        processed_data['who_bmi'] = 1 
        
        # Depression Severity
        if phq < 5: processed_data['depression_severity'] = 0
        elif phq < 10: processed_data['depression_severity'] = 1
        elif phq < 15: processed_data['depression_severity'] = 2
        elif phq < 20: processed_data['depression_severity'] = 3
        else: processed_data['depression_severity'] = 4
        
        # Anxiety Severity
        if gad < 5: processed_data['anxiety_severity'] = 0
        elif gad < 10: processed_data['anxiety_severity'] = 1
        elif gad < 15: processed_data['anxiety_severity'] = 2
        else: processed_data['anxiety_severity'] = 3
        
        processed_data['PHQGADCombined'] = phq + gad
        processed_data['AgeGAD'] = age * gad
        
        processed_data['depression_diagnosis'] = 0
        processed_data['depression_treatment'] = 0
        processed_data['anxiety_diagnosis'] = 0
        processed_data['anxiety_treatment'] = 0
        processed_data['epworth_score'] = 0 
        
        processed_data['MentalHealthRisk'] = 1 if (phq + gad) > 20 else 0
        processed_data['ClinicalDepression'] = 1 if phq > 10 else 0
        processed_data['HighRiskProfile'] = 1 if (getattr(data, 'suicidal', False) or (phq+gad)>25) else 0

        feature_columns = [
            'school_year', 'age', 'gender', 'bmi', 'who_bmi', 'phq_score', 
            'depression_severity', 'suicidal', 'depression_diagnosis', 'depression_treatment', 
            'gad_score', 'anxiety_severity', 'anxiety_diagnosis', 'anxiety_treatment', 
            'epworth_score', 'MentalHealthRisk', 'PHQGADCombined', 'ClinicalDepression', 
            'AgeGAD', 'HighRiskProfile'
        ]
        
        df = pd.DataFrame([processed_data], columns=feature_columns)
        
        probability = model.predict_proba(df)[0][1]
        current_app.logger.info(f"Mental Health prediction: {probability}")
        return float(probability)
            
    except Exception as e:
        current_app.logger.error(f"Mental Health prediction error: {e}")
        raise ValueError(f"Failed to preprocess mental health data: {e}")


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
    """Generates lifestyle recommendations using Gemini with fallback."""
    from app.config import get_language_for_state
    
    # --- Hardcoded Fallback Recommendations (Safety Net) ---
    FALLBACK_DATA = {
        "diet": [
            {"disease_type": "General", "risk_level": "Medium", "category": "Diet", "recommendation_text": "Eat more leafy greens and whole grains daily."},
            {"disease_type": "General", "risk_level": "Medium", "category": "Diet", "recommendation_text": "Reduce sugar intake and avoid processed foods."},
             {"disease_type": "General", "risk_level": "Medium", "category": "Diet", "recommendation_text": "Drink at least 8 glasses of water every day."}
        ],
        "exercise": [
            {"disease_type": "General", "risk_level": "Medium", "category": "Exercise", "recommendation_text": "Walk for at least 30 minutes every day."},
            {"disease_type": "General", "risk_level": "Medium", "category": "Exercise", "recommendation_text": "Try light yoga or stretching exercises morning."}
        ],
        "sleep": [
             {"disease_type": "General", "risk_level": "Medium", "category": "Sleep", "recommendation_text": "Maintain a consistent sleep schedule of 7-8 hours."},
             {"disease_type": "General", "risk_level": "Medium", "category": "Sleep", "recommendation_text": "Avoid screens 1 hour before bedtime."}
        ],
        "lifestyle": [
            {"disease_type": "General", "risk_level": "Medium", "category": "Lifestyle", "recommendation_text": "Practice deep breathing to manage stress levels."},
            {"disease_type": "General", "risk_level": "Medium", "category": "Lifestyle", "recommendation_text": "Monitor your health vitals regularly."}
        ]
    }

    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        current_app.logger.warning("GEMINI_API_KEY not set. Returning fallback recommendations.")
        return FALLBACK_DATA

    try:
        genai.configure(api_key=api_key)
        # Try a lighter model first, often higher availability
        model = genai.GenerativeModel('gemini-2.0-flash-lite') 
        
        target_language = get_language_for_state(patient_state)
        
        risk_summary = []
        has_high_risk = False
        for disease, level in risk_map.items():
            if level in ['Medium', 'High']:
                disease_name = disease.replace("_risk_level", "").capitalize()
                risk_summary.append(f"- {disease_name}: {level} risk")
                if level == 'High':
                    has_high_risk = True

        prompt = f"""
        Act as a health assistant. Patient Profile: {patient_state or 'India'}.
        Risks: {', '.join(risk_summary) if risk_summary else 'None (General Prevention)'}.
        
        Task: Provide a JSON list of strictly 3-4 SHORT, ACTIONABLE lifestyle tips (Diet, Exercise, Sleep, etc) tailored to these risks. { 'Focus on High risks.' if has_high_risk else '' }
        
        CRITICAL RULES:
        1. Output MUST be valid JSON list.
        2. Keys: "disease_type" (English), "risk_level" (English), "category" (English), "recommendation_text".
        3. "recommendation_text" MUST be in {target_language}.
        4. Keep tips under 10 words each.
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
        
        grouped_recs = {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}
        for rec in recommendations:
            cat = rec.get("category", "Lifestyle").lower()
            if cat in grouped_recs:
                grouped_recs[cat].append(rec)
            else:
                grouped_recs["lifestyle"].append(rec)
            
        return grouped_recs

        return grouped_recs

    except Exception as e:
        current_app.logger.error(f"Error calling Gemini API (using fallback): {e}")
        # Return fallback data instead of empty dict or None
        return FALLBACK_DATA


def save_recommendations_to_db(patient_id: int, prediction_id: int, recommendations: dict, language: str) -> bool:
    """Saves generated recommendations to the database."""
    from app.models import LifestyleRecommendation
    from app.extensions import db
    
    try:
        LifestyleRecommendation.query.filter_by(patient_id=patient_id, is_active=True).update({'is_active': False})
        
        priority = 1
        for category, recs in recommendations.items():
            for rec in recs:
                new_rec = LifestyleRecommendation(
                    patient_id=patient_id, prediction_id=prediction_id,
                    disease_type=rec.get('disease_type', 'General'),
                    risk_level=rec.get('risk_level', 'Medium'),
                    category=category.title(),
                    recommendation_text=rec.get('recommendation_text', ''),
                    language=language, priority=priority, is_active=True
                )
                db.session.add(new_rec)
                priority += 1
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving recommendations: {e}")
        return False


def get_stored_recommendations(patient_id: int, prediction_id: int = None) -> Dict[str, List[Dict[str, Any]]]:
    """Retrieves stored recommendations."""
    from app.models import LifestyleRecommendation
    
    try:
        query = LifestyleRecommendation.query.filter_by(patient_id=patient_id, is_active=True)
        if prediction_id:
            query = query.filter_by(prediction_id=prediction_id)
        
        stored_recs = query.order_by(LifestyleRecommendation.priority).all()
        if not stored_recs:
            return None
        
        grouped = {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}
        for rec in stored_recs:
            cat = rec.category.lower()
            if cat in grouped:
                grouped[cat].append(rec.to_dict())
            else:
                grouped["lifestyle"].append(rec.to_dict())
        return grouped
    except Exception as e:
        current_app.logger.error(f"Error retrieving recommendations: {e}")
        return None