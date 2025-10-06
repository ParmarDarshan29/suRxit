from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SeverityLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CONTRAINDICATED = "contraindicated"

class AlertType(str, Enum):
    DRUG_INTERACTION = "drug_interaction"
    ADVERSE_REACTION = "adverse_reaction"
    ALLERGY = "allergy"
    DOSING = "dosing"
    MONITORING = "monitoring"

# Drug Interaction Models
class DrugInteraction(BaseModel):
    drug1: str
    drug2: str
    severity: SeverityLevel
    mechanism: str
    clinical_effects: str
    management: str
    evidence_level: Optional[str] = "moderate"
    onset: Optional[str] = None
    documentation: Optional[str] = None

class AdverseReaction(BaseModel):
    drug: str
    reaction: str
    frequency: str
    severity: SeverityLevel
    onset: Optional[str] = None
    management: str
    monitoring: Optional[str] = None

class FoodInteraction(BaseModel):
    drug: str
    food: str
    interaction_type: str
    severity: SeverityLevel
    mechanism: Optional[str] = None
    recommendation: str
    timing: Optional[str] = None

class HomeRemedy(BaseModel):
    name: str
    indication: str
    preparation: str
    dosage: Optional[str] = None
    precautions: str
    evidence_level: str
    interactions: Optional[List[str]] = []
    contraindications: Optional[List[str]] = []

class SafetyAlert(BaseModel):
    id: str
    message: str
    alert_type: AlertType
    severity: SeverityLevel
    patient_id: Optional[str] = None
    drug_name: Optional[str] = None
    timestamp: datetime
    requires_action: bool = False
    action_taken: bool = False

# Prescription Analysis Models
class PrescriptionAnalysis(BaseModel):
    analysis_id: str
    risk_score: float = Field(..., ge=0, le=10)
    risk_level: RiskLevel
    ddi_interactions: List[DrugInteraction] = []
    adr_reactions: List[AdverseReaction] = []
    dfi_interactions: List[FoodInteraction] = []
    home_remedies: List[HomeRemedy] = []
    alerts: List[str] = []
    recommendations: List[str] = []
    processed_drugs: List[str] = []
    timestamp: datetime
    processing_time: Optional[float] = None

class PrescriptionRequest(BaseModel):
    text: Optional[str] = None
    patient_id: Optional[str] = None
    include_alternatives: bool = True
    include_home_remedies: bool = True

# Patient Models
class LabValue(BaseModel):
    name: str
    value: float
    unit: str
    reference_range: str
    status: str  # normal, high, low, critical
    date: datetime

class Patient(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None  # kg
    height: Optional[float] = None  # cm
    allergies: List[str] = []
    conditions: List[str] = []
    medications: List[str] = []
    lab_values: Dict[str, LabValue] = {}
    insurance: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None

class PatientDashboard(BaseModel):
    patient: Patient
    recent_prescriptions: List[Dict[str, Any]] = []
    safety_alerts: List[str] = []
    recommendations: List[str] = []
    upcoming_appointments: List[Dict[str, Any]] = []
    lab_reminders: List[str] = []
    medication_adherence: Optional[float] = None

# Chat Models
class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[datetime] = None
    confidence: Optional[float] = None
    sources: Optional[List[str]] = []

class ChatRequest(BaseModel):
    message: str
    context: List[ChatMessage] = []
    session_id: Optional[str] = None
    user_type: str = "doctor"  # doctor, patient, admin

class ChatResponse(BaseModel):
    message: str
    confidence: float
    sources: List[str] = []
    session_id: str
    timestamp: datetime
    follow_up_questions: Optional[List[str]] = []

# Drug Information Models
class DrugInfo(BaseModel):
    name: str
    generic_name: str
    brand_names: List[str] = []
    drug_class: str
    mechanism_of_action: Optional[str] = None
    indications: List[str] = []
    contraindications: List[str] = []
    side_effects: List[str] = []
    dosing: Optional[Dict[str, Any]] = {}
    monitoring_parameters: List[str] = []
    pregnancy_category: Optional[str] = None
    controlled_substance: Optional[str] = None

# User Models
class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str
    is_active: bool = True
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = {}

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "doctor"

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

# Analytics Models
class AnalyticsData(BaseModel):
    total_analyses: int
    total_interactions: int
    risk_distribution: Dict[str, int]
    common_drugs: List[Dict[str, Any]]
    alert_trends: List[Dict[str, Any]]
    user_activity: Dict[str, Any]

# API Response Models
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool