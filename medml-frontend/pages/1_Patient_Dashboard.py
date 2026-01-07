
import streamlit as st
import api_client
import utils
import pandas as pd
import time
from datetime import datetime, timedelta
from theme import apply_light_theme, create_navbar, create_metric_card

st.set_page_config(
    page_title="Patient Dashboard", 
    layout="wide",
    page_icon="👤"
)

# --- Custom CSS for Glassmorphism & Modern UI ---
st.markdown("""
<style>
    /* Global Background & Font */
    .stApp {
        background-color: #f0f2f6; 
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphic Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.2s ease-in-out;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.1);
    }

    /* Typography */
    h1, h2, h3 {
        color: #1a1a1a;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    p, span, div {
        color: #4a4a4a;
    }

    /* Metrics in Glass Card */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(45deg, #2563eb, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        font-weight: 600;
    }

    /* Gradient Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
    }

    /* Status Badges */
    .badge {
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-high { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .badge-medium { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-low { background-color: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }

    /* Actionable Tips Card */
    .tip-card {
        background: white;
        border-left: 4px solid #2563eb;
        padding: 16px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

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

# --- Step 1: Immediate Profile Display ---
# Fetch ONLY patient profile first (fast)
patient_data = api_client.get_patient_details(patient_id)

if not patient_data:
    st.error("❌ Could not load patient profile. Please try again later.")
    if st.button("Retry Loading"):
        st.rerun()
    st.stop()

# --- Header Section ---
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.markdown(f"### Welcome back, {user_name}! 👋")
    st.markdown(f"**Patient ID:** `{patient_data.get('patient_id', 'N/A')}` | **ABHA ID:** `{patient_data.get('abha_id', 'N/A')}`")
    
with col_header_2:
    if st.button("🔄 Refresh Analysis", use_container_width=True):
        st.rerun()

st.divider()

# --- Section 1: Glassmorphic Profile Metrics ---
st.markdown("##### 👤 Vital Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">Age</div>
        <div class="metric-value">{patient_data.get('age', 'N/A')}</div>
        <div style="font-size: 0.9rem; color: #64748b;">Years Old</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">Height</div>
        <div class="metric-value">{patient_data.get('height', 0)}</div>
        <div style="font-size: 0.9rem; color: #64748b;">Centimeters</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">Weight</div>
        <div class="metric-value">{(patient_data.get('weight') or 0):.1f}</div>
        <div style="font-size: 0.9rem; color: #64748b;">Kilograms</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    bmi_value = patient_data.get('bmi') or 0
    bmi_color = "#ef4444" if bmi_value > 30 else "#f59e0b" if bmi_value > 25 else "#10b981"
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">BMI Score</div>
        <div class="metric-value" style="-webkit-text-fill-color: {bmi_color} !important;">{bmi_value:.1f}</div>
        <div style="font-size: 0.9rem; color: #64748b;">index</div>
    </div>
    """, unsafe_allow_html=True)

# --- Step 2: AI Processing Phase & Results ---

# We check if we already have risk data in session state to avoid re-running on every interaction
# For this "Phase" feeling, we'll force a short realistic delay if it's a fresh load or refresh

risk_data = None
recommendations = None

with st.container():
    st.markdown("##### 🤖 Health Intelligence")
    
    # Placeholder for AI status
    ai_status = st.empty()
    progress_bar = st.empty()
    
    # Simulate or Fetch Data
    with st.spinner(""):
        ai_status.info("🚀 Authenticating health records...")
        progress_bar.progress(10)
        time.sleep(0.5) 
        
        ai_status.info("🧠 Analyzing risk map with MedML models...")
        progress_bar.progress(40)
        
        # Real Fetch 1: Prediction
        risk_data = api_client.get_latest_prediction(patient_id)
        
        ai_status.info("⚕️ Consulting Gemini AI for personalized insights...")
        progress_bar.progress(70)
        
        # Real Fetch 2: Recommendations
        # Note: Backend handles generation if not present
        recommendations = api_client.get_recommendations(patient_id)
        
        ai_status.success("✅ Analysis Complete!")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Clear progress indicators
        ai_status.empty()
        progress_bar.empty()

# --- Section 2: Results Display ---

col_risk, col_recs = st.columns([1, 2])

