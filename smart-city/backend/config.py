"""Application configuration from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./smart_city.db")
    tomtom_api_key: str = os.getenv("TOMTOM_API_KEY", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    api_secret_key: str = os.getenv("API_SECRET_KEY", "dev-secret-key")
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    alert_email_to: str = os.getenv("ALERT_EMAIL_TO", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

settings = Settings()
