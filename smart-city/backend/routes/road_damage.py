"""Road damage detection API."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.schemas import DamageReportResponse
from backend.services.damage_service import (
    detect_road_damage,
    get_annotated_image_base64,
    get_damage_reports,
    get_damage_stats,
)

router = APIRouter(prefix="/road-damage", tags=["Road Damage"])


@router.get("", response_model=List[DamageReportResponse])
def list_reports(
    city: Optional[str] = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return get_damage_reports(db, city=city, limit=limit)


@router.get("/stats")
def damage_stats(city: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return get_damage_stats(db, city=city)


@router.post("/detect", response_model=DamageReportResponse, status_code=201)
async def detect_damage(
    file: UploadFile = File(...),
    city: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(400, "No file provided")
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png"):
        raise HTTPException(400, "Only jpg, jpeg, png supported")
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")
    try:
        return await detect_road_damage(db, contents, file.filename, city, location)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/image/{report_id}")
def get_annotated_image(report_id: int, db: Session = Depends(get_db)):
    from backend.database.models import RoadDamageReport

    report = db.query(RoadDamageReport).filter(RoadDamageReport.id == report_id).first()
    if not report or not report.image_url:
        raise HTTPException(404, "Image not found")
    b64 = get_annotated_image_base64(report.image_url)
    if not b64:
        raise HTTPException(404, "Image file missing")
    return {"image_base64": b64}
