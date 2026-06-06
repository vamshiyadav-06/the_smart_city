"""Generate local city placeholder images under assets/images/."""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.data.indian_cities import CITY_SLUGS, INDIAN_CITIES

OUT = ROOT / "assets" / "images"
OUT.mkdir(parents=True, exist_ok=True)

PALETTES = [
    ("#0d1b2a", "#ff9933"),
    ("#1b263b", "#e0e1dd"),
    ("#14213d", "#fca311"),
    ("#1a1a2e", "#00d4ff"),
]


def make_image(city: str, index: int, slug: str):
    w, h = 960, 540
    bg, accent = PALETTES[index % len(PALETTES)]
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)
    try:
        font_lg = ImageFont.truetype("arial.ttf", 52)
        font_sm = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font_lg = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    state = INDIAN_CITIES[city]["state"]
    draw.text((40, 180), city, fill=accent, font=font_lg)
    draw.text((40, 260), state, fill="#a0a0b8", font=font_sm)
    draw.text((40, 310), f"Smart City India · View {index}", fill="#888899", font=font_sm)
    draw.rectangle([0, h - 8, w, h], fill=accent)

    path = OUT / f"{slug}_{index}.jpg"
    img.save(path, "JPEG", quality=88)
    print(f"Created {path}")


def main():
    for city, slug in CITY_SLUGS.items():
        make_image(city, 1, slug)
        make_image(city, 2, slug)
    print("Done — 24 city images generated.")


if __name__ == "__main__":
    main()
