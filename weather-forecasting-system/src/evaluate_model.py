
import pandas as pd

FEATURES = [
    "temperature_lag1",
    "temperature_lag2",
    "temperature_lag3",
    "humidity_lag1",
    "rainfall_lag1",
    "wind_lag1",
    "month",
    "day_of_year"
]

TARGETS = [
    "temperature",
    "humidity",
    "rainfall"
]


def clean_data(df):
    data = df.copy()

    data["date"] = pd.to_datetime(
        data["date"], errors="coerce"
    )

    columns = [
        "temperature",
        "humidity",
        "rainfall",
        "wind_speed"
    ]

    for column in columns:
        data[column] = pd.to_numeric(
            data[column], errors="coerce"
        )

    data = data.dropna(subset=["date"])
    data = data.sort_values("date")
    data = data.drop_duplicates(subset=["date"])
    data = data.set_index("date")

    data[columns] = data[columns].interpolate(
        method="time", limit=3
    )

    data = data.dropna().reset_index()

    data["humidity"] = data["humidity"].clip(0, 100)
    data["rainfall"] = data["rainfall"].clip(lower=0)

    return data


def prepare_data(df):
    data = clean_data(df)

    data["temperature_lag1"] = (
        data["temperature"].shift(1)
    )
    data["temperature_lag2"] = (
        data["temperature"].shift(2)
    )
    data["temperature_lag3"] = (
        data["temperature"].shift(3)
    )
    data["humidity_lag1"] = (
        data["humidity"].shift(1)
    )
    data["rainfall_lag1"] = (
        data["rainfall"].shift(1)
    )
    data["wind_lag1"] = (
        data["wind_speed"].shift(1)
    )

    data["month"] = data["date"].dt.month
    data["day_of_year"] = data["date"].dt.dayofyear

    data = data.dropna(
        subset=FEATURES + TARGETS
    ).reset_index(drop=True)

    return data
