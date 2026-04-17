#!/usr/bin/env python
"""
AirHealth AI - Quick Start & Execution Guide
Run this after virtual environment is set up
"""

import os
import subprocess
import sys
from pathlib import Path

class ProjectExecutor:
    """Helper for running AirHealth AI project"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
        self.venv_pip = self.project_root / "venv" / "Scripts" / "pip.exe"
    
    def check_environment(self):
        """Verify environment is ready"""
        print("=" * 70)
        print("🔍 ENVIRONMENT VERIFICATION")
        print("=" * 70)
        
        checks = {
            "Virtual Environment": self.venv_python.exists(),
            "Requirements File": (self.project_root / "requirements.txt").exists(),
            "Config Template": (self.project_root / "config" / ".env.template").exists(),
            "Database Schema": (self.project_root / "scripts" / "init_db.sql").exists(),
            "Streamlit App": (self.project_root / "ui" / "streamlit_app.py").exists(),
            "Data Collector": (self.project_root / "src" / "main_collector.py").exists(),
        }
        
        all_good = True
        for check_name, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}")
            if not result:
                all_good = False
        
        return all_good
    
    def show_quick_start(self):
        """Show quick start instructions"""
        print("\n" + "=" * 70)
        print("🚀 QUICK START - 5 STEPS")
        print("=" * 70)
        
        steps = [
            ("CONFIG", "Edit config/.env with your API key and MySQL password"),
            ("INIT DB", "Run: mysql -u root -p < scripts/init_db.sql"),
            ("COLLECT", "Run: .\\venv\\Scripts\\python.exe src/main_collector.py"),
            ("FEATURES", "Run: .\\venv\\Scripts\\python.exe -m src.processors.feature_engineer"),
            ("DASHBOARD", "Run: .\\venv\\Scripts\\streamlit run ui/streamlit_app.py"),
        ]
        
        for i, (step, instruction) in enumerate(steps, 1):
            print(f"\n{i}. {step}")
            print(f"   → {instruction}")
        
        print("\n" + "=" * 70)
        print("⏱️  ESTIMATED TIME: 5 minutes setup + 1-2 minutes first data collection")
        print("=" * 70)
    
    def show_commands(self):
        """Show useful commands"""
        print("\n" + "=" * 70)
        print("📋 USEFUL COMMANDS")
        print("=" * 70)
        
        commands = {
            "Check Dependencies": ".\\venv\\Scripts\\python.exe -m pip show pandas",
            "List Installed Packages": ".\\venv\\Scripts\\python.exe -m pip list",
            "Run Health Check": ".\\venv\\Scripts\\python.exe health_check.py",
            "Run Simulation": ".\\venv\\Scripts\\python.exe simulate_workflow.py",
            "Run Collector": ".\\venv\\Scripts\\python.exe src/main_collector.py",
            "Process Features": ".\\venv\\Scripts\\python.exe -m src.processors.feature_engineer",
            "Start Dashboard": ".\\venv\\Scripts\\streamlit run ui/streamlit_app.py",
            "Start API Server": ".\\venv\\Scripts\\python.exe api/flask_server.py",
        }
        
        for desc, cmd in commands.items():
            print(f"\n{desc}:")
            print(f"  {cmd}")
    
    def show_database_info(self):
        """Show database setup info"""
        print("\n" + "=" * 70)
        print("🗄️  DATABASE SETUP")
        print("=" * 70)
        
        print("\n1. ENSURE MYSQL IS RUNNING")
        print("   Windows: Services → MySQL80 → Start")
        print("   Or: net start MySQL80")
        
        print("\n2. INITIALIZE DATABASE")
        print("   mysql -u root -p < scripts/init_db.sql")
        print("   (Enter your MySQL password when prompted)")
        
        print("\n3. VERIFY DATABASE")
        print("   mysql -u root -p")
        print("   > USE airhealth_db;")
        print("   > SHOW TABLES;")
        print("   (Should show 11 tables)")
    
    def show_api_info(self):
        """Show API information"""
        print("\n" + "=" * 70)
        print("🔌 API ENDPOINTS & ACCESS")
        print("=" * 70)
        
        print("\nSTREAMLIT DASHBOARD:")
        print("  URL: http://localhost:8501")
        print("  Command: .\\venv\\Scripts\\streamlit run ui/streamlit_app.py")
        print("  Features: Real-time metrics, 30-day trends, recommendations")
        
        print("\nFLASK API SERVER (Optional):")
        print("  URL: http://localhost:5000")
        print("  Command: .\\venv\\Scripts\\python.exe api/flask_server.py")
        print("  Endpoints:")
        print("    GET  /api/cities")
        print("    GET  /api/city/<id>/current")
        print("    GET  /api/city/<id>/forecast")
        print("    POST /api/predict")
        
        print("\nDATABASE:")
        print("  Host: localhost")
        print("  Port: 3306")
        print("  User: root")
        print("  Database: airhealth_db")
    
    def show_data_flow(self):
        """Show data flow diagram"""
        print("\n" + "=" * 70)
        print("📊 DATA FLOW DIAGRAM")
        print("=" * 70)
        
        flow = """
