import requests


def get_coordinates(location):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    result = data["results"][0]

    return {
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "name": result["name"],
        "country": result.get("country", "")
    }