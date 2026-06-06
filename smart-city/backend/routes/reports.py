"""Reports export API."""

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database.models import AIAnalysisReport
from backend.services.damage_service import get_damage_reports, get_damage_stats
from backend.services.parking_service import get_city_parking_analytics, get_parking_data
from backend.services.traffic_service import get_city_traffic_analytics, get_traffic_data

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/traffic/csv")
def export_traffic_csv(city: str = Query("Hyderabad"), db: Session = Depends(get_db)):
    records = get_traffic_data(db, city=city, limit=1000)
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["id", "city", "location", "vehicle_count", "avg_speed", "congestion_level", "timestamp"])
    for r in records:
        w.writerow([r.id, r.city, r.location, r.vehicle_count, r.avg_speed, r.congestion_level, r.timestamp])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=traffic_{city}.csv"},
    )


@router.get("/parking/csv")
def export_parking_csv(city: str = Query("Hyderabad"), db: Session = Depends(get_db)):
    records = get_parking_data(db, city=city, limit=1000)
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["id", "city", "parking_name", "total_slots", "occupied_slots", "available_slots", "timestamp"])
    for r in records:
        w.writerow([r.id, r.city, r.parking_name, r.total_slots, r.occupied_slots, r.available_slots, r.timestamp])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=parking_{city}.csv"},
    )


@router.get("/damage/csv")
def export_damage_csv(city: str = Query(None), db: Session = Depends(get_db)):
    records = get_damage_reports(db, city=city, limit=1000)
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["id", "city", "damage_type", "severity", "pothole_count", "crack_count", "confidence", "timestamp"])
    for r in records:
        w.writerow([r.id, r.city, r.damage_type, r.severity, r.pothole_count, r.crack_count, r.confidence, r.timestamp])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=road_damage.csv"},
    )


@router.get("/full/pdf")
def export_full_pdf(city: str = Query("Hyderabad"), db: Session = Depends(get_db)):
    from fpdf import FPDF

    traffic = get_city_traffic_analytics(db, city)
    parking = get_city_parking_analytics(db, city)
    damage = get_damage_stats(db, city=city)
    ai_report = (
        db.query(AIAnalysisReport)
        .filter(AIAnalysisReport.city == city)
        .order_by(AIAnalysisReport.timestamp.desc())
        .first()
    )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Smart City India - {city} Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")
    pdf.ln(8)

    sections = [
        ("Traffic Analytics", [
            f"Congestion: {traffic['congestion_level']}",
            f"Avg Speed: {traffic['avg_speed']} km/h",
            f"Density Score: {traffic['density_score']}/100",
        ]),
        ("Parking Analytics", [
            f"Total Slots: {parking['total_slots']}",
            f"Utilization: {parking['utilization_pct']}%",
            f"Available: {parking['available_slots']}",
        ]),
        ("Road Damage", [
            f"Total Reports: {damage['total']}",
            f"Potholes: {damage['pothole_count']}",
            f"Cracks: {damage['crack_count']}",
        ]),
    ]
    for title, lines in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 9)
        for line in lines:
            pdf.cell(0, 5, line, ln=True)
        pdf.ln(4)

    if ai_report:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "AI Analysis Summary", ln=True)
        pdf.set_font("Helvetica", "", 8)
        for line in ai_report.analysis_text.split("\n")[:30]:
            clean = line.replace("##", "").strip()[:90]
            if clean:
                pdf.cell(0, 4, clean, ln=True)

    return StreamingResponse(
        io.BytesIO(pdf.output()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=smart_city_india_{city}.pdf"},
    )
