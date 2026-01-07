import streamlit as st
from theme import create_risk_badge

def risk_color(level):
    """Returns a hex color based on risk level."""
    if level == "High":
        return "#DC3545"  # Red
    if level == "Medium":
        return "#FFC107"  # Yellow
    if level == "Low":
        return "#28A745"  # Green
    return "#5A6D7A"  # Gray

def display_risk_assessment(risk_data):
    """Displays the main risk assessment table using new card styles."""
    st.subheader("🚨 Disease Risk Assessment")
    
    if not risk_data:
        st.warning("No risk assessment has been performed yet.")
        return

    data = [
        {"Disease": "🩺 Diabetes", "Risk Level": risk_data.get('diabetes_risk_level', 'N/A')},
        {"Disease": "🫀 Liver Disease", "Risk Level": risk_data.get('liver_risk_level', 'N/A')},
        {"Disease": "❤️ Heart Disease", "Risk Level": risk_data.get('heart_risk_level', 'N/A')},
        {"Disease": "🧠 Mental Health", "Risk Level": risk_data.get('mental_health_risk_level', 'N/A')}
    ]
    
    for item in data:
        level = item['Risk Level']
        badge_html = create_risk_badge(level)
        
        st.markdown(f"""
        <div class_name="risk-item-card" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.25rem; background-color: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--border-radius-md); margin-bottom: 0.5rem;">
            <span style="font-size: 1.1em; font-weight: 500; color: var(--color-text-primary);">{item['Disease']}</span>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)

def logout():
    """Clears session state and returns to login."""
    # Added all session keys from 2_Admin_Dashboard.py to ensure a clean slate
    keys_to_clear = [
        "logged_in", "user_role", "user_id", "user_name", "token", 
        "admin_view", "add_user_step", "new_patient_id", "new_patient_name",
        "assessment_status", "view_patient_id", "edit_patient_data",
        "patient_view", "show_pdf_download", "show_share_options",
        "patient_category", "patient_sort", "appointment_success", 
        "show_appointment_modal"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.login_type = "admin" # Reset to default login
    st.rerun()

def check_login(role=None):
    """Checks if user is logged in and has the correct role."""
    if not st.session_state.get("logged_in", False):
        st.error("Access Denied. Please log in first.")
        st.switch_page("app.py")
    
    if role and st.session_state.get("user_role") != role:
        st.error(f"Access Denied. You must be a {role}.")
        st.switch_page("app.py")


INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", 
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", 
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", 
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", 
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", 
    "Ladakh", "Lakshadweep", "Puducherry"
]