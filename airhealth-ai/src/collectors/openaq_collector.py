"""
API client for OpenAQ - free air quality data
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenAQCollector:
    """Collect air quality data from OpenAQ API"""
    
    BASE_URL = "https://api.openaq.org/v2"
    TIMEOUT = 10
    
    @staticmethod
    def get_latest_by_city(city_name: str, lat: float = None, lon: float = None) -> Optional[Dict]:
        """
        Fetch latest AQI data for a specific city
        
        Args:
            city_name: Name of the city
            lat: Latitude (optional, for more precise location)
            lon: Longitude (optional, for more precise location)
        
        Returns:
            Dict with AQI data or None if failed
        """
        try:
            # Use country filter first, then city
            params = {
                'country': 'IN',  # India
                'city': city_name,
                'order_by': 'lastUpdated',
                'sort': 'desc',
                'limit': 1,
                'offset': 0
            }
            
            url = f"{OpenAQCollector.BASE_URL}/latest"
            response = requests.get(url, params=params, timeout=OpenAQCollector.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                result = data['results'][0]
                
                # Extract pollutants
                pollutants = {}
                for pollutant_obj in result.get('measurements', []):
                    param = pollutant_obj.get('parameter', '').lower()
                    value = pollutant_obj.get('value')
                    pollutants[param] = value
                
                return {
                    'city': result.get('city'),
                    'country': result.get('country'),
                    'timestamp': result.get('lastUpdated'),
                    'aqi': pollutants.get('useepi') or pollutants.get('um-aqi'),  # US EPA AQI
                    'pm25': pollutants.get('pm25'),
                    'pm10': pollutants.get('pm10'),
                    'o3': pollutants.get('o3'),
                    'no2': pollutants.get('no2'),
                    'so2': pollutants.get('so2'),
                    'co': pollutants.get('co'),
                    'raw_response': result,
                    'source': 'OpenAQ'
                }
            
            logger.warning(f"No data found for city: {city_name}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from OpenAQ for {city_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing OpenAQ response: {e}")
            return None
    
    @staticmethod
    def get_latest_in_box(lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> List[Dict]:
        """
        Fetch latest AQI data for all stations in a bounding box
        
        Args:
            lat_min, lat_max, lon_min, lon_max: Bounding box coordinates
        
        Returns:
            List of dictionaries with AQI data
        """
        try:
            params = {
                'country': 'IN',
                'order_by': 'lastUpdated',
                'sort': 'desc',
                'limit': 100,
                'offset': 0
            }
            
            url = f"{OpenAQCollector.BASE_URL}/latest"
            response = requests.get(url, params=params, timeout=OpenAQCollector.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get('results', []):
                pollutants = {}
                for pollutant_obj in result.get('measurements', []):
                    param = pollutant_obj.get('parameter', '').lower()
                    value = pollutant_obj.get('value')
                    pollutants[param] = value
                
                results.append({
                    'city': result.get('city'),
                    'country': result.get('country'),
                    'timestamp': result.get('lastUpdated'),
                    'latitude': result.get('coordinates', {}).get('latitude'),
                    'longitude': result.get('coordinates', {}).get('longitude'),
                    'aqi': pollutants.get('useepi') or pollutants.get('um-aqi'),
                    'pm25': pollutants.get('pm25'),
                    'pm10': pollutants.get('pm10'),
                    'o3': pollutants.get('o3'),
                    'no2': pollutants.get('no2'),
                    'so2': pollutants.get('so2'),
                    'co': pollutants.get('co'),
                    'source': 'OpenAQ'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching data from OpenAQ: {e}")
            return []
