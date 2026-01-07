# Disease Prediction Models - API Contract Documentation

> **Generated:** 2025-12-29  
> **Models Location:** `results/training/models/`  
> **Contracts Location:** `results/training/contracts/`

---

## Quick Start

```python
import joblib
import pandas as pd

# Load any model
model = joblib.load("results/training/models/<disease>_best_model.pkl")

# Load contract for feature info
import json
with open("results/training/contracts/<disease>_contract.json") as f:
    contract = json.load(f)

# Get optimal threshold
threshold = contract.get("optimal_threshold", 0.5)

# Make prediction
proba = model.predict_proba(input_df)[0][1]
prediction = 1 if proba >= threshold else 0
```

---

## 1. Diabetes Prediction Model

### Model Information
| Property | Value |
|----------|-------|
| **File** | `diabetes_best_model.pkl` |
| **Algorithm** | Random Forest Classifier |
| **Optimal Threshold** | 0.50 |
| **Test F1-Score** | 0.7634 |
| **Test AUC-ROC** | 0.8403 |

### Input Features (7 features)
| Feature | Type | Description |
|---------|------|-------------|
| `Glucose` | float | Plasma glucose concentration (scaled) |
| `BloodPressure` | float | Diastolic blood pressure mm Hg (scaled) |
| `SkinThickness` | float | Triceps skin fold thickness mm (scaled) |
| `Insulin` | float | 2-Hour serum insulin mu U/ml (scaled) |
| `BMI` | float | Body mass index (scaled) |
| `DiabetesPedigreeFunction` | float | Diabetes pedigree function (scaled) |
| `Age` | float | Age in years (scaled) |

### Target Column
- **Name:** `Has_Diabetes`
- **Values:** `0` = No Diabetes, `1` = Has Diabetes

### Usage Example
```python
import joblib
import pandas as pd

# Load model
model = joblib.load("results/training/models/diabetes_best_model.pkl")

# Prepare input (features must be pre-scaled using StandardScaler)
input_data = pd.DataFrame([{
    "Glucose": 0.5,           # scaled value
    "BloodPressure": 0.2,     # scaled value
    "SkinThickness": -0.1,    # scaled value
    "Insulin": 0.3,           # scaled value
    "BMI": 0.8,               # scaled value
    "DiabetesPedigreeFunction": 0.1,
    "Age": 0.5                # scaled value
}])

# Predict
proba = model.predict_proba(input_data)[0][1]
threshold = 0.5
prediction = "Diabetes Detected" if proba >= threshold else "No Diabetes"
print(f"Probability: {proba:.2%}, Prediction: {prediction}")
```

---

## 2. Heart Disease Prediction Model

### Model Information
| Property | Value |
|----------|-------|
| **File** | `heart_best_model.pkl` |
| **Algorithm** | Random Forest Classifier |
| **Optimal Threshold** | 0.50 |
| **Test F1-Score** | 0.7711 |
| **Test AUC-ROC** | 0.8206 |

### Input Features (47 features)
**Continuous Features (10):**
| Feature | Type | Description |
|---------|------|-------------|
| `Age` | float | Patient age (scaled) |
| `Diet_Score` | float | Diet quality score (scaled) |
| `Cholesterol_Level` | float | Total cholesterol (scaled) |
| `Triglyceride_Level` | float | Triglyceride level (scaled) |
| `LDL_Level` | float | LDL cholesterol (scaled) |
| `HDL_Level` | float | HDL cholesterol (scaled) |
| `Systolic_BP` | float | Systolic blood pressure (scaled) |
| `Diastolic_BP` | float | Diastolic blood pressure (scaled) |
| `Air_Pollution_Exposure` | float | Pollution exposure index (scaled) |
| `Stress_Level` | float | Stress level (scaled) |

**Binary Features (9):**
| Feature | Type | Values |
|---------|------|--------|
| `Gender` | int | 0=Female, 1=Male |
| `Diabetes` | int | 0=No, 1=Yes |
| `Hypertension` | int | 0=No, 1=Yes |
| `Obesity` | int | 0=No, 1=Yes |
| `Smoking` | int | 0=No, 1=Yes |
| `Alcohol_Consumption` | int | 0=No, 1=Yes |
| `Physical_Activity` | int | 0=Low, 1=High |
| `Family_History` | int | 0=No, 1=Yes |
| `Heart_Attack_History` | int | 0=No, 1=Yes |

**State Features (27):** `State_2` through `State_28` (one-hot encoded, bool/int)

### Target Column
- **Name:** `Has_Heart_Disease`
- **Values:** `0` = Healthy, `1` = Heart Disease

