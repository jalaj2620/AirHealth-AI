"""
XGBoost model for health risk classification
"""
import logging
import json
import pickle
import os
from datetime import datetime
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from src.utils.db import get_connection
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger('risk_classifier')


class RiskClassifier:
    """Train and use XGBoost model for health risk classification"""
    
    RISK_CATEGORIES = ['Safe', 'Moderate', 'Dangerous']
    MODEL_DIR = os.path.join(os.path.dirname(__file__), '../../models')
    
    def __init__(self):
        self.db = get_connection()
        self.model = None
        self.label_encoder = None
        self.feature_columns = None
        self.model_version = Config.MODEL_VERSION
        self.scaler_params = {}
    
    def prepare_training_data(self) -> Optional[Tuple[pd.DataFrame, pd.Series]]:
        """
        Prepare training dataset from processed features in database
        
        Returns:
            Tuple of (features_df, labels_series) or None if insufficient data
        """
        logger.info("Preparing training data...")
        
        try:
            # Query to get processed features and create labels
            query = """
            SELECT 
                c.id as city_id,
                r.date,
                a.aqi_value,
                a.aqi_category,
                a.pollution_stress_index,
                a.pm25_pm10_ratio,
                w.avg_temperature,
                w.avg_humidity,
                w.avg_wind_speed,
                w.temperature_humidity_index,
                w.wind_stress_category,
                w.heat_index,
                rf.air_quality_weather_compound_risk,
                rf.respiratory_stress_factor
            FROM risk_features rf
            JOIN aqi_processed a ON rf.city_id = a.city_id AND rf.date = a.date
            JOIN weather_processed w ON rf.city_id = w.city_id AND rf.date = w.date
            JOIN cities c ON rf.city_id = c.id
            WHERE rf.date >= DATE_SUB(CURDATE(), INTERVAL 180 DAY)
            ORDER BY rf.date DESC
            LIMIT 1000
            """
            
            data = self.db.fetch_query(query)
            
            if not data:
                logger.warning("No training data available in database")
                return None
            
            df = pd.DataFrame(data)
            logger.info(f"Loaded {len(df)} training records")
            
            # Create risk labels based on domain rules (rule-based labeling)
            rules = Config.load_health_rules()
            thresholds = rules.get('thresholds', {})
            
            def assign_risk_label(row):
                aqi = row['aqi_value']
                thi = row['temperature_humidity_index']
                pollution_stress = row['pollution_stress_index']
                
                # Hazardous
                if aqi > thresholds.get('aqi_unhealthy_limit', 200):
                    return 'Dangerous'
                # Unhealthy
                elif aqi > thresholds.get('aqi_moderate_limit', 100) or (thi and thi > thresholds.get('thi_moderate_limit', 32)):
                    return 'Dangerous'
                # Moderate
                elif aqi > thresholds.get('aqi_safe_limit', 50) or (thi and thi > thresholds.get('thi_safe_limit', 28)):
                    return 'Moderate'
                # Safe
                else:
                    return 'Safe'
            
            df['risk_label'] = df.apply(assign_risk_label, axis=1)
            
            logger.info(f"Label distribution:\n{df['risk_label'].value_counts()}")
            
            # Select features for modeling
            feature_cols = [
                'aqi_value', 'pollution_stress_index', 'pm25_pm10_ratio',
                'avg_temperature', 'avg_humidity', 'avg_wind_speed',
                'temperature_humidity_index', 'heat_index',
                'air_quality_weather_compound_risk', 'respiratory_stress_factor'
            ]
            
            self.feature_columns = feature_cols
            
            # Handle missing values
            df[feature_cols] = df[feature_cols].fillna(df[feature_cols].mean())
            
            X = df[feature_cols]
            y = df['risk_label']
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return None
    
    def train_model(self, X: pd.DataFrame, y: pd.Series) -> bool:
        """
        Train XGBoost model
        
        Args:
            X: Feature matrix
            y: Target labels
        
        Returns:
            True if successful
        """
        logger.info("Training XGBoost model...")
        
        try:
            # Encode labels
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            logger.info(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")
            
            # Train model
            self.model = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.08,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=42,
                objective='multi:softprob',
                num_class=len(self.RISK_CATEGORIES)
            )
            
            self.model.fit(X_train, y_train, verbose=10)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            
            metrics = {
                'accuracy': float(accuracy_score(y_test, y_pred)),
                'precision': float(precision_score(y_test, y_pred, average='weighted')),
                'recall': float(recall_score(y_test, y_pred, average='weighted')),
                'f1': float(f1_score(y_test, y_pred, average='weighted'))
            }
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X, y_encoded, cv=5)
            
            logger.info("Model Performance:")
            logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
            logger.info(f"  Precision: {metrics['precision']:.4f}")
            logger.info(f"  Recall: {metrics['recall']:.4f}")
            logger.info(f"  F1-Score: {metrics['f1']:.4f}")
            logger.info(f"  CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
            
            # Save model
            self.save_model(metrics)
            
            # Log metrics to database
            self._log_metrics_to_db(metrics, len(X_test), len(self.feature_columns))
            
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def predict_risk_level(self, features: Dict[str, float]) -> Tuple[str, float]:
        """
        Predict health risk level for given features
        
        Args:
            features: Dict with feature values
        
        Returns:
            Tuple of (risk_level, confidence_score)
        """
        try:
            if self.model is None:
                self.load_model()
            
            # Prepare feature vector
            feature_vector = np.array([[features.get(col, 0) for col in self.feature_columns]])
            
            # Predict
            predictions = self.model.predict(feature_vector, verbose=0)
            probabilities = self.model.predict_proba(feature_vector, verbose=0)[0]
            
            # Get top prediction
            top_idx = np.argmax(predictions)
            risk_label = self.label_encoder.inverse_transform([top_idx])[0]
            confidence = float(probabilities[top_idx])
            
            return risk_label, confidence
            
        except Exception as e:
            logger.error(f"Error predicting risk level: {e}")
            return 'Moderate', 0.5  # Default to moderate if error
    
    def save_model(self, metrics: Dict = None):
        """Save trained model to disk"""
        try:
            os.makedirs(self.MODEL_DIR, exist_ok=True)
            
            model_path = os.path.join(self.MODEL_DIR, f'risk_classifier_{self.model_version}.pkl')
            
            model_data = {
                'model': self.model,
                'label_encoder': self.label_encoder,
                'feature_columns': self.feature_columns,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat(),
                'version': self.model_version
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, version: str = None) -> bool:
        """Load trained model from disk"""
        try:
            version = version or self.model_version
            model_path = os.path.join(self.MODEL_DIR, f'risk_classifier_{version}.pkl')
            
            if not os.path.exists(model_path):
                logger.warning(f"Model file not found: {model_path}")
                return False
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.feature_columns = model_data['feature_columns']
            
            logger.info(f"Model loaded from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def _log_metrics_to_db(self, metrics: Dict, test_size: int, features_count: int):
        """Log model metrics to database"""
        query = """
        INSERT INTO model_metrics 
        (model_version, model_type, accuracy, precision, recall, f1_score, training_date, test_data_size, features_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            self.model_version, 'XGBoost',
            metrics.get('accuracy'), metrics.get('precision'), 
            metrics.get('recall'), metrics.get('f1'),
            datetime.now(), test_size, features_count
        )
        self.db.execute_query(query, params)


def main():
    """Train model from command line"""
    classifier = RiskClassifier()
    
    # Prepare data
    result = classifier.prepare_training_data()
    if result:
        X, y = result
        classifier.train_model(X, y)
    else:
        logger.error("Failed to prepare training data")


if __name__ == '__main__':
    main()
