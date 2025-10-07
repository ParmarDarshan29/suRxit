from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import time
from datetime import datetime

# Import the AI service for real analysis
from ai_service import MedLMService

app = FastAPI(title="suRxit API", version="1.0.0")

# Initialize the AI service
try:
    from ai_service import MedLMService
    medlm_service = MedLMService()
    print("✅ AI Service loaded successfully")
except ImportError as e:
    print(f"⚠️  AI Service not available: {e}")
    medlm_service = None

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://upgraded-train-9wpgvrx45q72rpr-5173.app.github.dev",
        "https://upgraded-train-9wpgvrx45q72rpr-8000.app.github.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models
class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str
    context: list = []

# Mock user data
MOCK_USERS = {
    "doctor@example.com": {"password": "password", "name": "Dr. Smith", "role": "doctor"},
    "admin@surxit.com": {"password": "admin123", "name": "Admin", "role": "admin"}
}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Simple authentication
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    user = MOCK_USERS.get(request.email)
    if user and user["password"] == request.password:
        return {
            "token": "mock_jwt_token_12345",
            "user": {"email": request.email, "name": user["name"], "role": user["role"]},
            "expires_in": 3600
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/verify")
async def verify_token():
    return {"valid": True, "user": {"email": "doctor@example.com", "role": "doctor"}}

# Prescription analysis
@app.post("/api/analyze/prescription")
async def analyze_prescription(
    text: str = Form(...),
    allergies: str = Form("[]"),
    file: Optional[UploadFile] = File(None)
):
    # Parse allergies JSON string
    try:
        allergies_list = json.loads(allergies)
    except json.JSONDecodeError:
        allergies_list = []
    
    # Handle file upload if present
    file_content = None
    if file:
        file_content = await file.read()
        # In a real implementation, you'd process the file content here
        # For now, we'll just acknowledge it was received
    
    # Use real AI service if available, otherwise fall back to enhanced mock
    if medlm_service:
        try:
            # Use the real AI service for analysis
            analysis = await medlm_service.analyze_prescription(
                text, 
                patient_data={
                    "allergies": allergies_list,
                    "age": 65,  # Default for demo
                    "conditions": []
                }
            )
            
            # Convert AI service response to expected format
            risk_score = analysis.get("risk_score", 50)
            risk_level = "HIGH" if risk_score > 70 else "MOD" if risk_score > 40 else "LOW"
            
            return {
                "risk_score": risk_score,
                "level": risk_level,
                "ddi_summary": analysis.get("drug_interactions", []),
                "adr_flags": analysis.get("adverse_reactions", []),
                "dfi_cautions": analysis.get("food_interactions", []),
                "home_remedies": analysis.get("home_remedies", []),
                "evidence_paths": analysis.get("evidence_paths", []),
                "contributors": analysis.get("risk_factors", []),
                "history": [
                    {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "summary": f"Analysis of: {text[:50]}...",
                        "risk_score": risk_score,
                        "level": risk_level
                    }
                ],
                "analysis_input": {
                    "text": text,
                    "allergies": allergies_list,
                    "file_uploaded": file is not None,
                    "file_name": file.filename if file else None
                }
            }
            
        except Exception as e:
            print(f"AI Service error: {e}")
            # Fall through to mock data if AI service fails
    
    # Enhanced mock analysis that actually responds to input
    detected_drugs = extract_drug_names(text.lower())
    allergy_conflicts = check_allergy_conflicts(detected_drugs, allergies_list)
    drug_interactions = find_drug_interactions(detected_drugs)
    
    # Calculate risk based on actual input
    base_risk = 30
    if len(detected_drugs) > 2:
        base_risk += 20  # Multiple drugs increase risk
    if allergy_conflicts:
        base_risk += 25  # Allergy conflicts are serious
    if drug_interactions:
        base_risk += len(drug_interactions) * 15
    
    risk_score = min(base_risk, 95)  # Cap at 95
    risk_level = "HIGH" if risk_score > 70 else "MOD" if risk_score > 40 else "LOW"
    
    return {
        "risk_score": risk_score,
        "level": risk_level,
        "ddi_summary": drug_interactions,
        "adr_flags": allergy_conflicts + generate_side_effects(detected_drugs),
        "dfi_cautions": generate_food_interactions(detected_drugs),
        "home_remedies": generate_home_remedies(detected_drugs),
        "evidence_paths": [
            f"Drug database analysis → {', '.join(detected_drugs)} → Risk assessment",
            f"Allergy cross-reference → {', '.join(allergies_list)} → Safety check"
        ],
        "contributors": [
            f"Detected medications: {', '.join(detected_drugs) if detected_drugs else 'None detected'}",
            f"Known allergies: {', '.join(allergies_list) if allergies_list else 'None reported'}",
            f"Drug count: {len(detected_drugs)} medications",
            f"Interaction count: {len(drug_interactions)} potential interactions"
        ],
        "history": [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": f"Analysis of: {text[:50]}...",
                "risk_score": risk_score,
                "level": risk_level
            }
        ],
        "analysis_input": {
            "text": text,
            "allergies": allergies_list,
            "file_uploaded": file is not None,
            "file_name": file.filename if file else None
        }
    }

