#!/bin/bash

# Start script for Newspaper Layout Parser

echo "🚀 Starting Newspaper Layout Parser..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v14 or higher."
    exit 1
fi

# Check if backend dependencies are installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  Backend dependencies not found. Installing..."
    pip3 install -r requirements.txt
fi

# Check if frontend dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "⚠️  Frontend dependencies not found. Installing..."
    npm install
fi

echo "✅ Dependencies checked"
echo ""
echo "📝 Starting backend server on http://localhost:5000"
echo "📝 Starting frontend server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
npm start

# Kill backend when frontend stops
kill $BACKEND_PID 2>/dev/null

