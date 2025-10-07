#!/bin/bash

echo "🔧 suRxit Prescription Analysis Diagnostic Script"
echo "================================================"

echo ""
echo "📡 Backend Health Check:"
echo "------------------------"
curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "❌ Backend not responding or jq not available"

echo ""
echo "🧪 Backend Prescription Endpoint Test:"
echo "--------------------------------------"
curl -X POST \
  -F "text=Diagnostic test prescription" \
  -F "allergies=[\"Test Allergy\"]" \
  http://localhost:8000/api/analyze/prescription \
  -s | jq '.risk_score, .level' 2>/dev/null || echo "❌ Prescription endpoint failed"

echo ""
echo "🌐 Frontend Accessibility:"
echo "-------------------------"
curl -s http://localhost:5173 >/dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend not accessible"

echo ""
echo "📁 Environment File Check:"
echo "--------------------------"
if [ -f "/workspaces/suRxit/frontend/.env" ]; then
    echo "✅ .env file exists"
    echo "API Base URL: $(grep VITE_API_BASE_URL /workspaces/suRxit/frontend/.env)"
    echo "Mock Data: $(grep VITE_ENABLE_MOCK_DATA /workspaces/suRxit/frontend/.env)"
else
    echo "❌ .env file missing"
fi

echo ""
echo "🔄 Process Check:"
echo "----------------"
echo "Backend processes:"
ps aux | grep uvicorn | grep -v grep || echo "❌ No uvicorn processes found"
echo ""
echo "Frontend processes:"
ps aux | grep vite | grep -v grep || echo "❌ No vite processes found"

echo ""
echo "🔧 Next Steps:"
echo "-------------"
echo "1. Open http://localhost:5173 in browser"
echo "2. Open Browser DevTools (F12)"
echo "3. Go to Console tab"
echo "4. Try submitting prescription form"
echo "5. Check console output and network tab"
echo "6. Update troubleshooting-prescription-analysis.md with findings"