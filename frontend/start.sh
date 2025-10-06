#!/bin/bash

# suRxit Frontend Startup Script
# This script helps manage the development environment

echo "🏥 suRxit - AI-Powered Medication Safety Dashboard"
echo "=================================================="

# Check if backend is running
echo "🔍 Checking backend availability..."
if curl -s http://localhost:8000/api/auth/verify > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
    # Set to use real API
    sed -i 's/VITE_ENABLE_MOCK_DATA=true/VITE_ENABLE_MOCK_DATA=false/' .env
    echo "🔧 Configured to use real backend API"
else
    echo "❌ Backend not detected at http://localhost:8000"
    echo "🔧 Configured to use mock data for demo"
    # Set to use mock data
    sed -i 's/VITE_ENABLE_MOCK_DATA=false/VITE_ENABLE_MOCK_DATA=true/' .env
    
    echo ""
    echo "📖 To set up the backend server:"
    echo "   1. See backend-setup.md for detailed instructions"
    echo "   2. Choose Python FastAPI or Node.js Express"
    echo "   3. Run the backend server on port 8000"
    echo "   4. Restart this frontend server"
    echo ""
fi

echo ""
echo "🚀 Starting frontend development server..."
echo "📱 Frontend will be available at: http://localhost:5174"
echo "🎯 Use demo credentials: doctor@example.com / password"
echo ""

# Start the development server
npm run dev