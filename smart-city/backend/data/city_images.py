"""Local city image asset helpers."""

from pathlib import Path
from typing import List

from backend.data.indian_cities import CITY_SLUGS

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "images"
EXTENSIONS = (".png", ".jpg", ".jpeg")


def city_slug(city: str) -> str:
    return CITY_SLUGS.get(city, city.lower().replace(" ", "_"))


def get_city_image_paths(city: str) -> List[str]:
    """Return public URL paths (e.g. /assets/images/hyderabad_1.png) for up to 2 images."""
    slug = city_slug(city)
    paths = []
    for i in (1, 2):
        for ext in EXTENSIONS:
            candidate = ASSETS_DIR / f"{slug}_{i}{ext}"
            if candidate.exists():
                paths.append(f"/assets/images/{slug}_{i}{ext}")
                break
    return paths


def count_png_assets() -> int:
    return len(list(ASSETS_DIR.glob("*.png")))


def count_city_assets() -> int:
    """Count city image slots (1 or 2 per city) that have any supported file."""
    total = 0
    for slug in CITY_SLUGS.values():
        for i in (1, 2):
            if any((ASSETS_DIR / f"{slug}_{i}{ext}").exists() for ext in EXTENSIONS):
                total += 1
    return total


def list_required_assets() -> List[str]:
    return [f"{slug}_{i}.png" for slug in CITY_SLUGS.values() for i in (1, 2)]
