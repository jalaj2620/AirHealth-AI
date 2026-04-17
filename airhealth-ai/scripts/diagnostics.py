"""
Diagnostic and debugging tools for AirHealth AI
"""
import logging
from src.utils.db import get_connection
from src.utils.config import validate_config, Config
from src.collectors.openaq_collector import OpenAQCollector
from src.collectors.openweathermap_collector import OpenWeatherMapCollector

logger = logging.getLogger(__name__)


def diagnose_system():
    """Run comprehensive system diagnostics"""
    print("\n🔍 AirHealth AI - System Diagnostics\n" + "=" * 50)
    
    # 1. Configuration
    print("\n1️⃣  Configuration Check")
    print("-" * 50)
    if validate_config():
        print("✅ Configuration valid")
    else:
        print("⚠️  Configuration issues detected (see warnings above)")
    
    # 2. Database Connectivity
    print("\n2️⃣  Database Connectivity")
    print("-" * 50)
    try:
        db = get_connection()
        if db.connect():
            print("✅ MySQL connected successfully")
            
            # Count records
            cities = db.fetch_query("SELECT COUNT(*) as count FROM cities")
            aqi = db.fetch_query("SELECT COUNT(*) as count FROM aqi_raw")
            weather = db.fetch_query("SELECT COUNT(*) as count FROM weather_raw")
            
            print(f"   - Cities: {cities[0]['count']} (expected: 30)")
            print(f"   - AQI records: {aqi[0]['count']}")
            print(f"   - Weather records: {weather[0]['count']}")
        else:
            print("❌ Failed to connect to MySQL")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. API Connectivity
    print("\n3️⃣  API Connectivity")
    print("-" * 50)
    
    # Test OpenAQ
    try:
        result = OpenAQCollector.get_latest_by_city("Delhi")
        if result:
            print("✅ OpenAQ API working")
            print(f"   - Sample: AQI={result.get('aqi')}, PM2.5={result.get('pm25')}")
        else:
            print("⚠️  OpenAQ returned no data for test city")
    except Exception as e:
        print(f"❌ OpenAQ error: {e}")
    
    # Test OpenWeatherMap
    try:
        owm = OpenWeatherMapCollector()
        result = owm.get_weather("Delhi", 28.7041, 77.1025)
        if result:
            print("✅ OpenWeatherMap API working")
            print(f"   - Sample: Temp={result.get('temperature')}°C, Humidity={result.get('humidity')}%")
        else:
            print("⚠️  OpenWeatherMap returned no data")
    except Exception as e:
        print(f"❌ OpenWeatherMap error: {e}")
    
    # 4. Feature Engineering
    print("\n4️⃣  Feature Engineering")
    print("-" * 50)
    try:
        from src.processors.feature_engineer import FeatureEngineer
        eng = FeatureEngineer()
        
        # Test feature calculations
        thi = eng.calculate_temperature_humidity_index(25, 60)
        psi = eng.calculate_pollution_stress_index(35, 50, 100, 20)
        rsf = eng.calculate_respiratory_stress_factor(0.5, 70, 2.0)
        
        print("✅ Feature engineering working")
        print(f"   - THI(25°C, 60%): {thi:.2f}")
        print(f"   - PSI(PM2.5=35, PM10=50, NO2=100, SO2=20): {psi:.2f}")
        print(f"   - RSF: {rsf:.2f}")
    except Exception as e:
        print(f"❌ Feature engineering error: {e}")
    
    # 5. Model Status
    print("\n5️⃣  ML Model Status")
    print("-" * 50)
    try:
        from src.models.risk_classifier import RiskClassifier
        import os
        
        classifier = RiskClassifier()
        model_file = os.path.join(classifier.MODEL_DIR, f'risk_classifier_{classifier.model_version}.pkl')
        
        if os.path.exists(model_file):
            print("✅ Trained model found")
            if classifier.load_model():
                print("✅ Model loaded successfully")
                # Test prediction
                test_features = {
                    'aqi_value': 75,
                    'pollution_stress_index': 0.4,
                    'pm25_pm10_ratio': 0.7,
                    'avg_temperature': 25,
                    'avg_humidity': 60,
                    'avg_wind_speed': 2.5,
                    'temperature_humidity_index': 25,
                    'heat_index': 28,
                    'air_quality_weather_compound_risk': 0.3,
                    'respiratory_stress_factor': 0.3
                }
                risk, confidence = classifier.predict_risk_level(test_features)
                print(f"   - Test prediction: {risk} (confidence: {confidence:.2%})")
            else:
                print("⚠️  Model found but failed to load")
        else:
            print("⚠️  No trained model found (expected after first training run)")
    except Exception as e:
        print(f"❌ Model error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Diagnostics Complete\n")


def test_data_pipeline():
    """Test end-to-end data pipeline"""
    print("\n🔄 Testing Data Pipeline\n" + "=" * 50)
    
    try:
        print("\n1. Collecting data...")
        from src.main_collector import DataCollectionOrchestrator
        collector = DataCollectionOrchestrator()
        collector.collect_all_data()
        
        print("\n2. Processing features...")
        from src.processors.feature_engineer import FeatureEngineer
        engineer = FeatureEngineer()
        engineer.process_all_features()
        
        print("\n3. Generating predictions...")
        from src.models.inference import InferencePipeline
        pipeline = InferencePipeline()
        pipeline.generate_predictions()
        
        print("\n4. Generating recommendations...")
        from src.engine.recommendations import RecommendationEngine
        engine = RecommendationEngine()
        engine.generate_for_all_cities()
        
        print("\n✅ Full pipeline executed successfully!")
        
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'pipeline':
        test_data_pipeline()
    else:
        diagnose_system()
