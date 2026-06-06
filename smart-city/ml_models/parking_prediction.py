"""Parking occupancy prediction using LightGBM."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent / "saved"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "parking_lgbm_model.joblib"


def _generate_training_data(n_samples: int = 2000) -> pd.DataFrame:
    np.random.seed(42)
    hours = np.random.randint(0, 24, n_samples)
    dow = np.random.randint(0, 7, n_samples)
    total = np.random.choice([80, 100, 150, 200, 350, 500], n_samples)
    business_hours = (hours >= 9) & (hours <= 18) & (dow < 5)
    base_occ = np.where(business_hours, 0.75, 0.35)
    occupancy_ratio = np.clip(base_occ + np.random.randn(n_samples) * 0.15, 0.05, 0.98)
    occupied = (total * occupancy_ratio).astype(int)
    return pd.DataFrame(
        {
            "hour": hours,
            "day_of_week": dow,
            "total_slots": total,
            "occupied_slots": occupied,
            "occupancy_ratio": occupancy_ratio,
        }
    )


def train_model():
    """Train LightGBM model (falls back to sklearn GBM if LightGBM unavailable)."""
    df = _generate_training_data()
    X = df[["hour", "day_of_week", "total_slots"]]
    y = df["occupancy_ratio"]

    try:
        import lightgbm as lgb

        model = lgb.LGBMRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42,
            verbose=-1,
        )
    except ImportError:
        from sklearn.ensemble import GradientBoostingRegressor

        model = GradientBoostingRegressor(n_estimators=100, random_state=42)

    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    logger.info("Parking model saved to %s", MODEL_PATH)
    return model


def _load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return train_model()


def predict_occupancy(history: List) -> dict:
    """Predict future parking occupancy."""
    model = _load_model()
    now = datetime.utcnow()
    next_hour = (now.hour + 1) % 24

    if history:
        latest = history[0]
        total = latest.total_slots
    else:
        total = 200

    features = np.array([[next_hour, now.weekday(), total]])
    ratio = float(model.predict(features)[0])
    ratio = np.clip(ratio, 0.05, 0.99)

    # Estimate peak hour from model predictions across day
    hour_preds = []
    for h in range(24):
        pred = float(model.predict(np.array([[h, now.weekday(), total]]))[0])
        hour_preds.append((h, pred))
    peak_hour = max(hour_preds, key=lambda x: x[1])[0]

    return {
        "occupancy_pct": round(ratio * 100, 1),
        "peak_hour": peak_hour,
    }


if __name__ == "__main__":
    train_model()
    print("Parking prediction model trained successfully.")
