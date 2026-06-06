"""SQLAlchemy ORM models — Smart City India."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from backend.database.db import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    state = Column(String(255), nullable=False)
    population = Column(String(100))
    famous_for = Column(Text)
    description = Column(Text)
    lat = Column(Float)
    lon = Column(Float)


class TrafficData(Base):
    __tablename__ = "traffic_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    vehicle_count = Column(Integer, nullable=False)
    avg_speed = Column(Float, nullable=False)
    congestion_level = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ParkingData(Base):
    __tablename__ = "parking_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(255), nullable=False, index=True)
    parking_name = Column(String(255), nullable=False, index=True)
    total_slots = Column(Integer, nullable=False)
    occupied_slots = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class RoadDamageReport(Base):
    __tablename__ = "road_damage_reports"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(255), nullable=True, index=True)
    image_url = Column(Text, nullable=True)
    damage_type = Column(String(255), nullable=False)
    severity = Column(String(100), nullable=False)
    location = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    pothole_count = Column(Integer, default=0)
    crack_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class AIAnalysisReport(Base):
    __tablename__ = "ai_analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(255), nullable=False, index=True)
    analysis_text = Column(Text, nullable=False)
    confidence = Column(Float, default=0.85)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
