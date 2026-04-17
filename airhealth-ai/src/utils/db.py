"""
Database connection and query utilities for AirHealth AI
"""
import os
import logging
from typing import Optional, List, Dict, Any
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Manages MySQL database connections and queries"""

    def __init__(self, host: str = None, user: str = None, password: str = None, database: str = None, port: int = 3306):
        """
        Initialize database connector with credentials from env vars or parameters
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.user = user or os.getenv('DB_USER', 'airhealth_user')
        self.password = password or os.getenv('DB_PASSWORD', 'airhealth_password_123')
        self.database = database or os.getenv('DB_NAME', 'airhealth_db')
        self.port = port or int(os.getenv('DB_PORT', 3306))
        self.connection = None

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True
            )
            logger.info(f"Connected to MySQL database: {self.database}")
            return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Disconnected from MySQL database")

    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute INSERT, UPDATE, or DELETE query"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Error executing query: {e}\nQuery: {query}")
            return False

    def fetch_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results as list of dicts"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Error fetching data: {e}\nQuery: {query}")
            return []

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Execute SELECT query and return single result"""
        results = self.fetch_query(query, params)
        return results[0] if results else None

    def insert_or_update_aqi(self, city_id: int, aqi_data: Dict) -> bool:
        """Insert AQI data into aqi_raw table"""
        query = """
        INSERT INTO aqi_raw 
        (city_id, timestamp, aqi, pm25, pm10, no2, so2, co, source, raw_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            city_id,
            aqi_data.get('timestamp'),
            aqi_data.get('aqi'),
            aqi_data.get('pm25'),
            aqi_data.get('pm10'),
            aqi_data.get('no2'),
            aqi_data.get('so2'),
            aqi_data.get('co'),
            aqi_data.get('source', 'OpenAQ'),
            aqi_data.get('raw_json', '')
        )
        return self.execute_query(query, params)

    def insert_or_update_weather(self, city_id: int, weather_data: Dict) -> bool:
        """Insert weather data into weather_raw table"""
        query = """
        INSERT INTO weather_raw 
        (city_id, timestamp, temperature, humidity, wind_speed, cloudiness, rain_1h, pressure, visibility, source, raw_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            city_id,
            weather_data.get('timestamp'),
            weather_data.get('temperature'),
            weather_data.get('humidity'),
            weather_data.get('wind_speed'),
            weather_data.get('cloudiness'),
            weather_data.get('rain_1h'),
            weather_data.get('pressure'),
            weather_data.get('visibility'),
            weather_data.get('source', 'OpenWeatherMap'),
            weather_data.get('raw_json', '')
        )
        return self.execute_query(query, params)

    def get_city_by_name(self, city_name: str) -> Optional[Dict]:
        """Get city ID and coordinates by name"""
        query = "SELECT id, name, latitude, longitude FROM cities WHERE name = %s"
        return self.fetch_one(query, (city_name,))

    def get_all_cities(self) -> List[Dict]:
        """Get all cities from database"""
        query = "SELECT id, name, latitude, longitude, state FROM cities ORDER BY tier, name"
        return self.fetch_query(query)

    def log_collection(self, source: str, attempted: int, successful: int, failed: int, duration: float, error: str = None):
        """Log data collection statistics"""
        query = """
        INSERT INTO collection_logs 
        (source, cities_attempted, cities_successful, cities_failed, duration_seconds, error_message)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (source, attempted, successful, failed, duration, error)
        return self.execute_query(query, params)


# Global connection pool (use singleton pattern)
_db_connection: Optional[DatabaseConnector] = None


def get_connection() -> DatabaseConnector:
    """Get or create database connection"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnector()
        _db_connection.connect()
    return _db_connection
