import os
import requests
import logging
from typing import Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WeatherData:
    location: str
    temperature_c: float
    temperature_f: float
    condition: str
    icon_url: str
    humidity: int
    wind_kph: float
    wind_mph: float
    last_updated: datetime

class WeatherAPIError(Exception):
    """Custom exception for Weather API errors"""
    pass

def get_current_weather(location: str) -> Union[WeatherData, Dict[str, str]]:
    """
    Get the current weather for a given location using weatherapi.com API.

    Args:
        location (str): The location for which to retrieve weather data.

    Returns:
        Union[WeatherData, Dict[str, str]]: WeatherData object containing weather information,
        or dictionary with error message if request fails.

    Raises:
        WeatherAPIError: If there's an issue with the API key or request.
    """
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
    
    if not WEATHER_API_KEY:
        logging.error("WEATHER_API_KEY environment variable not set")
        raise WeatherAPIError("Weather API key not set")

    # URL encode the location parameter
    encoded_location = requests.utils.quote(location)
    url = f"http://api.weatherapi.com/v1/current.json"
    
    params = {
        "key": WEATHER_API_KEY,
        "q": encoded_location,
        "aqi": "no"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10  # Add timeout to prevent hanging
        )
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            error_message = data["error"].get("message", "Unknown error")
            logging.error(f"Error from weather API: {error_message}")
            return {"error": error_message}
        
        # Parse the last_updated string into a datetime object
        last_updated = datetime.strptime(
            data['current']['last_updated'],
            '%Y-%m-%d %H:%M'
        )
        
        # Create WeatherData object
        weather_data = WeatherData(
            location=f"{data['location']['name']}, {data['location']['region']}, {data['location']['country']}",
            temperature_c=float(data['current']['temp_c']),
            temperature_f=float(data['current']['temp_f']),
            condition=data['current']['condition']['text'],
            icon_url=f"https:{data['current']['condition']['icon']}",  # Use HTTPS
            humidity=int(data['current']['humidity']),
            wind_kph=float(data['current']['wind_kph']),
            wind_mph=float(data['current']['wind_mph']),
            last_updated=last_updated
        )
        
        return weather_data
        
    except requests.Timeout:
        logging.error("Request timed out")
        return {"error": "Request timed out"}
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        return {"error": str(e)}
    except (KeyError, ValueError) as e:
        logging.error(f"Data parsing error: {e}")
        return {"error": "Error parsing weather data"}