# Helper functions for enhanced mock analysis
def extract_drug_names(text):
    """Extract common drug names from prescription text"""
    common_drugs = [
        "warfarin", "aspirin", "metformin", "lisinopril", "atorvastatin",
        "amlodipine", "metoprolol", "hydrochlorothiazide", "omeprazole",
        "levothyroxine", "gabapentin", "losartan", "furosemide", "prednisone",
        "ibuprofen", "acetaminophen", "tramadol", "sertraline", "citalopram"
    ]
    
    detected = []
    for drug in common_drugs:
        if drug in text:
            detected.append(drug.title())
    
    return detected

def check_allergy_conflicts(drugs, allergies):
    """Check for allergy conflicts"""
    conflicts = []
    allergy_map = {
        "penicillin": ["amoxicillin", "ampicillin"],
        "sulfa": ["sulfamethoxazole", "furosemide"],
        "aspirin": ["aspirin", "nsaids"],
        "nsaids": ["ibuprofen", "naproxen", "aspirin"]
    }
    
    for allergy in [a.lower() for a in allergies]:
        if allergy in allergy_map:
            for drug in drugs:
                if drug.lower() in allergy_map[allergy]:
                    conflicts.append(f"ALLERGY ALERT: {drug} conflicts with {allergy} allergy")
    
    return conflicts

def find_drug_interactions(drugs):
    """Find interactions between detected drugs"""
    interactions = []
    interaction_db = {
        ("warfarin", "aspirin"): {
            "drug1": "Warfarin", "drug2": "Aspirin",
            "interaction": "Increased bleeding risk", "severity": "HIGH"
        },
        ("warfarin", "ibuprofen"): {
            "drug1": "Warfarin", "drug2": "Ibuprofen", 
            "interaction": "Enhanced anticoagulation", "severity": "HIGH"
        },
        ("lisinopril", "ibuprofen"): {
            "drug1": "Lisinopril", "drug2": "Ibuprofen",
            "interaction": "Reduced antihypertensive effect", "severity": "MOD"
        },
        ("metformin", "furosemide"): {
            "drug1": "Metformin", "drug2": "Furosemide",
            "interaction": "Risk of lactic acidosis", "severity": "MOD"
        }
    }
    
    drug_names_lower = [d.lower() for d in drugs]
    for (drug1, drug2), interaction in interaction_db.items():
        if drug1 in drug_names_lower and drug2 in drug_names_lower:
            interactions.append(interaction)
    
    return interactions