with col_risk:
    st.markdown("""
    <div class="glass-card" style="height: 100%;">
        <h3 style="margin-top:0;">Risk Assessment</h3>
        <p style="font-size: 0.9rem; margin-bottom: 20px;">AI-driven risk analysis based on your data.</p>
    """, unsafe_allow_html=True)
    
    if risk_data:
        risks = [
            ("Diabetes", risk_data.get("diabetes_risk_level", "N/A")),
            ("Liver", risk_data.get("liver_risk_level", "N/A")),
            ("Heart", risk_data.get("heart_risk_level", "N/A")),
            ("Mental Health", risk_data.get("mental_health_risk_level", "N/A")),
        ]
        
        for name, level in risks:
            badge_class = "badge-high" if level == "High" else "badge-medium" if level == "Medium" else "badge-low" if level == "Low" else "badge"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #eee;">
                <span style="font-weight:600;">{name}</span>
                <span class="badge {badge_class}">{level}</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Add timestamp
        pred_date = risk_data.get('created_at', 'Just now')
        if 'T' in pred_date: pred_date = pred_date.split('T')[0]
        st.markdown(f"<p style='font-size: 0.8rem; color: #999; margin-top: 15px; text-align: right;'>Last analysis: {pred_date}</p>", unsafe_allow_html=True)
        
    else:
        st.info("No risk profile found. Please contact your healthcare worker for an assessment.")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_recs:
    st.markdown("""
    <div class="glass-card" style="min-height: 100%;">
        <h3 style="margin-top:0;">💡 Your Personalized Health Tips</h3>
    """, unsafe_allow_html=True)
    
    if recommendations and any(recommendations.values()):
        # Determine language for display message
        patient_state = patient_data.get('state_name', 'India')
        # Simple mapping for UI message
        lang_display = "English"
        if patient_state == "Karnataka": lang_display = "Kannada"
        elif patient_state in ["Uttar Pradesh", "Bihar", "Madhya Pradesh", "Rajasthan", "Delhi", "Haryana"]: lang_display = "Hindi"
        elif patient_state == "Maharashtra": lang_display = "English"
        
        st.markdown(f"""
        <div style="background: #eff6ff; border-left: 4px solid #1d4ed8; padding: 12px; border-radius: 4px; margin-bottom: 20px;">
            <p style="margin:0; font-size: 0.95rem; color: #1e3a8a;">
                📢 <strong>Localized for you:</strong> Analyzing your data for {patient_state}. Insights below are in <strong>{lang_display}</strong> (or regional language).
            </p>
        </div>
        """, unsafe_allow_html=True)

        categories = ["diet", "exercise", "sleep", "lifestyle"]
        
        rec_cols = st.columns(2)
        
        # Flatten and distribute for grid layout
        all_recs = []
        for cat in categories:
            for item in recommendations.get(cat, []):
                item['category_label'] = cat.title()
                all_recs.append(item)
                
        # Limit to top 6 to prevent overcrowding, or show all if reasonable
        for idx, rec in enumerate(all_recs):
            with rec_cols[idx % 2]:
                text = rec.get('recommendation_text', '')
                cat = rec.get('category_label', 'Health')
                disease = rec.get('disease_type', 'General')
                risk = rec.get('risk_level', 'Medium')
                
                # Dynamic border color based on category
                cat_color = "#10b981" if cat == "Diet" else "#3b82f6" if cat == "Exercise" else "#8b5cf6"
                
                st.markdown(f"""
                <div class="tip-card" style="border-left: 4px solid {cat_color};">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #999; display: flex; justify-content: space-between;">
                        <span>{cat}</span>
                        <span>{disease} • {risk} Risk</span>
                    </div>
                    <div style="font-weight: 600; font-size: 1.05rem; color: #333; margin-top: 6px;">
                        {text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                

        if not all_recs:
             st.info("Your health looks good! Maintain your current lifestyle.")
             
    else:
        # Debugging/Traceability for "Tips not showing"
        with st.container():
            st.info("✨ Tips are being generated by our AI. They will appear here shortly.")
            
            # --- DEBUG INFO (Hidden unless expanded) ---
            with st.expander("🛠️ Debug Info (Why aren't tips showing?)"):
                st.write(f"**Patient ID:** `{patient_id}`")
                st.write("**Recommendations Data:**")
                st.json(recommendations if recommendations is not None else "None (API returned None)")
                
                if recommendations == {}:
                    st.warning("API returned an empty dictionary `{}`, which means the model didn't generate specific tips or failed silently.")
                elif recommendations is None:
                    st.error("API call returned `None`. This usually indicates a connection error or 500 server error.")
                    
                if st.button("🔄 Force Retry Recommendations"):
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# --- Section 3: PDF Generation (Preserved functionality, updated UI) ---
st.subheader("📥 Reports & Documents")
col_pdf_1, col_pdf_2 = st.columns([3, 1])

with col_pdf_1:
    st.info("Generate a detailed PDF report containing your profile, risk analysis, and these personalized recommendations in your language.")

with col_pdf_2:
    if st.button("📄 Generate Full Report", type="primary", use_container_width=True):
        with st.spinner("Compiling PDF..."):
            all_sections = ["Overview", "Diabetes", "Liver", "Heart", "Mental Health"]
            pdf_content = api_client.get_pdf_report(patient_id, all_sections)
            
            if pdf_content:
                st.session_state['pdf_report'] = pdf_content
                st.toast("✅ PDF Report Generated!", icon="📄")
            else:
                st.error("Failed to generate PDF.")

    if 'pdf_report' in st.session_state:
        st.download_button(
            label="⬇️ Download PDF",
            data=st.session_state['pdf_report'],
            file_name=f"Health_Report_{patient_data.get('abha_id', 'patient')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.divider()

# --- Section 4: Upcoming Appointments (Card Style) ---
st.subheader("📅 Upcoming Consultations")

consultations = api_client.get_patient_consultations(patient_id)

if consultations:
    cols = st.columns(3)
    for idx, consult in enumerate(consultations):
        with cols[idx % 3]:
            # Parsing date for better display
            date_str = consult.get('consultation_datetime', 'TBD')
            status = consult.get('status', 'Pending')
            
            status_color = "#f59e0b"  # Amber/Pending
            if status.lower() == 'confirmed': status_color = "#10b981"
            elif status.lower() == 'completed': status_color = "#3b82f6"
            elif status.lower() == 'cancelled': status_color = "#ef4444"

            st.markdown(f"""
            <div class="glass-card" style="padding: 16px; border-left: 5px solid {status_color};">
                <h4 style="margin: 0 0 8px 0; color: #333;">{consult.get('disease', 'General Checkup')}</h4>
                <p style="font-size: 0.9rem; color: #666; margin-bottom: 4px;">
                    🗓️ <strong>Date:</strong> {date_str}
                </p>
                <p style="font-size: 0.9rem; color: #666; margin-bottom: 12px;">
                    🩺 <strong>Type:</strong> {consult.get('consultation_type', 'Teleconsultation').replace('_', ' ').title()}
                </p>
                <div style="text-align: right;">
                    <span class="badge" style="background-color: {status_color}20; color: {status_color}; border: 1px solid {status_color}40;">
                        {status.title()}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No upcoming appointments scheduled.")

# --- Section 5: Medication Schedule (Dummy Data) ---
st.subheader("💊 Medication Schedule")

# Dummy Data as requested
med_data = [
    {"Medication": "Metformin", "Dosage": "500mg", "Frequency": "Twice Daily", "Time": "8:00 AM, 8:00 PM", "Status": "Active"},
    {"Medication": "Atorvastatin", "Dosage": "10mg", "Frequency": "Once Daily", "Time": "9:00 PM", "Status": "Active"},
    {"Medication": "Vitamin D3", "Dosage": "60000 IU", "Frequency": "Weekly", "Time": "Sunday Morning", "Status": "Completed"},
    {"Medication": "Paracetamol", "Dosage": "650mg", "Frequency": "SOS (As needed)", "Time": "-", "Status": "Inactive"},
]

med_df = pd.DataFrame(med_data)

# Custom styling for dataframe is limited, so we use HTML table or st.dataframe with column config
st.dataframe(
    med_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.TextColumn(
            "Status",
            help="Current status of the prescription",
            validate="^(Active|Completed|Inactive)$"
        ),
    }
)