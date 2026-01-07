# PreventVance AI - System Architecture

> **Technical Design Document**
> *Version 2.0 | Last Updated: January 2026*

---

## 1. Executive Summary

**PreventVance AI** is a healthcare analytics platform designed for rural healthcare workers. It enables early detection of chronic diseases—**Diabetes, Heart Disease, Liver Disease, and Mental Health issues**—using Machine Learning, and provides personalized lifestyle recommendations via Google Gemini AI.

The system uses a decoupled **Client-Server architecture** with a **Streamlit** frontend and a **Flask** REST API backend.

---

## 2. High-Level Architecture

### System Context Diagram
This diagram shows the interactions between users, the system, and external services.

```mermaid
flowchart TD
    subgraph Users
        Admin["👨‍⚕️ Healthcare Worker"]
        Patient["👤 Patient"]
    end

    subgraph "PreventVance AI Platform"
        WebApp["🖥️ Web Application<br/>(Streamlit + Flask)"]
    end

    subgraph "External Services"
        Gemini["🤖 Google Gemini AI<br/>(Recommendations)"]
    end

    Admin -->|"Registers patients,<br/>performs assessments"| WebApp
    Patient -->|"Views health records,<br/>risk reports"| WebApp
    WebApp <-->|"REST API<br/>(Risk Profile → Tips)"| Gemini
```

---

### Container Architecture
The high-level technical components and their responsibilities.

```mermaid
flowchart TB
    subgraph "Client Layer"
        FE["Streamlit Frontend<br/>(app.py, pages/)"]
    end

    subgraph "Server Layer"
        API["Flask REST API<br/>(Blueprints)"]
        Auth["Auth Service<br/>(JWT)"]
        ML["ML Inference<br/>(services.py)"]
        Recs["Recommendation<br/>Service"]
    end

    subgraph "Data Layer"
        DB[("SQLite<br/>(medml.db)")]
        Models["Model Store<br/>(.pkl files)"]
    end

    subgraph "External"
        GenAI["Gemini 2.0 Flash"]
    end

    FE <-->|"HTTP/JSON"| API
    API --> Auth
    API --> ML
    API --> Recs

    Auth --> DB
    ML --> Models
    Recs --> GenAI
    Recs --> DB
    API -->|"CRUD"| DB
```

---

## 3. Database Schema (ER Diagram)

The database uses **SQLAlchemy ORM** with **SQLite**. Below is the entity-relationship diagram based on `models.py`.

```mermaid
erDiagram
    User ||--o{ Patient : "registers"
    User ||--o{ Consultation : "books"
    User ||--o{ ConsultationNote : "writes"

    Patient ||--o{ DiabetesAssessment : "has"
    Patient ||--o{ HeartAssessment : "has"
    Patient ||--o{ LiverAssessment : "has"
    Patient ||--o{ MentalHealthAssessment : "has"
    Patient ||--o{ RiskPrediction : "has"
    Patient ||--o{ Consultation : "attends"
    Patient ||--o{ ConsultationNote : "has"
    Patient ||--o{ LifestyleRecommendation : "receives"

    RiskPrediction ||--o{ LifestyleRecommendation : "triggers"

    User {
        int id PK
        string name
        string email UK
        string username UK
        string password_hash
        string role
        string designation
        string facility_name
    }

    Patient {
        int id PK
        string abha_id UK
        string name
        int age
        string gender
        float height
        float weight
        string state_name
        int created_by_admin_id FK
    }

    DiabetesAssessment {
        int id PK
        int patient_id FK
        bool pregnancy
        float glucose
        float blood_pressure
        float skin_thickness
        float insulin
        bool diabetes_history
        datetime assessed_at
    }

    HeartAssessment {
        int id PK
        int patient_id FK
        bool diabetes
        bool hypertension
        bool smoking
        float cholesterol_level
        int systolic_bp
        int diastolic_bp
        bool family_history
        datetime assessed_at
    }

    LiverAssessment {
        int id PK
        int patient_id FK
        float total_bilirubin
        float direct_bilirubin
        float alkaline_phosphatase
        float sgpt
        float sgot
        float total_protein
        float albumin
        datetime assessed_at
    }

    MentalHealthAssessment {
        int id PK
        int patient_id FK
        int phq_score
        int gad_score
        bool depressiveness
        bool suicidal
        bool anxiousness
        bool sleepiness
        datetime assessed_at
    }

    RiskPrediction {
        int id PK
        int patient_id FK
        float diabetes_risk_score
        string diabetes_risk_level
        float heart_risk_score
        string heart_risk_level
        float liver_risk_score
        string liver_risk_level
        float mental_health_risk_score
        string mental_health_risk_level
        string model_version
        datetime predicted_at
    }

    LifestyleRecommendation {
        int id PK
        int patient_id FK
        int prediction_id FK
        string disease_type
        string risk_level
        string category
        text recommendation_text
        string language
        int priority
        bool is_active
    }

    Consultation {
        int id PK
        int patient_id FK
        int admin_id FK
        string disease
        string consultation_type
        datetime consultation_datetime
        string status
    }

    ConsultationNote {
        int id PK
        int patient_id FK
        int admin_id FK
        text notes
        datetime created_at
    }
```

