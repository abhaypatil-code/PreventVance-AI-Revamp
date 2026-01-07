import pandas as pd
from sklearn.preprocessing import LabelEncoder, PowerTransformer
import numpy as np

def preprocess_liver():
    print("Preprocessing Liver Dataset...")
    
    # 1. Load Data
    input_file = '../../data/raw/Liver.csv'
    output_file = '../../data/processed/Liver_Processed.csv'
    
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {input_file} with shape {df.shape}")
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # 2. Exploratory Checks / Data Cleaning
    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"Found {duplicates} duplicates, dropping them...")
        df = df.drop_duplicates()
        print(f"New shape: {df.shape}")
        
    # 3. Feature Encoding
    # Encode Gender: Female/Male -> 0/1
    if 'Gender' in df.columns:
        print("Encoding 'Gender'...")
        le = LabelEncoder()
        df['Gender'] = le.fit_transform(df['Gender'])
        print(f"Gender mapping: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    
    # 3.2 Winsorization is handled implicitly by PowerTransformer's robustness or we can keep it.
    # Let's keep winsorization to prevent outliers from distorting PowerTransformer
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'Has_Liver_Disease' in numeric_cols:
        numeric_cols.remove('Has_Liver_Disease')
    print("Winsorizing outliers at 1st/99th percentile...")
    for col in numeric_cols:
        lower = df[col].quantile(0.01)
        upper = df[col].quantile(0.99)
        df[col] = df[col].clip(lower=lower, upper=upper)
        
    # 3.5 Feature Engineering (Add medically relevant ratios)
    print("Generating interaction features...")
    
    # Globulin = Total Proteins - Albumins
    df['Globulin'] = df['Total Protiens'] - df['Albumins']
    
    # Albumin/Globulin Ratio (Recalculate to ensure consistency)
    # Handle division by zero or NaN
    df['Albumin_Globulin_Ratio'] = df['Albumins'] / df['Globulin'].replace(0, 0.001)
    
    # AST/ALT Ratio (SGOT/SGPT)
    df['AST_ALT_Ratio'] = df['SGOT'] / df['SGPT'].replace(0, 0.001)
    
    # Bilirubin Ratio (Direct/Total)
    df['Bilirubin_Ratio'] = df['Direct Bilburin'] / df['Total Bilburin'].replace(0, 0.001)
    
    # Check for NaNs created by engineering
    if df.isnull().sum().sum() > 0:
        print("Imputing NaNs in new features...")
        df.fillna(0, inplace=True)
    
    # Drop original redundant columns if desired, but Random Forest works well with them.
    # We will keep them for now but ensure we drop 'A/G Ratio' if we recalculated it to avoid perfect collinearity confusion
    # though RF handles it fine. Let's keep existing 'A/G Ratio' comparison or drop it.
    # The dataset has 'A/G Ratio'. Let's see if we should drop the original one to rely on ours.
    if 'A/G Ratio' in df.columns:
        df = df.drop(columns=['A/G Ratio']) # Use our recalculated one

        
    # 4. Data Cleaning/Normalization
    target_col = 'Has_Liver_Disease'
    
    if target_col not in df.columns:
        print(f"Error: Target column {target_col} not found.")
        return

    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Scaling using PowerTransformer (Yeo-Johnson)
    # This handles skewness and standardization simultaneously
    print("Applying PowerTransformer (Yeo-Johnson)...")
    pt = PowerTransformer(method='yeo-johnson', standardize=True)
    X_scaled = pd.DataFrame(pt.fit_transform(X), columns=X.columns)
    
    # Recombine
    df_processed = pd.concat([X_scaled, y.reset_index(drop=True)], axis=1)
    
    # 5. Save to disk
    df_processed.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")
    print("Sample:\n", df_processed.head())

if __name__ == "__main__":
    preprocess_liver()
