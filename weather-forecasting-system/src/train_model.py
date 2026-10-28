
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

from src.data_collection import get_historical_weather
from src.preprocessing import FEATURES, TARGETS, clean_data, prepare_data


# Project directories
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
MODEL_DIR = ROOT_DIR / "models"


def unpack_weather_result(result):
    """Accept a DataFrame or a (DataFrame, location) tuple."""

    location = {}

    if isinstance(result, tuple):
        if len(result) != 2:
            raise ValueError(
                "get_historical_weather() must return a DataFrame "
                "or a (DataFrame, location) tuple."
            )

        first, second = result

        if hasattr(first, "columns"):
            data = first
            location = second if isinstance(second, dict) else {}
        elif hasattr(second, "columns"):
            data = second
            location = first if isinstance(first, dict) else {}
        else:
            raise TypeError(
                "The returned tuple does not contain a pandas DataFrame."
            )
    else:
        data = result

    if not hasattr(data, "columns"):
        raise TypeError(
            "Weather data must be a pandas DataFrame. "
            "Check get_historical_weather() in src/data_collection.py."
        )

    return data, location


def train_model(city="Nagpur", days=730):
    """Download weather data, train models, and save evaluation metrics."""

    # Create directories if they do not exist.
    for directory in (RAW_DIR, PROCESSED_DIR, MODEL_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    print(f"Downloading historical weather data for {city}...")

    # FIX: Handle both DataFrame and (DataFrame, location) returns.
    result = get_historical_weather(city, days=days)
    data, location = unpack_weather_result(result)

    if data.empty:
        raise ValueError(
            "No historical weather data was returned. "
            "Check your internet connection and city name."
        )

    required_columns = [
        "date",
        "temperature",
        "humidity",
        "rainfall",
        "wind_speed",
    ]

    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        raise ValueError(
            f"Weather data is missing columns: {missing}. "
            f"Available columns: {list(data.columns)}"
        )

    raw_path = RAW_DIR / "weather_data.csv"
    data.to_csv(raw_path, index=False)
    print(f"Raw data saved: {raw_path}")
    print(f"Downloaded records: {len(data)}")

    # Clean and prepare data.
    cleaned = clean_data(data)

    if cleaned.empty:
        raise ValueError("No valid records remain after cleaning.")

    cleaned_path = PROCESSED_DIR / "cleaned_weather.csv"
    cleaned.to_csv(cleaned_path, index=False)

    features, targets = prepare_data(cleaned)

    if features.empty or targets.empty:
        raise ValueError(
            "Not enough valid weather records to create training features."
        )

    if len(features) < 10:
        raise ValueError(
            f"Only {len(features)} training rows are available. "
            "Try collecting more historical data."
        )

    print(f"Usable training records: {len(features)}")

    # Chronological split: train on earlier dates, test on later dates.
    split_index = int(len(features) * 0.8)
    split_index = max(1, min(split_index, len(features) - 1))

    X_train = features.iloc[:split_index]
    X_test = features.iloc[split_index:]

    y_train = targets.iloc[:split_index]
    y_test = targets.iloc[split_index:]

    metrics = {}

    # Train a separate model for each weather target.
    for target in TARGETS:
        print(f"\nTraining model for {target}...")

        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

        model.fit(X_train, y_train[target])

        predictions = model.predict(X_test)
        mae = float(mean_absolute_error(y_test[target], predictions))
        rmse = float(np.sqrt(mean_squared_error(y_test[target], predictions)))

        model_path = MODEL_DIR / f"{target}_model.joblib"
        joblib.dump(model, model_path)

        metrics[target] = {
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
        }

        print(f"MAE:  {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"Saved model: {model_path}")

    # Save metadata for prediction and reporting.
    metadata = {
        "city": str(location.get("name", city)),
        "country": str(location.get("country", "")),
        "rows": int(len(features)),
        "features": FEATURES,
        "targets": TARGETS,
        "metrics": metrics,
    }

    metadata_path = MODEL_DIR / "model_metadata.json"
    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    print("\nTraining completed successfully!")
    print(f"Metadata saved: {metadata_path}")
    print(f"Cleaned data saved: {cleaned_path}")

    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train weather forecasting machine-learning models."
    )
    parser.add_argument(
        "--city",
        default="Nagpur",
        help="City used to collect historical weather data.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=730,
        help="Number of historical days to request.",
    )

    args = parser.parse_args()

    if args.days < 30:
        parser.error("--days must be at least 30.")

    try:
        train_model(city=args.city, days=args.days)
    except Exception as error:
        print(f"\nTraining failed: {error}")
        raise