def generate_side_effects(drugs):
    """Generate relevant side effects for detected drugs"""
    side_effects = []
    effects_db = {
        "warfarin": "Monitor for unusual bleeding or bruising",
        "metformin": "Watch for nausea, stomach upset, or unusual fatigue",
        "lisinopril": "Monitor for persistent dry cough or dizziness",
        "atorvastatin": "Report muscle pain or weakness",
        "aspirin": "Watch for stomach irritation or bleeding"
    }
    
    for drug in drugs:
        if drug.lower() in effects_db:
            side_effects.append(effects_db[drug.lower()])
    
    return side_effects

def generate_food_interactions(drugs):
    """Generate food interaction warnings"""
    interactions = []
    food_db = {
        "warfarin": {
            "drug": "Warfarin", "food": "Leafy greens (Vitamin K)",
            "advice": "Maintain consistent vitamin K intake"
        },
        "metformin": {
            "drug": "Metformin", "food": "Alcohol",
            "advice": "Limit alcohol consumption"
        },
        "lisinopril": {
            "drug": "Lisinopril", "food": "Salt substitutes",
            "advice": "Avoid potassium-rich salt substitutes"
        }
    }
    
    for drug in drugs:
        if drug.lower() in food_db:
            interactions.append(food_db[drug.lower()])
    
    return interactions

def generate_home_remedies(drugs):
    """Generate relevant home care advice"""
    remedies = []
    remedy_db = {
        "metformin": {
            "drug": "Metformin", "remedy": "Take with meals to reduce stomach upset",
            "caution": "Monitor blood sugar levels regularly"
        },
        "warfarin": {
            "drug": "Warfarin", "remedy": "Maintain consistent daily routine and diet",
            "caution": "Watch for signs of bleeding, use soft toothbrush"
        },
        "lisinopril": {
            "drug": "Lisinopril", "remedy": "Rise slowly from sitting to prevent dizziness",
            "caution": "Stay hydrated but avoid salt substitutes"
        }
    }
    
    for drug in drugs:
        if drug.lower() in remedy_db:
            remedies.append(remedy_db[drug.lower()])
    
    return remedies

# Patient dashboard
@app.get("/api/patient/dashboard/{patient_id}")
async def get_patient_dashboard(patient_id: str):
    return {
        "patient": {
            "id": patient_id,
            "name": "John Doe",
            "age": 45,
            "medications": ["Lisinopril 10mg", "Metformin 500mg"],
            "allergies": ["Penicillin"],
            "conditions": ["Hypertension", "Diabetes Type 2"]
        },
        "recent_prescriptions": [
            {
                "id": "rx1",
                "date": "2024-12-15",
                "medications": ["Lisinopril 10mg", "Metformin 500mg"],
                "prescriber": "Dr. Smith"
            }
        ],
        "safety_alerts": ["Drug interaction detected"],
        "recommendations": ["Take Metformin with food", "Monitor blood pressure daily"]
    }

# Chat endpoint
@app.post("/api/chat/session")
async def chat_session(request: ChatRequest):
    responses = [
        "Based on your prescription, I recommend taking medications as directed.",
        "Drug interactions can be serious. Always consult your healthcare provider.",
        "Common side effects include nausea and dizziness. Contact your doctor if severe."
    ]
    
    import random
    response = random.choice(responses)
    
    return {
        "message": response,
        "confidence": 0.85,
        "sources": ["Clinical guidelines", "Drug database"]
    }

# Real-time alerts stream
@app.get("/api/alerts/stream")
async def stream_alerts():
    from fastapi.responses import StreamingResponse
    import asyncio
    
    async def generate_alerts():
        alerts = [
            "New drug interaction detected",
            "Patient vitals updated",
            "Prescription renewal required"
        ]
        
        for i, alert in enumerate(alerts):
            alert_data = {
                "id": f"alert_{i}",
                "message": alert,
                "severity": "medium",
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(alert_data)}\n\n"
            await asyncio.sleep(10)
    
    return StreamingResponse(
        generate_alerts(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

if __name__ == "__main__":
    import uvicorn
    print("🏥 Starting suRxit Backend API")
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔑 Login: doctor@example.com / password")
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)