import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import joblib
import re
from pathlib import Path

# ============================================================================
# DESIGN SYSTEM TOKENS
# ============================================================================
THEME_COLORS = {
    "primary": "#e94560",         # Vibrant Healthcare Pink/Red
    "primary_hover": "#ff6b6b",
    "background": "#0a0a1a",      # Deep Space Blue
    "surface": "#1a1a2e",         # Card Navy
    "surface_glass": "rgba(26, 26, 46, 0.7)",
    "border": "rgba(233, 69, 96, 0.2)",
    "text_main": "#ffffff",
    "text_dim": "#8a8a9a",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "error": "#f44336",
    "info": "#2196F3"
}

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Disease Prediction Pipeline",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# UNIFIED THEME INJECTION
# ============================================================================
def apply_global_theme():
    st.markdown(f"""
    <style>
    /* 1. Typography & Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* 2. Global Background & Layout */
    .stApp {{
        background: radial-gradient(circle at top right, #16213e, #0a0a1a) !important;
        background-color: {THEME_COLORS['background']} !important;
    }}
    
    .main .block-container {{
        padding: 3rem 4rem !important;
        max-width: 1400px !important;
    }}

    /* 3. Headers Styling */
    h1, h2, h3, h4, h5, h6 {{
        color: {THEME_COLORS['text_main']} !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}
    
    h1 {{
        font-size: 3rem !important;
        background: linear-gradient(135deg, #ffffff 0%, {THEME_COLORS['primary']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem !important;
    }}
    
    /* 4. Glassmorphism Panels & Cards */
    [data-testid="stMetric"] {{
        background: {THEME_COLORS['surface_glass']} !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid {THEME_COLORS['border']} !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease;
    }}
    
    [data-testid="stMetric"]:hover {{
        border-color: {THEME_COLORS['primary']} !important;
        transform: translateY(-5px);
    }}

    /* 5. Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {THEME_COLORS['primary']} 0%, {THEME_COLORS['primary_hover']} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3) !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(233, 69, 96, 0.5) !important;
        border: none !important;
    }}

    /* 6. Form Inputs & Selectboxes */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {{
        background-color: rgba(10, 10, 26, 0.6) !important;
        border: 1px solid {THEME_COLORS['border']} !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.75rem 1rem !important;
    }}

    /* 7. Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%) !important;
        border-right: 1px solid {THEME_COLORS['border']} !important;
    }}
    
    /* Sidebar Radio Styling */
    [data-testid="stSidebar"] .stRadio > div {{
        gap: 0.75rem;
    }}
    
    [data-testid="stSidebar"] .stRadio label {{
        color: {THEME_COLORS['text_dim']};
    }}

    /* 8. Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1.5rem !important;
        background: transparent !important;
        border-bottom: 2px solid {THEME_COLORS['border']} !important;
        margin-bottom: 2rem !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {THEME_COLORS['primary']} !important;
        border-bottom: 2px solid {THEME_COLORS['primary']} !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: #0a0a1a;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #1a1a2e;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {THEME_COLORS['primary']};
    }}

    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    </style>
    """, unsafe_allow_html=True)

apply_global_theme()

# ============================================================================
# CONSTANTS
# ============================================================================
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
SCRIPTS_DIR = BASE_DIR / "scripts"

DISEASES = {
    "Diabetes": {
        "key": "diabetes",
        "raw_file": "Diabetes.csv",
        "processed_file": "Diabetes_Processed.csv",
        "target": "Has_Diabetes",
        "icon": "🩺",
        "color": "#4CAF50"
    },
    "Heart": {
        "key": "heart",
        "raw_file": "Heart.csv",
        "processed_file": "Heart_Processed.csv",
        "target": "Has_Heart_Disease",
        "icon": "❤️",
        "color": "#E91E63"
    },
    "Liver": {
        "key": "liver",
        "raw_file": "Liver.csv",
        "processed_file": "Liver_Processed.csv",
        "target": "Has_Liver_Disease",
        "icon": "🫁",
        "color": "#FF9800"
    }
}

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================
@st.cache_data
def load_raw_data(disease_key):
    config = DISEASES.get(disease_key)
    if not config: return None
    path = DATA_DIR / "raw" / config["raw_file"]
    return pd.read_csv(path) if path.exists() else None

