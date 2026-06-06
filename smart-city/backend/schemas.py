"""Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TrafficCreate(BaseModel):
    location: str = Field(..., min_length=1, max_length=255)
    vehicle_count: int = Field(..., ge=0)
    avg_speed: float = Field(..., ge=0, le=200)


class TrafficResponse(TrafficCreate):
    id: int
    city: str
    congestion_level: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ParkingCreate(BaseModel):
    parking_name: str = Field(..., min_length=1, max_length=255)
    total_slots: int = Field(..., gt=0)
    occupied_slots: int = Field(..., ge=0)


class ParkingResponse(BaseModel):
    id: int
    city: str
    parking_name: str
    total_slots: int
    occupied_slots: int
    available_slots: int
    timestamp: datetime

    class Config:
        from_attributes = True


class DamageReportResponse(BaseModel):
    id: int
    city: Optional[str] = None
    damage_type: str
    severity: str
    confidence: Optional[float] = None
    location: Optional[str] = None
    pothole_count: int = 0
    crack_count: int = 0
    image_url: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class TrafficPrediction(BaseModel):
    location: str
    predicted_vehicle_count: float
    congestion_probability: float
    predicted_congestion: str


class ParkingPrediction(BaseModel):
    parking_name: str
    predicted_occupancy: float
    peak_hour: int


class AIAnalysisResponse(BaseModel):
    city: str
    analysis: str
    confidence: float
    timestamp: str
    cached: bool = False
