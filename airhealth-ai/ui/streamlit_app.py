"""
Streamlit MVP Dashboard for AirHealth AI
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from src.utils.db import get_connection

# Page configuration
st.set_page_config(
    page_title="AirHealth AI - Air Quality & Health Risk Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .safe { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .moderate { background: linear-gradient(135deg, #fa7e1e 0%, #fbb034 100%); }
    .dangerous { background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%); }
    .hazardous { background: linear-gradient(135deg, #8b0000 0%, #d32f2f 100%); }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_connection():
    """Get cached database connection"""
    return get_connection()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_cities():
    """Load city list from database"""
    db = get_db_connection()
    cities = db.get_all_cities()
    return {f"{city['name']} ({city['state']})": city['id'] for city in cities}


@st.cache_data(ttl=300)
def load_current_data(city_id: int):
    """Load current metrics for a city"""
    db = get_db_connection()
    
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
    SELECT general_advice, sensitive_groups_advice, activity_level, precautions, recommendation_date
    FROM recommendations
    WHERE city_id = %s
    ORDER BY recommendation_date DESC LIMIT 1
    """
    recommendation = db.fetch_one(rec_query, (city_id,))
    
    return aqi, weather, prediction, recommendation


@st.cache_data(ttl=300)
def load_historical_data(city_id: int, days: int = 30):
    """Load historical AQI data for charting"""
    db = get_db_connection()
    
    query = """
    SELECT DATE(date) as date, aqi_value, aqi_category
    FROM aqi_processed
    WHERE city_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
    ORDER BY date ASC
    """
    
    results = db.fetch_query(query, (city_id, days))
    return pd.DataFrame(results) if results else pd.DataFrame()


def get_risk_color(risk_level: str) -> str:
    """Get color code for risk level"""
    colors = {
        'Safe': '#43e97b',
        'Moderate': '#fa7e1e',
        'Dangerous': '#f857a6',
        'Hazardous': '#8b0000'
    }
    return colors.get(risk_level, '#667eea')


def get_aqi_color(aqi: int) -> str:
    """Get color code for AQI value"""
    if aqi <= 50:
        return '#43e97b'
    elif aqi <= 100:
        return '#ffd700'
    elif aqi <= 200:
        return '#fa7e1e'
    else:
        return '#d32f2f'


# Main title
st.title("🌍 AirHealth AI - Air Quality & Health Risk Dashboard")
st.markdown("Real-time air quality monitoring and health risk assessment for Indian cities")

# Sidebar
st.sidebar.markdown("## 📍 City Selection")
city_name = st.sidebar.selectbox(
    "Select a city to analyze:",
    options=load_cities().keys(),
    index=0
)
city_id = load_cities()[city_name]

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About This Dashboard")
st.sidebar.markdown("""
**AirHealth AI** combines:
- Real-time air quality data from OpenAQ
- Weather forecasts from OpenWeatherMap
- Machine learning risk classification
- Personalized health recommendations

**Data Updates:** Daily (6 AM UTC)

**Cities Covered:** 30 major Indian cities
""")

# Load data
aqi_data, weather_data, prediction_data, recommendation_data = load_current_data(city_id)
historical_df = load_historical_data(city_id, 30)

# Main metrics row
col1, col2, col3, col4 = st.columns(4)

if aqi_data:
    with col1:
        st.metric(
            "🌫️ Current AQI",
            f"{aqi_data['aqi_value']}",
            f"({aqi_data['aqi_category']})"
        )
else:
    with col1:
        st.metric("🌫️ Current AQI", "No Data")

if weather_data:
    with col2:
        st.metric(
            "🌡️ Temperature",
            f"{weather_data['temperature']:.1f}°C",
            f"Humidity: {weather_data['humidity']:.0f}%"
        )
else:
    with col2:
        st.metric("🌡️ Temperature", "No Data")

