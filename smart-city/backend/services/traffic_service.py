"""India-focused traffic management with TomTom API and city-specific simulation."""

import hashlib
import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
import numpy as np
from sqlalchemy.orm import Session

from backend.config import settings
from backend.data.indian_cities import INDIAN_CITIES
from backend.database.models import TrafficData
from backend.schemas import TrafficCreate, TrafficPrediction
from backend.services.alert_service import maybe_send_email
from backend.services.cache_service import tomtom_cache

logger = logging.getLogger(__name__)


def congestion_from_speed(avg_speed: float) -> str:
    if avg_speed < 15:
        return "High"
    if avg_speed < 30:
        return "Medium"
    return "Low"


def _city_seed(city: str) -> int:
    return int(hashlib.md5(city.encode()).hexdigest()[:8], 16)


def get_traffic_data(
    db: Session,
    city: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 100,
) -> List[TrafficData]:
    query = db.query(TrafficData).order_by(TrafficData.timestamp.desc())
    if city:
        query = query.filter(TrafficData.city == city)
    if location:
        query = query.filter(TrafficData.location == location)
    return query.limit(limit).all()


def create_traffic_record(db: Session, city: str, data: TrafficCreate) -> TrafficData:
    congestion = congestion_from_speed(data.avg_speed)
    record = TrafficData(
        city=city,
        location=data.location,
        vehicle_count=data.vehicle_count,
        avg_speed=data.avg_speed,
        congestion_level=congestion,
        timestamp=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    if data.vehicle_count > 500:
        maybe_send_email("Traffic", f"High traffic at {data.location}, {city}: {data.vehicle_count} vehicles")
    return record


async def fetch_tomtom_traffic(lat: float, lon: float) -> Optional[dict]:
    cache_key = f"tomtom:{lat:.4f}:{lon:.4f}"
    cached = tomtom_cache.get(cache_key)
    if cached:
        return cached
    if not settings.tomtom_api_key:
        return None
    url = (
        f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        f"?key={settings.tomtom_api_key}&point={lat},{lon}"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                flow = resp.json().get("flowSegmentData", {})
                speed = flow.get("currentSpeed", 30)
                free_flow = flow.get("freeFlowSpeed", 60)
                vehicle_est = int((1 - speed / max(free_flow, 1)) * 400 + random.randint(50, 150))
                result = {"avg_speed": float(speed), "vehicle_count": max(vehicle_est, 10), "source": "tomtom"}
                tomtom_cache.set(cache_key, result)
                return result
    except Exception as e:
        logger.warning("TomTom API error: %s", e)
    return None


def generate_city_traffic(city: str, zone: str) -> dict:
    rng = random.Random(_city_seed(city) + hash(zone))
    hour = datetime.utcnow().hour
    ist_hour = (hour + 5) % 24 + (1 if (hour + 5) >= 24 else 0)
    peak = 1.6 if 8 <= ist_hour <= 10 or 17 <= ist_hour <= 20 else 1.0
    pop_factor = INDIAN_CITIES.get(city, {}).get("population_num", 5000000) / 5000000
    base = rng.randint(120, 450)
    vehicle_count = int(base * peak * min(pop_factor, 2.5))
    avg_speed = rng.uniform(8, 22) if peak > 1.2 else rng.uniform(22, 55)
    return {"vehicle_count": vehicle_count, "avg_speed": round(avg_speed, 1)}


async def refresh_city_traffic(db: Session, city: str) -> List[TrafficData]:
    info = INDIAN_CITIES.get(city)
    if not info:
        return []
    records = []
    for zone in info["zones"]:
        api_data = await fetch_tomtom_traffic(info["lat"], info["lon"])
        if not api_data:
            api_data = generate_city_traffic(city, zone)
        record = create_traffic_record(
            db, city,
            TrafficCreate(location=zone, vehicle_count=api_data["vehicle_count"], avg_speed=api_data["avg_speed"]),
        )
        records.append(record)
    return records


def get_city_traffic_analytics(db: Session, city: str) -> dict:
    records = get_traffic_data(db, city=city, limit=50)
    if not records:
        return _simulated_analytics(city)

    latest_by_zone = {}
    for r in records:
        if r.location not in latest_by_zone:
            latest_by_zone[r.location] = r

    latest = list(latest_by_zone.values())
    avg_speed = sum(r.avg_speed for r in latest) / len(latest)
    avg_vehicles = sum(r.vehicle_count for r in latest) / len(latest)
    congestion = congestion_from_speed(avg_speed)
    density_score = min(int(avg_vehicles / 6), 100)

    hourly = _hourly_traffic_series(city, latest)
    peak_hours = sorted(range(24), key=lambda h: hourly[h], reverse=True)[:3]

    from ml_models.traffic_prediction import predict_next_hour
    pred = predict_next_hour(records[:20]) if records else {}

    return {
        "city": city,
        "congestion_level": congestion,
        "avg_speed": round(avg_speed, 1),
        "peak_hours": peak_hours,
        "density_score": density_score,
        "hourly_data": [{"hour": h, "vehicles": hourly[h]} for h in range(24)],
        "zone_data": [
            {"zone": r.location, "vehicles": r.vehicle_count, "speed": r.avg_speed, "congestion": r.congestion_level}
            for r in latest
        ],
        "forecast": pred,
        "ai_summary": _traffic_ai_summary(city, congestion, avg_speed, peak_hours),
    }


def _hourly_traffic_series(city: str, records: list) -> List[int]:
    rng = np.random.RandomState(_city_seed(city))
    base = int(sum(r.vehicle_count for r in records) / max(len(records), 1))
    hourly = []
    for h in range(24):
        factor = 1.8 if 8 <= h <= 10 or 17 <= h <= 20 else (0.5 if h < 6 or h > 22 else 1.0)
        hourly.append(int(base * factor * rng.uniform(0.85, 1.15)))
    return hourly


def _simulated_analytics(city: str) -> dict:
    info = INDIAN_CITIES.get(city, {})
    rng = random.Random(_city_seed(city))
    avg_speed = rng.uniform(15, 40)
    hourly = _hourly_traffic_series(city, [])
    return {
        "city": city,
        "congestion_level": congestion_from_speed(avg_speed),
        "avg_speed": round(avg_speed, 1),
        "peak_hours": [8, 9, 18],
        "density_score": rng.randint(45, 85),
        "hourly_data": [{"hour": h, "vehicles": hourly[h]} for h in range(24)],
        "zone_data": [
            {"zone": z, "vehicles": rng.randint(100, 400), "speed": round(rng.uniform(10, 45), 1),
             "congestion": congestion_from_speed(rng.uniform(10, 45))}
            for z in info.get("zones", ["Central"])
        ],
        "forecast": {"vehicle_count": 300, "congestion_probability": 0.5, "congestion_level": "Medium"},
        "ai_summary": _traffic_ai_summary(city, congestion_from_speed(avg_speed), avg_speed, [8, 9, 18]),
    }


def _traffic_ai_summary(city: str, congestion: str, speed: float, peak_hours: list) -> str:
    peaks = ", ".join(f"{h}:00" for h in peak_hours[:3])
    return (
        f"{city} currently shows **{congestion}** congestion with average speed of {speed:.0f} km/h. "
        f"Peak traffic expected at {peaks} IST. "
        f"{'Consider alternate routes and metro transit during peak hours.' if congestion == 'High' else 'Traffic flow is manageable; monitor commercial zones.'}"
    )


def predict_traffic(db: Session, city: str, location: str) -> TrafficPrediction:
    from ml_models.traffic_prediction import predict_next_hour
    history = get_traffic_data(db, city=city, location=location, limit=48)
    if not history:
        sample = generate_city_traffic(city, location)
        return TrafficPrediction(
            location=location,
            predicted_vehicle_count=float(sample["vehicle_count"]),
            congestion_probability=0.3,
            predicted_congestion=congestion_from_speed(sample["avg_speed"]),
        )
    result = predict_next_hour(history)
    return TrafficPrediction(
        location=location,
        predicted_vehicle_count=result["vehicle_count"],
        congestion_probability=result["congestion_probability"],
        predicted_congestion=result["congestion_level"],
    )


async def get_weather_impact(city: str) -> Optional[dict]:
    if not settings.openweather_api_key:
        info = INDIAN_CITIES.get(city, {})
        return {
            "condition": "Typical",
            "temperature": 32,
            "traffic_impact_factor": 1.1,
            "description": f"{info.get('climate_summary', 'Standard urban climate')} — moderate traffic impact expected.",
        }
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city},IN&appid={settings.openweather_api_key}&units=metric"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                weather = data["weather"][0]["main"]
                impact_map = {"Rain": 1.35, "Snow": 1.5, "Thunderstorm": 1.4, "Clouds": 1.1, "Clear": 1.0, "Mist": 1.2}
                factor = impact_map.get(weather, 1.1)
                return {
                    "condition": weather,
                    "temperature": data["main"]["temp"],
                    "traffic_impact_factor": factor,
                    "description": f"{weather} in {city} — estimated {int((factor - 1) * 100)}% traffic increase.",
                }
    except Exception as e:
        logger.warning("Weather API error: %s", e)
    return None
