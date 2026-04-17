# AirHealth AI - Complete System Workflow

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    AirHealth AI System Flow                      │
└─────────────────────────────────────────────────────────────────┘

STEP 1: DATA COLLECTION (main_collector.py)
├─ Fetch AQI data from OpenAQ API
│  └─ Pollutants: PM2.5, PM10, NO2, SO2, CO
├─ Fetch Weather data from OpenWeatherMap API
│  └─ Metrics: Temperature, Humidity, Wind Speed, Etc.
└─ Store raw data in MySQL (aqi_raw, weather_raw tables)

STEP 2: DATA PROCESSING (feature_engineer.py)
├─ Calculate AQI Processed Features:
│  ├─ AQI Category (Good/Moderate/Unhealthy/Hazardous)
│  └─ Pollution Stress Index
├─ Calculate Weather Processed Features:
│  ├─ Heat Index
│  └─ Temperature-Humidity Index
└─ Store processed features in MySQL

STEP 3: RISK FEATURE ENGINEERING
├─ Combine Air Quality + Weather features
├─ Calculate respiratory stress factors
└─ Generate combined risk scores

STEP 4: ML PREDICTION (XGBoost Model)
├─ Input: Combined risk features
├─ Model: risk_predictions.pkl
├─ Output: Risk Level (Safe/Moderate/Dangerous)
└─ Store predictions in risk_predictions table

STEP 5: RECOMMENDATION ENGINE
├─ Apply health_risk_rules.json
├─ Generate personalized health advice
├─ Advice by population group (sensitive vs general)
└─ Store in recommendations table

STEP 6: VISUALIZATION (Streamlit Dashboard)
├─ Display current metrics by city
├─ Show 30-day trend graphs
├─ Risk level indicators with color coding
├─ Health recommendations
└─ API: http://localhost:8501
```

---

## 📊 KEY COMPONENTS

### 1. DATA COLLECTION MODULE
**File:** `src/main_collector.py`
**Process:**
- Collects data for 30 Indian cities
- Queries OpenAQ for AQI (Air Quality Index)
- Queries OpenWeatherMap for weather data
- Runs hourly/daily based on schedule
- Handles API failures with retry logic

**Database Storage:**
```
aqi_raw table:
├─ city_id, timestamp, aqi, pm25, pm10, no2, so2, co
└─ Indices: city_id, timestamp for fast queries

weather_raw table:
├─ city_id, timestamp, temperature, humidity, wind_speed
└─ Indices: city_id, timestamp for fast queries
```

### 2. FEATURE ENGINEERING MODULE
**File:** `src/processors/feature_engineer.py`
**Features Generated:**
- PM2.5 to PM10 ratio
- Pollution stress index
- Temperature-humidity index (THI)
- Heat index
- Wind stress category

**Processing Pipeline:**
```
Raw Data → Validation → Aggregation → Feature Calculation → Storage
```

### 3. ML MODEL
**File:** `src/models/risk_classifier.pkl`
**Model Type:** XGBoost Classifier
**Input Features:** 15 engineered features
**Output Classes:**
- Safe (Green) - AQI 0-50
- Moderate (Yellow) - AQI 51-100
- Unhealthy (Orange) - AQI 101-150
- Dangerous (Red) - AQI 151+

### 4. DATABASE STRUCTURE (11 Tables)
```
✓ cities              - 30 Indian cities
✓ aqi_raw            - Raw AQI measurements
✓ weather_raw        - Raw weather measurements
✓ aqi_processed      - Daily processed AQI features
✓ weather_processed  - Daily processed weather features
✓ risk_features      - Combined risk indicators
✓ risk_predictions   - ML model predictions
✓ recommendations    - Health advice by risk level
✓ aqi_forecasts      - 7-day AQI forecasts (Prophet)
✓ model_metrics      - Model performance metrics
✓ data_quality_logs  - Data ingestion logs
```

### 5. DASHBOARD (Streamlit)
**File:** `ui/streamlit_app.py`
**Features:**
- Real-time city selection
- Current metrics display
- 30-day trend charts
- Health risk color coding
- Personalized recommendations
- API server integration

---

## 🔄 DAILY EXECUTION FLOW

```
6:00 AM (UTC) → Run main_collector.py
    ↓
Collect AQI + Weather data for 30 cities
    ↓
Store in aqi_raw & weather_raw tables
    ↓
Feature engineer raw data
    ↓
Store in *_processed tables
    ↓
Generate combined risk features
    ↓
Run XGBoost predictions
    ↓
Store results in risk_predictions
    ↓
Generate health recommendations
    ↓
Update Streamlit dashboard
    ↓
Users access dashboard at http://localhost:8501
```

---

## 🚀 RUNNING THE PROJECT

### Phase 1: Setup Environment
```powershell
cd "d:\PYTHON .DA projets\New folder\airhealth-ai"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Phase 2: Configure
```powershell
# Create config\.env from template
copy config\.env.template config\.env

# Edit with:
# OPENWEATHERMAP_API_KEY=your_api_key_here
# DB_USER=root
# DB_PASSWORD=your_mysql_password
```

### Phase 3: Initialize Database
```powershell
# Ensure MySQL is running
mysql -u root -p < scripts/init_db.sql
```

### Phase 4: Run Data Collection
```powershell
python src/main_collector.py
```

### Phase 5: Launch Dashboard
```powershell
streamlit run ui/streamlit_app.py
```

Open browser: **http://localhost:8501**

---

## 📈 WHAT HAPPENS WHEN YOU RUN IT

```
STEP 1: main_collector.py executes:
  ✓ Connects to MySQL database
  ✓ Loads 30 cities from config/cities.json
  ✓ Fetches AQI from OpenAQ API
    → PM2.5, PM10, NO2, SO2, CO measurements
  ✓ Fetches Weather from OpenWeatherMap
    → Temperature, Humidity, Wind, Cloudiness
  ✓ Inserts raw data into aqi_raw & weather_raw

STEP 2: Feature engineering:
  ✓ Aggregates 24-hour data into daily metrics
  ✓ Calculates derived features
  ✓ Stores in aqi_processed & weather_processed

STEP 3: Risk prediction:
  ✓ Loads trained XGBoost model
  ✓ Scores combined risk features
  ✓ Generates risk levels by city

STEP 4: Generate recommendations:
  ✓ Applies health rules based on risk level
  ✓ Creates personalized advice
  ✓ Stores recommendations table

STEP 5: Dashboard display:
  ✓ Streamlit loads all data from MySQL
  ✓ Users select city from dropdown
  ✓ Shows:
    - Current AQI with color indicator
    - Current weather metrics
    - 30-day trending charts
    - Health recommendations
    - Population-specific advice
```

---

## 🎯 KEY FEATURES DEMONSTRATED

1. **Real-time Data Collection**
   - OpenAQ API integration
   - OpenWeatherMap integration
   - Automated scheduling

2. **Data Processing Pipeline**
   - Data validation
   - Feature engineering
   - Time-series aggregation

3. **Machine Learning**
   - XGBoost classifier
   - Risk prediction
   - Confidence scoring

4. **Rule-Based Recommendations**
   - Health risk thresholds
   - Population-specific advice
   - Activity restrictions

5. **Interactive Dashboard**
   - Multi-city support (30 cities)
   - Real-time metrics
   - Historical trends
   - Responsive design

---

## 📊 EXAMPLE DATA FLOW

**Input:** Single City (e.g., Delhi)

```json
{
  "city": "Delhi",
  "aqi": 185,
  "pm25": 120,
  "pm10": 250,
  "temperature": 28,
  "humidity": 65,
  "wind_speed": 5
}
```

**Processing:**
```
AQI 185 → Category: "Unhealthy"
PM25/PM10 Ratio: 0.48
Heat Index: 31°C
Risk Score: 78%
```

**Model Prediction:**
```
Risk Level: DANGEROUS
Confidence: 0.94
```

**Recommendations:**
```
General: Avoid outdoor activities
Sensitive Groups: Stay indoors
Wearing N95 masks recommended
```

---

## 🔧 CONFIGURATION FILES

**config/.env** - API Keys & Database
**config/cities.json** - 30 Indian cities with coordinates
**data/external/health_risk_rules.json** - Health thresholds
**models/risk_predictions.pkl** - Trained ML model

---

## ✅ SYSTEM STATUS

- Python Modules: 19
- Database Tables: 11
- Pre-loaded Cities: 30
- ML Model Type: XGBoost
- Dashboard Framework: Streamlit
- Database: MySQL 8.0

---

**Ready to run!** 🚀

Execute: `python src/main_collector.py` then `streamlit run ui/streamlit_app.py`
```
