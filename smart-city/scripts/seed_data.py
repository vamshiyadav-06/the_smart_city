"""Seed traffic and parking data for demo cities."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.database.db import SessionLocal, init_db
from backend.services.parking_service import refresh_city_parking
from backend.services.traffic_service import refresh_city_traffic

DEMO_CITIES = ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Chennai"]


async def main():
    init_db()
    db = SessionLocal()
    try:
        for city in DEMO_CITIES:
            print(f"Seeding {city}…")
            await refresh_city_traffic(db, city)
            refresh_city_parking(db, city)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
