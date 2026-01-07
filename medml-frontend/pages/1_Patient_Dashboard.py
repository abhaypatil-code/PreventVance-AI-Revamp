import streamlit as st
import api_client
import utils
import pandas as pd
from datetime import datetime, timedelta
from theme import apply_light_theme, create_navbar, create_metric_card

st.set_page_config(
    page_title="Patient Dashboard", 
    layout="wide",
    page_icon="👤"
)

# --- Authentication Check ---
if "token" not in st.session_state or st.session_state.get("user_role") != "patient":
    st.warning("⚠️ Please log in to access your dashboard.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# --- Layout & Data Loading ---
apply_light_theme()

user_name = st.session_state.get("user_name", "Patient")
user_role = st.session_state.get("user_role", "Patient")
create_navbar(user_name, user_role)

patient_id = st.session_state.get("user_id")

if not patient_id:
    st.error("⚠️ User ID not found in session. Please log in again.")
    if st.button("Go to Login", key="login_redirect_missing_id"):
        utils.logout()
    st.stop()

# --- Header Section ---
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title(f"Welcome back! 👋")
with col_header_2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

with st.spinner("Loading your health profile..."):
    patient_data = api_client.get_patient_details(patient_id)
    risk_data = api_client.get_latest_prediction(patient_id)
    recommendations = api_client.get_recommendations(patient_id)

if not patient_data:
    st.error("❌ Could not load patient profile. Please try again later.")
    if st.button("Retry Loading"):
        st.rerun()
    st.stop()

# Update title with name after loading
st.markdown(f"**Patient ID:** `{patient_data.get('patient_id', 'N/A')}`")

st.divider()

# --- Tabs ---
tabs = st.tabs(["Overview", "Diabetes", "Liver", "Heart", "Mental Health"])

with tabs[0]:
    # --- Key Metrics ---
    st.subheader("📊 Health Overview")
    
    # CSS for metric cards
    st.markdown("""
    <style>
    .metric-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--color-primary);
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div>
                <div class="metric-label">Age</div>
                <div class="metric-value">{patient_data.get('age', 'N/A')} <span style="font-size: 0.8rem; color: #888;">yrs</span></div>
            </div>
            <div style="font-size: 1.5rem;">🎂</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div>
                <div class="metric-label">Height</div>
                <div class="metric-value">{patient_data.get('height', 0)} <span style="font-size: 0.8rem; color: #888;">cm</span></div>
            </div>
            <div style="font-size: 1.5rem;">📏</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div>
                <div class="metric-label">Weight</div>
                <div class="metric-value">{(patient_data.get('weight') or 0):.1f} <span style="font-size: 0.8rem; color: #888;">kg</span></div>
            </div>
            <div style="font-size: 1.5rem;">⚖️</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Disease Risk Assessment
    utils.display_risk_assessment(risk_data)
    
    # Retry Prediction Section (if no risk data available)
    if not risk_data:
        st.info("ℹ️ Risk assessment data is pending. Please complete your health assessments or contact your healthcare worker.")
    
    st.divider()

    # --- Recommendations & Appointments ---
    col1, col2 = st.columns(2)
    
    with col1:
        # Upcoming Appointments
        st.subheader("📅 Upcoming Appointments")
        appointments = []
        if risk_data:
            for risk_key, disease_name in [
                ("diabetes_risk_level", "Diabetes"),
                ("liver_risk_level", "Liver Disease"),
                ("heart_risk_level", "Heart Disease"),
                ("mental_health_risk_level", "Mental Health")
            ]:
                level = risk_data.get(risk_key)
                if level in ["Medium", "High"]:
                    consultation_type = "In-Person (High Risk)" if level == "High" else "Teleconsultation (Medium Risk)"
                    appointments.append({
                        "Disease": disease_name,
                        "Type": consultation_type,
                    })
        
        if appointments:
            for appt in appointments:
                st.markdown(f"""
                <div class="card">
                    <h4 style="margin: 0; color: var(--color-primary);">📅 {appt['Disease']} Consultation</h4>
                    <p style="margin: 0.5rem 0 0 0; color: var(--color-text-secondary);">
                        <strong>Type:</strong> {appt['Type']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No upcoming appointments scheduled.")

    with col2:
        # Medication Schedule (Dummy/Static)
        st.subheader("💊 Medication Schedule")
        medication_data = {
            "Medication": ["Metformin", "Atorvastatin", "Multivitamin"],
            "Morning": ["✓", "", "✓"],
            "Afternoon": ["", "", ""],
            "Evening": ["✓", "✓", ""]
        }
        df_meds = pd.DataFrame(medication_data)
        st.dataframe(df_meds, use_container_width=True)
        st.caption("This is example data. Please follow your doctor's prescription.")
    
    st.divider()
    
    # Enhanced Lifestyle Recommendations
    st.subheader("💡 Your Personalized Health Tips")
    
    if recommendations and any(recommendations.values()):
        st.info("Here are some personalized tips based on your health assessment.")
        
        for category, recs in recommendations.items():
            if recs:
                st.markdown(f"#### {category.title()} Tips")
                for rec in recs:
                    disease_type = rec.get('disease_type', 'General')
                    text = rec.get('recommendation_text', '')
                    risk_level = rec.get('risk_level', 'Medium')
                    
                    if risk_level == 'High':
                        style_class = "priority-high"
                        title = "⭐ Priority Action"
                        icon = "🚨"
                    elif risk_level == 'Medium':
                        style_class = "priority-medium"
                        title = "💪 Helpful Tip"
                        icon = "⚠️"
                    else:
                        style_class = "priority-low"
                        title = "🌱 Wellness Boost"
                        icon = "✅"
                    
                    st.markdown(f"""
                    <div class="priority-card {style_class}">
                        <h5>{icon} {title} ({disease_type})</h5>
                        <p>{text}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("🌟 Your assessment results look great! Continue maintaining a healthy lifestyle.")
    
    st.divider()
    
    # Assessment History
    st.subheader("📋 Assessment History")
    if patient_data.get('diabetes_assessments') or patient_data.get('liver_assessments') or patient_data.get('heart_assessments') or patient_data.get('mental_health_assessments'):
        assessment_tabs = st.tabs(["Diabetes", "Liver", "Heart", "Mental Health"])
        
        with assessment_tabs[0]:
            if patient_data.get('diabetes_assessments'):
                st.dataframe(patient_data['diabetes_assessments'], use_container_width=True)
            else:
                st.info("No diabetes assessments completed.")
        
        with assessment_tabs[1]:
            if patient_data.get('liver_assessments'):
                st.dataframe(patient_data['liver_assessments'], use_container_width=True)
            else:
                st.info("No liver assessments completed.")
        
        with assessment_tabs[2]:
            if patient_data.get('heart_assessments'):
                st.dataframe(patient_data['heart_assessments'], use_container_width=True)
            else:
                st.info("No heart assessments completed.")
        
        with assessment_tabs[3]:
            if patient_data.get('mental_health_assessments'):
                st.dataframe(patient_data['mental_health_assessments'], use_container_width=True)
            else:
                st.info("No mental health assessments completed.")
    else:
        st.info("📭 No assessment history available.")
    
    st.divider()
    
    # Healthcare Worker Information
    st.subheader("👨‍⚕️ Your Healthcare Worker")
    admin_info = patient_data.get('created_by_admin', {})
    
    if admin_info:
        st.markdown(f"""
        <div class="card">
            <h4 style="margin:0 0 0.5rem 0;">{admin_info.get('name', 'N/A')}</h4>
            <p style="margin:0;"><strong>Designation:</strong> {admin_info.get('designation', 'N/A')}</p>
            <p style="margin:0;"><strong>Contact:</strong> {admin_info.get('contact_number', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No healthcare worker information available.")


# --- View: Individual Disease Tabs ---
def render_disease_tab(disease_name, risk_key, score_key, icon):
    st.header(f"{icon} {disease_name} Assessment")
    
    if not risk_data:
        st.warning("No risk assessment data available. Please check the Overview tab.")
        return
    
    risk_level = risk_data.get(risk_key, 'N/A')
    risk_score = risk_data.get(score_key) or 0
    
    # Risk Score Display
    st.subheader("📊 Your Risk Score")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Risk Score (0-1)", f"{risk_score:.3f}")
        st.caption("A score closer to 1.0 indicates a higher risk.")
    with col2:
        badge_html = utils.create_risk_badge(risk_level)
        st.markdown(f"**Your calculated risk level is:**<br><br>{badge_html}", unsafe_allow_html=True)
    
    st.divider()
    
    # Next Recommended Action Steps
    st.subheader("🎯 Next Recommended Actions")
    if risk_level == "High":
        st.error("🚨 **Urgent Care Recommended:** Your risk level is high. Please consult your healthcare worker immediately for an in-person appointment.")
    elif risk_level == "Medium":
        st.warning("⚠️ **Monitoring Recommended:** Your risk level is medium. A teleconsultation is recommended. Please follow the lifestyle tips and monitor your health.")
    elif risk_level == "Low":
        st.success("✅ **Preventive Care:** Your risk level is low. Continue to maintain a healthy lifestyle and attend regular checkups.")
    else:
        st.info("ℹ️ No assessment data available to determine actions.")
    
    st.divider()
    
    # Disease-specific recommendations
    st.subheader("💡 Personalized Tips")
    disease_recs = []
    if recommendations:
        for category, recs in recommendations.items():
            for rec in recs:
                if rec.get('disease_type', '').lower() == disease_name.lower():
                    disease_recs.append(rec)
    
    if disease_recs:
        for rec in disease_recs:
            category = rec.get('category', 'General')
            text = rec.get('recommendation_text', '')
            risk_level = rec.get('risk_level', 'Medium')
            
            if risk_level == 'High':
                style_class = "priority-high"
                title = "⭐ Priority Action"
                icon = "🚨"
            elif risk_level == 'Medium':
                style_class = "priority-medium"
                title = "💪 Helpful Tip"
                icon = "⚠️"
            else:
                style_class = "priority-low"
                title = "🌱 Wellness Boost"
                icon = "✅"
            
            st.markdown(f"""
            <div class="priority-card {style_class}">
                <h5>{icon} {title} ({category})</h5>
                <p>{text}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"No specific tips available for {disease_name} at this time.")

with tabs[1]:
    render_disease_tab("Diabetes", "diabetes_risk_level", "diabetes_risk_score", "🩺")

with tabs[2]:
    render_disease_tab("Liver Disease", "liver_risk_level", "liver_risk_score", "🫀")

with tabs[3]:
    render_disease_tab("Heart Disease", "heart_risk_level", "heart_risk_score", "❤️")

with tabs[4]:
    render_disease_tab("Mental Health", "mental_health_risk_level", "mental_health_risk_score", "🧠")