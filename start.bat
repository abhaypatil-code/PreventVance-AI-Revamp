@echo off
SETLOCAL EnableExtensions

echo ====================================================
echo   PreventVance AI - System Startup
echo ====================================================

REM Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo.
echo [1/3] Checking and Installing Dependencies...

echo    - Backend dependencies...
cd medml-backend
pip install -r requirements.txt >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install backend dependencies.
    pass
)
cd ..

echo    - Frontend dependencies...
cd medml-frontend
pip install -r requirements.txt >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install frontend dependencies.
    pass
)
cd ..

echo.
echo [2/3] Starting Backend Service...
start "PreventVance Backend" cmd /k "cd medml-backend && python run.py"

echo.
echo [3/3] Starting Frontend Application...
echo    - Launching Streamlit...
echo    - The application should open in your browser automatically.
cd medml-frontend
start "PreventVance Frontend" cmd /k "streamlit run app.py --server.address localhost --server.port 8501"

echo.
echo [SUCCESS] System starting up!
echo Close the popup windows to stop the servers.
echo ====================================================

EXIT /B 0
