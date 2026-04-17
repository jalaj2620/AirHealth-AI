# AirHealth AI - Windows Setup Guide (No Docker)

## ⚡ Quick Setup (10 Minutes)

### Step 1: Download & Install Prerequisites

**Python 3.10+**
- Download: https://www.python.org/downloads/
- During installation: ✅ Check "Add Python to PATH"
- Verify: Open PowerShell and run `python --version`

**MySQL Server**
- Download: https://dev.mysql.com/downloads/mysql/
- Choose "MySQL Server 8.0" → Windows (x86, 64-bit)
- During installation: Remember your password!
- Verify: Open MySQL Command Line Client and login

**OpenWeatherMap API Key** (Free)
- Go to: https://openweathermap.org/api
- Sign up for free account
- Get API key from your account dashboard
- Copy this key for later

---

### Step 2: Navigate to Project Folder

Open PowerShell and run:
```powershell
cd "d:\PYTHON .DA projets\New folder\airhealth-ai"
```

---

### Step 3: Create Python Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of each PowerShell line.

---

### Step 4: Install Python Libraries

```powershell
pip install -r requirements.txt
```

This takes ~2-3 minutes. Wait for it to complete.

---

### Step 5: Configure Your API Key & Database

```powershell
copy config\.env.template config\.env
```

Open `config\.env` with Notepad and update these lines:

```
OPENWEATHERMAP_API_KEY=your_key_from_openweathermap
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_from_installation
```

Save the file.

---

### Step 6: Initialize Database

Ensure MySQL is running (check Windows Services or MySQL Workbench).

In PowerShell:
```powershell
mysql -u root -p < scripts/init_db.sql
```

When prompted, enter your MySQL password. This creates the database and loads 30 cities.

---

### Step 7: Test Everything Works

```powershell
# Test database connection
python -c "from src.utils.db import get_connection; db = get_connection(); print('✓ DB OK' if db.connect() else '✗ DB Failed')"

# Fetch real data from APIs (takes ~30 seconds)
python src/main_collector.py

# Process features
python -c "from src.processors.feature_engineer import FeatureEngineer; FeatureEngineer().process_all_features()"
```

---

### Step 8: Launch Dashboard

```powershell
streamlit run ui/streamlit_app.py
```

Browser will automatically open to **http://localhost:8501**

If not, manually open that URL in your browser.

---

## ✅ You're Done!

The dashboard is live! You should see:
- 30 Indian cities in the dropdown
- Current AQI values
- Temperature and weather info
- Health risk predictions
- 30-day trend chart

---

## 🔄 Daily Usage

Every day, run these commands (in order) in PowerShell:

```powershell
# Activate environment
venv\Scripts\activate

# Collect fresh data
python src/main_collector.py

# Process features
python -c "from src.processors.feature_engineer import FeatureEngineer; FeatureEngineer().process_all_features()"

# Generate predictions
python -c "from src.models.inference import InferencePipeline; InferencePipeline().generate_predictions()"

# Generate recommendations
python -c "from src.engine.recommendations import RecommendationEngine; RecommendationEngine().generate_for_all_cities()"

# Start dashboard
streamlit run ui/streamlit_app.py
```

Or create a `.bat` file (`run_all.bat`) with these commands and run it daily.

---

## 🆘 Common Issues

**"Python command not found"**
- Ensure Python is in PATH (reinstall with "Add to PATH" checked)

**"MySQL connection error"**
- Ensure MySQL Server is running (Windows Services → MySQL80)
- Check DB credentials in `config\.env`

**"ModuleNotFoundError"**
- Ensure virtual environment is activated: `venv\Scripts\activate`
- Reinstall requirements: `pip install -r requirements.txt`

**"Port 8501 already in use"**
- change port: `streamlit run ui/streamlit_app.py --server.port 8502`

**"No data in dashboard"**
- Run `python src/main_collector.py` first
- Wait for it to complete
- Refresh browser

---

## 📚 API Server (Optional)

To run the REST API in a second PowerShell:

```powershell
venv\Scripts\activate
python api/flask_server.py
```

Then access: http://localhost:5000/api/health

---

## 🎯 Full Documentation

See full details in:
- `README.md` - Complete architecture and features
- `scripts/START_HERE.md` - Generic quick reference

Let me know if issues come up!
