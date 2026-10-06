import requests


def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    current = data["current"]

    weather_code = current["weather_code"]

    # Convert Open-Meteo weather code
    # into a simple readable condition

    if weather_code == 0:
        condition = "Clear sky"

    elif weather_code in [1, 2, 3]:
        condition = "Cloudy"

    elif weather_code in [45, 48]:
        condition = "Foggy"

    elif weather_code in [51, 53, 55, 56, 57]:
        condition = "Drizzle"

    elif weather_code in [61, 63, 65, 66, 67]:
        condition = "Rainy"

    elif weather_code in [71, 73, 75, 77]:
        condition = "Snowy"

    elif weather_code in [80, 81, 82]:
        condition = "Rain showers"

    elif weather_code in [85, 86]:
        condition = "Snow showers"

    elif weather_code in [95, 96, 99]:
        condition = "Thunderstorm"

    else:
        condition = "Unknown"

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "rainfall": current["precipitation"],
        "condition": condition
    }
