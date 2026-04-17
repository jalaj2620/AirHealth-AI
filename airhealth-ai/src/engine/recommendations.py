"""
Rule-based health recommendation engine
"""
import logging
import json
from datetime import datetime
from typing import Dict, List
from src.utils.db import get_connection
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger('recommendations')


class RecommendationEngine:
    """Generate personalized health and activity recommendations"""
    
    def __init__(self):
        self.db = get_connection()
        self.rules = Config.load_health_rules()
    
    def generate_recommendation(self, risk_level: str, aqi_value: int, 
                               temperature: float, wind_speed: float) -> Dict[str, str]:
        """
        Generate health recommendations based on risk level and environmental factors
        
        Args:
            risk_level: 'Safe', 'Moderate', 'Dangerous', 'Hazardous'
            aqi_value: Air Quality Index value
            temperature: Current temperature in Celsius
            wind_speed: Wind speed in m/s
        
        Returns:
            Dict with general_advice, sensitive_groups_advice, activity_level, precautions
        """
        recommendations = self.rules.get('recommendation_rules', {})
        rec_template = recommendations.get(risk_level.lower(), recommendations.get('moderate'))
        
        recommendation = {
            'risk_level': risk_level,
            'general_advice': rec_template.get('general', ''),
            'sensitive_groups_advice': rec_template.get('sensitive_groups', ''),
            'activity_level': rec_template.get('activity_level', 'moderate'),
            'precautions': rec_template.get('precautions', [])
        }
        
        # Add dynamic recommendations based on environmental factors
        if wind_speed < 1.0 and aqi_value > 100:
            recommendation['additional_warning'] = "⚠️ Wind stagnation detected - air not dispersing. Pollution concentration may increase."
        
        if temperature > 35 and aqi_value > 100:
            recommendation['additional_warning'] = "⚠️ High heat + poor air quality: Extreme health risk. Avoid outdoor activities."
        
        if temperature < 5 and aqi_value > 100:
            recommendation['additional_warning'] = "❄️ Cold + poor air quality: Can exacerbate asthma. Use inhalers as needed."
        
        return recommendation
    
    def generate_for_city(self, city_id: int, date: str = None) -> bool:
        """
        Generate and store recommendations for a city
        
        Args:
            city_id: City database ID
            date: Date for recommendations (default: today)
        
        Returns:
            True if successful
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Get prediction and environmental data
            pred_query = """
            SELECT rp.risk_level, a.aqi_value, w.avg_temperature, w.avg_wind_speed
            FROM risk_predictions rp
            LEFT JOIN aqi_processed a ON rp.city_id = a.city_id AND rp.prediction_date = a.date
            LEFT JOIN weather_processed w ON rp.city_id = w.city_id AND rp.prediction_date = w.date
            WHERE rp.city_id = %s AND rp.prediction_date = %s
            """
            
            result = self.db.fetch_one(pred_query, (city_id, date))
            
            if not result:
                logger.warning(f"No prediction data for city {city_id} on {date}")
                return False
            
            # Generate recommendation
            rec = self.generate_recommendation(
                result['risk_level'],
                result['aqi_value'] or 0,
                result['avg_temperature'] or 25,
                result['avg_wind_speed'] or 2
            )
            
            # Store recommendation
            insert_query = """
            INSERT INTO recommendations 
            (city_id, recommendation_date, risk_level, general_advice, sensitive_groups_advice, 
             activity_level, precautions)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                risk_level = %s, general_advice = %s, sensitive_groups_advice = %s,
                activity_level = %s, precautions = %s
            """
            
            precautions_json = json.dumps(rec['precautions'])
            params = (
                city_id, date, rec['risk_level'],
                rec['general_advice'], rec['sensitive_groups_advice'],
                rec['activity_level'], precautions_json,
                rec['risk_level'], rec['general_advice'], rec['sensitive_groups_advice'],
                rec['activity_level'], precautions_json
            )
            
            return self.db.execute_query(insert_query, params)
            
        except Exception as e:
            logger.error(f"Error generating recommendation for city {city_id}: {e}")
            return False
    
    def generate_for_all_cities(self, date: str = None):
        """Generate recommendations for all cities"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Generating recommendations for {date}...")
        
        cities = self.db.get_all_cities()
        success_count = 0
        
        for city in cities:
            if self.generate_for_city(city['id'], date):
                success_count += 1
        
        logger.info(f"Recommendations generated: {success_count}/{len(cities)}")
    
    def get_outdoor_safety_verdict(self, risk_level: str) -> str:
        """Get simple outdoor activity safety verdict"""
        verdicts = {
            'Safe': '✅ Safe to go outside',
            'Moderate': '⚠️ Caution - limit outdoor activities',
            'Dangerous': '🚫 Avoid outdoor activities',
            'Hazardous': '🚨 Emergency - Stay indoors'
        }
        return verdicts.get(risk_level, '❓ Unknown')


def main():
    """Generate recommendations from command line"""
    engine = RecommendationEngine()
    engine.generate_for_all_cities()


if __name__ == '__main__':
    main()
