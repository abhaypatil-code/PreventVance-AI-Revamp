"""
Heart Disease Model Training Script
====================================
This script performs supervised learning training, evaluation, and result logging
for the Heart Disease preprocessed dataset.

Models evaluated:
- Logistic Regression
- Random Forest Classifier
- Support Vector Machine (SVM)

Author: Auto-generated
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Tuple, Dict, Any, List, Optional
import joblib
import json

# Scikit-learn imports
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    auc
)

# Visualization imports
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots

# =============================================================================
# CONFIGURATION
# =============================================================================

# Dataset configuration
DATASET_NAME = "Heart Disease"
DATASET_PATH = "../../data/processed/Heart_Processed.csv"
TARGET_COLUMN = "Has_Heart_Disease"

# Split ratios
TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15

# Reproducibility
RANDOM_STATE = 42

# Output configuration
OUTPUT_DIR = "../../results/training"
RESULTS_FILE = "heart_results.txt"
PLOTS_DIR = "../../results/training/plots"
MODELS_DIR = "../../results/training/models"
CONTRACTS_DIR = "../../results/training/contracts"


# =============================================================================
# DATA LOADING
# =============================================================================

def load_data(filepath: str, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Load the preprocessed dataset and separate features from target.
    
    Args:
        filepath: Path to the CSV file
        target_column: Name of the target column
        
    Returns:
        Tuple of (feature matrix X, target vector y)
    """
    print(f"Loading dataset from: {filepath}")
    
    # Load dataset
    df = pd.read_csv(filepath)
    print(f"Dataset loaded successfully. Shape: {df.shape}")
    
    # Validate target column exists
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset. "
                        f"Available columns: {df.columns.tolist()}")
    
    # Check for missing values
    missing_count = df.isnull().sum().sum()
    if missing_count > 0:
        print(f"WARNING: Dataset contains {missing_count} missing values")
    else:
        print("Validation passed: No missing values detected")
    
    # Separate features and target
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    return X, y


# =============================================================================
# DATA SPLITTING
# =============================================================================

