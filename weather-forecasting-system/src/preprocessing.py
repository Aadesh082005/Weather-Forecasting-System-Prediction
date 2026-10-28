
import pandas as pd

FEATURES = [
    "temperature_lag1",
    "temperature_lag2",
    "temperature_lag3",
    "humidity_lag1",
    "rainfall_lag1",
    "wind_lag1",
    "month",
    "day_of_year",
]

TARGETS = ["temperature", "humidity", "rainfall"]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and sort historical weather observations."""
    required = [
        "date",
        "temperature",
        "humidity",
        "rainfall",
        "wind_speed",
    ]

    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    result = df[required].copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce")

    for column in required[1:]:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    result = result.dropna(subset=["date"])
    result = result.sort_values("date")
    result = result.drop_duplicates(subset=["date"], keep="last")
    result = result.set_index("date")

    result = result.interpolate(method="time", limit=3)
    result = result.dropna(subset=required[1:])

    result["humidity"] = result["humidity"].clip(0, 100)
    result["rainfall"] = result["rainfall"].clip(lower=0)

    return result.reset_index()


def prepare_data(df: pd.DataFrame):
    """Create lag features for next-day weather prediction."""
    result = clean_data(df)

    result["temperature_lag1"] = result["temperature"].shift(1)
    result["temperature_lag2"] = result["temperature"].shift(2)
    result["temperature_lag3"] = result["temperature"].shift(3)
    result["humidity_lag1"] = result["humidity"].shift(1)
    result["rainfall_lag1"] = result["rainfall"].shift(1)
    result["wind_lag1"] = result["wind_speed"].shift(1)

    result["month"] = result["date"].dt.month
    result["day_of_year"] = result["date"].dt.dayofyear

    result = result.dropna(subset=FEATURES + TARGETS)

    return result[FEATURES], result[TARGETS]
