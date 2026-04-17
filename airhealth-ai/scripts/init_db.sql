-- Create Database
CREATE DATABASE IF NOT EXISTS airhealth_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE airhealth_db;

-- Cities Table
CREATE TABLE IF NOT EXISTS cities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    state VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    tier INT DEFAULT 2,
    country VARCHAR(50) DEFAULT 'India',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Raw AQI Data Table
CREATE TABLE IF NOT EXISTS aqi_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    aqi INT,
    pm25 FLOAT,
    pm10 FLOAT,
    no2 FLOAT,
    so2 FLOAT,
    co FLOAT,
    source VARCHAR(50),
    raw_json LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    INDEX idx_city_timestamp (city_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Raw Weather Data Table
CREATE TABLE IF NOT EXISTS weather_raw (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature FLOAT,
    humidity INT,
    wind_speed FLOAT,
    cloudiness INT,
    rain_1h FLOAT,
    pressure INT,
    visibility INT,
    source VARCHAR(50),
    raw_json LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    INDEX idx_city_timestamp (city_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Processed AQI Features Table
CREATE TABLE IF NOT EXISTS aqi_processed (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    date DATE NOT NULL,
    aqi_value INT,
    aqi_category VARCHAR(50),
    pollution_stress_index FLOAT,
    pm25_pm10_ratio FLOAT,
    data_quality_flag VARCHAR(50),
    data_points_count INT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    UNIQUE KEY unique_city_date (city_id, date),
    INDEX idx_city_date (city_id, date),
    INDEX idx_aqi_category (aqi_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Processed Weather Features Table
CREATE TABLE IF NOT EXISTS weather_processed (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    date DATE NOT NULL,
    avg_temperature FLOAT,
    avg_humidity INT,
    avg_wind_speed FLOAT,
    temperature_humidity_index FLOAT,
    wind_stress_category VARCHAR(50),
    heat_index FLOAT,
    data_points_count INT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    UNIQUE KEY unique_city_date (city_id, date),
    INDEX idx_city_date (city_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Combined Risk Features Table
CREATE TABLE IF NOT EXISTS risk_features (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    date DATE NOT NULL,
    air_quality_weather_compound_risk FLOAT,
    respiratory_stress_factor FLOAT,
    combined_risk_score FLOAT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    UNIQUE KEY unique_city_date (city_id, date),
    INDEX idx_city_date (city_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Risk Predictions Table
CREATE TABLE IF NOT EXISTS risk_predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    prediction_date DATE NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    confidence_score FLOAT NOT NULL,
    model_version VARCHAR(50),
    prediction_features LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    UNIQUE KEY unique_city_date (city_id, prediction_date),
    INDEX idx_city_date (city_id, prediction_date),
    INDEX idx_risk_level (risk_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Health Recommendations Table
CREATE TABLE IF NOT EXISTS recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    recommendation_date DATE NOT NULL,
    risk_level VARCHAR(50),
    general_advice TEXT,
    sensitive_groups_advice TEXT,
    activity_level VARCHAR(50),
    precautions LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    UNIQUE KEY unique_city_date (city_id, recommendation_date),
    INDEX idx_city_date (city_id, recommendation_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AQI Forecasts Table (for Phase 3 - Prophet)
CREATE TABLE IF NOT EXISTS aqi_forecasts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_id INT NOT NULL,
    forecast_date DATE NOT NULL,
    forecast_aqi FLOAT,
    forecast_lower_bound FLOAT,
    forecast_upper_bound FLOAT,
    forecast_confidence FLOAT,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    INDEX idx_city_date (city_id, forecast_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Performance Metrics Table
CREATE TABLE IF NOT EXISTS model_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_version VARCHAR(50) NOT NULL UNIQUE,
    model_type VARCHAR(50),
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    auc_score FLOAT,
    training_date DATETIME,
    test_data_size INT,
    features_count INT,
    training_duration_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_version (model_version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert Initial Cities Data
INSERT IGNORE INTO cities (id, name, state, latitude, longitude, tier, country) VALUES
(1, 'Delhi', 'Delhi', 28.7041, 77.1025, 1, 'India'),
(2, 'Mumbai', 'Maharashtra', 19.0760, 72.8777, 1, 'India'),
(3, 'Bangalore', 'Karnataka', 12.9716, 77.5946, 1, 'India'),
(4, 'Hyderabad', 'Telangana', 17.3850, 78.4867, 1, 'India'),
(5, 'Chennai', 'Tamil Nadu', 13.0827, 80.2707, 1, 'India'),
(6, 'Kolkata', 'West Bengal', 22.5726, 88.3639, 1, 'India'),
(7, 'Pune', 'Maharashtra', 18.5204, 73.8567, 2, 'India'),
(8, 'Ahmedabad', 'Gujarat', 23.0225, 72.5714, 2, 'India'),
(9, 'Jaipur', 'Rajasthan', 26.9124, 75.7873, 2, 'India'),
(10, 'Lucknow', 'Uttar Pradesh', 26.8467, 80.9462, 2, 'India'),
(11, 'Kanpur', 'Uttar Pradesh', 26.4499, 80.3319, 2, 'India'),
(12, 'Surat', 'Gujarat', 21.1458, 72.8336, 2, 'India'),
(13, 'Varanasi', 'Uttar Pradesh', 25.3200, 82.9850, 2, 'India'),
(14, 'Nagpur', 'Maharashtra', 21.1314, 79.0855, 2, 'India'),
(15, 'Indore', 'Madhya Pradesh', 22.7196, 75.8577, 2, 'India'),
(16, 'Bhopal', 'Madhya Pradesh', 23.1815, 79.9864, 2, 'India'),
(17, 'Visakhapatnam', 'Andhra Pradesh', 17.6869, 83.2185, 2, 'India'),
(18, 'Patna', 'Bihar', 25.5941, 85.1376, 2, 'India'),
(19, 'Vadodara', 'Gujarat', 22.3072, 73.1812, 2, 'India'),
(20, 'Ghaziabad', 'Uttar Pradesh', 28.6692, 77.4538, 2, 'India'),
(21, 'Ludhiana', 'Punjab', 30.9010, 75.8573, 2, 'India'),
(22, 'Agra', 'Uttar Pradesh', 27.1767, 78.0081, 2, 'India'),
(23, 'Nashik', 'Maharashtra', 19.9975, 73.7898, 2, 'India'),
(24, 'Aurangabad', 'Maharashtra', 19.8762, 75.3433, 2, 'India'),
(25, 'Ranchi', 'Jharkhand', 23.3441, 85.3096, 2, 'India'),
(26, 'Coimbatore', 'Tamil Nadu', 11.0081, 76.9124, 2, 'India'),
(27, 'Madurai', 'Tamil Nadu', 9.9185, 78.1198, 2, 'India'),
(28, 'Kochi', 'Kerala', 9.9312, 76.2673, 2, 'India'),
(29, 'Thiruvananthapuram', 'Kerala', 8.5241, 76.9366, 2, 'India'),
(30, 'Allahabad', 'Uttar Pradesh', 25.4358, 81.8463, 2, 'India');

-- Create logging table for data collection operations
CREATE TABLE IF NOT EXISTS collection_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    collection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    cities_attempted INT,
    cities_successful INT,
    cities_failed INT,
    error_message LONGTEXT,
    duration_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_collection_date (collection_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
