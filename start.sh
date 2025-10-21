#!/bin/bash

echo "🚀 Starting Bangla Chat Pro..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Start backend in background
echo "⚡ Starting FastAPI backend..."
python run.py &
BACKEND_PID=$!

# Go back to root directory
cd ..

# Setup frontend
echo "🎨 Setting up frontend..."

# Install Node dependencies
echo "📥 Installing Node dependencies..."
npm install

# Start frontend in background
echo "⚡ Starting Next.js frontend..."
npm run dev &
FRONTEND_PID=$!

echo "✅ Bangla Chat Pro is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
