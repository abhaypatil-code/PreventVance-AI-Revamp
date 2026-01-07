"""
Theme configuration for the Healthcare System
Light theme with blue and white color palette for trust, calm, and peace
"""

import streamlit as st

# Color Palette - Healthcare Light & Calm Theme
THEME_COLORS = {
    # Primary Colors (Trust & Brand)
    'primary': '#0067A5',         # Deep Cerulean (Pantone 301 C)
    'primary_dark': '#004F80',    # Darker shade for hover/active
    'primary_light': '#E6F0F6',   # Very light tint for backgrounds
    
    # Secondary Colors (Calm & Support)
    'secondary': '#A0D2EB',       # Light Sky Blue
    
    # Base & Text Colors (Cleanliness & Readability)
    'background': '#FFFFFF',      # Pure White (main background)
    'surface': '#F4F7F9',        # Off-white (for content sections, cards)
    'text_primary': '#253B4A',    # Dark Slate Blue (for headings)
    'text_secondary': '#5A6D7A',  # Medium Gray (for body text)
    'border': '#DDE4E9',          # Light Gray (for borders/dividers)
    
    # Accent & Status Colors (Action & Information)
    'accent': '#007BFF',          # Active Blue (for buttons/links)
    'success': '#28A745',         # Reassuring Green
    'warning': '#FFC107',         # Soft Yellow
    'error': '#DC3545',           # Clear Red
}

def apply_light_theme():
    """Apply the enhanced light theme CSS to Streamlit."""
    st.markdown(f"""
    <style>
    /* Import Google Fonts for better typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {{
        --font-family: 'Inter', sans-serif;
        
        --color-primary: {THEME_COLORS['primary']};
        --color-primary-dark: {THEME_COLORS['primary_dark']};
        --color-primary-light: {THEME_COLORS['primary_light']};
        
        --color-secondary: {THEME_COLORS['secondary']};
        
        --color-background: {THEME_COLORS['background']};
        --color-surface: {THEME_COLORS['surface']};
        --color-text-primary: {THEME_COLORS['text_primary']};
        --color-text-secondary: {THEME_COLORS['text_secondary']};
        --color-border: {THEME_COLORS['border']};
        
        --color-success: {THEME_COLORS['success']};
        --color-warning: {THEME_COLORS['warning']};
        --color-danger: {THEME_COLORS['error']};
        --color-info: {THEME_COLORS['accent']};
        
        --border-radius-sm: 0.25rem;
        --border-radius-md: 0.5rem;
        --border-radius-lg: 0.75rem;
        
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }}
    
    /* Global styles */
    .stApp {{
        background-color: var(--color-background);
        font-family: var(--font-family);
        color: var(--color-text-secondary);
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: var(--color-text-primary);
        font-weight: 600;
    }}
    
    h1 {{ font-size: 2rem; }}
    h2 {{ font-size: 1.75rem; }}
    h3 {{ font-size: 1.25rem; }}
    h4 {{ font-size: 1.1rem; }}
    
    /* Center layout and add max-width for large screens */
    .main .block-container {{
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }}
    
    /* Sticky Header */
    header[data-testid="stHeader"] {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background-color: var(--color-background);
        border-bottom: 1px solid var(--color-border);
        box-shadow: var(--shadow-sm);
    }}
    
    /* Adjust main content for sticky header */
    .main .block-container {{
        padding-top: 5rem;
    }}

    /* HIDE SIDEBAR COMPLETELY */
    [data-testid="stSidebar"] {{
        display: none;
    }}
    section[data-testid="stSidebar"] {{
        display: none;
    }}
    
    /* --- Component Styling --- */

    /* Buttons */
    .stButton > button {{
        border-radius: var(--border-radius-md);
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }}
    .stButton > button[kind="primary"] {{
        background-color: var(--color-primary);
        color: white;
        border: 1px solid var(--color-primary);
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: var(--color-primary-dark);
        border-color: var(--color-primary-dark);
    }}
    .stButton > button[kind="secondary"] {{
        background-color: var(--color-background);
        color: var(--color-text-primary);
        border: 1px solid var(--color-border);
    }}
    .stButton > button[kind="secondary"]:hover {{
        background-color: var(--color-surface);
        border-color: var(--color-secondary);
    }}
    
    /* Form Inputs */
    .stTextInput input, .stPassword input, .stNumberInput input, 
    .stTextArea textarea, .stSelectbox [data-baseweb="select"] {{
        border-radius: var(--border-radius-md);
        border: 1px solid var(--color-border);
        background-color: var(--color-background);
        color: var(--color-text-primary);
    }}
    .stTextInput input:focus, .stPassword input:focus, .stNumberInput input:focus,
    .stTextArea textarea:focus, .stSelectbox [data-baseweb="select"]:focus {{
        border-color: var(--color-primary);
        box-shadow: 0 0 0 2px var(--color-primary-light);
    }}
    
    /* Tabs */
    button[data-baseweb="tab"] {{
        font-size: 1rem;
        font-weight: 500;
        color: var(--color-text-secondary);
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--color-primary);
        border-bottom-color: var(--color-primary);
    }}
    
    /* Alerts (Info, Error, etc.) */
    .stAlert {{
        border-radius: var(--border-radius-md);
        border: none;
    }}
    .stAlert[data-baseweb="notification-success"] {{
        background-color: var(--color-success);
        color: white;
    }}
    .stAlert[data-baseweb="notification-warning"] {{
        background-color: var(--color-warning);
        color: var(--color-text-primary); /* Better contrast on yellow */
    }}
    .stAlert[data-baseweb="notification-error"] {{
        background-color: var(--color-danger);
        color: white;
    }}
    .stAlert[data-baseweb="notification-info"] {{
        background-color: var(--color-primary-light);
        color: var(--color-primary-dark);
        border: 1px solid var(--color-primary);
    }}
    
    /* Expander */
    .stExpander {{
        border-radius: var(--border-radius-md);
        border: 1px solid var(--color-border);
    }}
    .stExpander header {{
        background-color: var(--color-surface);
    }}
    
    /* Dataframe */
    .stDataFrame {{
        border-radius: var(--border-radius-lg);
        border: 1px solid var(--color-border);
    }}
    
    /* Divider */
    hr {{
        margin: 1.5rem 0;
        background: var(--color-border);
    }}

    /* --- Custom Utility Classes --- */
    
    /* Main Navigation Bar */
    .navbar {{
        width: 100%;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--color-border);
        background-color: var(--color-background);
    }}
    .navbar-brand {{
        color: var(--color-primary);
        font-size: 1.25rem;
        font-weight: 700;
        text-decoration: none;
    }}
    .navbar-nav {{
        display: flex;
        gap: 1rem;
        align-items: center;
    }}
    
    /* Card Component */
    .card {{
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-lg);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
    }}

    /* Metric Card */
    .metric-card {{
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-left: 4px solid var(--color-primary);
        border-radius: var(--border-radius-md);
        padding: 1.25rem 1.5rem;
    }}
    .metric-card.success {{ border-left-color: var(--color-success); }}
    .metric-card.warning {{ border-left-color: var(--color-warning); }}
    .metric-card.danger {{ border-left-color: var(--color-danger); }}
    
    /* Risk Badges */
    .risk-badge {{
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
        color: white;
        display: inline-block;
    }}
    .risk-high {{ background-color: var(--color-danger); }}
    .risk-medium {{ background-color: var(--color-warning); color: var(--color-text-primary); }}
    .risk-low {{ background-color: var(--color-success); }}
    .risk-na {{ background-color: var(--color-border); color: var(--color-text-secondary); }}

    /* Priority Recommendation Cards */
    .priority-card {{
        padding: 1.25rem;
        border-radius: var(--border-radius-md);
        margin: 0.75rem 0;
        border: 1px solid;
    }}
    .priority-high {{
        background-color: #fef2f2; /* Red 50 */
        border-color: #f87171; /* Red 400 */
        color: #b91c1c; /* Red 700 */
    }}
    .priority-medium {{
        background-color: #fffbeb; /* Amber 50 */
        border-color: #fbbf24; /* Amber 400 */
        color: #b45309; /* Amber 700 */
    }}
    .priority-low {{
        background-color: #f0fdf4; /* Green 50 */
        border-color: #4ade80; /* Green 400 */
        color: #15803d; /* Green 700 */
    }}
    .priority-card h5 {{
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 0.25rem 0;
        color: inherit; /* Inherit from parent card */
    }}
    .priority-card p {{
        margin: 0;
        color: var(--color-text-primary);
        font-size: 0.95rem;
    }}
    
    </style>
    """, unsafe_allow_html=True)


