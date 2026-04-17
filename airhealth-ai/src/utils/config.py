"""
Config utilities for AirHealth AI
"""
import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '../../config/.env'))

logger = logging.getLogger(__name__)


class Config:
    """Application configuration"""
    
    # API Configuration
    OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', '')
    OPENWEATHERMAP_BASE_URL = os.getenv('OPENWEATHERMAP_BASE_URL', 'https://api.openweathermap.org/data/2.5')
    OPENAQ_BASE_URL = os.getenv('OPENAQ_BASE_URL', 'https://api.openaq.org/v2')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'airhealth_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'airhealth_password_123')
    DB_NAME = os.getenv('DB_NAME', 'airhealth_db')
    
    # System Configuration
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DATA_COLLECTION_HOUR = int(os.getenv('DATA_COLLECTION_HOUR', 6))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
    
    # Model Configuration
    MODEL_VERSION = os.getenv('MODEL_VERSION', 'v1')
    PREDICTION_CONFIDENCE_THRESHOLD = float(os.getenv('PREDICTION_CONFIDENCE_THRESHOLD', 0.6))
    RETRAIN_FREQUENCY_DAYS = int(os.getenv('RETRAIN_FREQUENCY_DAYS', 7))
    
    @staticmethod
    def load_cities():
        """Load cities from config/cities.json"""
        cities_file = os.path.join(os.path.dirname(__file__), '../../config/cities.json')
        try:
            with open(cities_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cities config: {e}")
            return []
    
    @staticmethod
    def load_health_rules():
        """Load health risk rules from external config"""
        rules_file = os.path.join(os.path.dirname(__file__), '../../data/external/health_risk_rules.json')
        try:
            with open(rules_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading health rules: {e}")
            return {}


def validate_config():
    """Validate that all required configuration is set"""
    config = Config()
    
    issues = []
    
    if not config.OPENWEATHERMAP_API_KEY or config.OPENWEATHERMAP_API_KEY == '':
        issues.append("⚠️  OPENWEATHERMAP_API_KEY not set. Get free key from https://openweathermap.org/api")
    
    if not config.DB_HOST:
        issues.append("❌ DB_HOST not configured")
    
    if not config.DB_USER:
        issues.append("❌ DB_USER not configured")
    
    if issues:
        logger.warning("Configuration Issues Found:")
        for issue in issues:
            logger.warning(f"  {issue}")
        return False
    
    logger.info("✓ Configuration valid")
    return True
