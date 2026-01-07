import streamlit as st
import api_client
from utils import logout
from theme import apply_light_theme
import requests

st.set_page_config(
    page_title="HealthCare System", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🩺"
)

# Apply enhanced global theme
apply_light_theme()

def check_backend_status():
    """Check if the backend server is running."""
    try:
        response = requests.get("http://127.0.0.1:5000/api/v1/auth/me", timeout=3)
        return True
    except requests.exceptions.ConnectionError:
        return False
    except:
        return True # Assume running if connection is not refused

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "token" not in st.session_state:
    st.session_state.token = None

def handle_patient_login(abha_id):
    """Callback for patient login (password-free)."""
    data = api_client.patient_login(abha_id)
    if data:
        st.session_state.logged_in = True
        st.session_state.user_role = "patient"
        st.session_state.token = data.get("access_token")
        st.session_state.user_id = data.get("patient_id")
        st.session_state.user_name = data.get("name")
        st.rerun()

def handle_admin_login(username, password):
    """Callback for admin login."""
    data = api_client.admin_login(username, password)
    if data:
        st.session_state.logged_in = True
        st.session_state.user_role = "admin"
        st.session_state.token = data.get("access_token")
        st.session_state.user_id = data.get("admin_id")
        st.session_state.user_name = data.get("name")
        st.rerun()

# --- Main Content Area ---
if st.session_state.logged_in:
    # This section is shown briefly before redirect
    # We use the main app.py for login/logout logic
    
    st.success(f"Welcome back, {st.session_state.user_name}! Redirecting to your dashboard...")
    
    if st.session_state.user_role == "admin":
        st.switch_page("pages/2_Admin_Dashboard.py")
    else:
        st.switch_page("pages/1_Patient_Dashboard.py")

else:
    # --- Main Login Interface ---
    
    # Center the login form for a professional look
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
            <h1 style="color: var(--color-primary); margin-bottom: 0.5rem; font-size: 2.5rem;">🩺 HealthCare System</h1>
            <p style="color: var(--color-text-secondary); font-size: 1.1rem; margin-bottom: 0.25rem;">
                Early Disease Detection & Prevention for Rural Healthcare
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Backend status check
        if not check_backend_status():
            st.error("⚠️ **Backend Server Offline:** Cannot connect to the server at `http://127.0.0.1:5000`. Please ensure the backend is running.")
            if st.button("🔄 Retry Connection"):
                st.rerun()
            with st.expander("How to start the backend server"):
                st.code("python medml-backend/run.py", language="bash")
            st.stop()
        else:
            st.success("🟢 Backend server connection established.")
        
        st.divider()

        # Initialize login type in session state
        if "login_type" not in st.session_state:
            st.session_state.login_type = "admin"
        
        # Login type selector
        login_type = st.radio(
            "Select Login Type",
            ["admin", "patient"],
            format_func=lambda x: "👨‍⚕️ Healthcare Worker" if x == "admin" else "👤 Patient",
            horizontal=True,
            label_visibility="collapsed",
            key="login_type_selector"
        )
        st.session_state.login_type = login_type
        
        st.markdown("---") # Visual separator
        
        # --- Admin Login Form ---
        if st.session_state.login_type == "admin":
            st.subheader("👨‍⚕️ Healthcare Worker Login")
            
            with st.form("admin_login_form"):
                username = st.text_input("Username or Email", placeholder="Enter your username or email", key="admin_username")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="admin_password")
                
                submitted = st.form_submit_button("Login as Admin", use_container_width=True, type="primary")
                
                if submitted:
                    if not username or not password:
                        st.error("Username and Password are required.")
                    else:
                        with st.spinner("Logging in..."):
                            handle_admin_login(username, password)
            
            with st.expander("Test Credentials (Admin)"):
                st.code("Username: admin\nPassword: Admin123!", language="text")
        
        # --- Patient Login Form ---
        else:
            st.subheader("👤 Patient Login")
            
            with st.form("patient_login_form"):
                abha_id = st.text_input("ABHA ID", placeholder="Enter your ABHA ID", key="patient_abha")
                
                submitted = st.form_submit_button("Login as Patient", use_container_width=True, type="primary")
                
                if submitted:
                    if not abha_id or not abha_id.strip():
                        st.error("Please enter your ABHA ID.")
                    else:
                        with st.spinner("Logging in..."):
                            handle_patient_login(abha_id.strip())

            with st.expander("Patient Information"):
                st.info("Patients must be registered by a healthcare worker. Use your ABHA ID to log in.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: var(--color-text-secondary); margin-top: 2rem;'>
        <p style="font-size: 0.9rem;">Healthcare Management System</p>
    </div>
    """, unsafe_allow_html=True)