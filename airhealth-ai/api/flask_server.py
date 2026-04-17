"""
Flask REST API for AirHealth AI predictions
"""
import json
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from src.utils.db import get_connection
from src.utils.logger import get_logger

app = Flask(__name__)
CORS(app)

# Setup logging
logger = get_logger('flask_api')


@app.before_request
def log_request():
    """Log incoming requests"""
    logger.info(f"{request.method} {request.path}")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()})


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get list of all available cities"""
    try:
        db = get_connection()
        cities = db.get_all_cities()
        
        return jsonify({
            'status': 'success',
            'count': len(cities),
            'cities': cities
        })
    except Exception as e:
        logger.error(f"Error getting cities: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/current/<int:city_id>', methods=['GET'])
def get_current_data(city_id):
    """Get current metrics and predictions for a city"""
    try:
        db = get_connection()
        
        # Get city info
        city_query = "SELECT name, state FROM cities WHERE id = %s"
        city = db.fetch_one(city_query, (city_id,))
        
        if not city:
            return jsonify({'status': 'error', 'message': 'City not found'}), 404
        
        # Get latest AQI
        aqi_query = """
        SELECT aqi_value, aqi_category, pollution_stress_index, timestamp
        FROM aqi_raw
        WHERE city_id = %s
        ORDER BY timestamp DESC LIMIT 1
        """
        aqi = db.fetch_one(aqi_query, (city_id,))
        
        # Get latest weather
        weather_query = """
        SELECT temperature, humidity, wind_speed, timestamp
        FROM weather_raw
        WHERE city_id = %s
        ORDER BY timestamp DESC LIMIT 1
        """
        weather = db.fetch_one(weather_query, (city_id,))
        
        # Get latest prediction
        pred_query = """
        SELECT risk_level, confidence_score, prediction_date
        FROM risk_predictions
        WHERE city_id = %s
        ORDER BY prediction_date DESC LIMIT 1
        """
        prediction = db.fetch_one(pred_query, (city_id,))
        
        # Get latest recommendation
        rec_query = """
        SELECT general_advice, sensitive_groups_advice, activity_level, precautions
        FROM recommendations
        WHERE city_id = %s
        ORDER BY recommendation_date DESC LIMIT 1
        """
        recommendation = db.fetch_one(rec_query, (city_id,))
        
        return jsonify({
            'status': 'success',
            'city': city,
            'aqi': aqi,
            'weather': weather,
            'prediction': prediction,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting current data: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/history/<int:city_id>', methods=['GET'])
def get_history(city_id):
    """Get historical AQI data for charting"""
    try:
        db = get_connection()
        days = request.args.get('days', 30, type=int)
        
        # Validate city exists
        city_query = "SELECT name FROM cities WHERE id = %s"
        city = db.fetch_one(city_query, (city_id,))
        
        if not city:
            return jsonify({'status': 'error', 'message': 'City not found'}), 404
        
        # Get historical data
        history_query = """
        SELECT DATE(date) as date, aqi_value, aqi_category
        FROM aqi_processed
        WHERE city_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY date ASC
        """
        
        history = db.fetch_query(history_query, (city_id, days))
        
        return jsonify({
            'status': 'success',
            'city_id': city_id,
            'days': days,
            'data_points': len(history),
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/forecast/<int:city_id>', methods=['GET'])
def get_forecast(city_id):
    """Get AQI forecast for next 7 days (Phase 3)"""
    try:
        db = get_connection()
        
        # For now, return last 7 days as placeholder
        forecast_query = """
        SELECT DATE(date) as forecast_date, aqi_value
        FROM aqi_processed
        WHERE city_id = %s
        ORDER BY date DESC LIMIT 7
        """
        
        forecast = db.fetch_query(forecast_query, (city_id,))
        
        return jsonify({
            'status': 'success',
            'city_id': city_id,
            'forecast_days': 7,
            'note': 'Prophet forecasting coming in Phase 3',
            'recent_data': list(reversed(forecast))
        })
        
    except Exception as e:
        logger.error(f"Error getting forecast: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        db = get_connection()
        
        # Get counts
        cities_query = "SELECT COUNT(*) as count FROM cities"
        cities_count = db.fetch_one(cities_query, ())['count']
        
        aqi_records_query = "SELECT COUNT(*) as count FROM aqi_raw"
        aqi_count = db.fetch_one(aqi_records_query, ())['count']
        
        predictions_query = "SELECT COUNT(*) as count FROM risk_predictions"
        predictions_count = db.fetch_one(predictions_query, ())['count']
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_cities': cities_count,
                'total_aqi_records': aqi_count,
                'total_predictions': predictions_count,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting AirHealth AI Flask API server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
