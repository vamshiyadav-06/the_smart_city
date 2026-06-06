"""Groq-powered real-time city analysis."""

import logging
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from backend.config import settings
from backend.data.indian_cities import INDIAN_CITIES
from backend.database.models import AIAnalysisReport
from backend.services.cache_service import groq_cache

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

ANALYSIS_SECTIONS = [
    "City Overview",
    "Traffic Situation",
    "Road Infrastructure Quality",
    "Parking Challenges",
    "Urban Growth Analysis",
    "Transport Recommendations",
    "Smart City Improvement Suggestions",
    "Future Development Opportunities",
]


def _build_prompt(city: str, context: dict) -> str:
    info = INDIAN_CITIES.get(city, {})
    return f"""You are an expert Smart City analyst for India. Generate a detailed, professional urban intelligence report for {city}, {info.get('state', 'India')}.

City facts:
- Population: {info.get('population', 'N/A')}
- Famous for: {info.get('famous_for', 'N/A')}
- Major industries: {info.get('major_industries', 'N/A')}
- Transport: {info.get('transport_infrastructure', 'N/A')}
- Climate: {info.get('climate_summary', 'N/A')}

Live system data:
- Traffic congestion: {context.get('congestion_level', 'Medium')}
- Average speed: {context.get('avg_speed', 25)} km/h
- Traffic density score: {context.get('density_score', 65)}/100
- Parking utilization: {context.get('parking_utilization', 72)}%
- Road damage reports: {context.get('damage_count', 0)}

Write a structured report with exactly these 8 sections (use ## headers):
1. City Overview
2. Traffic Situation
3. Road Infrastructure Quality
4. Parking Challenges
5. Urban Growth Analysis
6. Transport Recommendations
7. Smart City Improvement Suggestions
8. Future Development Opportunities

Be specific to {city}. Use data-driven insights. Keep each section 2-4 sentences. Professional tone for government stakeholders."""


async def generate_city_analysis(
    db: Session,
    city: str,
    context: Optional[dict] = None,
    force_refresh: bool = False,
) -> dict:
    """Generate or return cached AI analysis for a city."""
    if not force_refresh:
        cached = (
            db.query(AIAnalysisReport)
            .filter(AIAnalysisReport.city == city)
            .order_by(AIAnalysisReport.timestamp.desc())
            .first()
        )
        if cached:
            age = (datetime.utcnow() - cached.timestamp).total_seconds()
            if age < 3600:
                return {
                    "city": city,
                    "analysis": cached.analysis_text,
                    "confidence": cached.confidence,
                    "timestamp": cached.timestamp.isoformat(),
                    "cached": True,
                }

    context = context or {}
    analysis_text = await _call_groq(city, context)
    confidence = 0.92 if settings.groq_api_key else 0.75

    report = AIAnalysisReport(
        city=city,
        analysis_text=analysis_text,
        confidence=confidence,
        timestamp=datetime.utcnow(),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "city": city,
        "analysis": report.analysis_text,
        "confidence": report.confidence,
        "timestamp": report.timestamp.isoformat(),
        "cached": False,
    }


async def generate_traffic_insights(city: str, traffic: dict) -> dict:
    """Groq-powered traffic insights for Traffic Analysis page."""
    cache_key = f"traffic_ai:{city}:{traffic.get('congestion_level')}:{traffic.get('density_score')}"
    cached = groq_cache.get(cache_key)
    if cached:
        return cached

    prompt = f"""Analyze traffic for {city}, India.
Congestion: {traffic.get('congestion_level')}
Avg speed: {traffic.get('avg_speed')} km/h
Density score: {traffic.get('density_score')}/100
Peak hours: {traffic.get('peak_hours')}

Respond in exactly 4 short sections with headers:
## Traffic Summary
## Congestion Causes
## Peak Hour Analysis
## Suggested Improvements
Be specific to {city}. Professional government report tone."""

    text = await _groq_chat(prompt, "You are an Indian urban traffic analyst.")
    if not text:
        text = _fallback_traffic_insights(city, traffic)

    result = {
        "city": city,
        "insights": text,
        "confidence": 0.9 if settings.groq_api_key else 0.72,
    }
    groq_cache.set(cache_key, result)
    return result


def _fallback_traffic_insights(city: str, traffic: dict) -> str:
    c = traffic.get("congestion_level", "Medium")
    peaks = ", ".join(f"{h}:00" for h in traffic.get("peak_hours", [8, 9, 18])[:3])
    return f"""## Traffic Summary
{city} is experiencing **{c}** congestion with average speeds of {traffic.get('avg_speed', 25):.0f} km/h.

## Congestion Causes
Peak commuter flows, commercial district activity, and junction bottlenecks contribute to delays.

## Peak Hour Analysis
Highest volumes expected at {peaks} IST on weekdays.

## Suggested Improvements
Expand metro feeder services, optimize signal timing, and promote staggered office hours."""


async def _groq_chat(prompt: str, system: str) -> Optional[str]:
    if not settings.groq_api_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"},
                json={
                    "model": MODEL,
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                    "temperature": 0.6,
                    "max_tokens": 800,
                },
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning("Groq chat failed: %s", e)
    return None


async def _call_groq(city: str, context: dict) -> str:
    prompt = _build_prompt(city, context)
    text = await _groq_chat(prompt, "You are a Smart City India urban analytics expert.")
    return text if text else _fallback_analysis(city, context)


def _fallback_analysis(city: str, context: dict) -> str:
    info = INDIAN_CITIES.get(city, {})
    congestion = context.get("congestion_level", "Medium")
    util = context.get("parking_utilization", 70)
    return f"""## City Overview
{city} in {info.get('state', 'India')} is {info.get('description', 'a major Indian urban center.')}

## Traffic Situation
Current congestion level is **{congestion}** with average speeds around {context.get('avg_speed', 28):.0f} km/h. Peak hours typically occur 8–10 AM and 5–8 PM on major corridors.

## Road Infrastructure Quality
Road networks in {city} show mixed conditions. {context.get('damage_count', 0)} damage reports logged. Priority maintenance needed on high-traffic arterials.

## Parking Challenges
Parking utilization stands at **{util:.0f}%**. Commercial zones face peak-hour shortages; metro-linked parking offers relief.

## Urban Growth Analysis
With population of {info.get('population', 'N/A')}, {city} is experiencing rapid urbanization driven by {info.get('major_industries', 'diverse sectors')}.

## Transport Recommendations
Expand metro/BRTS coverage, implement dynamic traffic signals, and promote last-mile connectivity via e-rickshaws and bike-sharing.

## Smart City Improvement Suggestions
Deploy IoT sensors for air quality and traffic, integrate unified parking apps, and use AI for predictive maintenance of roads.

## Future Development Opportunities
Invest in {info.get('transport_infrastructure', 'transit infrastructure')}, smart grid pilots, and digital citizen services under the Smart Cities Mission."""
