
import requests
import pandas as pd
from datetime import date, timedelta

GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)
ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)


def get_city_location(city):
    response = requests.get(
        GEOCODING_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        },
        timeout=20
    )

    response.raise_for_status()
    results = response.json().get("results", [])

    if not results:
        raise ValueError(f"City not found: {city}")

    place = results[0]

    return {
        "name": place["name"],
        "country": place.get("country", ""),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "timezone": place.get("timezone", "auto")
    }


def get_historical_weather(city, days=730):
    location = get_city_location(city)

    # Recent archive records may not yet be available.
    end_date = date.today() - timedelta(days=6)
    start_date = end_date - timedelta(days=days - 1)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": (
            "temperature_2m_mean,"
            "relative_humidity_2m_mean,"
            "precipitation_sum,"
            "wind_speed_10m_mean"
        ),
        "timezone": location["timezone"]
    }

    response = requests.get(
        ARCHIVE_URL,
        params=params,
        timeout=60
    )
    response.raise_for_status()

    daily = response.json().get("daily", {})

    if not daily.get("time"):
        raise ValueError("Historical weather data not found.")

    df = pd.DataFrame({
        "date": daily["time"],
        "temperature": daily["temperature_2m_mean"],
        "humidity": daily["relative_humidity_2m_mean"],
        "rainfall": daily["precipitation_sum"],
        "wind_speed": daily["wind_speed_10m_mean"]
    })

    return df, location