@st.cache_data
def load_processed_data(disease_key):
    config = DISEASES.get(disease_key)
    if not config: return None
    path = DATA_DIR / "processed" / config["processed_file"]
    return pd.read_csv(path) if path.exists() else None

@st.cache_data
def load_contract(disease_key):
    contract_path = RESULTS_DIR / "training" / "contracts" / f"{disease_key.lower()}_contract.json"
    if contract_path.exists():
        with open(contract_path, 'r') as f:
            return json.load(f)
    return None

@st.cache_data
def load_training_results_raw(disease_key):
    """Load raw training results text file."""
    results_path = RESULTS_DIR / "training" / f"{disease_key.lower()}_results.txt"
    if results_path.exists():
        with open(results_path, 'r') as f:
            return f.read()
    return None

def get_training_plots(disease_key):
    """Get all training plots for a disease."""
    plots_dir = RESULTS_DIR / "training" / "plots"
    if plots_dir.exists():
        return [f for f in plots_dir.iterdir() if disease_key.lower() in f.name.lower()]
    return []

# ============================================================================
# NEW: PARSE TRAINING RESULTS FOR ALL MODELS
# ============================================================================
@st.cache_data
def parse_training_results(disease_key):
    """
    Parse the detailed results txt file to extract all model metrics.
    Returns structured data for configuration, best model, and all models.
    """
    content = load_training_results_raw(disease_key)
    if not content:
        return None
    
    result = {
        "config": {},
        "best_model": None,
        "models": {}
    }
    
    # Parse configuration section
    config_match = re.search(r"CONFIGURATION\n-+\n(.*?)(?=\n=)", content, re.DOTALL)
    if config_match:
        for line in config_match.group(1).strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                result["config"][key.strip()] = val.strip()
    
    # Parse best model line
    best_match = re.search(r"BEST MODEL: (.+?) \(Test F1-Score: ([\d.]+)\)", content)
    if best_match:
        result["best_model"] = {
            "name": best_match.group(1).strip(),
            "f1_score": float(best_match.group(2))
        }
    
    # Parse each model section
    # Split content by MODEL: headers
    model_pattern = r"={50,}\nMODEL: (.+?)\n={50,}\n(.*?)(?=\n={50,}\nMODEL:|\n={50,}\nEND OF REPORT|$)"
    model_sections = re.findall(model_pattern, content, re.DOTALL)
    
    for model_name, section in model_sections:
        model_data = {
            "name": model_name.strip(),
            "hyperparameters": {},
            "validation_metrics": {},
            "test_metrics": {},
            "plots": {}
        }
        
        # Parse hyperparameters
        hyper_match = re.search(r"Hyperparameters:\n-+\n(.*?)(?=\n\n|\nValidation)", section, re.DOTALL)
        if hyper_match:
            for line in hyper_match.group(1).strip().split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    model_data["hyperparameters"][key.strip()] = val.strip()
        
        # Parse validation performance
        val_match = re.search(r"Validation Performance:\n-+\n(.*?)(?=\n\n|\nTest Performance)", section, re.DOTALL)
        if val_match:
            for line in val_match.group(1).strip().split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    try:
                        model_data["validation_metrics"][key.strip()] = float(val.strip())
                    except ValueError:
                        model_data["validation_metrics"][key.strip()] = val.strip()
        
        # Parse test performance
        test_match = re.search(r"Test Performance:\n-+\n(.*?)(?=\n\n|\nGenerated Plots|$)", section, re.DOTALL)
        if test_match:
            for line in test_match.group(1).strip().split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    try:
                        model_data["test_metrics"][key.strip()] = float(val.strip())
                    except ValueError:
                        model_data["test_metrics"][key.strip()] = val.strip()
        
        # Parse generated plots
        plots_match = re.search(r"Generated Plots:\n-+\n(.*?)(?=\n\n|$)", section, re.DOTALL)
        if plots_match:
            for line in plots_match.group(1).strip().split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    model_data["plots"][key.strip()] = val.strip()
        
        result["models"][model_name.strip()] = model_data
    
    return result

