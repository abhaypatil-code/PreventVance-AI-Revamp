import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

def preprocess_diabetes():
    print("Preprocessing Diabetes Dataset...")
    
    # 1. Load Data
    input_file = '../../data/raw/Diabetes.csv'
    output_file = '../../data/processed/Diabetes_Processed.csv'
    
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {input_file} with shape {df.shape}")
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # 2. Exploratory Checks (already done in analysis, but good to have safety here)
    # replacing 0 with NaN for relevant columns
    cols_check_zero = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    print(f"Replacing 0 with NaN in: {cols_check_zero}")
    df[cols_check_zero] = df[cols_check_zero].replace(0, np.nan)
    
    print("Missing values after replacement:\n", df.isnull().sum())
    
    # 3. Handling Missing Values
    # Using Median imputation
    imputer = SimpleImputer(strategy='median')
    df[cols_check_zero] = imputer.fit_transform(df[cols_check_zero])
    print("Missing values imputed.")

    # 4. Data Cleaning/Normalization
    # Separating Target
    target_col = 'Has_Diabetes'
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Standardization (Z-score scaling)
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    
    # Recombine for saving
    df_processed = pd.concat([X_scaled, y], axis=1)
    
    # 5. Save to disk
    df_processed.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")
    print("Sample:\n", df_processed.head())

if __name__ == "__main__":
    preprocess_diabetes()
