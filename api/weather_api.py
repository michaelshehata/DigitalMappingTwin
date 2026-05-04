# api/weather_api.py

import requests

API_KEY = "YOUR_API_KEY"  # replace later


def get_live_weather(city="Norwich"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("API request failed")

    data = response.json()

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"]
    }