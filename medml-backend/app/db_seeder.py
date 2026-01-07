# HealthCare App/medml-backend/app/db_seeder.py
from app.models import db, LifestyleRecommendation
from flask import current_app

def seed_static_recommendations():
    """
    Populates the LifestyleRecommendation table with static MVP data
    if it is currently empty.
    """
    # NOTE: Disabling this for now because LifestyleRecommendation requires a patient_id (1:N relationship)
    # and these static ones don't have one.
    return
    try:
        if LifestyleRecommendation.query.first() is not None:
            # Data already exists, do nothing
            return

        recommendations = [
            # Diabetes
            LifestyleRecommendation(disease_type='diabetes', risk_level='Low', category='Diet', recommendation_text='Monitor blood sugar regularly. Maintain a balanced diet rich in fiber and whole grains.'),
            LifestyleRecommendation(disease_type='diabetes', risk_level='Medium', category='Exercise', recommendation_text='Increase physical activity to at least 150 minutes per week and include strength training.'),
            LifestyleRecommendation(disease_type='diabetes', risk_level='High', category='Lifestyle', recommendation_text='Urgent consult with endocrinologist; monitor glucose multiple times daily and follow prescribed plan.'),
            
            # Liver
            LifestyleRecommendation(disease_type='liver', risk_level='Low', category='Diet', recommendation_text='Avoid alcohol and processed foods. Eat a balanced diet with plenty of fruits and vegetables.'),
            LifestyleRecommendation(disease_type='liver', risk_level='Medium', category='Lifestyle', recommendation_text='Avoid alcohol completely. Limit fat, sugar, and salt. Consider liver function tests.'),
            LifestyleRecommendation(disease_type='liver', risk_level='High', category='Diet', recommendation_text='Strict dietary restrictions required. Avoid alcohol and fatty foods entirely; seek hepatologist advice.'),
            
            # Heart
            LifestyleRecommendation(disease_type='heart', risk_level='Low', category='Exercise', recommendation_text='Regular aerobic exercise (e.g., brisk walking, cycling) and manage stress levels.'),
            LifestyleRecommendation(disease_type='heart', risk_level='Medium', category='Diet', recommendation_text='Adopt a heart-healthy, low-sodium, low-saturated-fat diet; monitor BP and cholesterol.'),
            LifestyleRecommendation(disease_type='heart', risk_level='High', category='Lifestyle', recommendation_text='Urgent cardiologist consultation; adhere to supervised exercise and medication as prescribed.'),
            
            # Mental Health
            LifestyleRecommendation(disease_type='mental_health', risk_level='Low', category='Sleep', recommendation_text='Ensure 7-9 hours of quality sleep; practice daily mindfulness or meditation.'),
            LifestyleRecommendation(disease_type='mental_health', risk_level='Medium', category='Lifestyle', recommendation_text='Establish a consistent routine and consider therapy or counseling sessions.'),
            LifestyleRecommendation(disease_type='mental_health', risk_level='High', category='Lifestyle', recommendation_text='Seek immediate professional help; contact support lines if in distress; follow treatment plan.')
        ]
        
        db.session.bulk_save_objects(recommendations)
        db.session.commit()
        current_app.logger.info("Successfully seeded static LifestyleRecommendations.")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error seeding database: {e}")