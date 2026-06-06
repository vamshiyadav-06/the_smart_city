# Smart City AI Management System

AI-powered Smart City Dashboard combining **Traffic Management**, **Smart Parking**, **Road Damage Detection**, and **Real-Time Alerts**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red)

## Features

| Module | Capabilities |
|--------|-------------|
| **Dashboard** | KPI cards, auto-refresh, traffic/parking/damage charts, alerts |
| **Traffic** | Real-time monitoring, Folium maps, congestion prediction (Random Forest), weather impact |
| **Parking** | Slot utilization, occupancy forecast (LightGBM), 90% capacity alerts |
| **Road Damage** | YOLOv8 image detection, bounding boxes, severity scoring |
| **Reports** | PDF & CSV exports, AI city insights chat assistant |
| **Alerts** | Auto-generated for high traffic, full parking, severe road damage |

## Tech Stack

- **Frontend:** Streamlit (dark theme, Plotly, Folium)
- **Backend:** FastAPI, Pydantic, SQLAlchemy
- **Database:** PostgreSQL (Neon/Avion) with SQLite fallback for local dev
- **ML:** YOLOv8, Random Forest, LightGBM
- **Deploy:** Render

## Project Structure

```
smart-city/
├── frontend/           # Streamlit dashboard
├── backend/            # FastAPI REST API
├── ml_models/          # Traffic, parking, damage ML
├── datasets/           # SQL scripts, uploads
├── scripts/            # Seed data, utilities
├── requirements.txt
├── render.yaml
└── README.md
```

## Quick Start

### 1. Clone & Install

```bash
cd smart-city
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings. For local development, defaults work out of the box (SQLite).

```env
DATABASE_URL=postgresql://user:pass@host/dbname   # Optional
BACKEND_URL=http://localhost:8000
TOMTOM_API_KEY=your_key          # Optional
OPENWEATHER_API_KEY=your_key     # Optional
```

### 3. Run the Application

**Terminal 1 — Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
streamlit run frontend/app.py
```

**Terminal 3 — Seed sample data (optional):**
```bash
python scripts/seed_data.py
```

- **Dashboard:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/traffic` | List traffic records |
| POST | `/traffic` | Add traffic record |
| POST | `/traffic/refresh` | Refresh all zones |
| GET | `/parking` | List parking records |
| POST | `/parking` | Add parking record |
| POST | `/detect-road-damage` | Upload image for detection |
| GET | `/dashboard` | Dashboard aggregation |
| GET | `/alerts` | List alerts |
| GET | `/reports/traffic/csv` | Export traffic CSV |
| GET | `/reports/full/pdf` | Export full PDF report |
| POST | `/chat` | AI city insights assistant |

## Database Setup (PostgreSQL)

Run the SQL script on your Neon/Avion database:

```bash
psql $DATABASE_URL -f datasets/init.sql
```

Or let SQLAlchemy auto-create tables on first startup.

## ML Models

Models train automatically on first startup using synthetic data. For production, replace with real datasets:

```bash
python ml_models/traffic_prediction.py
python ml_models/parking_prediction.py
```

Place custom YOLOv8 weights at `ml_models/saved/road_damage_yolov8.pt`.

## Congestion Rules

```python
if speed < 15:   congestion = "High"
elif speed < 30: congestion = "Medium"
else:            congestion = "Low"
```

## Alert Triggers

- **Traffic:** `vehicle_count > 500`
- **Parking:** `occupancy > 90%`
- **Road Damage:** `severity == "High"`

## Deploy to Render

1. Push to GitHub
2. Create a new **Blueprint** on Render using `render.yaml`
3. Set environment variables:
   - `DATABASE_URL` (Neon PostgreSQL connection string)
   - `TOMTOM_API_KEY` (optional)
   - `OPENWEATHER_API_KEY` (optional)

Render deploys two services:
- **smart-city-api** — FastAPI backend
- **smart-city-dashboard** — Streamlit frontend

## Security

- All secrets in `.env` (never committed)
- `.env.example` provided as template
- Pydantic validation on all API inputs
- File upload size limits (10MB)

## Bonus Features

- AI Chat Assistant for city insights
- Email alerts via SMTP (configure in `.env`)
- Weather impact on traffic (OpenWeather API)
- Real-time dashboard auto-refresh
- Predictive analytics for traffic and parking

## License

MIT
