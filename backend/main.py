from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from typing import Optional, List, Dict, Any
import time
import uvicorn

app = FastAPI(title="suRxit API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[List[Dict]] = []

# Mock data storage
mock_users = {
    "doctor@example.com": {
        "id": "doc1",
        "email": "doctor@example.com",
        "password": "password",  # In production, this would be hashed
        "role": "doctor",
        "name": "Dr. Smith"
    }
}

mock_patients = {
    "patient1": {
        "id": "patient1",
        "name": "John Doe",
        "age": 45,
        "medications": ["Lisinopril", "Metformin"],
        "allergies": ["Penicillin"],
        "conditions": ["Hypertension", "Diabetes Type 2"]
    }
}

# Authentication helper
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        if not token or token != "mock_jwt_token_12345":
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": "doc1", "email": "doctor@example.com", "role": "doctor"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# Health check
@app.get("/")
async def root():
    return {"message": "suRxit API is running", "status": "healthy"}

# Auth endpoints
@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    email = credentials.email
    password = credentials.password
    
    if email in mock_users and mock_users[email]["password"] == password:
        return {
            "token": "mock_jwt_token_12345",
            "user": {
                "id": mock_users[email]["id"],
                "email": mock_users[email]["email"],
                "role": mock_users[email]["role"],
                "name": mock_users[email]["name"]
            },
            "expires_in": 3600
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/logout")
async def logout(user = Depends(get_current_user)):
    return {"message": "Logged out successfully"}

@app.post("/api/auth/register")
async def register(user_data: dict):
    return {"message": "User registered successfully", "user_id": "new_user_123"}

@app.get("/api/auth/verify")
async def verify_token(user = Depends(get_current_user)):
    return {"valid": True, "user": user}

# Prescription analysis endpoint
@app.post("/api/analyze/prescription")
async def analyze_prescription(
    prescription_text: Optional[str] = None,
    file: Optional[UploadFile] = File(None),
    user = Depends(get_current_user)
):
    # Simulate processing time for realistic feel
    await asyncio.sleep(1.5)
    
    # Mock analysis results with realistic medical data
    return {
        "risk_score": 8.2,
        "risk_level": "High",
        "confidence": 0.92,
        "processing_time": 1.5,
        "ddi_interactions": [
            {
                "drug1": "Warfarin",
                "drug2": "Aspirin",
                "severity": "High",
                "mechanism": "Increased bleeding risk due to dual antiplatelet effect",
                "clinical_effects": "Increased risk of gastrointestinal and intracranial bleeding",
                "management": "Consider alternative therapy. If concurrent use necessary, monitor INR closely and watch for bleeding signs",
                "evidence_level": "Strong"
            },
            {
                "drug1": "Metformin",
                "drug2": "Contrast Media",
                "severity": "Moderate", 
                "mechanism": "Risk of lactic acidosis in patients with renal impairment",
                "clinical_effects": "Potential kidney damage and lactic acidosis",
                "management": "Discontinue metformin 48 hours before contrast procedures",
                "evidence_level": "Moderate"
            }
        ],
        "adr_reactions": [
            {
                "drug": "Metformin",
                "reaction": "Gastrointestinal upset",
                "frequency": "Very Common (>10%)",
                "severity": "Mild",
                "management": "Take with food, start with low dose and titrate up slowly",
                "onset": "Within first week",
                "reversible": True
            },
            {
                "drug": "Lisinopril",
                "reaction": "Dry cough",
                "frequency": "Common (1-10%)",
                "severity": "Mild to Moderate",
                "management": "Consider switching to ARB if persistent",
                "onset": "2-4 weeks after initiation",
                "reversible": True
            }
        ],
        "dfi_interactions": [
            {
                "drug": "Warfarin",
                "food": "Leafy green vegetables (Spinach, Kale)",
                "interaction_type": "Vitamin K antagonism",
                "severity": "Moderate",
                "recommendation": "Maintain consistent daily intake rather than avoiding completely",
                "mechanism": "High vitamin K content can counteract warfarin's anticoagulant effect"
            },
            {
                "drug": "Metformin",
                "food": "Alcohol",
                "interaction_type": "Metabolic interaction",
                "severity": "High",
                "recommendation": "Limit alcohol consumption, avoid binge drinking",
                "mechanism": "Increased risk of lactic acidosis, especially with kidney impairment"
            }
        ],
        "home_remedies": [
            {
                "name": "Ginger Tea",
                "indication": "Nausea and digestive issues from Metformin",
                "preparation": "Steep 1-2g fresh ginger root in hot water for 10-15 minutes",
                "precautions": "May enhance anticoagulant effects - consult doctor if taking Warfarin",
                "evidence_level": "Moderate",
                "safety_rating": "Generally Safe",
                "dosage": "1-2 cups daily with meals"
            },
            {
                "name": "Hibiscus Tea",
                "indication": "Blood pressure support (complementary to Lisinopril)",
                "preparation": "Steep 2-3g dried hibiscus flowers in hot water for 15 minutes",
                "precautions": "May potentiate hypotensive effects, monitor blood pressure",
                "evidence_level": "Good",
                "safety_rating": "Generally Safe",
                "dosage": "1 cup twice daily"
            }
        ],
        "alerts": [
            "⚠️ CRITICAL: Patient has documented penicillin allergy - avoid all beta-lactam antibiotics",
            "⚠️ HIGH PRIORITY: Warfarin-Aspirin combination requires immediate clinical review",
            "⚠️ MONITORING: INR levels should be checked within 3-5 days",
            "ℹ️ INFO: Consider gastroprotection with PPI if continuing dual antiplatelet therapy"
        ],
        "recommendations": [
            "Discontinue aspirin and consider clopidogrel as alternative antiplatelet",
            "Schedule INR monitoring every 3-5 days for first 2 weeks",
            "Educate patient on bleeding precautions and when to seek medical attention",
            "Consider proton pump inhibitor for gastric protection"
        ]
    }

# Patient dashboard endpoint
@app.get("/api/patient/dashboard/{patient_id}")
async def get_patient_dashboard(patient_id: str, user = Depends(get_current_user)):
    if patient_id not in mock_patients:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient = mock_patients[patient_id]
    return {
        "patient": patient,
        "recent_prescriptions": [
            {
                "id": "rx001",
                "date": "2024-12-15",
                "medications": ["Lisinopril 10mg daily", "Metformin 500mg twice daily"],
                "prescriber": "Dr. Smith",
                "status": "Active",
                "risk_score": 6.5
            },
            {
                "id": "rx002", 
                "date": "2024-12-10",
                "medications": ["Warfarin 5mg daily", "Aspirin 81mg daily"],
                "prescriber": "Dr. Johnson",
                "status": "Under Review",
                "risk_score": 9.1
            }
        ],
        "safety_alerts": [
            {
                "level": "high",
                "message": "Drug interaction detected between Warfarin and Aspirin",
                "timestamp": "2024-12-15T10:30:00Z",
                "action_required": True
            },
            {
                "level": "medium",
                "message": "INR monitoring due in 2 days",
                "timestamp": "2024-12-14T08:00:00Z", 
                "action_required": False
            }
        ],
        "recommendations": [
            "Take Metformin with food to reduce gastrointestinal upset",
            "Monitor blood pressure daily and record readings",
            "Schedule INR test within next 48 hours",
            "Avoid sudden changes in green vegetable consumption"
        ],
        "vital_signs": {
            "last_updated": "2024-12-15T09:00:00Z",
            "blood_pressure": "142/88 mmHg",
            "heart_rate": "78 bpm",
            "weight": "82 kg",
            "bmi": 27.4
        }
    }

# Chat endpoint with medical AI simulation
@app.post("/api/chat/session")
async def chat_session(chat_request: ChatRequest, user = Depends(get_current_user)):
    message = chat_request.message.lower()
    
    # Simple rule-based responses for demo
    if "drug interaction" in message or "interaction" in message:
        response = "Drug interactions occur when one medication affects how another works. The most serious interaction in your current medications is between Warfarin and Aspirin, which significantly increases bleeding risk. Always consult your healthcare provider before starting new medications."
    elif "side effect" in message or "adverse" in message:
        response = "Common side effects from your medications include: dry cough from Lisinopril (affects 5-10% of patients) and stomach upset from Metformin (very common, >10%). Most side effects are mild and improve with time. Contact your doctor if side effects are severe or persistent."
    elif "food" in message or "diet" in message:
        response = "Important dietary considerations: Maintain consistent intake of green leafy vegetables if taking Warfarin (don't avoid them, just be consistent). Take Metformin with food to reduce stomach upset. Limit alcohol as it can increase lactic acidosis risk with Metformin."
    elif "warfarin" in message:
        response = "Warfarin is a blood thinner that requires careful monitoring. Key points: Take at the same time daily, be consistent with vitamin K foods (greens), avoid aspirin/NSAIDs, watch for unusual bleeding, and get regular INR blood tests as ordered by your doctor."
    elif "metformin" in message:
        response = "Metformin helps control blood sugar and has cardiovascular benefits. Take with meals to reduce stomach upset. Stop taking 48 hours before any procedure with contrast dye. Common side effects include stomach upset and metallic taste, which usually improve over time."
    elif "blood pressure" in message or "lisinopril" in message:
        response = "Lisinopril helps lower blood pressure and protects your heart and kidneys. Monitor your blood pressure regularly. A dry cough affects about 10% of patients - if bothersome, your doctor can switch you to a similar medication (ARB) without this side effect."
    else:
        response = "I'm here to help with questions about your medications, drug interactions, side effects, and general medication safety. Feel free to ask about specific drugs, food interactions, or any concerns about your prescription regimen."
    
    return {
        "message": response,
        "confidence": 0.88,
        "sources": ["Clinical pharmacology database", "Drug interaction guidelines", "FDA prescribing information"],
        "timestamp": time.time()
    }

# Server-Sent Events endpoint for real-time alerts
@app.get("/api/alerts/stream")
async def stream_alerts(user = Depends(get_current_user)):
    async def generate_alerts():
        alerts = [
            {
                "message": "🔴 CRITICAL: High-risk drug interaction detected - Warfarin + Aspirin",
                "level": "critical",
                "timestamp": time.time(),
                "patient_id": "patient1"
            },
            {
                "message": "🟡 REMINDER: INR monitoring due for patient on Warfarin therapy",
                "level": "warning", 
                "timestamp": time.time() + 15,
                "patient_id": "patient1"
            },
            {
                "message": "🟢 INFO: New medication safety guidelines available for review",
                "level": "info",
                "timestamp": time.time() + 30,
                "patient_id": None
            },
            {
                "message": "🔴 ALERT: Patient vitals indicate possible medication adjustment needed",
                "level": "critical",
                "timestamp": time.time() + 45,
                "patient_id": "patient1"
            }
        ]
        
        for i, alert in enumerate(alerts):
            yield f"data: {json.dumps(alert)}\n\n"
            if i < len(alerts) - 1:  # Don't sleep after last alert
                await asyncio.sleep(15)  # Send alert every 15 seconds
    
    return StreamingResponse(
        generate_alerts(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

if __name__ == "__main__":
    print("🏥 Starting suRxit Backend API Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📋 API docs available at: http://localhost:8000/docs")
    print("🔐 Demo credentials: doctor@example.com / password")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)