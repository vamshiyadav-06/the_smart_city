"""Road damage detection service — India edition."""

import base64
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database.models import RoadDamageReport
from backend.services.alert_service import maybe_send_email

logger = logging.getLogger(__name__)
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "datasets" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_damage_reports(db: Session, city: Optional[str] = None, limit: int = 100) -> List[RoadDamageReport]:
    query = db.query(RoadDamageReport).order_by(RoadDamageReport.timestamp.desc())
    if city:
        query = query.filter(RoadDamageReport.city == city)
    return query.limit(limit).all()


def get_damage_count(db: Session, city: Optional[str] = None) -> int:
    q = db.query(func.count(RoadDamageReport.id))
    if city:
        q = q.filter(RoadDamageReport.city == city)
    return q.scalar() or 0


def get_damage_stats(db: Session, city: Optional[str] = None) -> dict:
    reports = get_damage_reports(db, city=city, limit=500)
    potholes = sum(1 for r in reports if "pothole" in r.damage_type.lower())
    cracks = sum(1 for r in reports if "crack" in r.damage_type.lower())
    high = sum(1 for r in reports if r.severity == "High")
    return {
        "total": len(reports),
        "pothole_count": potholes,
        "crack_count": cracks,
        "high_severity": high,
    }


async def detect_road_damage(
    db: Session,
    image_bytes: bytes,
    filename: str,
    city: Optional[str] = None,
    location: Optional[str] = None,
) -> RoadDamageReport:
    from ml_models.road_damage_detection import detect_damage, draw_detections

    ext = Path(filename).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png"):
        raise ValueError("Only jpg, jpeg, and png files are supported")

    file_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{file_id}{ext}"
    with open(save_path, "wb") as f:
        f.write(image_bytes)

    detections = detect_damage(str(save_path))
    annotated_path = UPLOAD_DIR / f"{file_id}_annotated{ext}"
    draw_detections(str(save_path), detections, str(annotated_path))

    pothole_count = sum(1 for d in detections if "pothole" in d["damage_type"].lower())
    crack_count = sum(1 for d in detections if "crack" in d["damage_type"].lower())

    if detections:
        primary = max(detections, key=lambda d: d["confidence"])
        damage_type = primary["damage_type"]
        severity = primary["severity"]
        confidence = primary["confidence"]
    else:
        damage_type = "No Damage Detected"
        severity = "Low"
        confidence = 0.0

    report = RoadDamageReport(
        city=city,
        image_url=str(annotated_path),
        damage_type=damage_type,
        severity=severity,
        location=location,
        confidence=confidence,
        pothole_count=pothole_count,
        crack_count=crack_count,
        timestamp=datetime.utcnow(),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    if severity == "High":
        maybe_send_email("Road Damage", f"High severity {damage_type} in {city or 'Unknown'}")

    return report


def get_annotated_image_base64(image_path: str) -> Optional[str]:
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
