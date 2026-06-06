"""Parking API — India cities."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.schemas import ParkingCreate, ParkingPrediction, ParkingResponse
from backend.services.parking_service import (
    create_parking_record,
    get_city_parking_analytics,
    get_parking_data,
    predict_parking,
    refresh_city_parking,
)

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.get("", response_model=List[ParkingResponse])
def list_parking(
    city: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_parking_data(db, city=city, limit=limit)


@router.post("/{city}", response_model=ParkingResponse, status_code=201)
def add_parking(city: str, data: ParkingCreate, db: Session = Depends(get_db)):
    return create_parking_record(db, city, data)


@router.post("/{city}/refresh")
def refresh_parking(city: str, db: Session = Depends(get_db)):
    records = refresh_city_parking(db, city)
    return {"refreshed": len(records), "city": city}


@router.get("/{city}/analytics")
def parking_analytics(city: str, db: Session = Depends(get_db)):
    return get_city_parking_analytics(db, city)


@router.get("/{city}/predict/{parking_name}", response_model=ParkingPrediction)
def parking_prediction(city: str, parking_name: str, db: Session = Depends(get_db)):
    return predict_parking(db, city, parking_name)