Step 1: Data Collection (30 seconds)
├─ OpenAQ API → Fetch AQI for 30 cities
├─ OpenWeatherMap API → Fetch weather
└─ Store in MySQL (aqi_raw, weather_raw)

Step 2: Feature Engineering (10 seconds)
├─ Calculate 15+ derived features
├─ Aggregate daily metrics
└─ Store in MySQL (*_processed tables)

Step 3: Risk Prediction (5 seconds)
├─ Load XGBoost model
├─ Score combined features
└─ Store predictions in MySQL

Step 4: Health Recommendations (2 seconds)
├─ Apply health risk rules
├─ Generate personalized advice
└─ Store in recommendations table

Step 5: Dashboard Update (Real-time)
├─ Streamlit loads data from MySQL
├─ User selects city
└─ Display metrics, trends, recommendations
        """
        print(flow)
    
    def show_troubleshooting(self):
        """Show troubleshooting guide"""
        print("\n" + "=" * 70)
        print("🔧 TROUBLESHOOTING")
        print("=" * 70)
        
        issues = {
            "venv not found": ".\\venv\\Scripts\\python.exe -m venv venv",
            "Packages won't install": ".\\venv\\Scripts\\python.exe -m pip install --upgrade pip",
            "MySQL not found": "Ensure MySQL Server 8.0 is installed and running",
            "API key errors": "Check OPENWEATHERMAP_API_KEY in config/.env",
            "Database permission denied": "Check DB_USER and DB_PASSWORD in config/.env",
            "Port 8501 already in use": "streamlit run ui/streamlit_app.py --server.port 8502",
        }
        
        for issue, solution in issues.items():
            print(f"\n❌ {issue}")
            print(f"   ✓ Solution: {solution}")
    
    def run(self):
        """Run all information displays"""
        # Check environment
        env_ok = self.check_environment()
        
        if not env_ok:
            print("\n⚠️  Some environment checks failed. Please set up the project first.")
            print("   Run: .\\venv\\Scripts\\python.exe -m pip install -r requirements.txt")
            return
        
        # Show guides
        self.show_quick_start()
        self.show_commands()
        self.show_database_info()
        self.show_api_info()
        self.show_data_flow()
        self.show_troubleshooting()
        
        # Final message
        print("\n" + "=" * 70)
        print("✅ ENVIRONMENT READY - YOU'RE ALL SET!")
        print("=" * 70)
        print("\n📖 NEXT STEPS:")
        print("   1. Edit config/.env with your settings")
        print("   2. Initialize MySQL database")
        print("   3. Run data collection:")
        print("      .\\venv\\Scripts\\python.exe src/main_collector.py")
        print("   4. Launch dashboard:")
        print("      .\\venv\\Scripts\\streamlit run ui/streamlit_app.py")
        print("   5. Access: http://localhost:8501")
        print("\n" + "=" * 70)

def main():
    executor = ProjectExecutor()
    executor.run()

if __name__ == '__main__':
    main()