def create_navbar(user_name, user_role, show_logout=True):
    """Create a top navigation bar for authenticated users."""
    
    # Use standard Streamlit layout for the navbar to allow interactive buttons
    # We use a container with a custom class to style it like a navbar
    
    with st.container():
        st.markdown('<div class="navbar-spacer"></div>', unsafe_allow_html=True) # Spacer for fixed header
        
        col1, col2, col3 = st.columns([2, 4, 1.5])
        
        with col1:
            st.markdown(f"""
            <div style="font-size: 1.5rem; font-weight: 700; color: {THEME_COLORS['primary']}; display: flex; align-items: center; height: 100%;">
                🩺 HealthCare System
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            # User profile and logout
            if user_name and user_role:
                sub_c1, sub_c2 = st.columns([3, 1])
                with sub_c1:
                     st.markdown(f"""
                        <div style="text-align: right; line-height: 1.2;">
                            <span style="font-weight: 600; font-size: 0.9rem; color: {THEME_COLORS['text_primary']};">{user_name}</span><br>
                            <span style="font-size: 0.75rem; color: {THEME_COLORS['text_secondary']}; background: {THEME_COLORS['primary_light']}; padding: 2px 8px; border-radius: 10px;">{user_role.title()}</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                with sub_c2:
                    if show_logout:
                        if st.button("Logout", key="navbar_logout", type="secondary", use_container_width=True):
                            # Circular import workaround or just clear session
                            st.session_state.clear()
                            st.rerun()

        st.markdown("""<hr style="margin: 0.5rem 0 1rem 0; padding: 0;">""", unsafe_allow_html=True)

def create_metric_card(label, value, help_text=None, color="primary"):
    """Create a styled metric card."""
    color_map = {
        "primary": "primary",
        "success": "success",
        "warning": "warning",
        "error": "danger" # Map to danger class
    }
    color_class = color_map.get(color, "primary")
    
    st.markdown(f"""
    <div class="metric-card {color_class}">
        <h3 style="margin: 0; color: var(--color-text-secondary); font-size: 0.9rem; font-weight: 500; text-transform: uppercase;">{label}</h3>
        <p style="font-size: 2.25rem; font-weight: 700; margin: 0.5rem 0 0 0; color: var(--color-text-primary);">{value}</p>
        {f'<p style="font-size: 0.875rem; color: var(--color-text-secondary); margin: 0.25rem 0 0 0;">{help_text}</p>' if help_text else ""}
    </div>
    """, unsafe_allow_html=True)

def create_risk_badge(level):
    """Create a styled risk level badge."""
    level_lower = str(level).lower()
    if level_lower == "high":
        return f'<span class="risk-badge risk-high">High</span>'
    elif level_lower == "medium":
        return f'<span class="risk-badge risk-medium">Medium</span>'
    elif level_lower == "low":
        return f'<span class="risk-badge risk-low">Low</span>'
    else:
        return f'<span class="risk-badge risk-na">N/A</span>'