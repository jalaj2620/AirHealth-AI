# AirHealth AI - Quick Start Guide (Local Setup)

## 📋 Prerequisites
- **Python 3.10+** (download from https://www.python.org/)
- **MySQL Server** (download from https://dev.mysql.com/downloads/mysql/)
- **OpenWeatherMap API Key** (free account at https://openweathermap.org/api)

---

## 🚀 Setup Steps (5 Minutes)

### Step 1: Clone/Navigate to Project
```bash
cd "d:\PYTHON .DA projets\New folder\airhealth-ai"
```

### Step 2: Create Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy template to .env
copy config\.env.template config\.env

# Edit config\.env with your OpenWeatherMap API key:
# OPENWEATHERMAP_API_KEY=your_key_here
# DB_HOST=localhost
# DB_USER=root  (or your MySQL username)
# DB_PASSWORD=your_mysql_password
```

### Step 5: Initialize MySQL Database
```bash
# First, make sure MySQL Server is running

# Then initialize the database:
mysql -u root -p < scripts/init_db.sql

# You will be prompted for your MySQL password
# This creates the airhealth_db database and 30 cities
```

### Step 6: Test Database Connection
```bash
python -c "from src.utils.db import get_connection; db = get_connection(); print('✓ Database Connected!' if db.connect() else '✗ Connection Failed')"
```

### Step 7: Run Data Collection (Test)
```bash
python src/main_collector.py
# Wait ~30 seconds. You should see data being fetched for all 30 cities
```

### Step 8: Process Features
```bash
python -c "from src.processors.feature_engineer import FeatureEngineer; FeatureEngineer().process_all_features()"
```

### Step 9: Launch Dashboard
```bash
streamlit run ui/streamlit_app.py
```

**Access:** Open your browser to **http://localhost:8501**

## Verify Setup
- [ ] MySQL running (check `docker-compose ps`)
- [ ] Cities table populated (30 cities loaded)
- [ ] API keys configured in `.env`
- [ ] Python environment activated
- [ ] Dependencies installed (pip list | grep streamlit)

## Next Steps
1. Update API keys in config/.env (OpenWeatherMap required; OpenAQ is free/no-auth)
2. Test data collectors: `python src/collectors/aqi_collector.py`
3. Run daily batch job: `python src/main_collector.py`
4. Launch Streamlit UI: `streamlit run ui/streamlit_app.py`
