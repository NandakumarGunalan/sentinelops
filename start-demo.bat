@echo off
echo 🛡️  SentinelOps Demo Startup
echo ================================
echo.

REM Check if backend dependencies are installed
if not exist "backend\venv" (
    echo 📦 Setting up backend virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements-demo.txt
    cd ..
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo 🚀 Starting SentinelOps Demo...
echo.
echo Backend will start on: http://localhost:8000
echo Frontend will start on: http://localhost:5173
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start backend
start "SentinelOps Backend" cmd /k "cd backend && venv\Scripts\activate && python demo_server.py"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend
start "SentinelOps Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Demo started! Open http://localhost:5173 in your browser
echo.
pause
