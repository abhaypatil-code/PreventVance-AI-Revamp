import pandas as pd
import numpy as np
import os

datasets = [
    ("../../data/processed/Diabetes_Processed.csv", "Has_Diabetes"),
    ("../../data/processed/Heart_Processed.csv", "Has_Heart_Disease"),
    ("../../data/processed/Liver_Processed.csv", "Has_Liver_Disease")
]

print("="*60)
print("DATASET DIAGNOSTICS")
print("="*60)

for filepath, target_col in datasets:
    print(f"\nAnalyzing: {filepath}")
    if not os.path.exists(filepath):
        print("  File not found!")
        continue
        
    df = pd.read_csv(filepath)
    print(f"  Shape: {df.shape}")
    
    # Check Class Balance
    if target_col in df.columns:
        counts = df[target_col].value_counts()
        print(f"  Class Balance:\n{counts}")
        ratio = counts.min() / counts.max()
        print(f"  Balance Ratio: 1:{1/ratio:.2f}")
    else:
        print(f"  Target '{target_col}' not found!")
        
    # Check for Missing Values
    print(f"  Missing Values: {df.isnull().sum().sum()}")
    
    # Check Feature Stats for Scaling
    # Select numeric columns excluding target
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)
        
    stats = df[numeric_cols].describe().loc[['min', 'max', 'mean', 'std']]
    print("  Feature Stats (First 5):")
    print(stats.iloc[:, :5])
    
    # Check for potentially invalid zeros (common in Diabetes)
    if "Diabetes" in filepath:
        potential_zeros = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        print("  Zero counts in critical columns:")
        for col in potential_zeros:
            if col in df.columns:
                zero_count = (df[col] == 0).sum()
                print(f"    {col}: {zero_count} ({zero_count/len(df)*100:.1f}%)")

print("\nDiagnostics Completed.")
