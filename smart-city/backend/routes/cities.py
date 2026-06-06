"""Indian cities API."""

from typing import List

from fastapi import APIRouter, HTTPException

from backend.data.indian_cities import CITY_NAMES
from backend.services.city_service import get_city, get_city_overview, list_cities

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("", response_model=List[str])
def get_cities():
    return list_cities()


@router.get("/{city_name}")
def city_detail(city_name: str):
    city = get_city(city_name)
    if not city:
        raise HTTPException(404, f"City '{city_name}' not found")
    return city


@router.get("/{city_name}/overview")
def city_overview(city_name: str):
    overview = get_city_overview(city_name)
    if not overview:
        raise HTTPException(404, f"City '{city_name}' not found")
    return overview
