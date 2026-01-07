import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_style("whitegrid")
OUTPUT_DIR = "../../results/eda/heart"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_heart():
    print("Starting Heart EDA...")
    try:
        df = pd.read_csv('../../data/processed/Heart_Processed.csv')
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
        # Limit to top correlations or just plot all if reasonable size
        # If too many columns (like encoded states), maybe filter them out for heatmap
        # For now, we plot all but handle size
        plt.figure(figsize=(20, 15))
        corr = df.corr()
        sns.heatmap(corr, annot=False, cmap='coolwarm', linewidths=0.5) # Annot false if too many
        plt.title('Heart Correlation Heatmap')
        plt.savefig(f"{OUTPUT_DIR}/correlation_heatmap.png")
        plt.close()

        # 3. Distribution Plots
        # Separate numeric vs binary if possible, or just plot all
        # To avoid too many plots if we have many encoded cols, we filter for "State_" columns
        cols_to_plot = [c for c in df.columns if not c.startswith("State_")]
        
        # Add basic countplots for categorical/target potentially
        # Assuming Heart Attack or similar is target, let's just plot distributions of non-state cols
        
        n_cols = 3
        n_rows = (len(cols_to_plot) - 1) // n_cols + 1
        plt.figure(figsize=(15, 5 * n_rows))
        for i, col in enumerate(cols_to_plot):
            if col in df.columns: # Safety check
                plt.subplot(n_rows, n_cols, i + 1)
                sns.histplot(df[col], kde=True)
                plt.title(f'Distribution of {col}')
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/distribution_plots.png")
        plt.close()

        print("Heart EDA Completed. Results saved to", OUTPUT_DIR)

    except Exception as e:
        print(f"Error in Heart EDA: {e}")

if __name__ == "__main__":
    analyze_heart()