def split_data(X: pd.DataFrame, y: pd.Series, 
               train_ratio: float = 0.70,
               val_ratio: float = 0.15,
               test_ratio: float = 0.15,
               random_state: int = 42) -> Tuple:
    """
    Split data into training, validation, and test sets using stratification.
    
    Uses a two-stage split:
    1. Split into train and temp
    2. Split temp into validation and test
    
    Args:
        X: Feature matrix
        y: Target vector
        train_ratio: Proportion for training set
        val_ratio: Proportion for validation set
        test_ratio: Proportion for test set
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, \
        "Split ratios must sum to 1.0"
    
    print(f"\nSplitting data with ratios: {train_ratio}/{val_ratio}/{test_ratio}")
    
    # Stage 1: Split into train and temp
    temp_ratio = val_ratio + test_ratio
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=temp_ratio,
        stratify=y,
        random_state=random_state
    )
    
    # Stage 2: Split temp into validation and test
    val_proportion = val_ratio / temp_ratio
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=0.5,  # Equal split of temp
        stratify=y_temp,
        random_state=random_state
    )
    
    print(f"Training set:   {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"Validation set: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"Test set:       {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


# =============================================================================
# MODEL DEFINITION
# =============================================================================

def get_models(random_state: int = 42) -> Dict[str, Any]:
    """
    Define the supervised learning models to evaluate.
    
    Note: Data is already preprocessed and scaled, so no StandardScaler needed.
    
    Args:
        random_state: Random seed for reproducibility
        
    Returns:
        Dictionary of model name -> model instance
    """
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            random_state=random_state,
            solver='lbfgs',
            class_weight='balanced'
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=random_state,
            n_jobs=-1,
            class_weight='balanced'
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100,
            random_state=random_state,
            max_depth=3
        ),
        "Support Vector Machine": SVC(
            kernel='rbf',
            probability=True,
            random_state=random_state,
            class_weight='balanced'
        )
    }
    return models


def get_model_hyperparameters(model_name: str) -> Dict[str, Any]:
    """
    Get hyperparameter grid for optional tuning.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary of parameter grids
    """
    param_grids = {
        "Logistic Regression": {
            'C': [0.01, 0.1, 1.0, 10.0],
            'penalty': ['l2']
        },
        "Random Forest": {
            'n_estimators': [100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        },
        "Gradient Boosting": {
            'n_estimators': [100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.05, 0.1, 0.2]
        },
        "Support Vector Machine": {
            'C': [0.1, 1.0, 10.0],
            'gamma': ['scale', 'auto']
        }
    }
    return param_grids.get(model_name, {})


# =============================================================================
# MODEL TRAINING
# =============================================================================

def train_model(model: Any, X_train: pd.DataFrame, y_train: pd.Series,
                model_name: str = "", use_grid_search: bool = False,
                random_state: int = 42) -> Any:
    """
    Train a model on the training data.
    
    Args:
        model: Sklearn model instance
        X_train: Training features
        y_train: Training labels
        model_name: Name of the model (for grid search params)
        use_grid_search: Whether to perform hyperparameter tuning
        random_state: Random seed
        
    Returns:
        Trained model
    """
    print(f"\nTraining {model_name}...")
    
    if use_grid_search and model_name:
        param_grid = get_model_hyperparameters(model_name)
        if param_grid:
            grid_search = GridSearchCV(
                model, param_grid,
                cv=5,
                scoring='f1_weighted',
                n_jobs=-1
            )
            grid_search.fit(X_train, y_train)
            print(f"Best parameters: {grid_search.best_params_}")
            return grid_search.best_estimator_
    
    model.fit(X_train, y_train)
    print(f"Training completed.")
    return model


# =============================================================================
# MODEL EVALUATION
# =============================================================================

def evaluate_model(model: Any, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
    """
    Evaluate model performance and compute metrics.
    
    Args:
        model: Trained model
        X: Feature matrix
        y: True labels
        
    Returns:
        Dictionary of metric name -> value
    """
    # Generate predictions
    y_pred = model.predict(X)
    
    # Calculate metrics
    metrics = {
        'Accuracy': accuracy_score(y, y_pred),
        'Precision': precision_score(y, y_pred, average='weighted', zero_division=0),
        'Recall': recall_score(y, y_pred, average='weighted', zero_division=0),
        'F1-Score': f1_score(y, y_pred, average='weighted', zero_division=0)
    }
    
    # Calculate AUC if model supports probability predictions
    if hasattr(model, 'predict_proba'):
        try:
            y_proba = model.predict_proba(X)[:, 1]
            metrics['AUC-ROC'] = roc_auc_score(y, y_proba)
        except Exception as e:
            print(f"Warning: Could not calculate AUC - {e}")
            metrics['AUC-ROC'] = None
    else:
        metrics['AUC-ROC'] = None
    
    return metrics


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, 
                          save_path: str,
                          dataset_name: str = "",
                          model_name: str = "") -> str:
    """
    Generate and save a confusion matrix plot with standardized format.
    
    Standardized Layout:
        X-axis (Predicted labels): No_Disease (left), Has_Disease (right)
        Y-axis (True labels): Has_Disease (top), No_Disease (bottom)
    
    Matrix Cell Positions:
        ┌─────────────┬─────────────┐
        │     FN      │     TP      │  ← True: Has_Disease (1)
        │ (top-left)  │ (top-right) │
        ├─────────────┼─────────────┤
        │     TN      │     FP      │  ← True: No_Disease (0)
        │(bottom-left)│(bottom-right)│
        └─────────────┴─────────────┘
          Pred: 0       Pred: 1
          No_Disease    Has_Disease
    
    Args:
        y_true: Array of true labels (0 = No_Disease, 1 = Has_Disease)
        y_pred: Array of predicted labels (0 = No_Disease, 1 = Has_Disease)
        save_path: Full path where the plot image will be saved
        dataset_name: Name of the dataset (for plot title)
        model_name: Name of the model (for plot title)
        
    Returns:
        The save path of the generated plot
    """
    # Step 1: Compute raw confusion matrix with labels=[0, 1]
    # This gives: [[TN, FP], [FN, TP]] where rows are true labels, cols are predicted
    cm_raw = confusion_matrix(y_true, y_pred, labels=[0, 1])
    
    # Extract individual values from raw matrix
    tn = cm_raw[0, 0]  # True=0, Pred=0
    fp = cm_raw[0, 1]  # True=0, Pred=1
    fn = cm_raw[1, 0]  # True=1, Pred=0
    tp = cm_raw[1, 1]  # True=1, Pred=1
    
    # Step 2: Create display matrix with inverted Y-axis
    # We want: Row 0 = Has_Disease (top), Row 1 = No_Disease (bottom)
    # Columns: Col 0 = No_Disease (left), Col 1 = Has_Disease (right)
    cm_display = np.array([
        [fn, tp],  # Top row: True = Has_Disease (1)
        [tn, fp]   # Bottom row: True = No_Disease (0)
    ])
    
    # Step 3: Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Step 4: Create heatmap
    im = ax.imshow(cm_display, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    
    # Step 5: Configure axis labels
    # X-axis: No_Disease (left), Has_Disease (right)
    x_labels = ['No_Disease', 'Has_Disease']
    # Y-axis: Has_Disease (top), No_Disease (bottom)
    y_labels = ['Has_Disease', 'No_Disease']
    
    ax.set_xticks(np.arange(2))
    ax.set_yticks(np.arange(2))
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('True Label')
    ax.set_title(f'Confusion Matrix\n{dataset_name} - {model_name}')
    
    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    
    # Step 6: Add text annotations
    # Annotation layout matches cm_display: [[FN, TP], [TN, FP]]
    annotations = [['FN', 'TP'], ['TN', 'FP']]
    thresh = cm_display.max() / 2.0
    
    for i in range(2):
        for j in range(2):
            cell_label = annotations[i][j]
            cell_value = cm_display[i, j]
            ax.text(j, i, f'{cell_label}\n{cell_value}',
                   ha='center', va='center',
                   color='white' if cell_value > thresh else 'black',
                   fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # Step 7: Save the plot
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  Confusion matrix saved: {os.path.basename(save_path)}")
    return save_path


def plot_roc_curve(y_true: np.ndarray, y_scores: np.ndarray,
                   save_path: str,
                   dataset_name: str = "",
                   model_name: str = "") -> str:
    """
    Generate and save a ROC curve plot.
    
    This function creates a Receiver Operating Characteristic (ROC) curve
    showing the trade-off between True Positive Rate and False Positive Rate.
    Includes the AUC value in the legend and a diagonal reference line.
    
    Args:
        y_true: Array of true binary labels (0 or 1)
        y_scores: Array of predicted probabilities for the positive class
        save_path: Full path where the plot image will be saved
        dataset_name: Name of the dataset (for plot title)
        model_name: Name of the model (for plot title)
        
    Returns:
        The save path of the generated plot
        
    Assumptions:
        - Binary classification task
        - y_scores contains probabilities for the positive class (class 1)
    """
    # Compute ROC curve and AUC
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot ROC curve
    ax.plot(fpr, tpr, color='darkorange', lw=2,
            label=f'ROC Curve (AUC = {roc_auc:.4f})')
    
    # Plot diagonal reference line (random classifier)
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
            label='Random Classifier')
    
    # Configure plot
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate (FPR)', fontsize=12)
    ax.set_ylabel('True Positive Rate (TPR)', fontsize=12)
    ax.set_title(f'ROC Curve\n{dataset_name} - {model_name}', fontsize=14)
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Ensure directory exists and save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ROC curve saved: {os.path.basename(save_path)}")
    return save_path


def generate_model_plots(model: Any, X_test: pd.DataFrame, y_test: pd.Series,
                         model_name: str, dataset_name: str,
                         plots_dir: str) -> Dict[str, str]:
    """
    Generate all visualization plots for a trained model.
    
    This function generates both confusion matrix and ROC curve plots
    for a given trained model on the test set.
    
    Args:
        model: Trained sklearn model
        X_test: Test feature matrix
        y_test: Test labels
        model_name: Name of the model
        dataset_name: Name of the dataset
        plots_dir: Directory to save plots
        
    Returns:
        Dictionary with plot types as keys and file paths as values
    """
    plots = {}
    
    # Create safe filename from model name (replace spaces with underscores)
    safe_model_name = model_name.lower().replace(' ', '_')
    safe_dataset_name = dataset_name.lower().replace(' ', '_')
    
    # Generate predictions
    y_pred = model.predict(X_test)
    
    # 1. Confusion Matrix
    cm_filename = f"{safe_dataset_name}_{safe_model_name}_confusion_matrix.png"
    cm_path = os.path.join(plots_dir, cm_filename)
    plots['confusion_matrix'] = plot_confusion_matrix(
        y_test, y_pred, cm_path, dataset_name, model_name
    )
    
    # 2. ROC Curve (if model supports probability predictions)
    if hasattr(model, 'predict_proba'):
        try:
            y_scores = model.predict_proba(X_test)[:, 1]
            roc_filename = f"{safe_dataset_name}_{safe_model_name}_roc_curve.png"
            roc_path = os.path.join(plots_dir, roc_filename)
            plots['roc_curve'] = plot_roc_curve(
                y_test, y_scores, roc_path, dataset_name, model_name
            )
        except Exception as e:
            print(f"  Warning: Could not generate ROC curve - {e}")
    elif hasattr(model, 'decision_function'):
        # Use decision function for models without predict_proba
        try:
            y_scores = model.decision_function(X_test)
            roc_filename = f"{safe_dataset_name}_{safe_model_name}_roc_curve.png"
            roc_path = os.path.join(plots_dir, roc_filename)
            plots['roc_curve'] = plot_roc_curve(
                y_test, y_scores, roc_path, dataset_name, model_name
            )
        except Exception as e:
            print(f"  Warning: Could not generate ROC curve - {e}")
    else:
        print(f"  Warning: Model does not support probability estimates for ROC curve")
    
    return plots


# =============================================================================
# MODEL ARTIFACT SAVING
# =============================================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def save_model_artifact(model: Any, model_name: str, dataset_name: str,
                       input_features: List[str], metrics: Dict[str, Any],
                       optimal_threshold: float = 0.5) -> None:
    """
    Save the trained model and associated metadata (contract).
    """
    # Ensure directories exist
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(CONTRACTS_DIR, exist_ok=True)
    
    # Create safe names
    minified_dataset_name = dataset_name.lower().replace(" ", "_").replace("_disease", "")
    safe_model_name = "best_model" # Standardize name for easier app loading
    
    # 1. Save Model (.pkl)
    model_filename = f"{minified_dataset_name}_{safe_model_name}.pkl"
    model_path = os.path.join(MODELS_DIR, model_filename)
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    
    # 2. Save Contract/Metadata (.json)
    contract = {
        "dataset_name": dataset_name,
        "model_name": model_name,
        "input_features": input_features,
        "target_column": TARGET_COLUMN,
        "optimal_threshold": optimal_threshold,
        "metrics": metrics,
        "created_at": datetime.now().isoformat()
    }
    
    contract_filename = f"{minified_dataset_name}_contract.json"
    contract_path = os.path.join(CONTRACTS_DIR, contract_filename)
    
    with open(contract_path, 'w') as f:
        json.dump(contract, f, indent=4, cls=NumpyEncoder)
    print(f"Contract saved to: {contract_path}")


# =============================================================================
# RESULTS STORAGE
# =============================================================================

def save_results(results: Dict[str, Dict], filepath: str,
                 dataset_name: str, target_column: str,
                 random_state: int, split_ratios: Tuple[float, float, float]) -> None:
    """
    Save all model results to a text file.
    
    Args:
        results: Dictionary of model results
        filepath: Output file path
        dataset_name: Name of the dataset
        target_column: Name of the target column
        random_state: Random seed used
        split_ratios: Tuple of (train, val, test) ratios
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write(f"{'MODEL TRAINING RESULTS':^80}\n")
        f.write(f"{dataset_name.upper()} DATASET\n".center(80))
        f.write("=" * 80 + "\n\n")
        
        # Configuration
        f.write("CONFIGURATION\n")
        f.write("-" * 40 + "\n")
        f.write(f"Dataset:        {dataset_name}\n")
        f.write(f"Target Column:  {target_column}\n")
        f.write(f"Random Seed:    {random_state}\n")
        f.write(f"Split Ratios:   {int(split_ratios[0]*100)}% Train / "
                f"{int(split_ratios[1]*100)}% Validation / "
                f"{int(split_ratios[2]*100)}% Test\n")
        f.write(f"Timestamp:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")
        
        # Best model summary
        best_model = None
        best_f1 = -1
        for model_name, model_results in results.items():
            test_f1 = model_results['test_metrics'].get('F1-Score', 0)
            if test_f1 > best_f1:
                best_f1 = test_f1
                best_model = model_name
        
        f.write("=" * 80 + "\n")
        f.write(f"BEST MODEL: {best_model} (Test F1-Score: {best_f1:.4f})\n")
        f.write("=" * 80 + "\n\n")
        
        # Individual model results
        for model_name, model_results in results.items():
            f.write("=" * 80 + "\n")
            f.write(f"MODEL: {model_name}\n")
            f.write("=" * 80 + "\n\n")
            
            # Hyperparameters
            f.write("Hyperparameters:\n")
            f.write("-" * 40 + "\n")
            for param, value in model_results['hyperparameters'].items():
                f.write(f"  {param}: {value}\n")
            f.write("\n")
            
            # Validation performance
            f.write("Validation Performance:\n")
            f.write("-" * 40 + "\n")
            for metric, value in model_results['validation_metrics'].items():
                if value is not None:
                    f.write(f"  {metric:12}: {value:.4f}\n")
                else:
                    f.write(f"  {metric:12}: N/A\n")
            f.write("\n")
            
            # Test performance
            f.write("Test Performance:\n")
            f.write("-" * 40 + "\n")
            for metric, value in model_results['test_metrics'].items():
                if value is not None:
                    f.write(f"  {metric:12}: {value:.4f}\n")
                else:
                    f.write(f"  {metric:12}: N/A\n")
            f.write("\n")
            
            # Generated plots
            if 'plots' in model_results and model_results['plots']:
                f.write("Generated Plots:\n")
                f.write("-" * 40 + "\n")
                for plot_type, plot_path in model_results['plots'].items():
                    f.write(f"  {plot_type}: {os.path.basename(plot_path)}\n")
            f.write("\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print(f"\nResults saved to: {filepath}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main execution function that orchestrates the entire training pipeline.
    """
    print("=" * 60)
    print(f"Starting {DATASET_NAME} Model Training Pipeline")
    print("=" * 60)
    
    # Log configuration
    print(f"\nConfiguration:")
    print(f"  Dataset: {DATASET_PATH}")
    print(f"  Target: {TARGET_COLUMN}")
    print(f"  Random State: {RANDOM_STATE}")
    print(f"  Split: {int(TRAIN_RATIO*100)}/{int(VALIDATION_RATIO*100)}/{int(TEST_RATIO*100)}")
    
    # Step 1: Load data
    print("\n" + "=" * 60)
    print("STEP 1: Loading Data")
    print("=" * 60)
    X, y = load_data(DATASET_PATH, TARGET_COLUMN)
    
    # Step 2: Split data
    print("\n" + "=" * 60)
    print("STEP 2: Splitting Data")
    print("=" * 60)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        X, y,
        train_ratio=TRAIN_RATIO,
        val_ratio=VALIDATION_RATIO,
        test_ratio=TEST_RATIO,
        random_state=RANDOM_STATE
    )
    
    # Step 3: Get models
    print("\n" + "=" * 60)
    print("STEP 3: Initializing Models")
    print("=" * 60)
    models = get_models(RANDOM_STATE)
    print(f"Models to evaluate: {list(models.keys())}")
    
    # Step 4 & 5: Train and validate each model
    print("\n" + "=" * 60)
    print("STEP 4 & 5: Training and Validation")
    print("=" * 60)
    
    results = {}
    best_model = None
    best_model_name = None
    best_val_f1 = -1
    
    for model_name, model in models.items():
        print(f"\n{'─' * 40}")
        print(f"Processing: {model_name}")
        print(f"{'─' * 40}")
        
        # Train model
        trained_model = train_model(
            model, X_train, y_train,
            model_name=model_name,
            use_grid_search=True,  # Enable hyperparameter tuning
            random_state=RANDOM_STATE
        )
        
        # Validate model
        val_metrics = evaluate_model(trained_model, X_val, y_val)
        print(f"Validation F1-Score: {val_metrics['F1-Score']:.4f}")
        
        # Track best model
        if val_metrics['F1-Score'] > best_val_f1:
            best_val_f1 = val_metrics['F1-Score']
            best_model = trained_model
            best_model_name = model_name
        
        # Store results
        results[model_name] = {
            'model': trained_model,
            'hyperparameters': trained_model.get_params(),
            'validation_metrics': val_metrics,
            'test_metrics': None  # Will be filled in next step
        }
    
    print(f"\n*** Best model based on validation: {best_model_name} ***")
    
    # Step 6: Evaluate all models on test set
    print("\n" + "=" * 60)
    print("STEP 6: Test Set Evaluation")
    print("=" * 60)
    
    
    for model_name in results.keys():
        trained_model = results[model_name]['model']
        test_metrics = evaluate_model(trained_model, X_test, y_test)
        results[model_name]['test_metrics'] = test_metrics
        
        print(f"\n{model_name} Test Results:")
        for metric, value in test_metrics.items():
            if value is not None:
                print(f"  {metric}: {value:.4f}")
    
    # Step 7: Generate Visualizations
    print("\n" + "=" * 60)
    print("STEP 7: Generating Visualizations")
    print("=" * 60)
    
    for model_name in results.keys():
        print(f"\nGenerating plots for {model_name}...")
        trained_model = results[model_name]['model']
        plots = generate_model_plots(
            trained_model, X_test, y_test,
            model_name, DATASET_NAME, PLOTS_DIR
        )
        results[model_name]['plots'] = plots
    
    # Step 8: Save results
    print("\n" + "=" * 60)
    print("STEP 8: Saving Results")
    print("=" * 60)
    
    # Remove model objects before saving (not serializable to text)
    results_to_save = {
        name: {k: v for k, v in data.items() if k != 'model'}
        for name, data in results.items()
    }
    
    output_path = os.path.join(OUTPUT_DIR, RESULTS_FILE)
    save_results(
        results_to_save,
        output_path,
        DATASET_NAME,
        TARGET_COLUMN,
        RANDOM_STATE,
        (TRAIN_RATIO, VALIDATION_RATIO, TEST_RATIO)
    )
    
    print("\n" + "=" * 60)
    print("STEP 9: Saving Best Model Artifacts")
    print("=" * 60)
    
    if best_model_name and best_model_name in results:
        best_result = results[best_model_name]
        # Get features from train set columns
        input_features = X_train.columns.tolist()
        
        save_model_artifact(
            model=best_result['model'],
            model_name=best_model_name,
            dataset_name=DATASET_NAME,
            input_features=input_features,
            metrics=best_result['test_metrics'],
            optimal_threshold=best_result.get('optimal_threshold', 0.5)
        )
    
    print("\n" + "=" * 60)
    print("Training Pipeline Completed Successfully!")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()
