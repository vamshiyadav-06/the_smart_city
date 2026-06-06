"""Traffic API — India cities."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.schemas import TrafficCreate, TrafficPrediction, TrafficResponse
from backend.services.groq_service import generate_traffic_insights
from backend.services.traffic_service import (
    create_traffic_record,
    get_city_traffic_analytics,
    get_traffic_data,
    predict_traffic,
    refresh_city_traffic,
    get_weather_impact,
)

router = APIRouter(prefix="/traffic", tags=["Traffic"])


@router.get("", response_model=List[TrafficResponse])
def list_traffic(
    city: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_traffic_data(db, city=city, location=location, limit=limit)


@router.post("/{city}", response_model=TrafficResponse, status_code=201)
def add_traffic(city: str, data: TrafficCreate, db: Session = Depends(get_db)):
    return create_traffic_record(db, city, data)


@router.post("/{city}/refresh")
async def refresh_traffic(city: str, db: Session = Depends(get_db)):
    records = await refresh_city_traffic(db, city)
    return {"refreshed": len(records), "city": city}


@router.get("/{city}/analytics")
def traffic_analytics(city: str, db: Session = Depends(get_db)):
    return get_city_traffic_analytics(db, city)


@router.get("/{city}/predict/{location}", response_model=TrafficPrediction)
def traffic_prediction(city: str, location: str, db: Session = Depends(get_db)):
    return predict_traffic(db, city, location)


@router.get("/{city}/weather")
async def weather_impact(city: str):
    return await get_weather_impact(city)


@router.get("/{city}/ai-insights")
async def traffic_ai_insights(city: str, db: Session = Depends(get_db)):
    analytics = get_city_traffic_analytics(db, city)
    return await generate_traffic_insights(city, analytics)
