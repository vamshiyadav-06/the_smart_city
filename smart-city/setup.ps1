# Smart City AI - Windows Setup Script
Write-Host "Smart City AI Management System - Setup" -ForegroundColor Cyan

if (-not (Test-Path "venv")) {
    python -m venv venv
}

& .\venv\Scripts\pip install --upgrade pip
& .\venv\Scripts\pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete! Run:" -ForegroundColor Green
Write-Host "  Terminal 1: .\venv\Scripts\uvicorn backend.main:app --reload --port 8000"
Write-Host "  Terminal 2: .\venv\Scripts\streamlit run frontend/app.py"
Write-Host "  Optional:   .\venv\Scripts\python scripts\seed_data.py"
