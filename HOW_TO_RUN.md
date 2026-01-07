# How to Run the Healthcare App

## 🚀 Quick Start (Recommended)

### Option 1: One-Click Start (Windows)
1. **Double-click `start.bat`** in the project root directory.
2. The script will install dependencies and start both backend and frontend.
3. Your browser will open **http://localhost:8501** automatically.

### Option 2: Linux / macOS
1. Open a terminal in the project root.
2. Run: `./start.sh`
3. Connect to **http://localhost:8501**.

---

## 📋 Prerequisites
- **Python 3.8 or higher**
- **pip** package manager
- **Git**

---

## 🛠️ Manual Startup

If you prefer to run services manually:

### Step 1: Install Dependencies
```bash
# Backend
cd medml-backend
pip install -r requirements.txt

# Frontend
cd ../medml-frontend
pip install -r requirements.txt
```

### Step 2: Start Backend Server
```bash
cd medml-backend
python run.py
```
*Wait for: "Running on http://127.0.0.1:5000"*

### Step 3: Start Frontend (New Terminal)
```bash
cd medml-frontend
streamlit run app.py
```
*Access: http://localhost:8501*

---

## 🔑 Default Credentials

### Admin (Healthcare Worker)
- **Username:** `admin`
- **Password:** `Admin123!`

### Test Patient
- **ABHA ID:** `12345678901234`
- **Password:** `12345678901234@Default123`

---

## 💻 System Requirements
- **Python 3.8+**
- **Web Browser** (Chrome, Firefox, Edge)
- **8GB RAM** recommended
- **Internet connection** (optional, for external AI APIs)

