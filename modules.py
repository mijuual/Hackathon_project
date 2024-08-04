from flask import redirect, render_template, session
from functools import wraps
import requests


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


import requests


def get_weather(lat, lon, api_key):
    cnt = 7  # Specify the number of forecast data points you want
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(weather_url)
    if response.status_code == 200:
        weather_data = response.json()
        try:
            temperature = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            wind_speed = weather_data["wind"]["speed"]
            return {
                "temperature": temperature,
                "humidity": humidity,
                "wind_speed": wind_speed,
            }
        except KeyError as e:
            return {"error": f"KeyError: {e}"}
    else:
        return {"error": "Failed to fetch weather data"}