### Usage Example
```python
import joblib
import pandas as pd

model = joblib.load("results/training/models/heart_best_model.pkl")

# Prepare input with all 47 features
input_data = pd.DataFrame([{
    "Age": 0.5, "Diet_Score": 0.3, "Cholesterol_Level": 0.2,
    "Triglyceride_Level": 0.1, "LDL_Level": 0.4, "HDL_Level": -0.2,
    "Systolic_BP": 0.6, "Diastolic_BP": 0.3,
    "Air_Pollution_Exposure": 0.1, "Stress_Level": 0.5,
    "Gender": 1, "Diabetes": 0, "Hypertension": 1, "Obesity": 0,
    "Smoking": 1, "Alcohol_Consumption": 0, "Physical_Activity": 0,
    "Family_History": 1, "Heart_Attack_History": 0,
    # State one-hot encoding (27 features, all False by default)
    **{f"State_{i}": False for i in range(2, 29)}
}])

proba = model.predict_proba(input_data)[0][1]
prediction = "Heart Disease Detected" if proba >= 0.5 else "Healthy"
```

---

## 3. Liver Disease Prediction Model

### Model Information
| Property | Value |
|----------|-------|
| **File** | `liver_best_model.pkl` |
| **Algorithm** | Voting MLP Ensemble (5 MLPs) |
| **Optimal Threshold** | 0.5682 |
| **Test F1-Score** | 0.6661 |
| **Test AUC-ROC** | 0.7390 |
| **Specificity** | 0.84 |
| **Sensitivity** | 0.5738 |

### Input Features (7 features)
| Feature | Type | Description |
|---------|------|-------------|
| `Age` | float | Patient age (scaled) |
| `Total Bilburin` | float | Total bilirubin level (scaled) |
| `Alkphos` | float | Alkaline phosphatase (scaled) |
| `SGPT` | float | SGPT enzyme level (scaled) |
| `SGOT` | float | SGOT enzyme level (scaled) |
| `Globulin` | float | Globulin protein level (scaled) |
| `Albumin_Globulin_Ratio` | float | A/G ratio (scaled) |

### Target Column
- **Name:** `Has_Liver_Disease`
- **Values:** `0` = Healthy, `1` = Liver Disease

### ⚠️ Important: Threshold Tuning
This model uses an **optimized threshold of 0.5682** for better specificity. Always use the threshold from the contract:

```python
import joblib
import json
import pandas as pd

model = joblib.load("results/training/models/liver_best_model.pkl")

with open("results/training/contracts/liver_contract.json") as f:
    contract = json.load(f)
threshold = contract["optimal_threshold"]  # 0.5682

input_data = pd.DataFrame([{
    "Age": 0.2,
    "Total Bilburin": 0.5,
    "Alkphos": 0.3,
    "SGPT": 0.1,
    "SGOT": 0.2,
    "Globulin": -0.1,
    "Albumin_Globulin_Ratio": 0.4
}])

proba = model.predict_proba(input_data)[0][1]
prediction = "Liver Disease" if proba >= threshold else "Healthy"
print(f"Probability: {proba:.2%}, Threshold: {threshold:.4f}")
```

---

## Preprocessing Requirements

All models expect **StandardScaler-transformed** features. The preprocessing pipeline:

1. **Missing Values**: Filled with median (numerical) or mode (categorical)
2. **Outliers**: Clipped using IQR method or Winsorization
3. **Encoding**: Label encoding for binary, One-hot for multi-class categorical
4. **Scaling**: StandardScaler (zero mean, unit variance)
5. **Class Imbalance**: SMOTE + Tomek links applied during training

### To use with raw data:
```python
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Fit scaler on training data (or load saved scaler)
scaler = StandardScaler()
# ... fit on your training data ...

# Transform new data
raw_input = {"Glucose": 120, "BloodPressure": 80, ...}  # raw values
scaled_input = scaler.transform(pd.DataFrame([raw_input]))
```

---

## Model Files Summary

| Disease | Model File | Contract File | Size |
|---------|-----------|---------------|------|
| Diabetes | `diabetes_best_model.pkl` | `diabetes_contract.json` | ~975 KB |
| Heart | `heart_best_model.pkl` | `heart_contract.json` | ~9.9 MB |
| Liver | `liver_best_model.pkl` | `liver_contract.json` | ~147 KB |

---

## Error Handling

```python
def safe_predict(model, input_df, threshold=0.5):
    """Safe prediction with error handling."""
    try:
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(input_df)[0][1]
            return 1 if proba >= threshold else 0, proba
        else:
            return model.predict(input_df)[0], None
    except Exception as e:
        print(f"Prediction error: {e}")
        return None, None
```
