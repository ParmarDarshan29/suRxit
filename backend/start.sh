#!/bin/bash

# suRxit Backend Startup Script
echo "🏥 suRxit Backend - AI-Powered Medication Safety API"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/pyvenv.cfg" ] || [ "requirements.txt" -nt "venv/pyvenv.cfg" ]; then
    echo "📥 Installing/updating dependencies..."
    pip install -r requirements.txt
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    echo "✏️ Please edit .env file with your configuration"
fi

# Initialize database
echo "🗄️ Initializing database..."
python database.py

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 8000 is already in use. Stopping existing process..."
    pkill -f "uvicorn.*main:app"
    sleep 2
fi

echo ""
echo "🚀 Starting FastAPI development server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📚 ReDoc Documentation: http://localhost:8000/redoc"
echo ""
echo "🔑 Test accounts:"
echo "   Doctor: doctor@example.com / password"
echo "   Admin: admin@surxit.com / admin123"
echo ""

# Start the FastAPI server
python main.py