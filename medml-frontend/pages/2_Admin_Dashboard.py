import streamlit as st
import time
import api_client
import utils
import pandas as pd
from theme import apply_light_theme, create_navbar, create_metric_card

st.set_page_config(
    page_title="Admin Dashboard", 
    layout="wide",
    page_icon="👨‍⚕️"
)

# Apply enhanced light theme
apply_light_theme()

utils.check_login(role="admin")

# Create top navigation bar
create_navbar(st.session_state.user_name, st.session_state.user_role)

# --- State Management ---
if "admin_view" not in st.session_state:
    st.session_state.admin_view = "main" # main, add_user, view_patients, patient_detail, edit_patient
if "add_user_step" not in st.session_state:
    st.session_state.add_user_step = 1 # 1, 2, 'diabetes', 'liver', 'heart', 'mental_health'
if "new_patient_id" not in st.session_state:
    st.session_state.new_patient_id = None
if "new_patient_name" not in st.session_state:
    st.session_state.new_patient_name = None
if "assessment_status" not in st.session_state:
    st.session_state.assessment_status = {"diabetes": False, "liver": False, "heart": False, "mental_health": False}
if "view_patient_id" not in st.session_state:
    st.session_state.view_patient_id = None
if "edit_patient_data" not in st.session_state:
    st.session_state.edit_patient_data = None


# --- Navigation Callbacks ---
def set_view(view_name):
    st.session_state.admin_view = view_name
    
def go_to_patient_detail(patient_id):
    st.session_state.view_patient_id = patient_id
    st.session_state.admin_view = "patient_detail"

def go_to_edit_patient(patient_id):
    patient_data = api_client.get_patient_details(patient_id)
    if patient_data:
        st.session_state.edit_patient_data = patient_data
        st.session_state.admin_view = "edit_patient"
    else:
        st.error("Could not load patient data for editing.")

def reset_add_user_flow():
    st.session_state.add_user_step = 1
    st.session_state.new_patient_id = None
    st.session_state.new_patient_name = None
    st.session_state.assessment_status = {"diabetes": False, "liver": False, "heart": False, "mental_health": False}
    set_view("main")

# --- View: Main Dashboard ---
if st.session_state.admin_view == "main":
    
    st.markdown(f"""
    <div style="background: var(--color-primary-light); color: var(--color-primary-dark); padding: 2rem; border-radius: var(--border-radius-lg); margin-bottom: 1.5rem;">
        <h1 style="margin: 0; font-size: 2.25rem; font-weight: 700;">Admin Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Welcome, {st.session_state.user_name}. Manage patients and view system analytics.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Top Action Buttons
    st.subheader("🎯 Primary Actions")
    col1, col2 = st.columns(2)
    with col1:
        st.button("➕ Register New Patient", on_click=set_view, args=("add_user",), use_container_width=True, type="primary")
    with col2:
        st.button("👥 View Patient Directory", on_click=set_view, args=("view_patients",), use_container_width=True, type="secondary")
    
    st.divider()
    
    # Analytics Section
    st.subheader("📊 System Overview")
    stats = api_client.get_dashboard_stats()
    
    if stats:
        # Registration metrics
        st.markdown("<h5>📈 Patient Registrations</h5>", unsafe_allow_html=True)
        reg_col1, reg_col2, reg_col3, reg_col4 = st.columns(4)
        
        with reg_col1:
            create_metric_card("Today", str(stats.get("today_registrations", 0)), "New registrations", "primary")
        with reg_col2:
            create_metric_card("This Week", str(stats.get("this_week_registrations", 0)), "New registrations", "primary")
        with reg_col3:
            create_metric_card("This Month", str(stats.get("this_month_registrations", 0)), "New registrations", "primary")
        with reg_col4:
            create_metric_card("Total Patients", str(stats.get("total_patients", 0)), "All-time", "success")
        
        st.markdown("<br>", unsafe_allow_html=True) # Spacer
        
        # Risk Assessment Cards
        st.markdown("<h5>🚨 High/Medium Risk Patients</h5>", unsafe_allow_html=True)
        risk_cols = st.columns(4)
        
        with risk_cols[0]:
            create_metric_card("🩺 Diabetes", str(stats.get("diabetes_risk_count", 0)), "At-risk patients", "error")
        with risk_cols[1]:
            create_metric_card("🫀 Liver", str(stats.get("liver_risk_count", 0)), "At-risk patients", "warning")
        with risk_cols[2]:
            create_metric_card("❤️ Heart", str(stats.get("heart_risk_count", 0)), "At-risk patients", "error")
        with risk_cols[3]:
            create_metric_card("🧠 Mental Health", str(stats.get("mental_health_risk_count", 0)), "At-risk patients", "primary")
    else:
        st.warning("Could not load analytics.")

# --- View: Add New User ---
elif st.session_state.admin_view == "add_user":
    st.button("🏠 Back to Dashboard", on_click=set_view, args=("main",))
    
    st.title("➕ Register New Patient")
    
    # Progress indicator
    steps = ["1. Patient Demographics", "2. Clinical Assessments", "3. Complete"]
    current_step_index = st.session_state.add_user_step if isinstance(st.session_state.add_user_step, int) else 2
    
    st.markdown(f"**Step {current_step_index} of 3:** {steps[current_step_index-1]}")
    progress_percent = int(((current_step_index-1) / (len(steps)-1)) * 100)
    st.progress(progress_percent)
    
    st.divider()
    
    # --- Step 1: Basic Info ---
    if st.session_state.add_user_step == 1:
        st.header("Step 1: Patient Demographics")
        st.markdown("Enter the patient's basic information. An ABHA ID and password will be used for them to log in.")
        
        with st.form("basic_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("👤 Full Name*", placeholder="Enter patient's full name")
                abha_id = st.text_input("🆔 ABHA ID (14 digits)*", placeholder="14-digit ABHA ID", max_chars=14)
                age = st.number_input("🎂 Age*", min_value=0, max_value=120, step=1, help="Patient's age in years")
                gender = st.selectbox("⚥ Gender*", ["Male", "Female", "Other"])
            
            with col2:
                height = st.number_input("📏 Height (cm)*", min_value=50.0, max_value=300.0, step=0.5, format="%.1f")
                weight = st.number_input("⚖️ Weight (kg)*", min_value=10.0, max_value=300.0, step=0.1, format="%.1f")
                state_name = st.selectbox("🗺️ State*", utils.INDIAN_STATES, help="Patient's state of residence")
            
            if height > 0 and weight > 0:
                bmi = weight / ((height / 100) ** 2)
                st.info(f"📊 **Calculated BMI**: {bmi:.2f}")
            
            # Auto-generate password
            password = f"{abha_id}@Default123" 
            
            st.divider()
            submitted = st.form_submit_button("Save and Proceed to Assessments", use_container_width=True, type="primary")
            
            if submitted:
                # Validation
                if len(abha_id) != 14 or not abha_id.isdigit():
                    st.error("ABHA ID must be exactly 14 digits.")
                elif not name or len(name.strip()) < 2:
                    st.error("Name is required.")
                elif not age or age <= 0:
                    st.error("Please enter a valid age.")
                elif not height or height <= 0:
                    st.error("Please enter a valid height.")
                elif not weight or weight <= 0:
                    st.error("Please enter a valid weight.")
                else:
                    data = {
                        "name": name.strip(), "abha_id": abha_id.strip(), "password": password,
                        "age": int(age), "gender": gender, "height": float(height),
                        "weight": float(weight), "state_name": state_name
                    }
                    
                    with st.spinner("Registering patient..."):
                        new_patient = api_client.add_patient(data)
                    if new_patient:
                        st.session_state.new_patient_id = new_patient.get("patient_id")
                        st.session_state.new_patient_name = new_patient.get("name")
                        st.session_state.add_user_step = 2
                        st.rerun()
                    # Error is handled by api_client.py

    # --- Step 2: Assessment Hub ---
    elif st.session_state.add_user_step == 2:
        st.header("Step 2: Clinical Assessments")
        patient_id = st.session_state.new_patient_id
        patient_name = st.session_state.new_patient_name
        
        st.info(f"Complete all 4 health assessments for **{patient_name}** (ID: {patient_id}) to enable risk analysis.")
        
        status = st.session_state.assessment_status
        
        assessment_cols = st.columns(4)
        assessments = [
            ("diabetes", "🩺", "Diabetes", assessment_cols[0]),
            ("liver", "🫀", "Liver", assessment_cols[1]),
            ("heart", "❤️", "Heart", assessment_cols[2]),
            ("mental_health", "🧠", "Mental Health", assessment_cols[3])
        ]
        
        for key, icon, title, col in assessments:
            with col:
                is_complete = status[key]
                button_label = "✅ Edit" if is_complete else f"Start {icon}"
                button_type = "secondary" if is_complete else "primary"
                
                st.markdown(f"<h5>{icon} {title}</h5>", unsafe_allow_html=True)
                if is_complete:
                    st.markdown("✅ **Completed**")
                else:
                    st.markdown("⏳ Pending")
                
                if st.button(button_label, key=f"btn_{key}", use_container_width=True, type=button_type):
                    st.session_state.add_user_step = key
                    st.rerun()
        
        st.divider()
        
        st.divider()
        
        # Finish Survey button
        any_done = any(status.values())
        all_done = all(status.values())
        
        if any_done:
            if not all_done:
                st.info("ℹ️ You can proceed with the analysis now, or complete the remaining assessments for a more comprehensive report.")
            else:
                st.success("🎉 All assessments are complete!")
            
            st.markdown("You can now run the AI-powered risk analysis for this patient.")
            
            if st.button("✅ Complete Registration & Run Analysis", use_container_width=True, type="primary"):
                with st.spinner("🤖 Running AI-powered risk analysis... This may take a moment."):
                    result = api_client.trigger_prediction(patient_id)
                if result:
                    st.success(f"✅ Successfully added patient and triggered risk assessment!")
                    reset_add_user_flow()
                    st.rerun()
                else:
                    st.error("❌ Failed to trigger prediction. The patient is saved, but you may need to retry the prediction from their profile.")
                    # Still reset, as the patient *is* saved.
                    reset_add_user_flow()
                    st.rerun()
        else:
            st.warning("⚠️ Please complete at least one assessment to proceed.")

    # --- Step 3: Individual Forms ---
    def render_assessment_form(name, fields, api_key, icon):
        st.header(f"Step 2: {icon} {name} Assessment")
        st.button("⬅️ Back to Assessment Hub", on_click=lambda: st.session_state.update(add_user_step=2))
        
        with st.form(f"{api_key}_form"):
            st.markdown(f"Fill in the details for the {name} assessment.")
            form_data = {}
            for field, field_type, kwargs in fields:
                label = kwargs.pop("label", field.replace("_", " ").title())
                if field_type == "number":
                    form_data[field] = st.number_input(label, **kwargs)
                elif field_type == "bool":
                    form_data[field] = st.checkbox(label, **kwargs)
                elif field_type == "select":
                    form_data[field] = st.selectbox(label, **kwargs)
            
            submitted = st.form_submit_button("Save Assessment", use_container_width=True, type="primary")
            
            if submitted:
                with st.spinner("Saving assessment..."):
                    result = api_client.add_assessment(st.session_state.new_patient_id, api_key, form_data)
                if result:
                    st.toast(f"✅ {name} assessment saved!", icon=icon)
                    st.session_state.assessment_status[api_key] = True
                    st.session_state.add_user_step = 2
                    st.rerun()

    if st.session_state.add_user_step == 'diabetes':
        fields = [
            ("pregnancy", "bool", {"label": "Patient is pregnant"}),
            ("glucose", "number", {"min_value": 0.0, "step": 1.0, "format": "%.1f", "label": "Glucose (mg/dL)"}),
            ("blood_pressure", "number", {"min_value": 0.0, "step": 1.0, "format": "%.1f", "label": "Blood Pressure (mm Hg)"}),
            ("skin_thickness", "number", {"min_value": 0.0, "step": 0.1, "format": "%.1f", "label": "Skin Thickness (mm)"}),
            ("insulin", "number", {"min_value": 0.0, "step": 1.0, "format": "%.1f", "label": "Insulin (μU/mL)"}),
            ("diabetes_history", "bool", {"label": "Patient has diabetes history"})
        ]
        render_assessment_form("Diabetes", fields, "diabetes", "🩺")

    if st.session_state.add_user_step == 'liver':
        st.header("Step 2: 🫀 Liver Assessment")
        st.button("⬅️ Back to Assessment Hub", on_click=lambda: st.session_state.update(add_user_step=2))
        
        with st.form("liver_form"):
            st.markdown("Fill in the patient's liver function test results.")
            col1, col2 = st.columns(2)
            
            with col1:
                total_bilirubin = st.number_input("Total Bilirubin (mg/dL)", min_value=0.0, step=0.1, format="%.1f")
                direct_bilirubin = st.number_input("Direct Bilirubin (mg/dL)", min_value=0.0, step=0.1, format="%.1f")
                alkaline_phosphatase = st.number_input("Alkaline Phosphatase (IU/L)", min_value=0.0, step=1.0, format="%.1f")
                sgpt_alamine_aminotransferase = st.number_input("SGPT (Alamine Aminotransferase) (U/L)", min_value=0.0, step=1.0, format="%.1f")
            
            with col2:
                sgot_aspartate_aminotransferase = st.number_input("SGOT (Aspartate Aminotransferase) (U/L)", min_value=0.0, step=1.0, format="%.1f")
                total_protein = st.number_input("Total Protein (g/dL)", min_value=0.0, step=0.1, format="%.1f")
                albumin = st.number_input("Albumin (g/dL)", min_value=0.0, step=0.1, format="%.1f")
            
            if total_protein > 0 and albumin > 0 and total_protein > albumin:
                globulin = total_protein - albumin
                if globulin > 0:
                    ag_ratio = albumin / globulin
                    st.info(f"📊 **Calculated A/G Ratio**: {ag_ratio:.2f}")
            
            submitted = st.form_submit_button("Save Assessment", use_container_width=True, type="primary")
            
            if submitted:
                form_data = {
                    "total_bilirubin": total_bilirubin, "direct_bilirubin": direct_bilirubin,
                    "alkaline_phosphatase": alkaline_phosphatase, "sgpt_alamine_aminotransferase": sgpt_alamine_aminotransferase,
                    "sgot_aspartate_aminotransferase": sgot_aspartate_aminotransferase,
                    "total_protein": total_protein, "albumin": albumin
                }
                with st.spinner("Saving assessment..."):
                    result = api_client.add_assessment(st.session_state.new_patient_id, "liver", form_data)
                if result:
                    st.toast("✅ Liver assessment saved!", icon="🫀")
                    st.session_state.assessment_status["liver"] = True
                    st.session_state.add_user_step = 2
                    st.rerun()

    if st.session_state.add_user_step == 'heart':
        fields = [
            ("diabetes", "bool", {"label": "Patient has diabetes"}), ("hypertension", "bool", {"label": "Patient has hypertension"}),
            ("obesity", "bool", {"label": "Patient has obesity"}), ("smoking", "bool", {"label": "Patient smokes"}),
            ("alcohol_consumption", "bool", {"label": "Patient consumes alcohol"}),
            ("physical_activity", "bool", {"label": "Patient is physically active"}),
            ("family_history", "bool", {"label": "Family history of heart disease"}),
            ("heart_attack_history", "bool", {"label": "Patient has history of heart attack"}),
            ("diet_score", "number", {"min_value": 1, "max_value": 10, "step": 1, "label": "Diet Score (1-10)"}),
            ("cholesterol_level", "number", {"min_value": 0.0, "step": 1.0, "format": "%.1f", "label": "Cholesterol (mg/dL)"}),
            ("triglyceride_level", "number", {"min_value": 0.0, "step": 1.0, "format": "%.1f", "label": "Triglycerides (mg/dL)"}),
            ("ldl_level", "number", {"min_value": 0.0, "step": 1.0, "format": "%.1f", "label": "LDL (mg/dL)"}),
            ("hdl_level", "number", {"min_value": 0.0, "step": 1.0, "format": "%.1f", "label": "HDL (mg/dL)"}),
            ("systolic_bp", "number", {"min_value": 0, "step": 1, "label": "Systolic BP (mm Hg)"}),
            ("diastolic_bp", "number", {"min_value": 0, "step": 1, "label": "Diastolic BP (mm Hg)"}),
            ("air_pollution_exposure", "number", {"min_value": 0.0, "step": 0.1, "format": "%.1f", "label": "Air Pollution Exposure (Index)"}),
            ("stress_level", "number", {"min_value": 1, "max_value": 10, "step": 1, "label": "Stress Level (1-10)"}),
        ]
        render_assessment_form("Heart", fields, "heart", "❤️")

    if st.session_state.add_user_step == 'mental_health':
        st.header("Step 2: 🧠 Mental Health Assessment")
        st.button("⬅️ Back to Assessment Hub", on_click=lambda: st.session_state.update(add_user_step=2))
        
        # Define PHQ-9 Questions (Simple Indian English)
        phq_questions = [
            "Not enjoying things you usually like to do",
            "Feeling sad, low, or hopeless",
            "Problem with sleep (difficulty sleeping, waking up often, or sleeping too much)",
            "Feeling tired or having very little energy",
            "Eating too little or eating too much",
            "Feeling bad about yourself (Feeling like you are not good enough, a failure, or that you have disappointed your family)",
            "Difficulty concentrating (For example, while reading, watching TV, or doing daily work)",
            "Moving or speaking very slowly, so others notice OR feeling very restless and unable to sit still",
            "Thoughts of harming yourself or feeling that life is not worth living"
        ]
        
        # Define GAD-7 Questions (Simple Version)
        gad_questions = [
            "Feeling nervous, worried, or tense",
            "Not able to stop worrying or control your worries",
            "Worrying too much about many different things",
            "Finding it hard to relax",
            "Feeling so restless that you cannot sit quietly",
            "Getting irritated or angry very easily",
            "Feeling scared that something bad may happen"
        ]
        
        # Answer options
        answer_options = {
            0: "Not at all",
            1: "On some days",
            2: "On many days",
            3: "Almost every day"
        }
        
        with st.form("mental_health_form"):
            # PHQ-9 Section
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="margin: 0; font-size: 1.2rem;">📋 PHQ-9: Depression Screening</h4>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; opacity: 0.9;">During the last 2 weeks, how often have you had these problems?</p>
            </div>
            """, unsafe_allow_html=True)
            
            phq_responses = []
            for i, question in enumerate(phq_questions):
                st.markdown(f"**{i+1}. {question}**")
                response = st.radio(
                    f"PHQ Question {i+1}",
                    options=[0, 1, 2, 3],
                    format_func=lambda x: answer_options[x],
                    horizontal=True,
                    key=f"phq_{i}",
                    label_visibility="collapsed"
                )
                phq_responses.append(response)
                if i < len(phq_questions) - 1:
                    st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
            
            st.divider()
            
            # GAD-7 Section
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="margin: 0; font-size: 1.2rem;">📋 GAD-7: Anxiety Screening</h4>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; opacity: 0.9;">In the last 2 weeks, how often have you felt troubled by these problems?</p>
            </div>
            """, unsafe_allow_html=True)
            
            gad_responses = []
            for i, question in enumerate(gad_questions):
                st.markdown(f"**{i+1}. {question}**")
                response = st.radio(
                    f"GAD Question {i+1}",
                    options=[0, 1, 2, 3],
                    format_func=lambda x: answer_options[x],
                    horizontal=True,
                    key=f"gad_{i}",
                    label_visibility="collapsed"
                )
                gad_responses.append(response)
                if i < len(gad_questions) - 1:
                    st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
            
            st.divider()
            
            # Additional Observations Section
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="margin: 0; font-size: 1.2rem;">👁️ Additional Clinical Observations</h4>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; opacity: 0.9;">Based on your interaction with the patient, check any applicable observations:</p>
            </div>
            """, unsafe_allow_html=True)
            
            obs_col1, obs_col2 = st.columns(2)
            with obs_col1:
                depressiveness = st.checkbox("Shows signs of Depressiveness", key="obs_depressiveness")
                suicidal = st.checkbox("Shows Suicidal Tendencies", key="obs_suicidal")
            with obs_col2:
                anxiousness = st.checkbox("Shows signs of Anxiousness", key="obs_anxiousness")
                sleepiness = st.checkbox("Reports excessive Sleepiness", key="obs_sleepiness")
            
            st.divider()
            
            # Calculate and display scores
            phq_score = sum(phq_responses)
            gad_score = sum(gad_responses)
            
            score_col1, score_col2 = st.columns(2)
            with score_col1:
                phq_color = "#28a745" if phq_score < 5 else "#ffc107" if phq_score < 10 else "#fd7e14" if phq_score < 15 else "#dc3545"
                st.markdown(f"""
                <div style="background: {phq_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0;">PHQ-9 Score: {phq_score}/27</h3>
                    <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem;">{'Minimal' if phq_score < 5 else 'Mild' if phq_score < 10 else 'Moderate' if phq_score < 15 else 'Moderately Severe' if phq_score < 20 else 'Severe'} Depression</p>
                </div>
                """, unsafe_allow_html=True)
            with score_col2:
                gad_color = "#28a745" if gad_score < 5 else "#ffc107" if gad_score < 10 else "#dc3545"
                st.markdown(f"""
                <div style="background: {gad_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0;">GAD-7 Score: {gad_score}/21</h3>
                    <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem;">{'Minimal' if gad_score < 5 else 'Mild' if gad_score < 10 else 'Moderate' if gad_score < 15 else 'Severe'} Anxiety</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("💾 Save Assessment", use_container_width=True, type="primary")
            
            if submitted:
                form_data = {
                    "phq_score": phq_score,
                    "gad_score": gad_score,
                    "depressiveness": depressiveness,
                    "suicidal": suicidal,
                    "anxiousness": anxiousness,
                    "sleepiness": sleepiness
                }
                with st.spinner("Saving assessment..."):
                    result = api_client.add_assessment(st.session_state.new_patient_id, "mental_health", form_data)
                if result:
                    st.toast("✅ Mental Health assessment saved!", icon="🧠")
                    st.session_state.assessment_status["mental_health"] = True
                    st.session_state.add_user_step = 2
                    st.rerun()

# --- View: Edit Patient ---
elif st.session_state.admin_view == "edit_patient":
    st.button("⬅️ Back to Patient Directory", on_click=set_view, args=("view_patients",))
    st.title("✏️ Edit Patient Information")

    p_data = st.session_state.edit_patient_data
    if not p_data:
        st.error("No patient data loaded for editing.")
        st.stop()

    st.subheader(f"Editing: {p_data.get('name')} (ID: {p_data.get('patient_id')})")

    try: state_index = utils.INDIAN_STATES.index(p_data.get('state_name'))
    except ValueError: state_index = 0
        
    try: gender_index = ["Male", "Female", "Other"].index(p_data.get('gender'))
    except ValueError: gender_index = 0

    with st.form("edit_patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Full Name*", value=p_data.get('name'))
            abha_id = st.text_input("🆔 ABHA ID (14 digits)*", value=p_data.get('abha_id'), max_chars=14)
            age = st.number_input("🎂 Age*", value=p_data.get('age'), min_value=0, max_value=120, step=1)
            gender = st.selectbox("⚥ Gender*", ["Male", "Female", "Other"], index=gender_index)
        with col2:
            height = st.number_input("📏 Height (cm)*", value=p_data.get('height'), min_value=50.0, max_value=300.0, step=0.5, format="%.1f")
            weight = st.number_input("⚖️ Weight (kg)*", value=p_data.get('weight'), min_value=10.0, max_value=300.0, step=0.1, format="%.1f")
            state_name = st.selectbox("🗺️ State*", utils.INDIAN_STATES, index=state_index)
        
        submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
        
        if submitted:
            if len(abha_id) != 14 or not abha_id.isdigit():
                st.error("ABHA ID must be 14 digits.")
            elif not all([name, age, gender, height, weight, state_name]):
                st.error("Please fill all required fields.")
            else:
                data = {
                    "name": name, "abha_id": abha_id, "age": age, "gender": gender, 
                    "height": height, "weight": weight, "state_name": state_name
                }
                with st.spinner("Updating patient..."):
                    updated_patient = api_client.update_patient(p_data.get('patient_id'), data)
                if updated_patient:
                    st.success("Patient details updated successfully!")
                    st.session_state.edit_patient_data = None
                    set_view("view_patients")
                    st.rerun()

# --- View: View Registered Patients ---
elif st.session_state.admin_view == "view_patients":
    st.button("🏠 Back to Dashboard", on_click=set_view, args=("main",))
    
    st.title("👥 Patient Directory")
    
    # Initialize session state for filters
    st.session_state.patient_category = st.session_state.get("patient_category", "All Users")
    st.session_state.patient_sort = st.session_state.get("patient_sort", "Recently Added")
    
    # Filter and Sort Panel
    st.subheader("🔍 Filter & Sort")
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        category = st.selectbox(
            "Filter by Condition",
            ["All Users", "Diabetes", "Liver", "Heart", "Mental Health"],
            key="category_selector"
        )
        st.session_state.patient_category = category
    
    with filter_col2:
        sort_option = st.selectbox(
            "Sort by",
            ["Recently Added", "High Risk", "Medium Risk", "Low Risk"],
            key="sort_selector"
        )
        st.session_state.patient_sort = sort_option
    
    st.divider()
    
    # Get patients data
    with st.spinner("Fetching patient list..."):
        patients = api_client.get_patients(
            category=st.session_state.patient_category, 
            sort=st.session_state.patient_sort
        )
    
    if not patients:
        st.info(f"📭 No patients found for the selected filters.")
    else:
        st.markdown(f"**Found {len(patients)} patients**")
        
        # Display patients in a modern grid layout
        
        # CSS for cards
        st.markdown("""
        <style>
        .patient-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #f0f0f0;
            transition: transform 0.2s;
            height: 100%;
        }
        .patient-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        .patient-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .patient-name {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--color-primary-dark);
            margin: 0;
        }
        .patient-meta {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.5rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Grid layout for patients
        cols = st.columns(3)
        for i, p in enumerate(patients):
            with cols[i % 3]:
                with st.container():
                    # Card Start
                    st.markdown(f"""
                    <div class="patient-card">
                        <div class="patient-header">
                            <h4 class="patient-name">👤 {p.get('name', 'N/A').title()}</h4>
                        </div>
                        <div class="patient-meta">
                            <strong>ID:</strong> {p.get('patient_id')} <br>
                            <strong>ABHA:</strong> {p.get('abha_id', 'N/A')} <br>
                            <strong>Age/Sex:</strong> {p.get('age', 'N/A')} / {p.get('gender', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Live Risk Badge (if filtered)
                    if st.session_state.patient_category != "All Users":
                        category_key_map = {
                            "diabetes": "diabetes_risk_level", "liver": "liver_risk_level",
                            "heart": "heart_risk_level", "mental health": "mental_health_risk_level",
                        }
                        cat_lower = st.session_state.patient_category.lower()
                        risk_key = category_key_map.get(cat_lower, "")
                        level = p.get('latest_prediction', {}).get(risk_key, 'N/A')
                        st.markdown(utils.create_risk_badge(level), unsafe_allow_html=True)
                    
                    # Action Buttons
                    c1, c2 = st.columns(2)
                    with c1:
                        st.button(
                            "✏️ Edit",
                            key=f"edit_{p['patient_id']}",
                            on_click=go_to_edit_patient,
                            args=(p['patient_id'],),
                            use_container_width=True
                        )
                    with c2:
                         st.button(
                            "👁️ Profile",
                            key=f"view_{p['patient_id']}",
                            on_click=go_to_patient_detail,
                            args=(p['patient_id'],),
                            use_container_width=True,
                            type="primary"
                        )
                    
                    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True) # Spacer

# --- View: Patient Detail ---
elif st.session_state.admin_view == "patient_detail":
    st.button("⬅️ Back to Patient Directory", on_click=set_view, args=("view_patients",))
    patient_id = st.session_state.view_patient_id
    
    if not patient_id:
        st.error("No patient selected."); st.stop()
        
    # Get fresh data
    patient_data = api_client.get_patient_details(patient_id)
    risk_data = api_client.get_latest_prediction(patient_id)
    
    if not patient_data:
        st.error("Failed to load patient data."); st.stop()
        
    st.title(f"👤 Patient Profile: {patient_data.get('name', '').title()}")
    st.caption(f"**ABHA ID:** {patient_data.get('abha_id')} | **Age:** {patient_data.get('age')} | **Gender:** {patient_data.get('gender')}")
    
    st.divider()
    
    # Display Risk Assessment
    utils.display_risk_assessment(risk_data)
    
    st.divider()
    
    # --- Main Detail View (Tabs) ---
    tab1, tab2, tab3 = st.tabs(["🩺 Consult & Act", "📋 Patient Information", "🗂️ Assessment History"])
    
    # --- Tab 1: Consult & Act ---
    with tab1:
        st.header("🩺 Consultation & Actions")
        
        # Risk Analysis Management
        st.subheader("⚙️ Risk Analysis")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Re-run Risk Analysis", use_container_width=True, type="secondary", help="Re-runs the ML models. Use if new assessment data is added."):
                with st.spinner("🔄 Retrying ML prediction..."):
                    result = api_client.retry_prediction(patient_id)
                    if result:
                        st.success("✅ Prediction retry successful!"); st.rerun()
                    else:
                        st.error("❌ Prediction retry failed. Check if all assessments are complete.")
        with col2:
            if st.button("📄 View Latest Report (JSON)", use_container_width=True):
                if risk_data:
                    st.json(risk_data)
                else:
                    st.warning("No prediction data available.")
        
        st.divider()
        
        # Consultation Actions
        st.subheader("📅 Book Consultation")
        if not risk_data:
            st.warning("⚠️ No risk assessment found. Cannot book consultation.")
        else:
            st.markdown("Book consultations based on the patient's risk levels.")
            
            def book_and_track(disease, level):
                with st.spinner(f"Booking consultation for {disease}..."):
                    res = api_client.book_consultation(patient_id, disease, level)
                    if res:
                        consultation_data = res.get('consultation', {})
                        st.session_state.appointment_success = {
                            'disease': disease,
                            'type': 'In-Person' if level == 'High' else 'Teleconsultation',
                            'risk_level': level,
                            'patient_name': patient_data.get('name', 'N/A'),
                            'consultation_datetime': consultation_data.get('consultation_datetime', 'Within 7 days'),
                            'doctor_name': 'Dr. Assigned Specialist',
                        }
                        st.session_state.show_appointment_modal = True
                    else:
                        st.error(f"Failed to book consultation for {disease}.")

            # Categorize diseases
            high_risk = []
            medium_risk = []
            for risk_key, disease_name in [
                ("diabetes_risk_level", "Diabetes"), ("liver_risk_level", "Liver"),
                ("heart_risk_level", "Heart"), ("mental_health_risk_level", "Mental Health")
            ]:
                level = risk_data.get(risk_key)
                if level == "High": high_risk.append(disease_name)
                elif level == "Medium": medium_risk.append(disease_name)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h5>🚨 High Risk (In-Person)</h5>", unsafe_allow_html=True)
                if high_risk:
                    for disease in high_risk:
                        if st.button(f"🏥 Book for {disease}", key=f"high_{disease}", use_container_width=True, type="primary"):
                            book_and_track(disease, "High"); st.rerun()
                else:
                    st.info("No high-risk conditions found.")
            
            with col2:
                st.markdown("<h5>⚠️ Medium Risk (Teleconsult)</h5>", unsafe_allow_html=True)
                if medium_risk:
                    for disease in medium_risk:
                        if st.button(f"💻 Book for {disease}", key=f"medium_{disease}", use_container_width=True):
                            book_and_track(disease, "Medium"); st.rerun()
                else:
                    st.info("No medium-risk conditions found.")

        # Appointment Success Modal
        if st.session_state.get('show_appointment_modal'):
            st.divider()
            success_data = st.session_state.get('appointment_success', {})
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                        color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                <h3 style="margin: 0;">✅ Consultation Booked Successfully!</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_modal1, col_modal2 = st.columns(2)
            with col_modal1:
                st.markdown(f"**🏥 Consultation Type:** {success_data.get('type')}")
                st.markdown(f"**📅 Scheduled:** {success_data.get('consultation_datetime')}")
                st.markdown(f"**🩺 Disease:** {success_data.get('disease')}")
            with col_modal2:
                st.markdown(f"**👤 Patient:** {success_data.get('patient_name')}")
                st.markdown(f"**👨‍⚕️ Doctor:** {success_data.get('doctor_name')}")
                st.markdown(f"**⚠️ Risk Level:** {success_data.get('risk_level')}")
            
            if st.button("Close", key="close_modal_btn"):
                st.session_state.show_appointment_modal = False
                st.rerun()
        
        st.divider()
        
        # Notes for Doctor
        st.subheader("📝 Add Clinical Notes")
        st.markdown("Add notes, symptoms, or observations for the patient and consulting doctor.")
        
        with st.form("notes_form"):
            notes = st.text_area("Notes", height=150, placeholder="Enter symptoms, observations, etc...")
            submitted = st.form_submit_button("💾 Save Notes", use_container_width=True, type="primary")
            
            if submitted:
                if not notes.strip():
                    st.warning("Please enter some notes.")
                else:
                    with st.spinner("Saving notes..."):
                        success = api_client.add_consultation_notes(patient_id, notes)
                        if success:
                            st.success("✅ Notes saved successfully!"); st.rerun()
                        else:
                            st.error("❌ Failed to save notes.")
        
        st.markdown("<h5>📋 Previous Notes</h5>", unsafe_allow_html=True)
        existing_notes = patient_data.get('consultation_notes', [])
        if existing_notes:
            for note in reversed(existing_notes): # Show newest first
                st.markdown(f"""
                <div class="card">
                    <p style="margin:0;">{note.get('notes', 'No content')}</p>
                    <small style="color: var(--color-text-secondary);">Added: {note.get('created_at', 'Unknown')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No previous notes found for this patient.")

    # --- Tab 2: Patient Info ---
    with tab2:
        st.header("📋 Patient Information")
        p = patient_data
        st.markdown(f"""
        - **Name:** {p.get('name', 'N/A').title()}
        - **ABHA ID:** {p.get('abha_id', 'N/A')}
        - **Age:** {p.get('age', 'N/A')}
        - **Gender:** {p.get('gender', 'N/A')}
        - **Height:** {p.get('height', 'N/A')} cm
        - **Weight:** {p.get('weight', 'N/A')} kg
        - **BMI:** {p.get('bmi', 0):.2f}
        - **State:** {p.get('state_name', 'N/A')}
        """)

    # --- Tab 3: Assessment History ---
    with tab3:
        st.header("🗂️ Patient Assessment History")
        st.markdown("View all historical assessment data submitted for this patient.")
        
        with st.expander("🩺 Diabetes Assessment History", expanded=True):
            if p.get('diabetes_assessments'):
                st.dataframe(p['diabetes_assessments'], use_container_width=True)
            else:
                st.info("No diabetes assessment data found.")
                
        with st.expander("🫀 Liver Assessment History"):
            if p.get('liver_assessments'):
                st.dataframe(p['liver_assessments'], use_container_width=True)
            else:
                st.info("No liver assessment data found.")

        with st.expander("❤️ Heart Assessment History"):
            if p.get('heart_assessments'):
                st.dataframe(p['heart_assessments'], use_container_width=True)
            else:
                st.info("No heart assessment data found.")

        with st.expander("🧠 Mental Health Assessment History"):
            if p.get('mental_health_assessments'):
                st.dataframe(p['mental_health_assessments'], use_container_width=True)
            else:
                st.info("No mental health assessment data found.")