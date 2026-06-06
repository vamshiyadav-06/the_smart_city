"""Start backend and frontend for local development."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    print("=" * 50)
    print("Smart City AI - Local Development")
    print("=" * 50)
    print("\nRun these commands in separate terminals:\n")
    print("Terminal 1 (Backend):")
    print(f"  cd {ROOT}")
    print("  uvicorn backend.main:app --reload --port 8000\n")
    print("Terminal 2 (Frontend):")
    print(f"  cd {ROOT}")
    print("  streamlit run frontend/app.py\n")
    print("Optional - Seed sample data:")
    print(f"  cd {ROOT}")
    print("  python scripts/seed_data.py\n")
    print("API Docs: http://localhost:8000/docs")
    print("Dashboard: http://localhost:8501")


if __name__ == "__main__":
    main()
