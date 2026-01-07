import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_style("whitegrid")
OUTPUT_DIR = "../../results/eda/liver"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_liver():
    print("Starting Liver EDA...")
    try:
        df = pd.read_csv('../../data/processed/Liver_Processed.csv')
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
        plt.title('Liver Correlation Heatmap')
        plt.savefig(f"{OUTPUT_DIR}/correlation_heatmap.png")
        plt.close()

        # 3. Distribution Plots
        numeric_cols = df.select_dtypes(include=['number']).columns
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

        print("Liver EDA Completed. Results saved to", OUTPUT_DIR)

    except Exception as e:
        print(f"Error in Liver EDA: {e}")

if __name__ == "__main__":
    analyze_liver()
