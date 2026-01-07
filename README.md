# 🩺 PreventVance AI — Leading the Future of Early Health Defense

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Kaggle](https://img.shields.io/badge/Datasets-Kaggle-blue?logo=kaggle)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **PreventVance AI** is a comprehensive healthcare management system designed for **rural healthcare workers** to manage patient diagnostics and care delivery.  
> The system enables **early detection and preventive care** by identifying individuals at risk of diseases before they become symptomatic.

---
## 🧭 System Overview

**Project Goal:**  
Address critical gaps in diagnosis and treatment accessibility by enabling early detection and preventive care, particularly in underserved rural areas.

**Target Users:**
- **Primary:** Rural healthcare workers managing patient diagnostics and care delivery  
- **Secondary:** Corporate wellness programs seeking employee health monitoring solutions  

**Value Proposition:**  
Transform raw health data into actionable insights, enabling **preventive interventions** and **reducing long-term health complications**.

---
# PreventVance AI

Healthcare management system for early detection and preventive care.

## Overview
- Backend: Flask API (`/api/v1`) with JWT, rate limits, ML inference, PDF
- Frontend: Streamlit dashboards for admin and patient
- Database: SQLite (dev), migrations via Alembic; prod-ready for PostgreSQL/MySQL
- Models: XGBoost/LightGBM in `medml-backend/models_store`

## 🚀 Quick Start (One-Click)

**Windows:**
Double-click `start.bat`

**Mac/Linux:**
Run `./start.sh`

The application will automatically:
1. Install necessary dependencies
2. Start the Backend API
3. Launch the Frontend Dashboard in your browser (`http://localhost:8501`)

## Login Credentials
- **Admin:** `admin` / `Admin123!`

## Configuration
- Copy `medml-backend/.env.example` to `medml-backend/.env` (if available) to customize settings.
- Default API URL: `http://127.0.0.1:5000/api/v1`

## API Highlights
- **Auth**: `/auth/admin/login`, `/auth/patient/login`
- **Patients**: `/patients` (Create, List, Update, View)
- **Assessments**: `/patients/<id>/assessments/<type>`
- **Predictions**: `/patients/<id>/predict`
- **Reports**: `/patients/<id>/report/pdf`
- **Consultations**: `/consultations`
- **Recommendations**: `/patients/<id>/recommendations`

## Security
- JWT with token blocklist
- Bcrypt password hashing
- Role-based access (admin/patient)
- Rate limiting (`memory://`, `redis://`)
- CORS via env