---

## 4. ML & Recommendation Pipeline

### Sequence Diagram

```mermaid
sequenceDiagram
    participant HW as Healthcare Worker
    participant FE as Streamlit Frontend
    participant API as Flask API
    participant SVC as services.py
    participant DB as SQLite
    participant LLM as Gemini AI

    HW->>FE: Submit Assessment Form
    FE->>API: POST /api/v1/predict/{disease}

    API->>SVC: run_prediction(type, data)
    SVC->>SVC: Preprocess (BMI, encoding)
    SVC->>SVC: Load .pkl model
    SVC->>SVC: predict_proba()
    SVC-->>API: Risk Score (0.0 - 1.0)

    API->>DB: Save Assessment + RiskPrediction

    alt Risk >= Medium
        API->>LLM: Generate recommendations prompt
        LLM-->>API: JSON (Diet, Exercise tips)
        API->>DB: Save LifestyleRecommendation
    end

    API-->>FE: Return risk + recommendations
    FE-->>HW: Display Dashboard
```

---

### ML Models

| Disease | Model File | Algorithm |
|:--------|:-----------|:----------|
| **Diabetes** | `diabetes_LightGBM SMOTE.pkl` | LightGBM with SMOTE |
| **Heart** | `heart_SVM Weighted Tuned.pkl` | SVM (Weighted, Tuned) |
| **Liver** | `liver_LightGBM SMOTE.pkl` | LightGBM with SMOTE |
| **Mental Health** | `mental_health_depressiveness_Logistic Regression.pkl` | Logistic Regression |

---

## 5. Component Structure

### Frontend (`medml-frontend/`)

| File | Purpose |
|:-----|:--------|
| `app.py` | Main entry, login routing |
| `api_client.py` | HTTP wrapper for backend API, JWT management |
| `theme.py` | UI styling and theming |
| `pages/1_Patient_Dashboard.py` | Patient read-only view |
| `pages/2_Admin_Dashboard.py` | Admin multi-tab interface |

### Backend (`medml-backend/`)

| Directory/File | Purpose |
|:---------------|:--------|
| `app/api/auth.py` | JWT authentication (Admin/Patient login) |
| `app/api/patients.py` | Patient CRUD |
| `app/api/assessments.py` | Disease assessment endpoints |
| `app/api/predict.py` | ML prediction triggers |
| `app/api/recommendations.py` | Gemini recommendation retrieval |
| `app/api/reports.py` | PDF report generation |
| `app/services.py` | ML loading, preprocessing, Gemini integration |
| `app/models.py` | SQLAlchemy ORM models |
| `models_store/` | Pre-trained `.pkl` model files |

---

## 6. Deployment

- **Tech Stack**: Python 3.9+, Flask, Streamlit, SQLAlchemy, SQLite
- **ML Libraries**: Scikit-Learn, LightGBM, XGBoost, Joblib
- **Environment Variables**: `GEMINI_API_KEY`, `JWT_SECRET_KEY`
- **Local Run**: `start.bat` (Windows) or `start.sh` (Linux/Mac)
