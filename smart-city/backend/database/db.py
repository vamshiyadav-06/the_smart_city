"""Database connection and session management."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load .env from project root
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./smart_city.db",  # Fallback for local dev without PostgreSQL
)

# Use psycopg v3 driver on Python 3.14+ when using PostgreSQL
if DATABASE_URL.startswith("postgresql://"):
    import sys

    if sys.version_info >= (3, 14):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    elif "+" not in DATABASE_URL.split("://", 1)[0]:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# SQLite needs connect_args for threading
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from backend.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
