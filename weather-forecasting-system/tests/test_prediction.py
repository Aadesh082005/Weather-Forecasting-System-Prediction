
import pandas as pd

from src.preprocessing import clean_data, prepare_data


def sample_weather_data():
    dates = pd.date_range("2025-01-01", periods=20, freq="D")

    return pd.DataFrame({
        "date": dates,
        "temperature": [25 + i * 0.5 for i in range(20)],
        "humidity": [60 + i % 10 for i in range(20)],
        "rainfall": [float(i % 4) for i in range(20)],
        "wind_speed": [5 + i % 6 for i in range(20)],
    })


def test_clean_data_returns_valid_rows():
    df = sample_weather_data()

    result = clean_data(df)

    assert not result.empty
    assert result["date"].is_monotonic_increasing
    assert result["temperature"].notna().all()


def test_prepare_data_creates_features_and_targets():
    df = sample_weather_data()

    cleaned = clean_data(df)
    features, targets = prepare_data(cleaned)

    assert not features.empty
    assert not targets.empty
    assert len(features) == len(targets)

    assert "temperature_lag1" in features.columns
    assert "humidity_lag1" in features.columns
    assert "temperature" in targets.columns
    assert "rainfall" in targets.columns
