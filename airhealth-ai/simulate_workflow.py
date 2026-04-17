#!/usr/bin/env python
"""
AirHealth AI - Data Flow Simulation
Shows step-by-step what happens when you run the system
"""

import json
from datetime import datetime, timedelta
import random

class DataFlowSimulator:
    """Simulates the complete AirHealth AI data flow"""
    
    def __init__(self):
        self.cities = self.load_sample_cities()
        self.simulation_log = []
    
    def load_sample_cities(self):
        """Load sample Indian cities"""
        return [
            {"id": 1, "name": "Delhi", "state": "Delhi", "lat": 28.7041, "lon": 77.1025},
            {"id": 2, "name": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777},
            {"id": 3, "name": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
            {"id": 4, "name": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
            {"id": 5, "name": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
        ]
    
    def simulate_api_collection(self, city):
        """Simulate data collection from APIs"""
        self.log(f"\n📡 COLLECTING DATA FOR {city['name'].upper()}")
        self.log("=" * 60)
        
        # Simulate OpenAQ API call
        self.log(f"🔍 Querying OpenAQ API for {city['name']}...")
        aqi_data = {
            "city_id": city["id"],
            "timestamp": datetime.now().isoformat(),
            "aqi": random.randint(20, 250),
            "pm25": random.randint(5, 150),
            "pm10": random.randint(10, 250),
            "no2": random.randint(5, 100),
            "so2": random.randint(0, 50),
            "co": random.randint(200, 2000)
        }
        self.log(f"✓ AQI Data retrieved:")
        self.log(f"  - AQI Value: {aqi_data['aqi']}")
        self.log(f"  - PM2.5: {aqi_data['pm25']} µg/m³")
        self.log(f"  - PM10: {aqi_data['pm10']} µg/m³")
        
        # Simulate OpenWeatherMap API call
        self.log(f"\n🔍 Querying OpenWeatherMap API for {city['name']}...")
        weather_data = {
            "city_id": city["id"],
            "timestamp": datetime.now().isoformat(),
            "temperature": random.randint(15, 40),
            "humidity": random.randint(30, 90),
            "wind_speed": random.uniform(0, 20),
            "cloudiness": random.randint(0, 100),
            "pressure": random.randint(1000, 1020)
        }
        self.log(f"✓ Weather Data retrieved:")
        self.log(f"  - Temperature: {weather_data['temperature']}°C")
        self.log(f"  - Humidity: {weather_data['humidity']}%")
        self.log(f"  - Wind Speed: {weather_data['wind_speed']:.1f} m/s")
        
        return aqi_data, weather_data
    
    def simulate_database_storage(self, city_name, aqi_data, weather_data):
        """Simulate storing data in MySQL"""
        self.log(f"\n💾 STORING IN MYSQL DATABASE")
        self.log(f"✓ Inserting into aqi_raw table:")
        self.log(f"  → city_id={aqi_data['city_id']}, aqi={aqi_data['aqi']}")
        self.log(f"✓ Inserting into weather_raw table:")
        self.log(f"  → city_id={weather_data['city_id']}, temp={weather_data['temperature']}°C")
    
    def simulate_feature_engineering(self, aqi_data, weather_data):
        """Simulate feature engineering process"""
        self.log(f"\n⚙️  FEATURE ENGINEERING")
        
        # Calculate features
        pm_ratio = aqi_data['pm25'] / max(aqi_data['pm10'], 1)
        pollution_stress = (aqi_data['aqi'] / 500) * 100
        heat_index = weather_data['temperature'] + (weather_data['humidity'] * 0.1)
        temp_humidity_index = (weather_data['temperature'] * 0.8) + (weather_data['humidity'] * 0.2)
        
        features = {
            "pm25_pm10_ratio": round(pm_ratio, 2),
            "pollution_stress_index": round(pollution_stress, 2),
            "heat_index": round(heat_index, 2),
            "temp_humidity_index": round(temp_humidity_index, 2),
            "aqi_category": self.get_aqi_category(aqi_data['aqi']),
            "wind_stress": "High" if weather_data['wind_speed'] > 10 else "Low"
        }
        
        self.log(f"✓ Generated 15+ engineered features:")
        for feature, value in features.items():
            self.log(f"  - {feature}: {value}")
        
        return features
    
    def get_aqi_category(self, aqi):
        """Get AQI category"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy"
        else:
            return "Hazardous"
    
    def simulate_risk_prediction(self, features, aqi_data):
        """Simulate ML model prediction"""
        self.log(f"\n🤖 ML MODEL PREDICTION (XGBoost)")
        
        # Simulate model scoring
        feature_vector = [
            features['pm25_pm10_ratio'],
            features['pollution_stress_index'],
            features['heat_index'],
            features['temp_humidity_index'],
            aqi_data['aqi']
        ]
        
        # Simulate model output
        confidence = random.uniform(0.70, 0.99)
        
        if aqi_data['aqi'] <= 50:
            risk_level = "SAFE"
            color = "🟢"
        elif aqi_data['aqi'] <= 100:
            risk_level = "MODERATE"
            color = "🟡"
        elif aqi_data['aqi'] <= 150:
            risk_level = "UNHEALTHY"
            color = "🟠"
        else:
            risk_level = "DANGEROUS"
            color = "🔴"
        
        self.log(f"✓ Input Features: {feature_vector[:3]}... (15 features total)")
        self.log(f"✓ Model Version: v1 (XGBoost Classifier)")
        self.log(f"✓ Prediction: {color} {risk_level}")
        self.log(f"✓ Confidence Score: {confidence:.2%}")
        
        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "color": color
        }
    
    def simulate_recommendations(self, risk_level, aqi_data):
        """Simulate health recommendations"""
        self.log(f"\n👨‍⚕️  GENERATING HEALTH RECOMMENDATIONS")
        
        recommendations = {
            "SAFE": {
                "general": "Green light! Air quality is good. You can safely engage in outdoor activities.",
                "sensitive": "Safe for all groups including children, elderly, and those with respiratory conditions.",
                "activity": "All outdoor activities permitted",
                "precautions": "None required"
            },
            "MODERATE": {
                "general": "Moderate air quality. Consider limiting prolonged outdoor exertion.",
                "sensitive": "Sensitive groups should consider reducing outdoor activities.",
                "activity": "Light activities okay; avoid heavy exertion",
                "precautions": "Consider wearing a regular mask if sensitive"
            },
            "UNHEALTHY": {
                "general": "Unhealthy air quality. Everyone should reduce outdoor exertion.",
                "sensitive": "Sensitive groups should avoid outdoor activities.",
                "activity": "Severe restrictions on outdoor activity",
                "precautions": "Recommended to wear N95/N99 masks; stay indoors when possible"
            },
            "DANGEROUS": {
                "general": "HAZARDOUS: Avoid all outdoor activities. Stay indoors.",
                "sensitive": "High-risk groups MUST stay indoors and use air purifiers.",
                "activity": "All outdoor activities PROHIBITED",
                "precautions": "STAY INDOORS; Use HEPA air purifiers; Medical consultation advised"
            }
        }
        
        rec = recommendations.get(risk_level, recommendations["MODERATE"])
        self.log(f"✓ General Population: {rec['general']}")
        self.log(f"✓ Sensitive Groups: {rec['sensitive']}")
        self.log(f"✓ Activity Level: {rec['activity']}")
        self.log(f"✓ Precautions: {rec['precautions']}")
    
    def simulate_dashboard_display(self, city, aqi_data, weather_data, prediction):
        """Simulate dashboard display"""
        self.log(f"\n📊 DASHBOARD DISPLAY (Streamlit)")
        self.log("=" * 60)
        self.log(f"\n🏙️  CITY: {city['name'].upper()}")
        self.log(f"📍 Location: {city['state']}")
        self.log(f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST\n")
        
        self.log(f"AIR QUALITY METRICS:")
        self.log(f"  {prediction['color']} AQI: {aqi_data['aqi']} ({prediction['risk_level']})")
        self.log(f"  🟤 PM2.5: {aqi_data['pm25']} µg/m³")
        self.log(f"  🟫 PM10: {aqi_data['pm10']} µg/m³")
        self.log(f"  NO₂: {aqi_data['no2']} ppb")
        
        self.log(f"\nWEATHER METRICS:")
        self.log(f"  🌡️  Temperature: {weather_data['temperature']}°C")
        self.log(f"  💧 Humidity: {weather_data['humidity']}%")
        self.log(f"  💨 Wind Speed: {weather_data['wind_speed']:.1f} m/s")
        self.log(f"  ☁️  Cloudiness: {weather_data['cloudiness']}%")
        
        self.log(f"\n🔮 PREDICTION:")
        self.log(f"  {prediction['color']} Risk Level: {prediction['risk_level']}")
        self.log(f"  📈 Confidence: {prediction['confidence']:.2%}")
        self.log(f"  📅 30-Day Trend: [Graph with historical data]")
    
    def log(self, message=""):
        """Add message to simulation log"""
        print(message)
        self.simulation_log.append(message)
    
    def run_simulation(self, num_cities=3):
        """Run complete simulation"""
        self.log("\n" + "=" * 60)
        self.log("🚀 AIRHEALTH AI - COMPLETE DATA FLOW SIMULATION")
        self.log("=" * 60)
        self.log(f"\nSimulation: Processing {num_cities} Indian cities")
        self.log(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for city in self.cities[:num_cities]:
            self.log(f"\n{'*' * 60}")
            
            # Step 1: API Collection
            aqi_data, weather_data = self.simulate_api_collection(city)
            
            # Step 2: Database Storage
            self.simulate_database_storage(city['name'], aqi_data, weather_data)
            
            # Step 3: Feature Engineering
            features = self.simulate_feature_engineering(aqi_data, weather_data)
            
            # Step 4: Risk Prediction
            prediction = self.simulate_risk_prediction(features, aqi_data)
            
            # Step 5: Health Recommendations
            self.simulate_recommendations(prediction['risk_level'], aqi_data)
            
            # Step 6: Dashboard Display
            self.simulate_dashboard_display(city, aqi_data, weather_data, prediction)
        
        # Summary
        self.log_summary(num_cities)
    
    def log_summary(self, num_cities):
        """Log summary of simulation"""
        self.log("\n" + "=" * 60)
        self.log("✅ DATA FLOW SIMULATION COMPLETED")
        self.log("=" * 60)
        self.log(f"\n📊 SUMMARY:")
        self.log(f"  ✓ Cities Processed: {num_cities}")
        self.log(f"  ✓ Data Points Collected: {num_cities * 11} (AQI raw + Weather raw)")
        self.log(f"  ✓ Features Generated: {num_cities * 15} (15+ features per city)")
        self.log(f"  ✓ Predictions Made: {num_cities}")
        self.log(f"  ✓ Recommendations Generated: {num_cities}")
        self.log(f"\n📈 TYPICAL EXECUTION TIME:")
        self.log(f"  • API Collection (all cities): 30-60 seconds")
        self.log(f"  • Feature Engineering: 5-10 seconds")
        self.log(f"  • ML Predictions: 2-5 seconds")
        self.log(f"  • Total: 40-75 seconds per cycle")
        self.log(f"\n🔄 FREQUENCY:")
        self.log(f"  • Data Collection: Hourly automated")
        self.log(f"  • Predictions: Every cycle")
        self.log(f"  • Dashboard Update: Real-time")
        self.log(f"\n🌐 ACCESS POINTS:")
        self.log(f"  • Streamlit Dashboard: http://localhost:8501")
        self.log(f"  • Flask API: http://localhost:5000")
        self.log(f"  • Database: MySQL airhealth_db")

def main():
    print("\n🎯 Starting AirHealth AI Data Flow Simulation...\n")
    simulator = DataFlowSimulator()
    simulator.run_simulation(num_cities=3)
    
    print("\n" + "=" * 60)
    print("💡 NEXT STEPS TO RUN ACTUAL PROJECT:")
    print("=" * 60)
    print("\n1. Install Dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. Initialize Database:")
    print("   mysql -u root -p < scripts/init_db.sql")
    print("\n3. Run Data Collection:")
    print("   python src/main_collector.py")
    print("\n4. Launch Dashboard:")
    print("   streamlit run ui/streamlit_app.py")
    print("\n5. Access at: http://localhost:8501")
    print("=" * 60)

if __name__ == '__main__':
    main()
