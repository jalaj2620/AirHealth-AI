"""
Feature engineering pipeline - transforms raw data into ML-ready features
"""
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict
from src.utils.db import get_connection
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger('feature_engineer')


class FeatureEngineer:
    """Transform raw sensor data into meaningful features"""
    
    def __init__(self):
        self.db = get_connection()
        self.health_rules = Config.load_health_rules()
    
    def calculate_aqi_category(self, aqi_value: int) -> str:
        """
        Classify AQI value into category
        
        Args:
            aqi_value: AQI index (0-500+)
        
        Returns:
            Category: Safe, Moderate, Unhealthy, Hazardous
        """
        thresholds = self.health_rules.get('thresholds', {})
        
        if aqi_value <= thresholds.get('aqi_safe_limit', 50):
            return 'Safe'
        elif aqi_value <= thresholds.get('aqi_moderate_limit', 100):
            return 'Moderate'
        elif aqi_value <= thresholds.get('aqi_unhealthy_limit', 200):
            return 'Unhealthy'
        else:
            return 'Hazardous'
    
    def calculate_pollution_stress_index(self, pm25: float, pm10: float, no2: float, so2: float) -> Optional[float]:
        """
        Calculate composite pollution stress index (0-1)
        
        Combines multiple pollutants into single metric
        """
        if any(v is None for v in [pm25, pm10, no2, so2]):
            return None
        
        # Normalize each pollutant to 0-1 scale based on WHO guidelines
        pm25_norm = min(pm25 / 35.0, 1.0)  # WHO 24hr limit: 35 µg/m³
        pm10_norm = min(pm10 / 50.0, 1.0)  # WHO 24hr limit: 50 µg/m³
        no2_norm = min(no2 / 200.0, 1.0)   # WHO 1hr limit: 200 µg/m³
        so2_norm = min(so2 / 350.0, 1.0)   # WHO 10min limit: 350 µg/m³
        
        # Weighted average (PM2.5 and PM10 have higher weight)
        stress_index = (pm25_norm * 0.4 + pm10_norm * 0.3 + no2_norm * 0.2 + so2_norm * 0.1)
        return float(stress_index)
    
    def calculate_temperature_humidity_index(self, temp: float, humidity: int) -> Optional[float]:
        """
        Calculate Temperature-Humidity Index (THI)
        
        Indicates heat stress on humans
        Formula: THI = T + 0.5555 * (e) - 14.4
        where e = vapor pressure
        """
        if temp is None or humidity is None:
            return None
        
        # Calculate vapor pressure
        e = (humidity / 100.0) * 6.112 * np.exp((17.67 * temp) / (temp + 243.5))
        
        # THI formula
        thi = temp + 0.5555 * (e) - 14.4
        return float(thi)
    
    def classify_wind_stress(self, wind_speed: float) -> str:
        """
        Classify wind stress level
        
        Affects pollution dispersion
        """
        if wind_speed is None:
            return 'Unknown'
        elif wind_speed < 1.0:
            return 'Calm'
        elif wind_speed < 3.0:
            return 'Light'
        elif wind_speed < 7.0:
            return 'Moderate'
        else:
            return 'Strong'
    
    def calculate_heat_index(self, temp: float, humidity: int) -> Optional[float]:
        """
        Calculate heat index (apparent temperature)
        
        Accounts for both temperature and humidity
        Regress on Steadman formula
        """
        if temp is None or humidity is None:
            return None
        
        # Steadman formula for heat index
        HI = (-42.379 + 2.04901523 * temp + 10.14333127 * humidity 
              - 0.22475541 * temp * humidity 
              - 0.00683783 * temp ** 2 
              - 0.05481717 * humidity ** 2 
              + 0.00122874 * temp ** 2 * humidity 
              + 0.00085282 * temp * humidity ** 2 
              - 0.00000199 * temp ** 2 * humidity ** 2)
        
        return float(HI) if HI > 0 else temp
    
    def calculate_respiratory_stress_factor(self, pollution_stress: float, humidity: int, wind_speed: float) -> Optional[float]:
        """
        Composite respiratory stress factor
        
        Higher = more risk for respiratory system
        Combines pollution, humidity, and stagnation (low wind)
        """
        if any(v is None for v in [pollution_stress, humidity, wind_speed]):
            return None
        
        # Wind speed closer to 0 = stagnation (bad)
        wind_factor = 1.0 / (1.0 + wind_speed)  # Will be ~1.0 if wind_speed = 0
        
        # High humidity + pollution = worse respiratory impact
        humidity_factor = (humidity / 100.0)
        
        # Combine factors
        rsf = pollution_stress * humidity_factor * wind_factor
        return float(rsf)
    
    def calculate_compound_risk(self, pollution_stress: float, thi: float, wind_stress: str) -> Optional[float]:
        """
        Air quality + weather compound risk score
        """
        if pollution_stress is None or thi is None:
            return None
        
        # Wind stress multiplier (stagnation increases risk)
        wind_multipliers = {'Calm': 1.5, 'Light': 1.2, 'Moderate': 1.0, 'Strong': 0.7, 'Unknown': 1.0}
        wind_mult = wind_multipliers.get(wind_stress, 1.0)
        
        # THI-based multiplier (heat stress increases respiratory sensitivity)
        thi_threshold = 28  # Comfort threshold
        thi_mult = max(1.0, 1.0 + (thi - thi_threshold) / 10.0)  # Increases with heat stress
        
        # Compound risk
        compound_risk = pollution_stress * wind_mult * thi_mult
        return min(float(compound_risk), 1.0)  # Cap at 1.0
    
    def process_aqi_features(self, city_id: int, date: str = None) -> bool:
        """
        Process AQI data for a city on a specific date
        
        Args:
            city_id: City database ID
            date: Date to process (default: today)
        
        Returns:
            True if successful
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Get raw AQI data for the date
            query = """
            SELECT AVG(aqi) as avg_aqi, AVG(pm25) as avg_pm25, AVG(pm10) as avg_pm10, 
                   AVG(no2) as avg_no2, AVG(so2) as avg_so2, COUNT(*) as data_points
            FROM aqi_raw
            WHERE city_id = %s AND DATE(timestamp) = %s
            """
            result = self.db.fetch_one(query, (city_id, date))
            
            if not result or result['avg_aqi'] is None:
                logger.warning(f"No AQI data for city {city_id} on {date}")
                return False
            
            aqi_value = int(result['avg_aqi'])
            aqi_category = self.calculate_aqi_category(aqi_value)
            pollution_stress = self.calculate_pollution_stress_index(
                result['avg_pm25'], result['avg_pm10'], 
                result['avg_no2'], result['avg_so2']
            )
            pm_ratio = result['avg_pm25'] / result['avg_pm10'] if result['avg_pm10'] and result['avg_pm10'] > 0 else None
            
            # Insert into processed table
            insert_query = """
            INSERT INTO aqi_processed 
            (city_id, date, aqi_value, aqi_category, pollution_stress_index, pm25_pm10_ratio, data_quality_flag, data_points_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                aqi_value = %s, aqi_category = %s, pollution_stress_index = %s, pm25_pm10_ratio = %s, data_points_count = %s
            """
            params = (city_id, date, aqi_value, aqi_category, pollution_stress, pm_ratio, 'OK', result['data_points'],
                     aqi_value, aqi_category, pollution_stress, pm_ratio, result['data_points'])
            
            return self.db.execute_query(insert_query, params)
            
        except Exception as e:
            logger.error(f"Error processing AQI features for city {city_id}: {e}")
            return False
    
    def process_weather_features(self, city_id: int, date: str = None) -> bool:
        """Process weather data for a city on a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Get raw weather data for the date
            query = """
            SELECT AVG(temperature) as avg_temp, AVG(humidity) as avg_humidity, 
                   AVG(wind_speed) as avg_wind_speed, COUNT(*) as data_points
            FROM weather_raw
            WHERE city_id = %s AND DATE(timestamp) = %s
            """
            result = self.db.fetch_one(query, (city_id, date))
            
            if not result or result['avg_temp'] is None:
                logger.warning(f"No weather data for city {city_id} on {date}")
                return False
            
            temp = result['avg_temp']
            humidity = int(result['avg_humidity']) if result['avg_humidity'] else None
            wind_speed = result['avg_wind_speed']
            
            thi = self.calculate_temperature_humidity_index(temp, humidity)
            wind_stress = self.classify_wind_stress(wind_speed)
            heat_index = self.calculate_heat_index(temp, humidity)
            
            # Insert into processed table
            insert_query = """
            INSERT INTO weather_processed 
            (city_id, date, avg_temperature, avg_humidity, avg_wind_speed, temperature_humidity_index, wind_stress_category, heat_index, data_points_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                avg_temperature = %s, avg_humidity = %s, avg_wind_speed = %s, 
                temperature_humidity_index = %s, wind_stress_category = %s, heat_index = %s, data_points_count = %s
            """
            params = (city_id, date, temp, humidity, wind_speed, thi, wind_stress, heat_index, result['data_points'],
                     temp, humidity, wind_speed, thi, wind_stress, heat_index, result['data_points'])
            
            return self.db.execute_query(insert_query, params)
            
        except Exception as e:
            logger.error(f"Error processing weather features for city {city_id}: {e}")
            return False
    
    def process_combined_features(self, city_id: int, date: str = None) -> bool:
        """Calculate combined risk features"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Get processed AQI and weather data
            aqi_query = "SELECT pollution_stress_index FROM aqi_processed WHERE city_id = %s AND date = %s"
            aqi_result = self.db.fetch_one(aqi_query, (city_id, date))
            
            weather_query = "SELECT temperature_humidity_index, wind_stress_category FROM weather_processed WHERE city_id = %s AND date = %s"
            weather_result = self.db.fetch_one(weather_query, (city_id, date))
            
            if not aqi_result or not weather_result:
                logger.warning(f"Missing processed features for city {city_id} on {date}")
                return False
            
            pollution_stress = aqi_result['pollution_stress_index']
            thi = weather_result['temperature_humidity_index']
            wind_stress = weather_result['wind_stress_category']
            
            # Get raw data for respiratory stress calculation
            raw_query = """
            SELECT AVG(humidity) as avg_humidity, AVG(wind_speed) as avg_wind_speed
            FROM weather_raw
            WHERE city_id = %s AND DATE(timestamp) = %s
            """
            raw_result = self.db.fetch_one(raw_query, (city_id, date))
            
            compound_risk = self.calculate_compound_risk(pollution_stress, thi, wind_stress)
            respiratory_stress = self.calculate_respiratory_stress_factor(
                pollution_stress, 
                int(raw_result['avg_humidity']) if raw_result['avg_humidity'] else 50,
                raw_result['avg_wind_speed']
            )
            
            # Insert into combined features table
            insert_query = """
            INSERT INTO risk_features 
            (city_id, date, air_quality_weather_compound_risk, respiratory_stress_factor, combined_risk_score)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                air_quality_weather_compound_risk = %s, respiratory_stress_factor = %s, combined_risk_score = %s
            """
            params = (city_id, date, compound_risk, respiratory_stress, compound_risk,
                     compound_risk, respiratory_stress, compound_risk)
            
            return self.db.execute_query(insert_query, params)
            
        except Exception as e:
            logger.error(f"Error processing combined features for city {city_id}: {e}")
            return False
    
    def process_all_features(self, date: str = None):
        """Process all features for all cities"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Processing features for date: {date}")
        
        cities = self.db.get_all_cities()
        aqi_ok = 0
        weather_ok = 0
        combined_ok = 0
        
        for city in cities:
            city_id = city['id']
            if self.process_aqi_features(city_id, date):
                aqi_ok += 1
            if self.process_weather_features(city_id, date):
                weather_ok += 1
            if self.process_combined_features(city_id, date):
                combined_ok += 1
        
        logger.info(f"Feature processing complete - AQI: {aqi_ok}, Weather: {weather_ok}, Combined: {combined_ok}/{len(cities)}")


if __name__ == '__main__':
    engineer = FeatureEngineer()
    engineer.process_all_features()
