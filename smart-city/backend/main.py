"""Smart City India — FastAPI Backend."""
from dotenv import load_dotenv
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database.db import init_db
from backend.routes import ai_analysis, cities, parking, reports, road_damage, traffic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ASSETS = ROOT / "assets" / "images"
ASSETS.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Smart City India...")
    init_db()
    if len(list(ASSETS.glob("*.jpg"))) < 24:
        try:
            import subprocess
            subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_city_images.py")], check=False)
        except Exception as e:
            logger.warning("City image generation skipped: %s", e)
    try:
        from ml_models.traffic_prediction import train_model as train_traffic
        from ml_models.parking_prediction import train_model as train_parking
        train_traffic()
        train_parking()
    except Exception as e:
        logger.warning("Model training skipped: %s", e)
    yield


app = FastAPI(
    title="Smart City India API",
    description="AI-Powered Urban Analytics Platform for Indian Cities",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets/images", StaticFiles(directory=str(ASSETS)), name="city-images")

app.include_router(cities.router)
app.include_router(traffic.router)
app.include_router(parking.router)
app.include_router(road_damage.router)
app.include_router(ai_analysis.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "smart-city-india"}


@app.get("/")
def root():
    return {"message": "Smart City India API", "docs": "/docs"}
