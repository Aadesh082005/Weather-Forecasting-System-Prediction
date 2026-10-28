
const $ = (id) => document.getElementById(id);

const form = $("searchForm");
const cityInput = $("cityInput");

function format(value, digits = 1) {
    if (
        value === null ||
        value === undefined ||
        value === "" ||
        !Number.isFinite(Number(value))
    ) {
        return "--";
    }

    return Number(value).toFixed(digits);
}

function weatherIcon(code) {
    if (code === 0) return "☀️";
    if ([1, 2].includes(code)) return "🌤️";
    if (code === 3) return "☁️";
    if ([45, 48].includes(code)) return "🌫️";

    if ([51, 53, 55, 56, 57, 61, 63, 65, 66, 67,
         80, 81, 82].includes(code)) {
        return "🌧️";
    }

    if ([71, 73, 75, 77, 85, 86].includes(code)) {
        return "❄️";
    }

    if ([95, 96, 99].includes(code)) return "⛈️";

    return "🌡️";
}

function setStatus(message, isError = false) {
    const status = $("status");

    if (!status) return;

    status.textContent = message;
    status.classList.toggle("error", isError);
}

async function loadWeather(city) {
    setStatus(`Fetching weather for ${city}...`);

    try {
        const response = await fetch(
            `/api/weather?city=${encodeURIComponent(city)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to fetch weather data."
            );
        }

        if (!data.location) {
            throw new Error("Location information is unavailable.");
        }

        // Location
        $("location").textContent = [
            data.location.name,
            data.location.country
        ].filter(Boolean).join(", ");

        // Current weather
        const current = data.current || {};
        const units = data.current_units || {};

        $("temperature").textContent =
            `${format(current.temperature_2m)} ${units.temperature_2m || "°C"}`;

        $("humidity").textContent =
            `${format(current.relative_humidity_2m, 0)} ${units.relative_humidity_2m || "%"}`;

        $("wind").textContent =
            `${format(current.wind_speed_10m)} ${units.wind_speed_10m || "km/h"}`;

        $("rain").textContent =
            `${format(current.precipitation)} ${units.precipitation || "mm"}`;

        $("updated").textContent =
            `Updated: ${current.time || "Latest available data"}`;

        // Seven-day forecast
        showForecast(data.forecast || {});

        // Next-day ML prediction
        showPrediction(
            data.prediction,
            data.prediction_error
        );

        setStatus(`Weather loaded successfully for ${city}.`);

    } catch (error) {
        console.error("Weather loading error:", error);
        setStatus(error.message || "Something went wrong.", true);
    }
}

function showForecast(daily) {
    const forecastContainer = $("forecast");

    if (!forecastContainer) return;

    const dates = daily.time || [];
    const maximum = daily.temperature_2m_max || [];
    const minimum = daily.temperature_2m_min || [];
    const probability = daily.precipitation_probability_max || [];
    const codes = daily.weather_code || [];

    if (!dates.length) {
        forecastContainer.textContent =
            "Seven-day forecast is unavailable.";
        return;
    }

    forecastContainer.innerHTML = dates.map((date, index) => {
        const day = new Date(`${date}T12:00:00`);

        const dayName = day.toLocaleDateString("en-IN", {
            weekday: "short"
        });

        const rainChance = probability[index] ?? "--";
        const icon = weatherIcon(Number(codes[index]));

        return `
            <article class="day">
                <p>${dayName}</p>
                <div class="icon">${icon}</div>
                <strong>
                    ${format(maximum[index], 0)}° /
                    ${format(minimum[index], 0)}°
                </strong>
                <p>Rain: ${rainChance}%</p>
            </article>
        `;
    }).join("");
}

function showPrediction(prediction, errorMessage) {
    const temperature = $("predTemp");
    const humidity = $("predHumidity");
    const rainfall = $("predRain");
    const info = $("predictionInfo");

    if (!temperature || !humidity || !rainfall || !info) {
        console.error(
            "Prediction HTML elements are missing. Check index.html IDs."
        );
        return;
    }

    if (!prediction) {
        temperature.textContent = "-- °C";
        humidity.textContent = "--%";
        rainfall.textContent = "-- mm";

        info.textContent =
            errorMessage ||
            "ML prediction is unavailable. Check that the models are trained.";

        return;
    }

    temperature.textContent =
        `${format(prediction.temperature)} °C`;

    humidity.textContent =
        `${format(prediction.humidity, 0)}%`;

    rainfall.textContent =
        `${format(prediction.rainfall)} mm`;

    const date = prediction.date || "next day";
    const model = prediction.model_type || "ML model";

    info.textContent =
        `${model} estimate for ${date}. This is a prediction, not a guarantee.`;
}

// Search city
if (form) {
    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const city = cityInput.value.trim();

        if (!city) {
            setStatus("Please enter a city name.", true);
            cityInput.focus();
            return;
        }

        loadWeather(city);
    });
} else {
    console.error(
        'Search form not found. Check the "searchForm" ID in index.html.'
    );
}

// Initial dashboard data
loadWeather("Nagpur");
