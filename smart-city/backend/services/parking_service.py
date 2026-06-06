"""India-focused smart parking service."""

import hashlib
import random
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.data.indian_cities import INDIAN_CITIES
from backend.database.models import ParkingData
from backend.schemas import ParkingCreate, ParkingPrediction
from backend.services.alert_service import maybe_send_email


def _city_seed(city: str) -> int:
    return int(hashlib.md5(city.encode()).hexdigest()[:8], 16)


def get_parking_data(
    db: Session,
    city: Optional[str] = None,
    parking_name: Optional[str] = None,
    limit: int = 100,
) -> List[ParkingData]:
    query = db.query(ParkingData).order_by(ParkingData.timestamp.desc())
    if city:
        query = query.filter(ParkingData.city == city)
    if parking_name:
        query = query.filter(ParkingData.parking_name == parking_name)
    return query.limit(limit).all()


def create_parking_record(db: Session, city: str, data: ParkingCreate) -> ParkingData:
    available = data.total_slots - data.occupied_slots
    record = ParkingData(
        city=city,
        parking_name=data.parking_name,
        total_slots=data.total_slots,
        occupied_slots=data.occupied_slots,
        available_slots=available,
        timestamp=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    if data.total_slots > 0 and (data.occupied_slots / data.total_slots) > 0.9:
        maybe_send_email("Parking", f"{data.parking_name}, {city} above 90% capacity")
    return record


def refresh_city_parking(db: Session, city: str) -> List[ParkingData]:
    info = INDIAN_CITIES.get(city)
    if not info:
        return []
    rng = random.Random(_city_seed(city) + datetime.utcnow().hour)
    hour = (datetime.utcnow().hour + 5) % 24
    peak = 1.4 if 9 <= hour <= 18 else 0.65
    records = []
    for lot in info["parking_lots"]:
        occupied = int(lot["total"] * rng.uniform(0.35, 0.88) * peak)
        occupied = min(occupied, lot["total"])
        record = create_parking_record(
            db, city,
            ParkingCreate(parking_name=lot["name"], total_slots=lot["total"], occupied_slots=occupied),
        )
        records.append(record)
    return records


def get_city_parking_analytics(db: Session, city: str) -> dict:
    info = INDIAN_CITIES.get(city, {})
    lots = info.get("parking_lots", [])
    utilization = []

    for lot in lots:
        latest = (
            db.query(ParkingData)
            .filter(ParkingData.city == city, ParkingData.parking_name == lot["name"])
            .order_by(ParkingData.timestamp.desc())
            .first()
        )
        if latest:
            util = (latest.occupied_slots / latest.total_slots) * 100
            utilization.append({
                "parking_name": latest.parking_name,
                "total_slots": latest.total_slots,
                "occupied_slots": latest.occupied_slots,
                "available_slots": latest.available_slots,
                "utilization_pct": round(util, 1),
            })
        else:
            rng = random.Random(_city_seed(city) + hash(lot["name"]))
            occ = int(lot["total"] * rng.uniform(0.4, 0.8))
            utilization.append({
                "parking_name": lot["name"],
                "total_slots": lot["total"],
                "occupied_slots": occ,
                "available_slots": lot["total"] - occ,
                "utilization_pct": round((occ / lot["total"]) * 100, 1),
            })

    total_slots = sum(u["total_slots"] for u in utilization)
    occupied = sum(u["occupied_slots"] for u in utilization)
    available = sum(u["available_slots"] for u in utilization)
    avg_util = sum(u["utilization_pct"] for u in utilization) / max(len(utilization), 1)

    hourly = _hourly_occupancy(city, avg_util)
    recommendations = _parking_recommendations(city, utilization)

    from ml_models.parking_prediction import predict_occupancy
    history = get_parking_data(db, city=city, limit=20)
    forecast = predict_occupancy(history) if history else {"occupancy_pct": avg_util, "peak_hour": 12}

    return {
        "city": city,
        "total_zones": len(utilization),
        "total_slots": total_slots,
        "occupied_slots": occupied,
        "available_slots": available,
        "utilization_pct": round(avg_util, 1),
        "lots": utilization,
        "hourly_data": hourly,
        "forecast": forecast,
        "recommendations": recommendations,
    }


def _hourly_occupancy(city: str, base_util: float) -> List[dict]:
    data = []
    for h in range(24):
        factor = 1.3 if 9 <= h <= 18 else 0.7
        data.append({"hour": h, "utilization": round(min(base_util * factor, 99), 1)})
    return data


def _parking_recommendations(city: str, lots: list) -> List[str]:
    recs = []
    available_lots = sorted(lots, key=lambda x: x["utilization_pct"])
    if available_lots:
        best = available_lots[0]
        recs.append(f"Best availability: **{best['parking_name']}** ({best['available_slots']} slots free)")
    crowded = [l for l in lots if l["utilization_pct"] > 85]
    if crowded:
        recs.append(f"Avoid during peak: {', '.join(l['parking_name'] for l in crowded)}")
    recs.append(f"Use metro-linked parking in {city} for lower rates and better availability.")
    return recs


def predict_parking(db: Session, city: str, parking_name: str) -> ParkingPrediction:
    from ml_models.parking_prediction import predict_occupancy
    history = get_parking_data(db, city=city, parking_name=parking_name, limit=48)
    if not history:
        return ParkingPrediction(parking_name=parking_name, predicted_occupancy=65.0, peak_hour=12)
    result = predict_occupancy(history)
    return ParkingPrediction(
        parking_name=parking_name,
        predicted_occupancy=result["occupancy_pct"],
        peak_hour=result["peak_hour"],
    )
