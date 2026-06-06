# Smart City India

AI-powered urban analytics platform for 12 Indian cities — traffic, parking, road damage detection, Groq AI analysis, and PDF/CSV reports.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red)

## Features

| Module | Capabilities |
|--------|-------------|
| **Dashboard** | City metadata, image gallery, KPI overview, analytics module selector |
| **Traffic Analysis** | TomTom/simulated data, congestion heatmap, ML forecast (Random Forest), Groq insights |
| **Smart Parking** | Zone utilization, occupancy forecast (LightGBM), AI recommendations |
| **Road Damage** | YOLOv8 image detection, severity scoring, report history |
| **Real-Time AI Analysis** | Groq-powered full city intelligence report |
| **Reports** | PDF and CSV exports |

## Tech Stack

- **Frontend:** Streamlit (dark theme, Plotly)
- **Backend:** FastAPI, Pydantic, SQLAlchemy
- **Database:** SQLite (local) / PostgreSQL (production)
- **ML:** YOLOv8, Random Forest, LightGBM
- **Deploy:** Render (backend) + Streamlit Cloud (frontend)

## Project Structure

```
smart-city/
├── backend/              # FastAPI REST API
├── frontend/             # Streamlit dashboard
├── ml_models/            # Traffic, parking, damage ML
├── assets/images/        # City photos (PNG/JPG)
├── datasets/             # SQL init script, uploads
├── scripts/              # Seed data, image download, utilities
├── .streamlit/           # Streamlit Cloud config
├── requirements.txt
├── runtime.txt           # Python 3.11 for Streamlit Cloud
├── render.yaml           # Render Blueprint (backend)
├── Procfile
├── .env.example
└── README.md
```

## Quick Start (Local)

### 1. Install

```powershell
cd smart-city
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Or run `.\setup.ps1` on Windows.

### 2. Configure

```powershell
copy .env.example .env
```

Edit `.env` with your API keys. Defaults work out of the box with SQLite — no PostgreSQL required locally.

### 3. Run

**Terminal 1 — Backend:**
```powershell
.\venv\Scripts\uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```powershell
.\venv\Scripts\streamlit run frontend/app.py
```

**Optional — Seed sample data:**
```powershell
.\venv\Scripts\python scripts\seed_data.py
```

**Optional — Download city photos:**
```powershell
.\venv\Scripts\python scripts\download_city_images.py
```

- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/cities` | List all cities |
| GET | `/cities/{city}` | City metadata + image URLs |
| GET | `/traffic/{city}/analytics` | Traffic analytics |
| POST | `/traffic/{city}/refresh` | Refresh traffic data |
| GET | `/traffic/{city}/ai-insights` | Groq traffic insights |
| GET | `/parking/{city}/analytics` | Parking analytics |
| POST | `/parking/{city}/refresh` | Refresh parking data |
| POST | `/road-damage/detect` | Upload image for YOLOv8 detection |
| GET | `/road-damage` | List damage reports |
| GET | `/ai-analysis/{city}` | Full Groq AI city report |
| GET | `/reports/traffic/csv` | Export traffic CSV |
| GET | `/reports/parking/csv` | Export parking CSV |
| GET | `/reports/damage/csv` | Export damage CSV |
| GET | `/reports/full/pdf` | Export full PDF report |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Production | PostgreSQL connection string. Defaults to SQLite locally |
| `GROQ_API_KEY` | Optional | Groq AI analysis (falls back to template text) |
| `TOMTOM_API_KEY` | Optional | Live traffic data (falls back to simulation) |
| `OPENWEATHER_API_KEY` | Optional | Weather impact on traffic |
| `API_SECRET_KEY` | Recommended | API security key |
| `SMTP_HOST/USER/PASSWORD` | Optional | Email alerts |
| `ALERT_EMAIL_TO` | Optional | Alert recipient |
| `BACKEND_URL` | Frontend | Backend URL for Streamlit (local `.env` or Streamlit secrets) |

See `.env.example` for the full template.

---

## Deploy Backend (Render)

### Option A — Blueprint (`render.yaml`)

1. Push the `smart-city/` folder to GitHub (as repo root, or note the subfolder path).
2. On Render → **New Blueprint** → connect repo.
3. If your Git repo root is the parent of `smart-city/`, set **Root Directory** to `smart-city` in the Render dashboard.
4. Add environment variables in the Render dashboard.

### Option B — Manual Web Service

| Setting | Value |
|---------|-------|
| **Root Directory** | `smart-city` (if repo contains parent folder) or `.` (if repo root is smart-city) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt && python scripts/download_city_images.py` |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| **Health Check Path** | `/health` |

### Render Environment Variables

```
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
GROQ_API_KEY=your_groq_key
TOMTOM_API_KEY=your_tomtom_key
OPENWEATHER_API_KEY=your_openweather_key
API_SECRET_KEY=generate-a-random-string
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL_TO=alerts@example.com
```

PostgreSQL is auto-configured via SQLAlchemy on first startup. Optionally run `datasets/init.sql` manually.

---

## Deploy Frontend (Streamlit Cloud)

| Setting | Value |
|---------|-------|
| **Repository** | Your GitHub repo |
| **Branch** | `main` |
| **Main file path** | `frontend/app.py` (or `smart-city/frontend/app.py` if repo root is parent) |
| **Python version** | 3.11 (set in Advanced settings, or use `runtime.txt`) |

### Streamlit Secrets

In **App Settings → Secrets**, add:

```toml
BACKEND_URL = "https://your-api-name.onrender.com"
```

Do **not** use `python-dotenv` in the frontend — secrets are resolved via `st.secrets` with a localhost fallback for local dev.

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` for local Streamlit secrets (gitignored).

---

## Security

- Never commit `.env` or `.streamlit/secrets.toml`
- All API keys read from environment variables (backend) or `st.secrets` (frontend)
- `.env.example` provided as a safe template
- Pydantic validation on all API inputs
- Rotate any keys that were shared in chat or committed by mistake

## ML Models

Models train automatically on first backend startup using synthetic data. Pre-trained weights are saved to `ml_models/saved/`.

Place custom YOLOv8 weights at `ml_models/saved/road_damage_yolov8.pt` for production road damage detection.

## License

MIT
