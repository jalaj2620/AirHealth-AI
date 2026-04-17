"""
API client for OpenWeatherMap - weather data
"""
import requests
import logging
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)


class OpenWeatherMapCollector:
    """Collect weather data from OpenWeatherMap API"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    TIMEOUT = 10
    
    def __init__(self, api_key: str = None):
        """Initialize with API key"""
        self.api_key = api_key or os.getenv('OPENWEATHERMAP_API_KEY')
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not set. Set OPENWEATHERMAP_API_KEY environment variable.")
    
    def get_weather(self, city_name: str, lat: float = None, lon: float = None) -> Optional[Dict]:
        """
        Fetch current weather for a city
        
        Args:
            city_name: City name
            lat: Latitude (alternative to city_name)
            lon: Longitude (alternative to city_name)
        
        Returns:
            Dict with weather data or None if failed
        """
        try:
            if not self.api_key:
                logger.error("API key not available")
                return None
            
            params = {
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            # Use coordinates if provided, otherwise use city name
            if lat and lon:
                params['lat'] = lat
                params['lon'] = lon
            else:
                params['q'] = city_name
            
            url = f"{self.BASE_URL}/weather"
            response = requests.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'city': data.get('name'),
                'country': data.get('sys', {}).get('country'),
                'timestamp': data.get('dt'),
                'latitude': data.get('coord', {}).get('lat'),
                'longitude': data.get('coord', {}).get('lon'),
                'temperature': data.get('main', {}).get('temp'),
                'feels_like': data.get('main', {}).get('feels_like'),
                'humidity': data.get('main', {}).get('humidity'),
                'pressure': data.get('main', {}).get('pressure'),
                'wind_speed': data.get('wind', {}).get('speed'),
                'wind_deg': data.get('wind', {}).get('deg'),
                'cloudiness': data.get('clouds', {}).get('all'),
                'rain_1h': data.get('rain', {}).get('1h', 0),
                'visibility': data.get('visibility'),
                'weather_main': data.get('weather', [{}])[0].get('main'),
                'weather_description': data.get('weather', [{}])[0].get('description'),
                'raw_response': data,
                'source': 'OpenWeatherMap'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data for {city_name or 'coordinates'}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing weather response: {e}")
            return None
    
    def get_forecast(self, city_name: str = None, lat: float = None, lon: float = None) -> Optional[Dict]:
        """
        Fetch 5-day weather forecast for a city
        
        Args:
            city_name: City name
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dict with forecast data or None if failed
        """
        try:
            if not self.api_key:
                logger.error("API key not available")
                return None
            
            params = {
                'appid': self.api_key,
                'units': 'metric'
            }
            
            if lat and lon:
                params['lat'] = lat
                params['lon'] = lon
            else:
                params['q'] = city_name
            
            url = f"{self.BASE_URL}/forecast"
            response = requests.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            forecasts = []
            for item in data.get('list', [])[:8]:  # Get first 2 days (8 x 3hr intervals)
                forecasts.append({
                    'timestamp': item.get('dt'),
                    'temperature': item.get('main', {}).get('temp'),
                    'humidity': item.get('main', {}).get('humidity'),
                    'wind_speed': item.get('wind', {}).get('speed'),
                    'cloudiness': item.get('clouds', {}).get('all'),
                    'rain_probability': item.get('pop'),  # Probability of precipitation
                    'weather_main': item.get('weather', [{}])[0].get('main')
                })
            
            return {
                'city': data.get('city', {}).get('name'),
                'country': data.get('city', {}).get('country'),
                'forecasts': forecasts,
                'source': 'OpenWeatherMap'
            }
            
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return None
