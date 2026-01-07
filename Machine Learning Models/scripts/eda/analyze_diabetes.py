import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_style("whitegrid")
OUTPUT_DIR = "../../results/eda/diabetes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_diabetes():
    print("Starting Diabetes EDA...")
    try:
        df = pd.read_csv('../../data/processed/Diabetes_Processed.csv')
        print("Dataset Loaded Successfully")
        
        # 1. Statistical Summary
        with open(f"{OUTPUT_DIR}/summary.txt", "w") as f:
            f.write("SHAPE:\n")
            f.write(str(df.shape) + "\n\n")
            f.write("COLUMNS:\n")
            f.write(str(df.columns.tolist()) + "\n\n")
            f.write("INFO:\n")
            df.info(buf=f)
            f.write("\n\nDESCRIPTION:\n")
            f.write(str(df.describe()) + "\n\n")
            f.write("MISSING VALUES:\n")
            f.write(str(df.isnull().sum()) + "\n\n")
            f.write("SKEWNESS:\n")
            numeric_cols = df.select_dtypes(include=['number']).columns
            f.write(str(df[numeric_cols].skew()) + "\n")

        # 2. Correlation Heatmap
        plt.figure(figsize=(12, 10))
        corr = df.corr()
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', linewidths=0.5)
        plt.title('Diabetes Correlation Heatmap')
        plt.savefig(f"{OUTPUT_DIR}/correlation_heatmap.png")
        plt.close()

        # 3. Distribution Plots
        numeric_cols = df.select_dtypes(include=['number']).columns
        # Exclude encoded target if present or process it differently, but for general EDA plot everyone
        # We'll plot max 9 per figure to avoid clutter
        n_cols = 3
        n_rows = (len(numeric_cols) - 1) // n_cols + 1
        plt.figure(figsize=(15, 5 * n_rows))
        for i, col in enumerate(numeric_cols):
            plt.subplot(n_rows, n_cols, i + 1)
            sns.histplot(df[col], kde=True)
            plt.title(f'Distribution of {col}')
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/distribution_plots.png")
        plt.close()

        # 4. Boxplots
        plt.figure(figsize=(15, 5 * n_rows))
        for i, col in enumerate(numeric_cols):
            plt.subplot(n_rows, n_cols, i + 1)
            sns.boxplot(x=df[col])
            plt.title(f'Boxplot of {col}')
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/boxplots.png")
        plt.close()

        print("Diabetes EDA Completed. Results saved to", OUTPUT_DIR)

    except Exception as e:
        print(f"Error in Diabetes EDA: {e}")

if __name__ == "__main__":
    analyze_diabetes()
