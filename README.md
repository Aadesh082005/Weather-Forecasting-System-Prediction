# 🌦️ Weather Forecasting and Prediction System

A Machine Learning-based Weather Forecasting and Prediction System built using **Python, Flask, HTML, CSS, and JavaScript**. The application displays current weather conditions, provides a 7-day weather forecast, and uses a Random Forest model to predict next-day temperature, humidity, and rainfall.

## 📌 Project Overview

Weather conditions affect our daily activities, agriculture, transportation, and many other sectors. This project provides an easy-to-use web application where users can search for a city and view its weather information.

The system retrieves weather data from the Open-Meteo API and uses trained Machine Learning models to generate next-day weather estimates.

## ✨ Features

- 🌍 **City-Based Search:** Search for weather information by city name.
- 🌡️ **Current Weather:** View temperature, humidity, wind speed, and precipitation.
- 📅 **7-Day Forecast:** View upcoming daily weather forecasts.
- 🤖 **Machine Learning Prediction:** Predict next-day temperature, humidity, and rainfall using a Random Forest model.
- 📊 **Weather Data Processing:** Clean and prepare historical weather data for model training.
- 🖥️ **Web Dashboard:** Access weather information through a simple web interface.
- ⚠️ **Error Handling:** Display helpful messages when weather data or trained models are unavailable.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Backend web framework and API |
| Pandas | Data processing and manipulation |
| Scikit-learn | Machine Learning model training |
| Random Forest | Weather prediction algorithm |
| Joblib | Saving and loading trained models |
| Requests | Fetching weather data from APIs |
| HTML | Web page structure |
| CSS | Dashboard styling |
| JavaScript | Search, API requests, and dynamic updates |
| Open-Meteo API | Weather data and forecasts |
| Pytest | Automated testing |

## 📂 Project Structure

```text
weather-forecasting-system/
│
├── backend/
│   ├── __init__.py
│   └── app.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── src/
│   ├── __init__.py
│   ├── data_collection.py
│   ├── preprocessing.py
│   ├── train_model.py
│   └── predict.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│   └── Trained model files
│
├── tests/
│   └── test_prediction.py
│
├── requirements.txt
└── README.md
```

*Note: The exact files and folders may vary depending on your current project setup.*

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/weather-forecasting-and-prediction-system.git
```

Navigate to the project directory:

```bash
cd weather-forecasting-and-prediction-system
```

Replace `YOUR-USERNAME` with your GitHub username and use your actual repository URL.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

Make sure the `requirements.txt` file includes all the packages used by your project.

### 4. Train the Machine Learning Models

If trained models are not already available, train them using the project's training script:

```bash
python -m src.train_model --city Nagpur --days 730
```

This command assumes your training script supports the `--city` and `--days` arguments. Use the arguments supported by your actual implementation.

After successful training, verify that the required model files and metadata are present in the `models/` directory.

### 5. Run the Application

Start the Flask backend:

```bash
python -m backend.app
```

Open your browser and visit:

**http://127.0.0.1:5000**

Search for a city to view its current weather, 7-day forecast, and next-day prediction.

## 🤖 Machine Learning Approach

The system uses a Random Forest regression model to estimate the following weather parameters:

- **Temperature:** Predicted temperature for the next day in degrees Celsius.
- **Humidity:** Predicted relative humidity as a percentage.
- **Rainfall:** Estimated rainfall in millimeters.

The training workflow includes:

1. Collecting historical weather data.
2. Cleaning missing or invalid values.
3. Creating time-based and lag features.
4. Preparing features and target variables.
5. Training regression models.
6. Saving trained models for later predictions.
7. Loading the saved models to generate predictions.

The predictions depend on the quality of the training data and the selected features. They are estimates and are not guaranteed to match actual weather conditions.

## 🌐 Data Source

This project uses the **Open-Meteo API** for current weather information, forecast data, and historical weather data where supported.

- Website: https://open-meteo.com/
- Documentation: https://open-meteo.com/en/docs

Check the provider's current terms and attribution requirements before distributing the application.

## 🧪 Run Tests

To run the project's automated tests, install Pytest if necessary:

```bash
python -m pip install pytest
```

Then run:

```bash
python -m pytest -v
```

Tests verify the behavior covered by the test suite, such as data cleaning and feature preparation.

## 🔮 Future Enhancements

- Interactive weather charts and historical trends.
- Improved prediction accuracy through feature engineering and model evaluation.
- Additional Machine Learning algorithms for comparison.
- Weather alerts for heavy rainfall and extreme temperatures.
- Improved responsive design for mobile devices.
- Model evaluation using MAE, RMSE, and R² metrics.
- Deployment to a cloud hosting platform.

## 🎯 Project Objectives

- Develop a practical weather information web application.
- Integrate a Machine Learning model into a Flask backend.
- Process historical weather data for prediction.
- Display weather information through a user-friendly interface.
- Understand the complete workflow from data collection to model deployment.

## 👨‍💻 Author

**Your Name**

- GitHub: https://github.com/YOUR-USERNAME

Replace the placeholders with your actual name and GitHub profile.

## 📄 License

This project is intended for educational and learning purposes. If you plan to distribute it publicly, consider adding an appropriate open-source license, such as the MIT License.

---

⭐ If you find this project useful, consider giving the repository a star!
