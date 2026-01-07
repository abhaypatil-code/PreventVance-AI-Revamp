#!/bin/bash

echo "===================================================="
echo "  PreventVance AI - System Startup"
echo "===================================================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    exit 1
fi

echo ""
echo "[1/3] Checking and Installing Dependencies..."

echo "   - Backend dependencies..."
cd medml-backend
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[WARNING] Issue installing backend dependencies. Continuing..."
fi
cd ..

echo "   - Frontend dependencies..."
cd medml-frontend
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[WARNING] Issue installing frontend dependencies. Continuing..."
fi
cd ..

echo ""
echo "[2/3] Starting Backend Service..."
cd medml-backend
python3 run.py &
BACKEND_PID=$!
cd ..
echo "   - Backend started (PID: $BACKEND_PID)"

echo ""
echo "[3/3] Starting Frontend Application..."
echo "   - Launching Streamlit..."
cd medml-frontend
streamlit run app.py --server.address localhost --server.port 8501 &
FRONTEND_PID=$!
cd ..

echo ""
echo "[SUCCESS] System is running!"
echo "Press Ctrl+C to stop all services."

# Wait for process exit
wait $BACKEND_PID $FRONTEND_PID
