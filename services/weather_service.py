"""
Weather Service for WanderPlan AI.
Integrates with Open-Meteo API for real-time weather forecasts and geocoding.
Free, open-source, and requires no secret API key.
"""

import logging
import requests

logger = logging.getLogger(__name__)

# WMO Weather interpretation codes (WMO code -> { description, icon })
WMO_WEATHER_CODES = {
    0: {"desc": "Clear sky", "icon": "☀️"},
    1: {"desc": "Mainly clear", "icon": "🌤️"},
    2: {"desc": "Partly cloudy", "icon": "⛅"},
    3: {"desc": "Overcast", "icon": "☁️"},
    45: {"desc": "Foggy", "icon": "🌫️"},
    48: {"desc": "Depositing rime fog", "icon": "🌫️"},
    51: {"desc": "Light drizzle", "icon": "🌦️"},
    53: {"desc": "Moderate drizzle", "icon": "🌦️"},
    55: {"desc": "Dense drizzle", "icon": "🌧️"},
    61: {"desc": "Slight rain", "icon": "🌧️"},
    63: {"desc": "Moderate rain", "icon": "🌧️"},
    65: {"desc": "Heavy rain", "icon": "🌧️"},
    71: {"desc": "Slight snow fall", "icon": "🌨️"},
    73: {"desc": "Moderate snow fall", "icon": "❄️"},
    75: {"desc": "Heavy snow fall", "icon": "❄️"},
    77: {"desc": "Snow grains", "icon": "❄️"},
    80: {"desc": "Slight rain showers", "icon": "🌦️"},
    81: {"desc": "Moderate rain showers", "icon": "🌧️"},
    82: {"desc": "Violent rain showers", "icon": "⛈️"},
    85: {"desc": "Slight snow showers", "icon": "🌨️"},
    86: {"desc": "Heavy snow showers", "icon": "❄️"},
    95: {"desc": "Thunderstorm", "icon": "⛈️"},
    96: {"desc": "Thunderstorm with slight hail", "icon": "⛈️"},
    99: {"desc": "Thunderstorm with heavy hail", "icon": "⛈️"}
}

# Curated fallback coordinates for popular travel destinations
CURATED_COORDINATES = {
    "tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan"},
    "paris": {"lat": 48.8566, "lon": 2.3522, "country": "France"},
    "bali": {"lat": -8.4095, "lon": 115.1889, "country": "Indonesia"},
    "goa": {"lat": 15.2993, "lon": 74.1240, "country": "India"},
    "rome": {"lat": 41.9028, "lon": 12.4964, "country": "Italy"},
    "new york": {"lat": 40.7128, "lon": -74.0060, "country": "USA"},
    "new york city": {"lat": 40.7128, "lon": -74.0060, "country": "USA"},
    "london": {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom"},
    "dubai": {"lat": 25.2048, "lon": 55.2708, "country": "United Arab Emirates"},
    "jaipur": {"lat": 26.9124, "lon": 75.7873, "country": "India"},
    "barcelona": {"lat": 41.3879, "lon": 2.16992, "country": "Spain"},
    "singapore": {"lat": 1.3521, "lon": 103.8198, "country": "Singapore"},
    "sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia"},
    "bangkok": {"lat": 13.7563, "lon": 100.5018, "country": "Thailand"}
}


def geocode_destination(destination_name: str) -> dict:
    """
    Resolves destination name to geographic latitude & longitude.
    Checks curated table first, then queries Open-Meteo Geocoding API.
    """
    if not destination_name:
        return None

    dest_clean = destination_name.lower().strip()

    # Check curated cache first
    for key, coords in CURATED_COORDINATES.items():
        if key in dest_clean or dest_clean in key:
            return {
                "name": destination_name.title(),
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "country": coords.get("country", "")
            }

    # Query Open-Meteo Geocoding API
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": destination_name.strip(),
            "count": 1,
            "language": "en",
            "format": "json"
        }
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            results = data.get("results")
            if results and len(results) > 0:
                first = results[0]
                return {
                    "name": first.get("name", destination_name.title()),
                    "latitude": round(first.get("latitude", 0.0), 4),
                    "longitude": round(first.get("longitude", 0.0), 4),
                    "country": first.get("country", ""),
                    "timezone": first.get("timezone", "UTC")
                }
    except Exception as e:
        logger.warning(f"Geocoding lookup failed for '{destination_name}': {e}")

    # Default fallback to (0,0) if completely unresolvable
    return None


def get_destination_weather(destination_name: str) -> dict:
    """
    Fetches real-time weather and 5-day forecast for a destination using Open-Meteo.
    Returns clean structured dictionary with condition, icons, and temperature.
    """
    geo = geocode_destination(destination_name)
    if not geo:
        return {
            "status": "unavailable",
            "destination": destination_name,
            "message": "Geographic coordinates could not be resolved for live weather.",
            "is_available": False
        }

    lat = geo["latitude"]
    lon = geo["longitude"]

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto"
        }
        res = requests.get(url, params=params, timeout=6)
        if res.status_code == 200:
            data = res.json()
            current = data.get("current", {})
            daily = data.get("daily", {})

            w_code = current.get("weather_code", 0)
            w_info = WMO_WEATHER_CODES.get(w_code, {"desc": "Clear", "icon": "☀️"})

            # Build 5-day forecast list
            daily_forecast = []
            dates = daily.get("time", [])[:5]
            max_temps = daily.get("temperature_2m_max", [])[:5]
            min_temps = daily.get("temperature_2m_min", [])[:5]
            daily_codes = daily.get("weather_code", [])[:5]
            rain_probs = daily.get("precipitation_probability_max", [])[:5]

            for idx, date_str in enumerate(dates):
                code = daily_codes[idx] if idx < len(daily_codes) else 0
                day_info = WMO_WEATHER_CODES.get(code, {"desc": "Clear", "icon": "☀️"})
                daily_forecast.append({
                    "date": date_str,
                    "max_temp_c": round(max_temps[idx]) if idx < len(max_temps) else None,
                    "min_temp_c": round(min_temps[idx]) if idx < len(min_temps) else None,
                    "rain_prob": rain_probs[idx] if idx < len(rain_probs) else 0,
                    "condition": day_info["desc"],
                    "icon": day_info["icon"]
                })

            curr_temp = round(current.get("temperature_2m", 20.0))
            apparent_temp = round(current.get("apparent_temperature", curr_temp))

            return {
                "status": "success",
                "is_available": True,
                "destination": geo.get("name", destination_name),
                "country": geo.get("country", ""),
                "coordinates": {"lat": lat, "lon": lon},
                "current": {
                    "temperature_c": curr_temp,
                    "temperature_f": round(curr_temp * 9 / 5 + 32),
                    "feels_like_c": apparent_temp,
                    "humidity": current.get("relative_humidity_2m", 50),
                    "wind_speed_kmh": round(current.get("wind_speed_10m", 10.0)),
                    "precipitation_mm": current.get("precipitation", 0.0),
                    "condition": w_info["desc"],
                    "icon": w_info["icon"],
                    "is_day": current.get("is_day", 1) == 1
                },
                "daily_forecast": daily_forecast,
                "source": "Open-Meteo API",
                "disclaimer": "Live weather provided by Open-Meteo. Actual conditions may vary."
            }
        else:
            logger.warning(f"Open-Meteo returned status {res.status_code}")
    except Exception as e:
        logger.warning(f"Open-Meteo forecast request error: {e}")

    # Fallback response if network or parsing fails
    return {
        "status": "unavailable",
        "is_available": False,
        "destination": destination_name,
        "coordinates": {"lat": lat, "lon": lon},
        "message": "Live weather service is temporarily unavailable. Check local forecasts before travel.",
        "source": "Open-Meteo API (Offline Fallback)"
    }
