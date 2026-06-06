"""Ensure city images exist: download from Wikimedia or convert bundled JPG assets to PNG."""

import io
import sys
from pathlib import Path

import httpx
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.data.city_photo_urls import CITY_PHOTO_URLS
from backend.data.indian_cities import CITY_SLUGS

OUT_DIR = ROOT / "assets" / "images"
MAX_WIDTH = 960
HEADERS = {
    "User-Agent": "SmartCityIndia/1.0 (https://github.com/smart-city-india; educational)",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}


def save_resized_png(data: bytes, dest: Path) -> bool:
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.Resampling.LANCZOS)
        dest.parent.mkdir(parents=True, exist_ok=True)
        img.save(dest, "PNG", optimize=True)
        return True
    except Exception as exc:
        print(f"  FAIL save {dest.name}: {exc}")
        return False


def download_and_save(url: str, dest: Path) -> bool:
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True, headers=HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
        return save_resized_png(resp.content, dest)
    except Exception as exc:
        print(f"  FAIL download {dest.name}: {exc}")
        return False


def convert_local_jpg(slug: str, index: int, dest: Path) -> bool:
    for ext in (".jpg", ".jpeg", ".png"):
        src = OUT_DIR / f"{slug}_{index}{ext}"
        if src.exists() and src.suffix.lower() != ".png":
            try:
                img = Image.open(src).convert("RGB")
                if img.width > MAX_WIDTH:
                    ratio = MAX_WIDTH / img.width
                    img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.Resampling.LANCZOS)
                img.save(dest, "PNG", optimize=True)
                print(f"CONV {dest.name} from {src.name}")
                return True
            except Exception as exc:
                print(f"  FAIL convert {src.name}: {exc}")
    return False


def ensure_image(city: str, slug: str, index: int, url: str) -> str:
    dest = OUT_DIR / f"{slug}_{index}.png"
    if dest.exists():
        print(f"SKIP {dest.name}")
        return "skipped"

    print(f"GET  {dest.name} …")
    if download_and_save(url, dest):
        return "downloaded"

    if convert_local_jpg(slug, index, dest):
        return "converted"

    return "failed"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stats = {"downloaded": 0, "converted": 0, "skipped": 0, "failed": 0}

    for city, urls in CITY_PHOTO_URLS.items():
        slug = CITY_SLUGS.get(city, city.lower())
        for i, url in enumerate(urls[:2], start=1):
            result = ensure_image(city, slug, i, url)
            stats[result] = stats.get(result, 0) + 1

    print(
        f"\nDone: {stats['downloaded']} downloaded, {stats['converted']} converted, "
        f"{stats['skipped']} skipped, {stats['failed']} failed"
    )


if __name__ == "__main__":
    main()
