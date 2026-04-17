#!/bin/bash
# AirHealth AI - Complete Setup Script for Linux/Mac

set -e

echo "🌍 AirHealth AI - Automated Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.10+"; exit 1; }

# Create virtual environment
echo "✓ Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "✓ Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Copy environment template
echo "✓ Setting up environment configuration..."
if [ ! -f config/.env ]; then
    cp config/.env.template config/.env
    echo "⚠️  IMPORTANT: Edit config/.env and add your OPENWEATHERMAP_API_KEY"
else
    echo "✓ config/.env already exists"
fi

echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit config/.env with your OpenWeatherMap API key (https://openweathermap.org/api)"
echo "2. Start MySQL Server (via Homebrew or system package manager)"
echo "3. Initialize database: mysql -u root -p < scripts/init_db.sql"
echo "4. Run data collector: python src/main_collector.py"
echo "5. Start Streamlit: streamlit run ui/streamlit_app.py"
echo ""
echo "For detailed help, see: scripts/START_HERE.md"
