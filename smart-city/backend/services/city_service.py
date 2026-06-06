"""Indian city metadata service."""

from typing import List, Optional

from backend.data.city_images import get_city_image_paths
from backend.data.indian_cities import CITY_NAMES, INDIAN_CITIES


def list_cities() -> List[str]:
    return CITY_NAMES


def get_city(name: str) -> Optional[dict]:
    data = INDIAN_CITIES.get(name)
    if not data:
        return None
    return {
        "name": name,
        "state": data["state"],
        "population": data["population"],
        "famous_for": data["famous_for"],
        "description": data["description"],
        "lat": data["lat"],
        "lon": data["lon"],
        "area": data["area"],
        "major_industries": data["major_industries"],
        "tourist_importance": data["tourist_importance"],
        "transport_infrastructure": data["transport_infrastructure"],
        "climate_summary": data["climate_summary"],
        "zones": data["zones"],
        "image_paths": get_city_image_paths(name),
    }


def get_city_overview(name: str) -> Optional[dict]:
    city = get_city(name)
    if not city:
        return None
    return {
        "population": city["population"],
        "area": city["area"],
        "major_industries": city["major_industries"],
        "tourist_importance": city["tourist_importance"],
        "transport_infrastructure": city["transport_infrastructure"],
        "climate_summary": city["climate_summary"],
    }
