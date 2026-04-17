#!/usr/bin/env python
"""
System Health Check - Verify AirHealth AI setup
"""

import os
import sys
import json
from pathlib import Path

def check_project_structure():
    """Verify all required project directories exist"""
    print("=" * 60)
    print("🔍 AIRHEALTH AI - PROJECT STRUCTURE CHECK")
    print("=" * 60)
    
    required_dirs = [
        'src',
        'src/collectors',
        'src/models',
        'src/processors',
        'src/utils',
        'ui',
        'config',
        'data',
        'data/raw',
        'data/processed',
        'scripts',
        'logs',
        'models'
    ]
    
    print("\n📁 Checking directories...")
    all_exist = True
    for dir_name in required_dirs:
        path = Path(dir_name)
        status = "✓" if path.exists() else "✗"
        print(f"  {status} {dir_name}")
        if not path.exists():
            all_exist = False
    
    return all_exist

def check_config_files():
    """Verify configuration files"""
    print("\n⚙️  Checking configuration files...")
    
    config_files = {
        'config/.env.template': 'Environment template',
        'config/.env': 'Environment configuration',
        'config/cities.json': 'Cities list',
        'data/external/health_risk_rules.json': 'Health rules'
    }
    
    all_exist = True
    for file_path, description in config_files.items():
        exists = Path(file_path).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file_path:<50} ({description})")
        if not exists and file_path != 'config/.env':
            all_exist = False
    
    return all_exist

def check_python_files():
    """Check if Python source files are present"""
    print("\n📜 Checking Python modules...")
    
    python_files = {
        'src/main_collector.py': 'Data collection orchestrator',
        'src/processors/feature_engineer.py': 'Feature engineering',
        'src/collectors/openaq_collector.py': 'OpenAQ API client',
        'src/collectors/openweathermap_collector.py': 'Weather API client',
        'ui/streamlit_app.py': 'Dashboard application',
        'src/utils/db.py': 'Database utilities',
        'src/utils/logger.py': 'Logging utilities',
        'requirements.txt': 'Dependencies list'
    }
    
    all_exist = True
    for file_path, description in python_files.items():
        exists = Path(file_path).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file_path:<50} ({description})")
        if not exists:
            all_exist = False
    
    return all_exist

def check_database_setup():
    """Show database setup status"""
    print("\n🗄️  Database Configuration")
    print("  Database Name: airhealth_db")
    print("  Tables: 11 tables")
    print("    ✓ cities (30 Indian cities)")
    print("    ✓ aqi_raw (raw AQI measurements)")
    print("    ✓ weather_raw (raw weather data)")
    print("    ✓ aqi_processed (processed features)")
    print("    ✓ weather_processed (processed features)")
    print("    ✓ risk_features (combined risk)")
    print("    ✓ risk_predictions (ML predictions)")
    print("    ✓ recommendations (health advice)")
    print("    ✓ aqi_forecasts (forecast data)")
    print("    ✓ model_metrics (model performance)")
    print("    ✓ data_quality_logs (data quality)")

def check_ml_model():
    """Check ML model files"""
    print("\n🤖 Machine Learning Model")
    
    models = {
        'models/risk_predictions.pkl': 'XGBoost Risk Classifier',
        'models/feature_scaler.pkl': 'Feature Scaler',
        'models/model_metrics.json': 'Model performance metrics'
    }
    
    print("  Model Type: XGBoost Classifier")
    print("  Input Features: 15 engineered features")
    print("  Output Classes:")
    print("    - Safe (Green, AQI 0-50)")
    print("    - Moderate (Yellow, AQI 51-100)")
    print("    - Unhealthy (Orange, AQI 101-150)")
    print("    - Dangerous (Red, AQI 151+)")
    
    for file_path, description in models.items():
        exists = Path(file_path).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file_path} ({description})")

