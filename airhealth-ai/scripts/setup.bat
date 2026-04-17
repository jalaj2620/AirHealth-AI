@echo off
REM AirHealth AI - Complete Setup Script for Windows

echo.
echo 🌍 AirHealth AI - Automated Setup Script (Windows)
echo ====================================================
echo.

REM Check Python
echo ✓ Checking Python version...
python --version >nul 2>&1 || (
    echo ❌ Python not found. Please install Python 3.10+
    exit /b 1
)

REM Create virtual environment
echo ✓ Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo ✓ Installing Python dependencies...
pip install --no-cache-dir -r requirements.txt

REM Copy environment template
echo ✓ Setting up environment configuration...
if not exist "config\.env" (
    copy config\.env.template config\.env
    echo ⚠️  IMPORTANT: Edit config\.env and add your OPENWEATHERMAP_API_KEY
) else (
    echo ✓ config\.env already exists
)

echo.
echo ✅ Setup Complete!
echo.
echo Next steps:
echo 1. Edit config\.env with your OpenWeatherMap API key (https://openweathermap.org/api)
echo 2. Start MySQL Server (Windows Services or MySQL Workbench)
echo 3. Initialize database: mysql -u root -p less than scripts\init_db.sql
echo 4. Run data collector: python src\main_collector.py
echo 5. Start Streamlit: streamlit run ui\streamlit_app.py
echo.
echo For detailed help, see: scripts\START_HERE.md
echo.
pause
