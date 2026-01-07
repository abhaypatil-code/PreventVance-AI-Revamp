# PreventVance AI - System Architecture

> **Comprehensive Technical Design Document**
> *Version 2.0 | Last Updated: January 2026*

## 1. Executive Summary

**PreventVance AI** is a specialized healthcare analytics platform designed to empower healthcare workers in rural and resource-constrained environments. It enables the early detection of chronic diseases (Diabetes, Heart Disease, Liver Disease, Mental Health issues) using Machine Learning and provides personalized lifestyle recommendations via Generative AI.

The system is built on a decoupled **Client-Server architecture**, featuring a responsive **Streamlit** frontend for interactive dashboards and a robust **Flask** backend for API management, ML inference, and data persistence.

---

## 2. High-Level Architecture

### System Context Diagram (Level 0)
This diagram illustrates the interactions between the primary users and external systems.

```mermaid
C4Context
    title System Context Diagram - PreventVance AI

    Person(admin, "Healthcare Worker", "Registered medical staff who assesses patients and manages records.")
    Person(patient, "Patient", "Individual receiving care and viewing their own health reports.")

    System_Boundary(system, "PreventVance AI Platform") {
        System(webapp, "Web Application", "Provides dashboards for assessment, reporting, and management.")
    }

    System_Ext(gemini, "Google Gemini AI", "Generates personalized lifestyle recommendations.")
    
    Rel(admin, webapp, " performs assessments, manages patients using", "HTTPS")
    Rel(patient, webapp, " views health records using", "HTTPS")
    Rel(webapp, gemini, " sends risk profiles / receives recommendations", "REST API")
```

### Container Architecture (Level 1)
The high-level technical components and their responsibilities.

```mermaid
graph TD
    subgraph "Client Layer"
        Frontend[Streamlit Frontend]
        style Frontend fill:#f9f,stroke:#333,stroke-width:2px
    end

    subgraph "Server Layer"
        API[Flask REST API]
        style API fill:#bbf,stroke:#333,stroke-width:2px
        
        Auth[Auth Service]
        ML[ML Inference Engine]
        Recs[Recommendation Service]
    end

    subgraph "Data Layer"
        DB[(SQLite / SQL DB)]
        ModelStore["Model Store (.pkl)"]
    end

    subgraph "External"
        GenAI[Gemini 2.0 Flash]
    end

    Frontend <-->|HTTP/JSON| API
    API --> Auth
    API --> ML
    API --> Recs
    
    Auth --> DB
    ML --> ModelStore
    Recs --> GenAI
    Recs --> DB
    
    API -->|CRUD| DB
```

---

## 3. Data Architecture (ER Diagram)

The database schema is designed using **SQLAlchemy ORM** and enforces strict referential integrity. It supports users, patients, disease-specific assessments, predictions, and recommendations.

```mermaid
erDiagram
    User ||--o{ Patient : "registers"
    User ||--o{ Consultation : "conducts"
    
    Patient ||--o{ DiabetesAssessment : "has history of"
    Patient ||--o{ HeartAssessment : "has history of"
    Patient ||--o{ LiverAssessment : "has history of"
    Patient ||--o{ MentalHealthAssessment : "has history of"
    
    Patient ||--o{ RiskPrediction : "has results"
    RiskPrediction ||--o{ LifestyleRecommendation : "triggers"
    Patient ||--o{ LifestyleRecommendation : "receives"
    
    Patient ||--o{ Consultation : "attends"
    Patient ||--o{ ConsultationNote : "has notes"

    User {
        int id PK
        string username
        string role "Admin/Doctor"
        string facility_name
    }

    Patient {
        int id PK
        string abha_id UK "Unique Health ID"
        string name
        int age
        float bmi
    }

    RiskPrediction {
        int id PK
        float diabetes_risk_score
        float heart_risk_score
        string model_version
        datetime predicted_at
    }

    LifestyleRecommendation {
        int id PK
        string category "Diet/Exercise/Sleep"
        string risk_level
        text content_hindi
        text content_english
    }
```

---

## 4. Machine Learning & Recommendation Pipeline

The core intelligence of PreventVance AI involves a two-step process: **Predictive Analytics** (ML) followed by **Generative Guidance** (LLM).

### Operational Workflow

```mermaid
sequenceDiagram
    participant Admin as Healthcare Worker
    participant FE as Frontend
    participant API as Flask Backend
    participant ML as ML Service
    participant DB as Database
    participant LLM as Gemini AI

    Note over Admin, FE: 1. Assessment
    Admin->>FE: Fills Patient Form (e.g., Diabetes)
    FE->>API: POST /api/v1/predict/diabetes (JSON)

    Note over API, ML: 2. Inference
    API->>ML: Preprocess Data (Scale/Encode)
    ML->>ML: Load LightGBM Model
    ML->>ML: Generate Risk Probability
    ML-->>API: Return Score (e.g., 0.85 - High)

    Note over API, DB: 3. Persistence
    API->>DB: Save Assessment & Risk Score

    Note over API, LLM: 4. Recommendation (Async/Triggered)
    alt Risk Level > Medium
        API->>LLM: Prompt: "Patient High Diabetic Risk. Give Diet/Exercise tips."
        LLM-->>API: Return JSON {Category: "Diet", Tip: "Avoid white rice..."}
        API->>DB: Save Personalized Recommendations
    end

    API-->>FE: Return Risk Report & Tips
    FE-->>Admin: Display Dashboard
```

### ML Models
| Disease | Algorithm | Tuned Hyperparameters | Features |
| :--- | :--- | :--- | :--- |
| **Diabetes** | LightGBM (SMOTE) | `learning_rate`, `num_leaves` | Glucose, BP, BMI, Age, Insulin |
| **Heart** | SVM (Weighted) | `kernel='rbf'`, `C` | Cholesterol, BP, Smoking, Age |
| **Liver** | LightGBM | `max_depth` | Bilirubin, Enzymes (SGPT/SGOT), Protein |
| **Mental Health** | Logistic Regression | `solver='liblinear'` | PHQ-9, GAD-7 Scores |

---

## 5. Component Details

### Frontend (`medml-frontend/`)
*   **`app.py`**: Main entry point handling authentication routing.
*   **`api_client.py`**: Singleton service wrapper for all Backend API calls. Manages JWT tokens.
*   **`pages/`**:
    *   `1_Patient_Dashboard.py`: Read-only view for patients.
    *   `2_Admin_Dashboard.py`: Complex multi-tab interface for Registrations, Assessments, and Analytics.

### Backend (`medml-backend/`)
*   **`app/api/`**: Blueprints for distinct functional areas (`auth`, `patients`, `assessments`, `predict`).
*   **`app/services.py`**:
    *   **ML Loading**: Loads `.pkl` models into memory on startup.
    *   **Preprocessing**: Handles feature engineering (e.g., BMI calc, One-Hot Encoding) ensuring training-inference consistency.
    *   **Gemini Integration**: Manages prompts and JSON parsing for the LLM.
*   **`app/models.py`**: Defines the data schema.

## 6. Implementation & Deployment
*   **Tech Stack**: Python 3.9+, Flask 2.0+, Streamlit, SQLAlchemy.
*   **Environment**:
    *   Models are stored locally in `models_store/`.
    *   Environment variables manage secrets (`GEMINI_API_KEY`, `JWT_SECRET_KEY`).
*   **Scalability**: The stateless Flask API allows for horizontal scaling behind a load balancer (e.g., Nginx) if needed.
