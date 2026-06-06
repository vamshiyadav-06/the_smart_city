"""Traffic prediction using Random Forest / XGBoost."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent / "saved"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "traffic_rf_model.joblib"


def _extract_features(records: List) -> pd.DataFrame:
    """Build feature matrix from traffic records."""
    rows = []
    for r in records:
        ts = r.timestamp if hasattr(r, "timestamp") else datetime.fromisoformat(r["timestamp"])
        rows.append(
            {
                "hour": ts.hour,
                "day_of_week": ts.weekday(),
                "vehicle_count": r.vehicle_count if hasattr(r, "vehicle_count") else r["vehicle_count"],
                "avg_speed": r.avg_speed if hasattr(r, "avg_speed") else r["avg_speed"],
            }
        )
    return pd.DataFrame(rows)


def _generate_training_data(n_samples: int = 2000) -> pd.DataFrame:
    """Generate synthetic training data for initial model."""
    np.random.seed(42)
    hours = np.random.randint(0, 24, n_samples)
    dow = np.random.randint(0, 7, n_samples)
    peak = ((hours >= 7) & (hours <= 9)) | ((hours >= 17) & (hours <= 19))
    base = np.random.randint(50, 300, n_samples)
    vehicle_count = base + peak.astype(int) * np.random.randint(100, 250, n_samples)
    avg_speed = np.clip(65 - vehicle_count / 10 + np.random.randn(n_samples) * 5, 5, 70)
    congestion = (avg_speed < 15).astype(float) * 0.8 + (avg_speed < 30).astype(float) * 0.4
    return pd.DataFrame(
        {
            "hour": hours,
            "day_of_week": dow,
            "vehicle_count": vehicle_count,
            "avg_speed": avg_speed,
            "congestion_prob": np.clip(congestion, 0, 1),
        }
    )


def train_model() -> RandomForestRegressor:
    """Train Random Forest model on synthetic + optional real data."""
    df = _generate_training_data()
    X = df[["hour", "day_of_week", "vehicle_count", "avg_speed"]]
    y = df["vehicle_count"]
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    logger.info("Traffic model saved to %s", MODEL_PATH)
    return model


def _load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return train_model()


def congestion_from_speed(speed: float) -> str:
    if speed < 15:
        return "High"
    if speed < 30:
        return "Medium"
    return "Low"


def predict_next_hour(history: List) -> dict:
    """Predict next hour traffic from historical records."""
    model = _load_model()
    now = datetime.utcnow()
    next_hour = (now.hour + 1) % 24

    if history:
        latest = history[0]
        avg_speed = latest.avg_speed
        last_count = latest.vehicle_count
    else:
        avg_speed = 35.0
        last_count = 200

    features = np.array([[next_hour, now.weekday(), last_count, avg_speed]])
    predicted_count = float(model.predict(features)[0])
    predicted_count = max(predicted_count, 0)

    # Congestion probability based on predicted count and speed trend
    congestion_prob = min(predicted_count / 600, 1.0)
    if avg_speed < 20:
        congestion_prob = min(congestion_prob + 0.3, 1.0)

    predicted_speed = max(65 - predicted_count / 12, 5)
    return {
        "vehicle_count": round(predicted_count, 1),
        "congestion_probability": round(congestion_prob, 2),
        "congestion_level": congestion_from_speed(predicted_speed),
    }


if __name__ == "__main__":
    train_model()
    print("Traffic prediction model trained successfully.")
