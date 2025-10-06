# Backend Setup Guide for suRxit

This guide provides instructions to set up a backend server that matches the frontend API expectations.

## Option 1: Python FastAPI Backend (Recommended)

### 1. Setup Python Backend

```bash
# Create backend directory
mkdir -p ../backend
cd ../backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart
pip install httpx asyncio-mqtt python-socketio
```

### 2. Create FastAPI Server

Create `main.py`:

```python
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import Optional, List, Dict, Any
import time

app = FastAPI(title="suRxit API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Mock data storage
mock_users = {
    "doctor@example.com": {
        "id": "doc1",
        "email": "doctor@example.com",
        "password": "hashed_password",
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

# Authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production, verify JWT token here
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"id": "doc1", "email": "doctor@example.com", "role": "doctor"}

# Auth endpoints
@app.post("/api/auth/login")
async def login(credentials: dict):
    email = credentials.get("email")
    password = credentials.get("password")
    
    if email in mock_users and password == "password":  # Simple mock auth
        return {
            "token": "mock_jwt_token_12345",
            "user": mock_users[email],
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
    # Simulate processing time
    await asyncio.sleep(2)
    
    # Mock analysis results
    return {
        "risk_score": 7.5,
        "risk_level": "Medium",
        "ddi_interactions": [
            {
                "drug1": "Warfarin",
                "drug2": "Aspirin",
                "severity": "High",
                "mechanism": "Increased bleeding risk",
                "clinical_effects": "Monitor for signs of bleeding",
                "management": "Consider alternative therapy or frequent monitoring"
            }
        ],
        "adr_reactions": [
            {
                "drug": "Metformin",
                "reaction": "Gastrointestinal upset",
                "frequency": "Common",
                "severity": "Mild",
                "management": "Take with food"
            }
        ],
        "dfi_interactions": [
            {
                "drug": "Warfarin",
                "food": "Leafy greens",
                "interaction_type": "Vitamin K interaction",
                "severity": "Moderate",
                "recommendation": "Maintain consistent intake"
            }
        ],
        "home_remedies": [
            {
                "name": "Ginger Tea",
                "indication": "Nausea relief",
                "preparation": "Steep fresh ginger in hot water",
                "precautions": "Avoid if taking blood thinners",
                "evidence_level": "Moderate"
            }
        ],
        "alerts": [
            "Patient has documented penicillin allergy - avoid beta-lactam antibiotics"
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
                "id": "rx1",
                "date": "2024-01-15",
                "medications": ["Lisinopril 10mg", "Metformin 500mg"],
                "prescriber": "Dr. Smith"
            }
        ],
        "safety_alerts": [
            "Drug interaction detected between Warfarin and Aspirin"
        ],
        "recommendations": [
            "Take Metformin with food to reduce GI upset",
            "Monitor blood pressure daily"
        ]
    }

# Chat endpoint
@app.post("/api/chat/session")
async def chat_session(message_data: dict, user = Depends(get_current_user)):
    message = message_data.get("message", "")
    context = message_data.get("context", [])
    
    # Mock AI response
    responses = [
        "Based on your prescription, I recommend taking medications as directed.",
        "Drug interactions can be serious. Always consult your healthcare provider.",
        "Common side effects include nausea and dizziness. Contact your doctor if severe.",
        "Maintain a consistent medication schedule for best results."
    ]
    
    import random
    response = random.choice(responses)
    
    return {
        "message": response,
        "confidence": 0.85,
        "sources": ["Clinical guidelines", "Drug database"]
    }

# WebSocket/SSE endpoint for real-time alerts
@app.get("/api/alerts/stream")
async def stream_alerts():
    async def generate_alerts():
        alerts = [
            "New drug interaction detected",
            "Patient vitals updated",
            "Prescription renewal required",
            "Safety alert: Dosage adjustment needed"
        ]
        
        for alert in alerts:
            yield f"data: {json.dumps({'message': alert, 'timestamp': time.time()})}\n\n"
            await asyncio.sleep(10)  # Send alert every 10 seconds
    
    return StreamingResponse(
        generate_alerts(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### 3. Run the FastAPI Server

```bash
# In the backend directory
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Option 2: Node.js Express Backend

### 1. Setup Node.js Backend

```bash
# Create backend directory
mkdir -p ../backend-node
cd ../backend-node

# Initialize npm project
npm init -y

# Install dependencies
npm install express cors multer jsonwebtoken bcryptjs dotenv
npm install --save-dev nodemon
```

### 2. Create Express Server

Create `server.js`:

```javascript
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();
const PORT = process.env.PORT || 8000;
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// Middleware
app.use(cors({
    origin: ['http://localhost:5174', 'http://localhost:3000'],
    credentials: true
}));
app.use(express.json());

// File upload middleware
const upload = multer({ dest: 'uploads/' });

// Mock data
const mockUsers = {
    'doctor@example.com': {
        id: 'doc1',
        email: 'doctor@example.com',
        password: bcrypt.hashSync('password', 10),
        role: 'doctor',
        name: 'Dr. Smith'
    }
};

// Auth middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Invalid token' });
        req.user = user;
        next();
    });
};

// Auth routes
app.post('/api/auth/login', async (req, res) => {
    const { email, password } = req.body;
    
    const user = mockUsers[email];
    if (!user || !bcrypt.compareSync(password, user.password)) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign(
        { id: user.id, email: user.email, role: user.role },
        JWT_SECRET,
        { expiresIn: '1h' }
    );

    res.json({
        token,
        user: { id: user.id, email: user.email, role: user.role, name: user.name },
        expires_in: 3600
    });
});

app.post('/api/auth/logout', authenticateToken, (req, res) => {
    res.json({ message: 'Logged out successfully' });
});

app.get('/api/auth/verify', authenticateToken, (req, res) => {
    res.json({ valid: true, user: req.user });
});

// Prescription analysis
app.post('/api/analyze/prescription', authenticateToken, upload.single('file'), async (req, res) => {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    const mockResults = {
        risk_score: 7.5,
        risk_level: 'Medium',
        ddi_interactions: [
            {
                drug1: 'Warfarin',
                drug2: 'Aspirin',
                severity: 'High',
                mechanism: 'Increased bleeding risk',
                clinical_effects: 'Monitor for signs of bleeding',
                management: 'Consider alternative therapy or frequent monitoring'
            }
        ],
        adr_reactions: [
            {
                drug: 'Metformin',
                reaction: 'Gastrointestinal upset',
                frequency: 'Common',
                severity: 'Mild',
                management: 'Take with food'
            }
        ],
        dfi_interactions: [
            {
                drug: 'Warfarin',
                food: 'Leafy greens',
                interaction_type: 'Vitamin K interaction',
                severity: 'Moderate',
                recommendation: 'Maintain consistent intake'
            }
        ],
        home_remedies: [
            {
                name: 'Ginger Tea',
                indication: 'Nausea relief',
                preparation: 'Steep fresh ginger in hot water',
                precautions: 'Avoid if taking blood thinners',
                evidence_level: 'Moderate'
            }
        ],
        alerts: ['Patient has documented penicillin allergy - avoid beta-lactam antibiotics']
    };

    res.json(mockResults);
});

// Patient dashboard
app.get('/api/patient/dashboard/:patientId', authenticateToken, (req, res) => {
    const mockPatient = {
        patient: {
            id: req.params.patientId,
            name: 'John Doe',
            age: 45,
            medications: ['Lisinopril', 'Metformin'],
            allergies: ['Penicillin'],
            conditions: ['Hypertension', 'Diabetes Type 2']
        },
        recent_prescriptions: [
            {
                id: 'rx1',
                date: '2024-01-15',
                medications: ['Lisinopril 10mg', 'Metformin 500mg'],
                prescriber: 'Dr. Smith'
            }
        ],
        safety_alerts: ['Drug interaction detected between Warfarin and Aspirin'],
        recommendations: [
            'Take Metformin with food to reduce GI upset',
            'Monitor blood pressure daily'
        ]
    };

    res.json(mockPatient);
});

// Chat endpoint
app.post('/api/chat/session', authenticateToken, (req, res) => {
    const { message, context } = req.body;
    
    const responses = [
        'Based on your prescription, I recommend taking medications as directed.',
        'Drug interactions can be serious. Always consult your healthcare provider.',
        'Common side effects include nausea and dizziness. Contact your doctor if severe.',
        'Maintain a consistent medication schedule for best results.'
    ];

    const response = responses[Math.floor(Math.random() * responses.length)];

    res.json({
        message: response,
        confidence: 0.85,
        sources: ['Clinical guidelines', 'Drug database']
    });
});

// SSE endpoint for alerts
app.get('/api/alerts/stream', authenticateToken, (req, res) => {
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': req.headers.origin || '*',
        'Access-Control-Allow-Credentials': 'true'
    });

    const alerts = [
        'New drug interaction detected',
        'Patient vitals updated',
        'Prescription renewal required',
        'Safety alert: Dosage adjustment needed'
    ];

    let alertIndex = 0;
    const interval = setInterval(() => {
        if (alertIndex < alerts.length) {
            res.write(`data: ${JSON.stringify({
                message: alerts[alertIndex],
                timestamp: Date.now()
            })}\n\n`);
            alertIndex++;
        } else {
            clearInterval(interval);
            res.end();
        }
    }, 10000); // Send alert every 10 seconds

    req.on('close', () => {
        clearInterval(interval);
    });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
```

### 3. Update package.json

Add to `package.json`:

```json
{
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  }
}
```

### 4. Run the Node.js Server

```bash
# In the backend-node directory
npm run dev
```

## Frontend Configuration

Make sure your frontend `.env` file has:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
VITE_ALERTS_STREAM_URL=http://localhost:8000/api/alerts/stream
VITE_ENABLE_MOCK_DATA=false
```

## Testing the Integration

1. Start the backend server (Python or Node.js)
2. Start the frontend dev server: `npm run dev`
3. Open http://localhost:5174
4. Test login with: `doctor@example.com` / `password`
5. Try the prescription analysis form
6. Check the chatbot functionality
7. Verify real-time alerts are working

## Next Steps

1. **Add Real AI Integration**: Replace mock responses with actual MedLM/OpenAI API calls
2. **Database Integration**: Add PostgreSQL/MongoDB for persistent data storage
3. **Enhanced Authentication**: Implement proper JWT refresh tokens and role-based access
4. **File Processing**: Add OCR for prescription image analysis
5. **Real-time Features**: Implement proper WebSocket server for live updates
6. **Error Handling**: Add comprehensive error logging and monitoring
7. **Testing**: Add unit and integration tests for API endpoints
8. **Deployment**: Configure for production deployment with proper security