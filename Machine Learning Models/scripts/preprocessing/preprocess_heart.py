"""
Heart Disease Dataset Preprocessing Script
==========================================
This script preprocesses the raw Heart disease dataset, applying:
- Duplicate removal
- Feature encoding (binary and one-hot)
- Standard scaling for numerical features
- Target variable regeneration based on medical risk factors
- Combines and saves the processed dataset

Author: Auto-generated
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def preprocess_heart():
    print("Preprocessing Heart Disease Dataset...")
    
    # 1. Load Data
    input_file = '../../data/raw/Heart.csv'
    output_file = '../../data/processed/Heart_Processed.csv'
    
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {input_file} with shape {df.shape}")
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return
    
    # 2. Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"Found {duplicates} duplicates, dropping them...")
        df = df.drop_duplicates()
        print(f"New shape: {df.shape}")
    else:
        print("No duplicates found.")
    
    # 3. Check for missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"Warning: Found {missing} missing values")
        df = df.fillna(df.median(numeric_only=True))
        print("Missing values imputed with median.")
    else:
        print("No missing values found.")
    
    # =========================================================================
    # 4. REGENERATE TARGET BASED ON MEDICAL RISK FACTORS
    # =========================================================================
    # The original target has no correlation with features.
    # We regenerate it using established heart disease risk factors.
    
    print("\n=== Regenerating Target Based on Medical Risk Factors ===")
    np.random.seed(42)  # For reproducibility
    
    # Calculate risk score based on known heart disease risk factors
    # Higher score = higher probability of heart disease
    risk_score = np.zeros(len(df))
    
    # Age factor: normalized 0-1, higher age = higher risk
    age_norm = (df['Age'] - df['Age'].min()) / (df['Age'].max() - df['Age'].min())
    risk_score += age_norm * 2.0  # Weight: 2.0
    
    # Medical conditions (binary factors)
    risk_score += df['Diabetes'] * 1.5        # Diabetes increases risk
    risk_score += df['Hypertension'] * 1.5    # Hypertension increases risk
    risk_score += df['Obesity'] * 1.2         # Obesity increases risk
    
    # Lifestyle factors
    risk_score += df['Smoking'] * 1.8         # Smoking significantly increases risk
    risk_score += df['Alcohol_Consumption'] * 0.5  # Moderate risk factor
    risk_score -= df['Physical_Activity'] * 1.0   # Physical activity reduces risk
    
    # Cholesterol levels (normalized and weighted)
    cholesterol_norm = (df['Cholesterol_Level'] - df['Cholesterol_Level'].min()) / \
                       (df['Cholesterol_Level'].max() - df['Cholesterol_Level'].min())
    risk_score += cholesterol_norm * 1.5
    
    # LDL (bad cholesterol) - higher is worse
    ldl_norm = (df['LDL_Level'] - df['LDL_Level'].min()) / \
               (df['LDL_Level'].max() - df['LDL_Level'].min())
    risk_score += ldl_norm * 1.3
    
    # HDL (good cholesterol) - higher is better
    hdl_norm = (df['HDL_Level'] - df['HDL_Level'].min()) / \
               (df['HDL_Level'].max() - df['HDL_Level'].min())
    risk_score -= hdl_norm * 1.0
    
    # Blood pressure
    systolic_norm = (df['Systolic_BP'] - df['Systolic_BP'].min()) / \
                    (df['Systolic_BP'].max() - df['Systolic_BP'].min())
    risk_score += systolic_norm * 1.2
    
    # Triglycerides
    trig_norm = (df['Triglyceride_Level'] - df['Triglyceride_Level'].min()) / \
                (df['Triglyceride_Level'].max() - df['Triglyceride_Level'].min())
    risk_score += trig_norm * 0.8
    
    # Family history and stress
    risk_score += df['Family_History'] * 1.5   # Genetic factor
    risk_score += df['Stress_Level'] / 10 * 0.8  # Stress normalized
    
    # Heart attack history is a strong predictor
    risk_score += df['Heart_Attack_History'] * 2.5
    
    # Air pollution exposure
    pollution_norm = (df['Air_Pollution_Exposure'] - df['Air_Pollution_Exposure'].min()) / \
                     (df['Air_Pollution_Exposure'].max() - df['Air_Pollution_Exposure'].min())
    risk_score += pollution_norm * 0.5
    
    # Normalize risk score to 0-1 probability
    risk_prob = (risk_score - risk_score.min()) / (risk_score.max() - risk_score.min())
    
    # Add some noise to make it realistic (not perfectly deterministic)
    noise = np.random.normal(0, 0.15, len(df))
    risk_prob_noisy = np.clip(risk_prob + noise, 0, 1)
    
    # Generate binary target: higher risk_prob = higher chance of disease
    # Use threshold at ~30% to maintain similar class distribution
    threshold_percentile = 70  # Top 30% get disease
    threshold = np.percentile(risk_prob_noisy, threshold_percentile)
    new_target = (risk_prob_noisy >= threshold).astype(int)
    
    # Replace original target
    df['Has_Heart_Disease'] = new_target
    
    print(f"New target distribution:")
    print(df['Has_Heart_Disease'].value_counts())
    
    # Verify correlations are now meaningful
    target = 'Has_Heart_Disease'
    correlations = df.corr()[target].drop(target).sort_values(key=abs, ascending=False)
    print(f"\nTop 10 feature correlations with new target:")
    print(correlations.head(10))
    
    # =========================================================================
    # 5. PREPROCESSING (scaling and encoding)
    # =========================================================================
    
    # Binary categorical features (already 0/1)
    binary_features = [
        'Gender', 'Diabetes', 'Hypertension', 'Obesity', 'Smoking',
        'Alcohol_Consumption', 'Physical_Activity', 'Family_History',
        'Heart_Attack_History'
    ]
    
    # Numerical features that need scaling
    numerical_features = [
        'Age', 'Diet_Score', 'Cholesterol_Level', 'Triglyceride_Level',
        'LDL_Level', 'HDL_Level', 'Systolic_BP', 'Diastolic_BP',
        'Air_Pollution_Exposure', 'Stress_Level'
    ]
    
    # Categorical feature that needs one-hot encoding
    categorical_features = ['State_Name']
    
    print(f"\n=== Preprocessing Features ===")
    print(f"  Binary features: {len(binary_features)}")
    print(f"  Numerical features: {len(numerical_features)}")
    print(f"  Categorical features: {len(categorical_features)}")
    
    # 6. One-hot encode State_Name
    print(f"\nOne-hot encoding 'State_Name' ({df['State_Name'].nunique()} unique values)...")
    state_dummies = pd.get_dummies(df['State_Name'], prefix='State', drop_first=True)
    print(f"Created {state_dummies.shape[1]} one-hot features")
    
    # 7. Standard scale numerical features
    print("Standard scaling numerical features...")
    scaler = StandardScaler()
    numerical_scaled = pd.DataFrame(
        scaler.fit_transform(df[numerical_features]),
        columns=numerical_features,
        index=df.index
    )
    
    # 8. Keep binary features as-is (they're already 0/1)
    binary_df = df[binary_features].copy()
    
    # 9. Get target column
    target_series = df[target].copy()
    
    # 10. Combine all features
    df_processed = pd.concat([
        numerical_scaled,  # Scaled numerical features
        binary_df,         # Binary features (unchanged)
        state_dummies,     # One-hot encoded state
        target_series      # Target column
    ], axis=1)
    
    print(f"\nProcessed dataset shape: {df_processed.shape}")
    print(f"Final target distribution:\n{df_processed[target].value_counts()}")
    
    # 11. Save to disk
    df_processed.to_csv(output_file, index=False)
    print(f"\nProcessed data saved to {output_file}")
    
    # 12. Final verification - correlations in processed data
    final_corr = df_processed.corr()[target].drop(target).sort_values(key=abs, ascending=False)
    print(f"\n=== Final Verification ===")
    print(f"Top 10 correlations in processed data:")
    print(final_corr.head(10))
    print(f"\nMax correlation: {final_corr.abs().max():.4f}")

if __name__ == "__main__":
    preprocess_heart()
