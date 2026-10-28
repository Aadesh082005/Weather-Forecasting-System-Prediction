
import json
from pathlib import Path

import joblib
import pandas as pd
import requests

from src.data_collection import get_city_location
from src.preprocessing import FEATURES, TARGETS

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT_DIR / "models"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_recent_weather(location):
    """Fetch recent daily weather observations for model inputs."""
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": (
            "temperature_2m_mean,"
            "relative_humidity_2m_mean,"
            "precipitation_sum,"
            "wind_speed_10m_mean"
        ),
        "past_days": 7,
        "forecast_days": 1,
        "timezone": location.get("timezone") or "auto",
    }

    response = requests.get(FORECAST_URL, params=params, timeout=30)
    response.raise_for_status()

    daily = response.json().get("daily", {})
    if not daily or not daily.get("time"):
        raise ValueError("Weather API returned no daily data.")

    df = pd.DataFrame({
        "date": daily["time"],
        "temperature": daily.get("temperature_2m_mean"),
        "humidity": daily.get("relative_humidity_2m_mean"),
        "rainfall": daily.get("precipitation_sum"),
        "wind_speed": daily.get("wind_speed_10m_mean"),
    })

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for column in ["temperature", "humidity", "rainfall", "wind_speed"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return (
        df.dropna()
        .sort_values("date")
        .drop_duplicates("date")
        .reset_index(drop=True)
    )


def predict_next_day(city="Nagpur"):
    """Return the next-day ML estimate for temperature, humidity and rainfall."""
    metadata_path = MODEL_DIR / "model_metadata.json"

    if not metadata_path.exists():
        raise FileNotFoundError(
            "Trained models are missing. Run: "
            "python -m src.train_model --city Nagpur --days 730"
        )

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    location = get_city_location(city)

    if metadata.get("city", "").casefold() != location["name"].casefold():
        raise ValueError(
            f"Models are trained for {metadata.get('city')}, "
            f"not {location['name']}. Train models for this city first."
        )

    df = get_recent_weather(location)

    # Use data dated today or earlier; do not use tomorrow's forecast as input.
    today = pd.Timestamp.now(tz=location.get("timezone") or "UTC").date()
    df = df[df["date"].dt.date <= today].reset_index(drop=True)

    if len(df) < 4:
        raise ValueError("Not enough recent daily weather data to predict.")

    latest = df.iloc[-1]
    previous = df.iloc[:-1].tail(3)

    if len(previous) < 3:
        raise ValueError("At least four daily records are required.")

    prediction_date = latest["date"] + pd.Timedelta(days=1)

    input_values = {
        "temperature_lag1": float(latest["temperature"]),
        "temperature_lag2": float(previous.iloc[-1]["temperature"]),
        "temperature_lag3": float(previous.iloc[-2]["temperature"]),
        "humidity_lag1": float(latest["humidity"]),
        "rainfall_lag1": float(latest["rainfall"]),
        "wind_lag1": float(latest["wind_speed"]),
        "month": int(prediction_date.month),
        "day_of_year": int(prediction_date.day_of_year),
    }

    X = pd.DataFrame([input_values], columns=FEATURES)
    predictions = {}

    for target in TARGETS:
        model_path = MODEL_DIR / f"{target}_model.joblib"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Missing model: {model_path.name}. Retrain the models."
            )

        model = joblib.load(model_path)
        predictions[target] = float(model.predict(X)[0])

    return {
        "city": location["name"],
        "date": prediction_date.date().isoformat(),
        "based_on_date": latest["date"].date().isoformat(),
        "temperature": round(predictions["temperature"], 1),
        "humidity": round(max(0, min(100, predictions["humidity"])), 1),
        "rainfall": round(max(0, predictions["rainfall"]), 1),
        "model_type": "Random Forest",
    }


if __name__ == "__main__":
    result = predict_next_day("Nagpur")
    print("\nNEXT-DAY ML PREDICTION")
    for key, value in result.items():
        print(f"{key}: {value}")
