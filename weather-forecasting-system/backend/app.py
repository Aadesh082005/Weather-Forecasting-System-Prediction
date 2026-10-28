
from pathlib import Path
import sys

import requests
from flask import Flask, jsonify, render_template, request

# Project root directory
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

app = Flask(
    __name__,
    template_folder=str(ROOT / "frontend"),
    static_folder=str(ROOT / "frontend"),
    static_url_path="/static",
)

WEATHER_API = "https://api.open-meteo.com/v1/forecast"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city", "Nagpur").strip()

    if not city:
        return jsonify({"error": "Please enter a city name."}), 400

    try:
        from src.data_collection import get_city_location

        location = get_city_location(city)

        # Fetch current weather and 7-day forecast.
        response = requests.get(
            WEATHER_API,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "precipitation,"
                    "wind_speed_10m"
                ),
                "daily": (
                    "weather_code,"
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "precipitation_probability_max"
                ),
                "forecast_days": 7,
                "timezone": location.get("timezone") or "auto",
            },
            timeout=30,
        )
        response.raise_for_status()
        weather_data = response.json()

        result = {
            "location": location,
            "current": weather_data.get("current", {}),
            "current_units": weather_data.get("current_units", {}),
            "forecast": weather_data.get("daily", {}),
            "prediction": None,
            "prediction_error": None,
        }

        # Get next-day prediction from the trained ML models.
        try:
            from src.predict import predict_next_day

            result["prediction"] = predict_next_day(location["name"])
        except (FileNotFoundError, ValueError) as exc:
            result["prediction_error"] = str(exc)
        except Exception:
            app.logger.exception("ML prediction failed")
            result["prediction_error"] = (
                "Prediction failed. Check the trained models "
                "and recent weather data."
            )

        return jsonify(result)

    except requests.RequestException:
        app.logger.exception("Weather API request failed")
        return jsonify({
            "error": (
                "Could not fetch weather data. Check your internet "
                "connection and try again."
            )
        }), 502

    except Exception:
        app.logger.exception("Weather request failed")
        return jsonify({
            "error": (
                "Could not process this city. Check the city name "
                "and try again."
            )
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
