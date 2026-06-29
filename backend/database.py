from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from datetime import datetime
from backend.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class DrivingSession(Base):
    __tablename__ = "driving_sessions"
    id = Column(String(50), primary_key=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    avg_risk_score = Column(Float, default=0.0)
    max_risk_score = Column(Float, default=0.0)

class RiskEvent(Base):
    __tablename__ = "risk_events"
    id = Column(String(50), primary_key=True)
    session_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float)
    risk_level = Column(String(20))
    accident_probability = Column(Float)
    collision_type = Column(String(50))
    driver_attention = Column(Float)
    driver_fatigue = Column(Float)
    vehicle_speed = Column(Float)
    lane_position = Column(Float)
    details = Column(Text)

class InterventionLog(Base):
    __tablename__ = "intervention_logs"
    id = Column(String(50), primary_key=True)
    session_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float)
    severity = Column(String(20))
    action_taken = Column(String(100))
    success = Column(Boolean, default=True)

class DriverProfile(Base):
    __tablename__ = "driver_profiles"
    id = Column(String(50), primary_key=True)
    avg_blink_rate = Column(Float, default=15.0)
    avg_fatigue = Column(Float, default=10.0)
    driving_hours = Column(Float, default=0.0)
    risk_events_count = Column(Integer, default=0)
    preferred_speed = Column(Float, default=60.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
