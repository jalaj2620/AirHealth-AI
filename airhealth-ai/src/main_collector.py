"""
Main data collection orchestrator - fetches AQI and weather data daily
"""
import time
import logging
from datetime import datetime
from src.collectors.openaq_collector import OpenAQCollector
from src.collectors.openweathermap_collector import OpenWeatherMapCollector
from src.utils.db import get_connection
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger('main_collector')


class DataCollectionOrchestrator:
    """Orchestrates daily data collection from multiple APIs"""
    
    def __init__(self):
        self.db = get_connection()
        self.openaq = OpenAQCollector()
        self.weather = OpenWeatherMapCollector()
        self.stats = {
            'aqi_successful': 0,
            'aqi_failed': 0,
            'weather_successful': 0,
            'weather_failed': 0
        }
    
    def collect_all_data(self):
        """Main orchestration method - collect AQI and weather for all cities"""
        logger.info("🔄 Starting data collection cycle...")
        start_time = time.time()
        
        try:
            # Get all cities from database
            cities = self.db.get_all_cities()
            logger.info(f"Collecting data for {len(cities)} cities")
            
            for i, city in enumerate(cities):
                city_id = city['id']
                city_name = city['name']
                lat = city['latitude']
                lon = city['longitude']
                
                logger.info(f"[{i+1}/{len(cities)}] Processing {city_name}...")
                
                # Collect AQI data
                aqi_data = self.openaq.get_latest_by_city(city_name, lat, lon)
                if aqi_data:
                    if self.db.insert_or_update_aqi(city_id, aqi_data):
                        self.stats['aqi_successful'] += 1
                        logger.debug(f"✓ AQI data stored for {city_name}")
                    else:
                        self.stats['aqi_failed'] += 1
                        logger.warning(f"✗ Failed to store AQI data for {city_name}")
                else:
                    self.stats['aqi_failed'] += 1
                    logger.warning(f"✗ No AQI data retrieved for {city_name}")
                
                # Collect weather data
                weather_data = self.weather.get_weather(city_name, lat, lon)
                if weather_data:
                    if self.db.insert_or_update_weather(city_id, weather_data):
                        self.stats['weather_successful'] += 1
                        logger.debug(f"✓ Weather data stored for {city_name}")
                    else:
                        self.stats['weather_failed'] += 1
                        logger.warning(f"✗ Failed to store weather data for {city_name}")
                else:
                    self.stats['weather_failed'] += 1
                    logger.warning(f"✗ No weather data retrieved for {city_name}")
            
            duration = time.time() - start_time
            
            # Log collection statistics
            logger.info(f"📊 Collection Statistics:")
            logger.info(f"   AQI - Success: {self.stats['aqi_successful']}, Failed: {self.stats['aqi_failed']}")
            logger.info(f"   Weather - Success: {self.stats['weather_successful']}, Failed: {self.stats['weather_failed']}")
            logger.info(f"   Total Time: {duration:.2f} seconds")
            
            # Log to database
            self.db.log_collection(
                'AQI+Weather', 
                len(cities), 
                self.stats['aqi_successful'] + self.stats['weather_successful'],
                self.stats['aqi_failed'] + self.stats['weather_failed'],
                duration
            )
            
            logger.info("✓ Data collection cycle completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during data collection: {e}")
            return False


def main():
    """Run data collection"""
    from src.utils.config import validate_config
    
    # Validate configuration
    if not validate_config():
        logger.warning("Configuration validation failed - some features may not work")
    
    orchestrator = DataCollectionOrchestrator()
    orchestrator.collect_all_data()


if __name__ == '__main__':
    main()
