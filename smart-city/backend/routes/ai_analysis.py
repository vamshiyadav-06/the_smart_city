"""Real-time AI analysis API (Groq)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.services.damage_service import get_damage_count
from backend.services.groq_service import generate_city_analysis
from backend.services.parking_service import get_city_parking_analytics
from backend.services.traffic_service import get_city_traffic_analytics

router = APIRouter(prefix="/ai-analysis", tags=["AI Analysis"])


@router.get("/{city}")
async def get_analysis(
    city: str,
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
):
    traffic = get_city_traffic_analytics(db, city)
    parking = get_city_parking_analytics(db, city)
    context = {
        "congestion_level": traffic["congestion_level"],
        "avg_speed": traffic["avg_speed"],
        "density_score": traffic["density_score"],
        "parking_utilization": parking["utilization_pct"],
        "damage_count": get_damage_count(db, city),
    }
    return await generate_city_analysis(db, city, context, force_refresh=refresh)


@router.get("/{city}/history")
def analysis_history(city: str, limit: int = 5, db: Session = Depends(get_db)):
    from backend.database.models import AIAnalysisReport

    reports = (
        db.query(AIAnalysisReport)
        .filter(AIAnalysisReport.city == city)
        .order_by(AIAnalysisReport.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "city": r.city,
            "confidence": r.confidence,
            "timestamp": r.timestamp.isoformat(),
            "preview": r.analysis_text[:200] + "...",
        }
        for r in reports
    ]
