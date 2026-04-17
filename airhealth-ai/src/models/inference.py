"""
Batch inference pipeline - generate daily predictions for all cities
"""
import logging
import json
from datetime import datetime
from src.utils.db import get_connection
from src.utils.logger import get_logger
from src.models.risk_classifier import RiskClassifier

logger = get_logger('inference')


class InferencePipeline:
    """Generate daily health risk predictions for all cities"""
    
    def __init__(self):
        self.db = get_connection()
        self.classifier = RiskClassifier()
        self.classifier.load_model()
    
    def generate_predictions(self, date: str = None):
        """
        Generate risk predictions for all cities on given date
        
        Args:
            date: Date to generate predictions for (default: today)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Generating predictions for {date}...")
        
        cities = self.db.get_all_cities()
        success_count = 0
        
        for city in cities:
            city_id = city['id']
            city_name = city['name']
            
            # Get processed features for the city and date
            query = """
            SELECT 
                a.aqi_value, a.pollution_stress_index, a.pm25_pm10_ratio,
                w.avg_temperature, w.avg_humidity, w.avg_wind_speed,
                w.temperature_humidity_index, w.heat_index,
                rf.air_quality_weather_compound_risk, rf.respiratory_stress_factor
            FROM risk_features rf
            JOIN aqi_processed a ON rf.city_id = a.city_id AND rf.date = a.date
            JOIN weather_processed w ON rf.city_id = w.city_id AND rf.date = w.date
            WHERE rf.city_id = %s AND rf.date = %s
            """
            
            result = self.db.fetch_one(query, (city_id, date))
            
            if not result:
                logger.warning(f"No features available for {city_name} on {date}")
                continue
            
            # Prepare feature dict
            features = {
                'aqi_value': result['aqi_value'],
                'pollution_stress_index': result['pollution_stress_index'],
                'pm25_pm10_ratio': result['pm25_pm10_ratio'],
                'avg_temperature': result['avg_temperature'],
                'avg_humidity': result['avg_humidity'],
                'avg_wind_speed': result['avg_wind_speed'],
                'temperature_humidity_index': result['temperature_humidity_index'],
                'heat_index': result['heat_index'],
                'air_quality_weather_compound_risk': result['air_quality_weather_compound_risk'],
                'respiratory_stress_factor': result['respiratory_stress_factor']
            }
            
            # Generate prediction
            risk_level, confidence = self.classifier.predict_risk_level(features)
            
            # Store prediction
            insert_query = """
            INSERT INTO risk_predictions 
            (city_id, prediction_date, risk_level, confidence_score, model_version, prediction_features)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                risk_level = %s, confidence_score = %s, prediction_features = %s
            """
            
            features_json = json.dumps(features)
            params = (city_id, date, risk_level, confidence, 'v1', features_json,
                     risk_level, confidence, features_json)
            
            if self.db.execute_query(insert_query, params):
                success_count += 1
                logger.debug(f"✓ Prediction for {city_name}: {risk_level} ({confidence:.2%})")
            else:
                logger.warning(f"Failed to store prediction for {city_name}")
        
        logger.info(f"Predictions generated successfully: {success_count}/{len(cities)}")


def main():
    """Run inference pipeline"""
    pipeline = InferencePipeline()
    pipeline.generate_predictions()


if __name__ == '__main__':
    main()
