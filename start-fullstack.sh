#!/bin/bash

# suRxit Full-Stack Startup Script
echo "🏥 suRxit - Full-Stack Medical AI Dashboard"
echo "============================================"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start backend
start_backend() {
    echo "🚀 Starting Backend API..."
    cd /workspaces/suRxit/backend
    
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    if [ ! -f "venv/.deps_installed" ]; then
        echo "📥 Installing dependencies..."
        pip install -r requirements.txt
        touch venv/.deps_installed
    fi
    
    # Check if backend is already running
    if check_port 8000; then
        echo "✅ Backend already running on port 8000"
    else
        echo "📍 Starting backend on http://localhost:8000"
        uvicorn simple_main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        sleep 3  # Give backend time to start
        
        if check_port 8000; then
            echo "✅ Backend started successfully"
        else
            echo "❌ Backend failed to start"
            return 1
        fi
    fi
}

# Function to start frontend
start_frontend() {
    echo "🚀 Starting Frontend..."
    cd /workspaces/suRxit/frontend
    
    # Set to use real backend
    sed -i 's/VITE_ENABLE_MOCK_DATA=true/VITE_ENABLE_MOCK_DATA=false/' .env
    
    # Check if frontend is already running
    if check_port 5173; then
        echo "✅ Frontend already running on port 5173"
    else
        echo "📍 Starting frontend on http://localhost:5173"
        npm run dev &
        FRONTEND_PID=$!
        sleep 5  # Give frontend time to start
        
        if check_port 5173; then
            echo "✅ Frontend started successfully"
        else
            echo "❌ Frontend failed to start"
            return 1
        fi
    fi
}

# Function to show status
show_status() {
    echo ""
    echo "🌐 suRxit Dashboard Status:"
    echo "=========================="
    
    if check_port 8000; then
        echo "✅ Backend API:      http://localhost:8000"
        echo "📖 API Docs:        http://localhost:8000/docs"
    else
        echo "❌ Backend API:      Not running"
    fi
    
    if check_port 5173; then
        echo "✅ Frontend App:     http://localhost:5173"
    else
        echo "❌ Frontend App:     Not running"
    fi
    
    echo ""
    echo "🔑 Test Credentials:"
    echo "   Email:    doctor@example.com"
    echo "   Password: password"
    echo ""
    echo "💡 Tips:"
    echo "   - Use Ctrl+C to stop services"
    echo "   - Check logs in terminal for debugging"
    echo "   - Refresh browser if connection issues occur"
}

# Main execution
case "${1:-start}" in
    "backend")
        start_backend
        ;;
    "frontend") 
        start_frontend
        ;;
    "status")
        show_status
        ;;
    "stop")
        echo "🛑 Stopping services..."
        pkill -f "uvicorn.*simple_main:app" 2>/dev/null || true
        pkill -f "vite.*dev" 2>/dev/null || true
        echo "✅ Services stopped"
        ;;
    "start"|*)
        start_backend
        if [ $? -eq 0 ]; then
            start_frontend
        fi
        show_status
        ;;
esac