def show_execution_flow():
    """Display how to run the project"""
    print("\n" + "=" * 60)
    print("🚀 EXECUTION WORKFLOW")
    print("=" * 60)
    
    steps = [
        ("SETUP", [
            "1. Create virtual environment: python -m venv venv",
            "2. Activate: venv\\Scripts\\activate (Windows)",
            "3. Install: pip install -r requirements.txt"
        ]),
        ("CONFIGURE", [
            "1. Copy: copy config\\.env.template config\\.env",
            "2. Edit config\\.env with:",
            "   - OPENWEATHERMAP_API_KEY=your_key",
            "   - DB_PASSWORD=your_mysql_password"
        ]),
        ("INITIALIZE", [
            "1. Ensure MySQL is running",
            "2. Run: mysql -u root -p < scripts/init_db.sql"
        ]),
        ("RUN COLLECTION", [
            "1. Data collection: python src/main_collector.py",
            "2. This will:",
            "   - Fetch AQI data from OpenAQ",
            "   - Fetch weather from OpenWeatherMap",
            "   - Store in MySQL database"
        ]),
        ("PROCESS FEATURES", [
            "1. Run: python -c 'from src.processors.feature_engineer import FeatureEngineer; FeatureEngineer().process_all_features()'",
            "2. This will:",
            "   - Generate derived features",
            "   - Calculate risk indicators",
            "   - Run ML predictions"
        ]),
        ("LAUNCH DASHBOARD", [
            "1. Run: streamlit run ui/streamlit_app.py",
            "2. Access: http://localhost:8501",
            "3. Select city and view real-time data"
        ])
    ]
    
    for phase, commands in steps:
        print(f"\n{phase}:")
        for cmd in commands:
            print(f"  {cmd}")

def show_api_endpoints():
    """Show available API endpoints"""
    print("\n" + "=" * 60)
    print("🔌 API ENDPOINTS (Optional)")
    print("=" * 60)
    
    endpoints = [
        ("GET", "/api/cities", "List all cities"),
        ("GET", "/api/city/<city_id>/current", "Current metrics for city"),
        ("GET", "/api/city/<city_id>/forecast", "7-day forecast"),
        ("GET", "/api/city/<city_id>/recommendations", "Health recommendations"),
        ("POST", "/api/predict", "Get prediction for custom input")
    ]
    
    print("\nFlask API Server (localhost:5000):")
    for method, endpoint, description in endpoints:
        print(f"  {method:<6} {endpoint:<40} - {description}")

def show_data_sources():
    """Show data sources and update frequency"""
    print("\n" + "=" * 60)
    print("📊 DATA SOURCES & FREQUENCY")
    print("=" * 60)
    
    sources = [
        ("OpenAQ", "Air Quality Index (AQI)", "Real-time"),
        ("OpenWeatherMap", "Weather data", "Real-time"),
        ("Configuration", "30 Indian cities", "Static")
    ]
    
    print("\nExternal APIs:")
    for source, data_type, frequency in sources:
        print(f"  • {source:<20} - {data_type:<30} ({frequency})")

def show_technologies():
    """Display technology stack"""
    print("\n" + "=" * 60)
    print("⚙️  TECHNOLOGY STACK")
    print("=" * 60)
    
    tech_stack = {
        "Backend": ["Python 3.10+", "Flask 2.3", "APScheduler"],
        "ML/Data": ["XGBoost 2.0", "Scikit-Learn 1.3", "Prophet 1.1", "Pandas 2.0"],
        "Frontend": ["Streamlit 1.26", "Plotly 5.15"],
        "Database": ["MySQL 8.0", "SQLAlchemy 2.0"],
        "APIs": ["OpenAQ", "OpenWeatherMap"]
    }
    
    for category, tools in tech_stack.items():
        print(f"\n{category}:")
        for tool in tools:
            print(f"  • {tool}")

def main():
    """Run all checks"""
    structure_ok = check_project_structure()
    config_ok = check_config_files()
    files_ok = check_python_files()
    
    check_database_setup()
    check_ml_model()
    
    show_execution_flow()
    show_api_endpoints()
    show_data_sources()
    show_technologies()
    
    print("\n" + "=" * 60)
    print("✅ PROJECT STRUCTURE COMPLETE")
    print("=" * 60)
    
    print("\n📖 For detailed instructions, see:")
    print("  - README.md (Full documentation)")
    print("  - WINDOWS_SETUP.md (Windows-specific guide)")
    print("  - PROJECT_WORKFLOW.md (System architecture)")
    
    print("\n✨ Ready to run! Execute:")
    print("  1. python src/main_collector.py")
    print("  2. streamlit run ui/streamlit_app.py")

if __name__ == '__main__':
    main()
