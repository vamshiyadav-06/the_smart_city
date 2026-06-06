"""Print local development startup commands."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    print("Smart City India — Local Development\n")
    print(f"cd {ROOT}\n")
    print("Terminal 1: uvicorn backend.main:app --reload --port 8000")
    print("Terminal 2: streamlit run frontend/app.py")
    print("Optional:   python scripts/seed_data.py")
    print("Images:      python scripts/download_city_images.py")


if __name__ == "__main__":
    main()
