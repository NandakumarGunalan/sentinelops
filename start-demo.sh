#!/bin/bash

echo "🛡️  SentinelOps Demo Startup"
echo "================================"
echo ""

# Check if backend dependencies are installed
if [ ! -d "backend/venv" ]; then
    echo "📦 Setting up backend virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements-demo.txt
    cd ..
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "🚀 Starting SentinelOps Demo..."
echo ""
echo "Backend will start on: http://localhost:8000"
echo "Frontend will start on: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
cd backend
source venv/bin/activate
python demo_server.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait
