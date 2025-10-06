from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import json
import asyncio
import time
import uuid
from datetime import datetime, timedelta
import os
from pathlib import Path

# Import custom modules
from auth import AuthManager
from models import PrescriptionAnalysis, ChatMessage, Patient
from ai_service import MedLMService
from database import get_db, SessionLocal

app = FastAPI(
    title="suRxit API",
    description="AI-powered medication safety dashboard backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:3000",
        "https://your-production-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
auth_manager = AuthManager()
medlm_service = MedLMService()

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "doctor"

class ChatRequest(BaseModel):
    message: str
    context: List[Dict[str, str]] = []

class PrescriptionRequest(BaseModel):
    text: Optional[str] = None
    patient_id: Optional[str] = None

# Mock data for development
MOCK_PATIENTS = {
    "patient1": {
        "id": "patient1",
        "name": "John Doe",
        "age": 45,
        "gender": "male",
        "weight": 80,
        "height": 175,
        "medications": ["Lisinopril 10mg", "Metformin 500mg"],
        "allergies": ["Penicillin", "Sulfa drugs"],
        "conditions": ["Hypertension", "Type 2 Diabetes"],
        "lab_values": {
            "creatinine": 1.1,
            "egfr": 75,
            "hba1c": 7.2,
            "bp_systolic": 140,
            "bp_diastolic": 90
        }
    }
}

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = await auth_manager.verify_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    try:
        result = await auth_manager.authenticate_user(request.email, request.password)
        return {
            "token": result["token"],
            "user": result["user"],
            "expires_in": 3600
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    try:
        user = await auth_manager.create_user(
            email=request.email,
            password=request.password,
            name=request.name,
            role=request.role
        )
        return {"message": "User registered successfully", "user_id": user["id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/logout")
async def logout(user = Depends(get_current_user)):
    return {"message": "Logged out successfully"}

@app.get("/api/auth/verify")
async def verify_token(user = Depends(get_current_user)):
    return {"valid": True, "user": user}

# Prescription analysis endpoint
@app.post("/api/analyze/prescription")
async def analyze_prescription(
    prescription_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    patient_id: Optional[str] = Form(None),
    user = Depends(get_current_user)
):
    try:
        # Process uploaded file if provided
        prescription_content = prescription_text
        if file:
            # Save uploaded file temporarily
            file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Extract text from file (OCR for images, text extraction for PDFs)
            prescription_content = await extract_text_from_file(file_path)
            os.unlink(file_path)  # Clean up temp file

        if not prescription_content:
            raise HTTPException(status_code=400, detail="No prescription content provided")

        # Get patient context if provided
        patient_data = None
        if patient_id and patient_id in MOCK_PATIENTS:
            patient_data = MOCK_PATIENTS[patient_id]

        # Analyze prescription using AI service
        analysis = await medlm_service.analyze_prescription(
            prescription_content,
            patient_data=patient_data
        )

        # Calculate risk score
        risk_score = calculate_risk_score(analysis)

        return {
            "risk_score": risk_score,
            "risk_level": get_risk_level(risk_score),
            "ddi_interactions": analysis.get("drug_interactions", []),
            "adr_reactions": analysis.get("adverse_reactions", []),
            "dfi_interactions": analysis.get("food_interactions", []),
            "home_remedies": analysis.get("home_remedies", []),
            "alerts": analysis.get("alerts", []),
            "recommendations": analysis.get("recommendations", []),
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Patient dashboard endpoint
@app.get("/api/patient/dashboard/{patient_id}")
async def get_patient_dashboard(patient_id: str, user = Depends(get_current_user)):
    if patient_id not in MOCK_PATIENTS:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient = MOCK_PATIENTS[patient_id]
    
    return {
        "patient": patient,
        "recent_prescriptions": [
            {
                "id": "rx_001",
                "date": "2024-12-15",
                "medications": patient["medications"],
                "prescriber": "Dr. Smith",
                "status": "active"
            }
        ],
        "safety_alerts": [
            "Drug interaction detected between Lisinopril and NSAIDs",
            "Monitor kidney function due to ACE inhibitor use"
        ],
        "recommendations": [
            "Take Metformin with food to reduce GI upset",
            "Monitor blood pressure daily",
            "Check blood glucose levels as directed",
            "Avoid sudden position changes due to Lisinopril"
        ],
        "upcoming_appointments": [
            {
                "date": "2024-12-20",
                "type": "Follow-up",
                "provider": "Dr. Smith"
            }
        ],
        "lab_reminders": [
            "HbA1c due in 2 weeks",
            "Kidney function check recommended"
        ]
    }

# Chat endpoint with MedLM integration
@app.post("/api/chat/session")
async def chat_session(request: ChatRequest, user = Depends(get_current_user)):
    try:
        # Get AI response from MedLM service
        response = await medlm_service.get_chat_response(
            message=request.message,
            context=request.context,
            user_role=user.get("role", "user")
        )
        
        return {
            "message": response["content"],
            "confidence": response.get("confidence", 0.85),
            "sources": response.get("sources", ["Clinical guidelines", "Drug database"]),
            "session_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service unavailable: {str(e)}")

# Real-time alerts streaming endpoint
@app.get("/api/alerts/stream")
async def stream_alerts(user = Depends(get_current_user)):
    async def generate_alerts():
        alerts = [
            "New drug interaction detected for Patient #12345",
            "Critical lab value alert: Creatinine elevated",
            "Prescription renewal required for John Doe",
            "Safety alert: Dosage adjustment recommended",
            "New clinical guideline update available",
            "Patient reported adverse reaction"
        ]
        
        alert_index = 0
        while alert_index < len(alerts):
            alert_data = {
                "id": str(uuid.uuid4()),
                "message": alerts[alert_index],
                "severity": "medium" if alert_index % 2 == 0 else "high",
                "timestamp": datetime.now().isoformat(),
                "patient_id": f"patient_{alert_index + 1}",
                "type": "safety_alert"
            }
            
            yield f"data: {json.dumps(alert_data)}\n\n"
            alert_index += 1
            await asyncio.sleep(15)  # Send alert every 15 seconds
    
    return StreamingResponse(
        generate_alerts(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

# Drug information lookup
@app.get("/api/drugs/{drug_name}")
async def get_drug_info(drug_name: str, user = Depends(get_current_user)):
    # Mock drug information - in production, connect to drug database
    return {
        "name": drug_name,
        "generic_name": drug_name.lower(),
        "brand_names": [drug_name],
        "drug_class": "ACE Inhibitor" if "lisinopril" in drug_name.lower() else "Unknown",
        "indications": ["Hypertension", "Heart failure"],
        "contraindications": ["Pregnancy", "Angioedema history"],
        "side_effects": ["Dry cough", "Hyperkalemia", "Hypotension"],
        "interactions": ["NSAIDs", "Potassium supplements"],
        "monitoring": ["Blood pressure", "Kidney function", "Electrolytes"]
    }

# Utility functions
async def extract_text_from_file(file_path: str) -> str:
    """Extract text from uploaded file using OCR or text extraction"""
    # Placeholder for file processing
    # In production, implement OCR for images and text extraction for PDFs
    return "Sample prescription text extracted from file"

def calculate_risk_score(analysis: Dict[str, Any]) -> float:
    """Calculate overall risk score based on analysis results"""
    base_score = 3.0
    
    # Increase score based on interactions
    ddi_count = len(analysis.get("drug_interactions", []))
    adr_count = len(analysis.get("adverse_reactions", []))
    
    risk_score = base_score + (ddi_count * 1.5) + (adr_count * 1.0)
    return min(risk_score, 10.0)  # Cap at 10

def get_risk_level(score: float) -> str:
    """Convert numeric risk score to risk level"""
    if score <= 3.0:
        return "Low"
    elif score <= 6.0:
        return "Medium"
    elif score <= 8.0:
        return "High"
    else:
        return "Critical"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
