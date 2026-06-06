"""Local city image asset helpers."""

from pathlib import Path
from typing import List

from backend.data.indian_cities import CITY_SLUGS

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "images"


def city_slug(city: str) -> str:
    return CITY_SLUGS.get(city, city.lower().replace(" ", "_"))


def get_city_image_paths(city: str) -> List[str]:
    """Return absolute paths to exactly 2 city images if they exist."""
    slug = city_slug(city)
    paths = []
    for i in (1, 2):
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = ASSETS_DIR / f"{slug}_{i}{ext}"
            if candidate.exists():
                paths.append(str(candidate))
                break
    return paths[:2]


def list_required_assets() -> List[str]:
    """Filenames expected under assets/images/."""
    names = []
    for city, slug in CITY_SLUGS.items():
        names.append(f"{slug}_1.jpg")
        names.append(f"{slug}_2.jpg")
    return names
