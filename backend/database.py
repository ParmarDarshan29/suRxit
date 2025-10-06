from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
import os
from typing import Optional

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./surxit.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="doctor")  # doctor, admin, patient
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(String)
    weight = Column(Float)  # kg
    height = Column(Float)  # cm
    allergies = Column(JSON)  # List of allergies
    conditions = Column(JSON)  # Medical conditions
    medications = Column(JSON)  # Current medications
    lab_values = Column(JSON)  # Latest lab results
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class PrescriptionAnalysis(Base):
    __tablename__ = "prescription_analyses"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)  # Doctor who ran analysis
    patient_id = Column(String)  # Optional patient context
    prescription_text = Column(Text, nullable=False)
    risk_score = Column(Float)
    risk_level = Column(String)
    drug_interactions = Column(JSON)
    adverse_reactions = Column(JSON)
    food_interactions = Column(JSON)
    home_remedies = Column(JSON)
    alerts = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    messages = Column(JSON)  # List of messages in conversation
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String)
    message = Column(Text, nullable=False)
    severity = Column(String, default="medium")  # low, medium, high, critical
    alert_type = Column(String)  # safety_alert, lab_alert, medication_alert
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)

class DrugInteraction(Base):
    __tablename__ = "drug_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    drug1 = Column(String, nullable=False, index=True)
    drug2 = Column(String, nullable=False, index=True)
    severity = Column(String)  # mild, moderate, severe, contraindicated
    mechanism = Column(Text)
    clinical_effects = Column(Text)
    management = Column(Text)
    evidence_level = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class Drug(Base):
    __tablename__ = "drugs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    generic_name = Column(String, index=True)
    brand_names = Column(JSON)
    drug_class = Column(String)
    mechanism_of_action = Column(Text)
    indications = Column(JSON)
    contraindications = Column(JSON)
    side_effects = Column(JSON)
    dosing = Column(JSON)
    monitoring_parameters = Column(JSON)
    pregnancy_category = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# Database dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Initialize database with sample data
def init_sample_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Drug).first():
            return
        
        # Add sample drugs
        sample_drugs = [
            {
                "name": "Lisinopril",
                "generic_name": "lisinopril",
                "brand_names": ["Prinivil", "Zestril"],
                "drug_class": "ACE Inhibitor",
                "mechanism_of_action": "Inhibits angiotensin-converting enzyme",
                "indications": ["Hypertension", "Heart failure", "Post-MI"],
                "contraindications": ["Pregnancy", "Angioedema history"],
                "side_effects": ["Dry cough", "Hyperkalemia", "Hypotension"],
                "monitoring_parameters": ["Blood pressure", "Kidney function", "Electrolytes"]
            },
            {
                "name": "Metformin",
                "generic_name": "metformin",
                "brand_names": ["Glucophage", "Fortamet"],
                "drug_class": "Biguanide",
                "mechanism_of_action": "Decreases hepatic glucose production",
                "indications": ["Type 2 diabetes", "PCOS"],
                "contraindications": ["Severe kidney disease", "Metabolic acidosis"],
                "side_effects": ["Nausea", "Diarrhea", "Lactic acidosis (rare)"],
                "monitoring_parameters": ["Blood glucose", "Kidney function", "Vitamin B12"]
            }
        ]
        
        for drug_data in sample_drugs:
            drug = Drug(**drug_data)
            db.add(drug)
        
        # Add sample drug interactions
        interaction = DrugInteraction(
            drug1="Lisinopril",
            drug2="NSAIDs",
            severity="moderate",
            mechanism="NSAIDs reduce antihypertensive effect",
            clinical_effects="Increased blood pressure, reduced kidney function",
            management="Monitor blood pressure and kidney function closely",
            evidence_level="well-established"
        )
        db.add(interaction)
        
        db.commit()
        print("Sample data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    init_sample_data()