# ============================================================================
# NEW: GET EDA ARTIFACTS
# ============================================================================
@st.cache_data
def get_eda_artifacts(disease_key):
    """
    Get all EDA outputs for a disease including plots and summary.
    """
    eda_dir = RESULTS_DIR / "eda" / disease_key.lower()
    if not eda_dir.exists():
        return None
    
    artifacts = {
        "plots": {},
        "summary": None
    }
    
    # Get all plot files with their types
    plot_files = list(eda_dir.glob("*.png"))
    for pf in plot_files:
        # Categorize by name
        if "correlation" in pf.name.lower():
            artifacts["plots"]["correlation_heatmap"] = pf
        elif "distribution" in pf.name.lower():
            artifacts["plots"]["distribution"] = pf
        elif "boxplot" in pf.name.lower():
            artifacts["plots"]["boxplots"] = pf
        else:
            artifacts["plots"][pf.stem] = pf
    
    # Get summary
    summary_path = eda_dir / "summary.txt"
    if summary_path.exists():
        with open(summary_path, 'r') as f:
            artifacts["summary"] = f.read()
    
    return artifacts

# ============================================================================
# NEW: CALCULATE ACTUAL DATA QUALITY
# ============================================================================
def calculate_data_quality(df):
    """
    Calculate actual data quality metrics from a DataFrame.
    Returns dictionary with quality metrics.
    """
    if df is None:
        return None
    
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    missing_pct = (missing_cells / total_cells) * 100 if total_cells > 0 else 0
    
    duplicate_rows = df.duplicated().sum()
    duplicate_pct = (duplicate_rows / len(df)) * 100 if len(df) > 0 else 0
    
    # Quality score: 100% minus penalties
    quality_score = 100 - missing_pct - (duplicate_pct * 0.5)
    quality_score = max(0, min(100, quality_score))
    
    return {
        "total_records": len(df),
        "total_features": len(df.columns),
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": duplicate_pct,
        "completeness": 100 - missing_pct,
        "quality_score": quality_score
    }

# ============================================================================
# NEW: LOAD MODEL FOR INFERENCE
# ============================================================================
@st.cache_resource
def load_model_for_inference(disease_key):
    """
    Load the trained model pickle file for real inference.
    """
    model_path = RESULTS_DIR / "training" / "models" / f"{disease_key.lower()}_best_model.pkl"
    if model_path.exists():
        try:
            return joblib.load(model_path)
        except Exception as e:
            st.error(f"Failed to load model: {e}")
            return None
    return None

def run_inference(model, contract, input_data):
    """
    Run actual model inference with real predictions.
    """
    if model is None or contract is None:
        return None
    
    try:
        # Get features in correct order
        features = contract.get("input_features", [])
        threshold = contract.get("optimal_threshold", 0.5)
        
        # Prepare input DataFrame
        X = pd.DataFrame([input_data])[features]
        
        # Get prediction probability
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)[0][1]
        else:
            # Fallback for models without predict_proba
            proba = float(model.predict(X)[0])
        
        # Apply threshold
        prediction = 1 if proba >= threshold else 0
        
        return {
            "probability": proba,
            "prediction": prediction,
            "risk_level": "HIGH" if prediction == 1 else "LOW",
            "threshold": threshold,
            "confidence": abs(proba - 0.5) * 2  # 0-1 scale, higher = more confident
        }
    except Exception as e:
        st.error(f"Inference error: {e}")
        return None

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 3rem 0;">
        <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem;">🏥 Disease Prediction System</h1>
        <p style="color: #8a8a9a; font-size: 1.15rem;">End-to-End Machine Learning Pipeline Visualization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🧬</div>
        <h2 style="font-size: 1.5rem; letter-spacing: 2px;">ML PIPELINE</h2>
        <p style="color: #e94560; font-size: 0.8rem; font-weight: 600;">STATUS: PRODUCTION READY</p>
    </div>
    <hr style="margin: 0 0 2rem 0; opacity: 0.2;">
    """, unsafe_allow_html=True)
    
    disease = st.sidebar.radio(
        "Select Disease Track",
        list(DISEASES.keys()),
        format_func=lambda x: f"{DISEASES[x]['icon']}  {x} Disease"
    )
    
    config = DISEASES[disease]
    contract = load_contract(config["key"])
    training_results = parse_training_results(config["key"])
    eda_artifacts = get_eda_artifacts(config["key"])
    
    # Disease Info Card in Sidebar
    st.sidebar.markdown(f"""
    <div style="background: rgba(233, 69, 96, 0.1); border: 1px solid rgba(233, 69, 96, 0.3); border-radius: 16px; padding: 1.5rem; margin-top: 2rem;">
        <h3 style="margin:0; font-size: 1.1rem; color: #ffffff;">{config['icon']} {disease} Analysis</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #8a8a9a; line-height: 1.5;">
            Visualizing the architecture, data flow, and predictive reliability for {disease.lower()} diagnosis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Overview",
        "📊 Data Insights",
        "🤖 Model Performance",
        "🔮 Inference Demo"
    ])
    
    # ========================================================================
    # TAB 1: OVERVIEW
    # ========================================================================
    with tab1:
        st.header(f"{config['icon']} {disease} Pipeline Overview")
        
        # Display training configuration from actual results
        if training_results and training_results.get("config"):
            cfg = training_results["config"]
            
            st.markdown("""
            This pipeline visualizes the transformation of raw clinical data into a production-grade predictive model. 
            Select tabs above to explore the data distribution, model metrics, and real-time inference.
            """)
            
            st.markdown("### 📊 Training Configuration")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Dataset", cfg.get("Dataset", disease))
            col2.metric("Target", cfg.get("Target Column", config["target"]))
            col3.metric("Random Seed", cfg.get("Random Seed", "42"))
            col4.metric("Trained On", cfg.get("Timestamp", "N/A")[:10] if cfg.get("Timestamp") else "N/A")
            
            # Split ratios
            split_info = cfg.get("Split Ratios", "70% Train / 15% Validation / 15% Test")
            st.info(f"📈 **Data Split**: {split_info}")
            
            # Best model summary
            if training_results.get("best_model"):
                best = training_results["best_model"]
                st.success(f"🏆 **Best Model**: {best['name']} (Test F1-Score: {best['f1_score']:.4f})")
        else:
            st.markdown(f"""
            This pipeline visualizes the transformation of raw clinical data into a production-grade predictive model. 
            Select tabs above to explore the data distribution, model metrics, and real-time inference.
            """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 🎯 Target Variable: `{config['target']}`")
            st.markdown(f"""
            <div style="padding: 1.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 12px; border-left: 4px solid {THEME_COLORS['primary']};">
                The objective is to binary classify patients based on their likelihood of having {disease.lower()} disease.
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("### 🛠️ Pipeline Components")
            st.markdown("- **Preprocessing**: Missing value imputation, scaling")
            st.markdown("- **Training**: Multiple model comparison")
            st.markdown("- **Evaluation**: Validation & Test metrics")
            st.markdown("- **Artifacts**: Models, plots, contracts")

    # ========================================================================
    # TAB 2: DATA INSIGHTS
    # ========================================================================
    with tab2:
        df_raw = load_raw_data(config["key"])
        df_proc = load_processed_data(config["key"])
        
        if df_raw is not None:
            st.subheader("📁 Raw Clinical Data")
            st.dataframe(df_raw.head(10), use_container_width=True)
            
            # Calculate ACTUAL data quality
            raw_quality = calculate_data_quality(df_raw)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Records", raw_quality["total_records"])
            c2.metric("Features", raw_quality["total_features"] - 1)  # Exclude target
            c3.metric("Missing Values", raw_quality["missing_cells"])
            c4.metric("Data Completeness", f"{raw_quality['completeness']:.1f}%")
            
        if df_proc is not None:
            st.divider()
            st.subheader("🔄 Preprocessed Feature Matrix")
            st.dataframe(df_proc.head(10), use_container_width=True)
            
            proc_quality = calculate_data_quality(df_proc)
            c1, c2, c3 = st.columns(3)
            c1.metric("Processed Records", proc_quality["total_records"])
            c2.metric("Features", proc_quality["total_features"] - 1)
            c3.metric("Quality Score", f"{proc_quality['quality_score']:.1f}%")
        
        # EDA Visualizations
        if eda_artifacts:
            st.divider()
            st.subheader("📈 Exploratory Data Analysis")
            
            # Display EDA plots
            if eda_artifacts.get("plots"):
                plots = eda_artifacts["plots"]
                
                # Show distribution plots
                if "distribution" in plots:
                    st.markdown("#### Distribution Plots")
                    st.image(str(plots["distribution"]), use_container_width=True)
                
                # Show correlation heatmap
                if "correlation_heatmap" in plots:
                    st.markdown("#### Correlation Heatmap")
                    st.image(str(plots["correlation_heatmap"]), use_container_width=True)
                
                # Show boxplots if available
                if "boxplots" in plots:
                    st.markdown("#### Feature Boxplots")
                    st.image(str(plots["boxplots"]), use_container_width=True)
            
            # Show EDA summary in expander
            if eda_artifacts.get("summary"):
                with st.expander("📄 View EDA Summary Statistics"):
                    st.code(eda_artifacts["summary"], language="text")

    # ========================================================================
    # TAB 3: MODEL PERFORMANCE
    # ========================================================================
    with tab3:
        if training_results and training_results.get("models"):
            models_data = training_results["models"]
            best_model_info = training_results.get("best_model")
            
            # Header with best model
            if best_model_info:
                st.subheader(f"🏆 Best Model: {best_model_info['name']}")
                st.markdown(f"Selected based on highest Test F1-Score: **{best_model_info['f1_score']:.4f}**")
            
            st.divider()
            
            # All Models Comparison Table
            st.subheader("📊 All Models Comparison")
            
            # Build comparison dataframe
            comparison_data = []
            for model_name, model_info in models_data.items():
                test_metrics = model_info.get("test_metrics", {})
                row = {
                    "Model": model_name,
                    "Accuracy": test_metrics.get("Accuracy", "-"),
                    "Precision": test_metrics.get("Precision", "-"),
                    "Recall": test_metrics.get("Recall", "-"),
                    "F1-Score": test_metrics.get("F1-Score", "-"),
                    "AUC-ROC": test_metrics.get("AUC-ROC", "-")
                }
                # Add additional metrics for liver (if present)
                if "Specificity" in test_metrics:
                    row["Specificity"] = test_metrics.get("Specificity", "-")
                if "Sensitivity" in test_metrics:
                    row["Sensitivity"] = test_metrics.get("Sensitivity", "-")
                comparison_data.append(row)
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Highlight best model
            def highlight_best(row):
                if best_model_info and row["Model"] == best_model_info["name"]:
                    return ['background-color: rgba(76, 175, 80, 0.3)'] * len(row)
                return [''] * len(row)
            
            st.dataframe(
                comparison_df.style.apply(highlight_best, axis=1).format({
                    col: "{:.4f}" for col in comparison_df.columns if col != "Model" and comparison_df[col].dtype == float
                }),
                use_container_width=True
            )
            
            st.divider()
            
            # Detailed view per model
            st.subheader("📋 Detailed Model Results")
            
            model_names = list(models_data.keys())
            selected_model = st.selectbox("Select Model to View Details", model_names)
            
            if selected_model:
                model_info = models_data[selected_model]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Validation Performance")
                    val_metrics = model_info.get("validation_metrics", {})
                    for metric, value in val_metrics.items():
                        if isinstance(value, float):
                            st.metric(metric, f"{value:.4f}")
                        else:
                            st.metric(metric, value)
                
                with col2:
                    st.markdown("##### Test Performance")
                    test_metrics = model_info.get("test_metrics", {})
                    for metric, value in test_metrics.items():
                        if isinstance(value, float):
                            st.metric(metric, f"{value:.4f}")
                        else:
                            st.metric(metric, value)
                
                # Hyperparameters
                with st.expander("🔧 View Hyperparameters"):
                    hyperparams = model_info.get("hyperparameters", {})
                    if hyperparams:
                        hp_df = pd.DataFrame(list(hyperparams.items()), columns=["Parameter", "Value"])
                        st.dataframe(hp_df, use_container_width=True)
                    else:
                        st.info("No hyperparameters recorded.")
                
                # Plots for selected model
                st.markdown("##### Model Visualizations")
                plots_info = model_info.get("plots", {})
                plots_dir = RESULTS_DIR / "training" / "plots"
                
                plot_col1, plot_col2 = st.columns(2)
                
                with plot_col1:
                    if "confusion_matrix" in plots_info:
                        cm_path = plots_dir / plots_info["confusion_matrix"]
                        if cm_path.exists():
                            st.image(str(cm_path), caption="Confusion Matrix", use_container_width=True)
                
                with plot_col2:
                    if "roc_curve" in plots_info:
                        roc_path = plots_dir / plots_info["roc_curve"]
                        if roc_path.exists():
                            st.image(str(roc_path), caption="ROC Curve", use_container_width=True)
        
        elif contract:
            # Fallback to contract if results parsing failed
            st.subheader(f"Model Summary: {contract['model_name']}")
            
            metrics = contract.get('metrics', {})
            cols = st.columns(len(metrics))
            for i, (key, val) in enumerate(metrics.items()):
                cols[i].metric(key, f"{val:.2%}" if isinstance(val, float) and val <= 1 else f"{val}")
            
            # Plots from training
            plots = get_training_plots(config["key"])
            if plots:
                st.markdown("---")
                st.subheader("Model Visualizations")
                for plot in plots:
                    st.image(str(plot), caption=plot.name, use_container_width=True)
        else:
            st.warning("No training results available for this disease track.")

    # ========================================================================
    # TAB 4: INFERENCE DEMO
    # ========================================================================
    with tab4:
        st.header("🔮 Real-Time Inference")
        
        if contract:
            # Load actual model
            model = load_model_for_inference(config["key"])
            
            if model is not None:
                st.success(f"✅ Loaded **{contract['model_name']}** model for {disease} prediction.")
                
                # Display threshold info
                threshold = contract.get("optimal_threshold", 0.5)
                st.info(f"📊 **Decision Threshold**: {threshold:.4f}")
                
                st.markdown("---")
                st.markdown("### Enter Patient Data")
                
                with st.form("inference_form"):
                    inputs = {}
                    features = contract.get('input_features', [])
                    
                    # Create input fields in columns
                    num_cols = 3
                    cols = st.columns(num_cols)
                    
                    for i, feature in enumerate(features):
                        with cols[i % num_cols]:
                            inputs[feature] = st.number_input(
                                feature,
                                value=0.0,
                                format="%.4f",
                                help=f"Enter value for {feature}"
                            )
                    
                    submitted = st.form_submit_button("🔍 Run Prediction", type="primary", use_container_width=True)
                    
                    if submitted:
                        # Run REAL inference
                        result = run_inference(model, contract, inputs)
                        
                        if result:
                            st.markdown("---")
                            st.markdown("### 📋 Prediction Results")
                            
                            # Display results
                            res_col1, res_col2, res_col3 = st.columns(3)
                            
                            with res_col1:
                                st.metric("Probability", f"{result['probability']:.4f}")
                            
                            with res_col2:
                                risk_color = "🔴" if result['risk_level'] == "HIGH" else "🟢"
                                st.metric("Risk Level", f"{risk_color} {result['risk_level']}")
                            
                            with res_col3:
                                st.metric("Confidence", f"{result['confidence']:.2%}")
                            
                            # Detailed explanation
                            if result['prediction'] == 1:
                                st.error(f"""
                                **⚠️ HIGH RISK DETECTED**
                                
                                The model predicts this patient has a **high likelihood** of {disease.lower()} disease.
                                
                                - Probability: {result['probability']:.4f}
                                - Threshold: {result['threshold']:.4f}
                                - Status: Probability ≥ Threshold → Positive prediction
                                """)
                            else:
                                st.success(f"""
                                **✅ LOW RISK**
                                
                                The model predicts this patient has a **low likelihood** of {disease.lower()} disease.
                                
                                - Probability: {result['probability']:.4f}
                                - Threshold: {result['threshold']:.4f}
                                - Status: Probability < Threshold → Negative prediction
                                """)
                        else:
                            st.error("Failed to run inference. Please check the input values.")
            else:
                st.error("⚠️ Model file not found. Please ensure training has been completed.")
        else:
            st.error("No model metadata (contract) found for this disease track.")

    # Footer
    st.markdown("""
    <div style="margin-top: 5rem; text-align: center; color: #4a4a5a; font-size: 0.8rem;">
        ML Pipeline Visualization • Healthcare Intelligence Framework • 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
