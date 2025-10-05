from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    allergies = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Prescription(Base):
    __tablename__ = 'prescriptions'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    drugs = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    risk_level = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True)
    event = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DFICache(Base):
    __tablename__ = 'dfi_cache'
    id = Column(Integer, primary_key=True)
    drug_id = Column(String)
    food_item = Column(String)
    advice = Column(String)
    cached_at = Column(DateTime, default=datetime.datetime.utcnow)

class HomeRemedyCache(Base):
    __tablename__ = 'home_remedy_cache'
    id = Column(Integer, primary_key=True)
    drug_id = Column(String)
    remedy = Column(String)
    cached_at = Column(DateTime, default=datetime.datetime.utcnow)

DATABASE_URL = "postgresql+asyncpg://user:password@db/surxit"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