if prediction_data:
    with col3:
        risk_level = prediction_data['risk_level']
        confidence = prediction_data['confidence_score']
        st.metric(
            "⚠️ Health Risk",
            risk_level,
            f"Confidence: {confidence:.1%}"
        )
else:
    with col3:
        st.metric("⚠️ Health Risk", "No Prediction")

if weather_data:
    with col4:
        st.metric(
            "💨 Wind Speed",
            f"{weather_data['wind_speed']:.1f} m/s",
            "Good for dispersion" if weather_data['wind_speed'] > 3 else "Stagnation risk"
        )
else:
    with col4:
        st.metric("💨 Wind Speed", "No Data")

# Risk visualization and recommendations
st.markdown("---")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("30-Day AQI Trend")
    
    if not historical_df.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=historical_df['date'],
            y=historical_df['aqi_value'],
            mode='lines+markers',
            line=dict(color='#667eea', width=2),
            marker=dict(size=6),
            name='AQI Value'
        ))
        
        # Add risk level zones
        fig.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="Safe", annotation_position="right")
        fig.add_hline(y=100, line_dash="dash", line_color="orange", annotation_text="Moderate", annotation_position="right")
        fig.add_hline(y=200, line_dash="dash", line_color="red", annotation_text="Dangerous", annotation_position="right")
        
        fig.update_layout(
            title="Air Quality Index",
            xaxis_title="Date",
            yaxis_title="AQI",
            hovermode="x unified",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No historical data available yet. Check back after first data collection.")

with right_col:
    st.subheader("Health Risk Status")
    
    if prediction_data:
        risk_level = prediction_data['risk_level']
        confidence = prediction_data['confidence_score']
        
        # Display risk level with color
        color = get_risk_color(risk_level)
        st.markdown(f"""
        <div style="background-color: {color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2>{risk_level}</h2>
            <p>Confidence: {confidence:.1%}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("⏳ Awaiting risk prediction...")

# Recommendations section
st.markdown("---")
st.subheader("💡 Health Recommendations")

if recommendation_data:
    rec1, rec2 = st.columns(2)
    
    with rec1:
        st.info(f"**General Population:** {recommendation_data['general_advice']}")
    
    with rec2:
        st.warning(f"**Sensitive Groups:** {recommendation_data['sensitive_groups_advice']}")
    
    # Precautions if applicable
    if recommendation_data['precautions']:
        try:
            precautions = json.loads(recommendation_data['precautions']) if isinstance(recommendation_data['precautions'], str) else recommendation_data['precautions']
            if precautions:
                st.markdown("**Recommended Precautions:**")
                for precaution in precautions:
                    st.write(f"- {precaution}")
        except:
            pass
else:
    st.info("No recommendations generated yet. Check back after first run.")

# Feature breakdown
st.markdown("---")
st.subheader("🔬 Air Quality & Weather Analysis")

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.markdown("### Air Quality Metrics")
    if aqi_data:
        st.write(f"**AQI Category:** {aqi_data['aqi_category']}")
        st.write(f"**Pollution Stress Index:** {aqi_data['pollution_stress_index']:.2f}" if aqi_data.get('pollution_stress_index') else "N/A")
    else:
        st.info("No AQI data available")

with metric_col2:
    st.markdown("### Weather Impact")
    if weather_data:
        st.write(f"**Temperature:** {weather_data['temperature']:.1f}°C")
        st.write(f"**Humidity:** {weather_data['humidity']:.0f}%")
        st.write(f"**Wind Speed:** {weather_data['wind_speed']:.1f} m/s")
    else:
        st.info("No weather data available")

with metric_col3:
    st.markdown("### Risk Factors")
    if prediction_data:
        st.write(f"**Overall Risk:** {prediction_data['risk_level']}")
        st.write(f"**Model Confidence:** {prediction_data['confidence_score']:.1%}")
    else:
        st.info("Prediction pending")

# Last update
st.markdown("---")
last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
st.caption(f"Dashboard updated: {last_update} | Data source: OpenAQ, OpenWeatherMap | ML Model: XGBoost v1")
