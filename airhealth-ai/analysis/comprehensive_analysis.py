"""
AirHealth AI - Comprehensive Data Analysis Module
==================================================
Generate comprehensive EDA, statistical analysis, and ML model evaluation reports.

Author: AirHealth AI Analytics Team
Version: 1.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
import json
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class AirHealthAnalyzer:
    """Comprehensive analyzer for AirHealth AI project."""
    
    def __init__(self, df):
        """Initialize analyzer with dataset."""
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns
        self.feature_cols = [col for col in self.numeric_cols if col not in ['AQI', 'Risk_Level']]
        self.models = {}
        self.results = {}
        
    def generate_statistical_summary(self):
        """Generate comprehensive statistical summary."""
        print("=" * 80)
        print("STATISTICAL SUMMARY")
        print("=" * 80)
        
        stats_summary = self.df[self.numeric_cols].describe().T
        stats_summary['skewness'] = [stats.skew(self.df[col].dropna()) for col in self.numeric_cols]
        stats_summary['kurtosis'] = [stats.kurtosis(self.df[col].dropna()) for col in self.numeric_cols]
        
        print("\n📊 Descriptive Statistics:")
        print(stats_summary.round(3))
        return stats_summary
    
    def analyze_data_quality(self):
        """Analyze data quality metrics."""
        print("\n" + "=" * 80)
        print("DATA QUALITY ASSESSMENT")
        print("=" * 80)
        
        missing_data = self.df.isnull().sum()
        missing_pct = (missing_data / len(self.df)) * 100
        data_quality = pd.DataFrame({
            'Missing_Count': missing_data,
            'Missing_Percentage': missing_pct,
            'Data_Type': self.df.dtypes
        })
        
        print("\n🔍 Data Quality Metrics:")
        print(data_quality[data_quality['Missing_Count'] > 0] if data_quality['Missing_Count'].sum() > 0 
              else "✓ No missing data detected")
        return data_quality
    
    def analyze_risk_distribution(self):
        """Analyze risk level distribution."""
        print("\n" + "=" * 80)
        print("RISK LEVEL DISTRIBUTION")
        print("=" * 80)
        
        risk_dist = self.df['Risk_Level'].value_counts().sort_index()
        risk_labels = {0: 'Low Risk', 1: 'Moderate Risk', 2: 'High Risk'}
        
        print("\n📈 Risk Distribution:")
        for level, count in risk_dist.items():
            pct = (count / len(self.df)) * 100
            print(f"  {risk_labels.get(level, f'Unknown (Level {level})')}: {count:5} ({pct:5.2f}%)")
        
        return risk_dist
    
    def analyze_cities(self):
        """Analyze city-wise statistics."""
        print("\n" + "=" * 80)
        print("CITY-WISE ANALYSIS")
        print("=" * 80)
        
        city_summary = self.df.groupby('city')[['AQI', 'PM25', 'Temperature', 'Humidity']].agg(
            ['mean', 'std', 'min', 'max']
        )
        
        print("\n🏙️ City-wise Statistics:")
        print(city_summary.round(2))
        
        # City rankings by AQI
        print("\n🎯 Cities By Average AQI (Highest to Lowest):")
        city_aqi = self.df.groupby('city')['AQI'].mean().sort_values(ascending=False)
        for rank, (city, aqi) in enumerate(city_aqi.items(), 1):
            risk_indicator = '🔴' if aqi > 150 else '🟡' if aqi > 100 else '🟢'
            print(f"  {rank}. {risk_indicator} {city:15} : {aqi:6.1f}")
        
        return city_summary
    
    def correlation_analysis(self):
        """Perform correlation analysis."""
        print("\n" + "=" * 80)
        print("CORRELATION ANALYSIS")
        print("=" * 80)
        
        correlation_matrix = self.df[self.numeric_cols].corr()
        
        print("\n🔗 Top Correlations with AQI:")
        aqi_corr = correlation_matrix['AQI'].sort_values(ascending=False)
        for factor, corr_val in aqi_corr.items():
            if factor != 'AQI':
                strength = 'Strong' if abs(corr_val) > 0.7 else 'Moderate' if abs(corr_val) > 0.4 else 'Weak'
                direction = 'Positive' if corr_val > 0 else 'Negative'
                print(f"  {factor:15} : {corr_val:+.3f} ({strength} {direction})")
        
        return correlation_matrix
    
    def outlier_detection(self):
        """Detect outliers using IQR method."""
        print("\n" + "=" * 80)
        print("OUTLIER DETECTION (IQR Method)")
        print("=" * 80)
        
        outlier_summary = {}
        
        for col in ['AQI', 'PM25', 'PM10', 'Temperature']:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            outlier_summary[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(self.df)) * 100,
                'bounds': (lower_bound, upper_bound)
            }
        
        print("\n🎯 Outlier Summary:")
        for col, summary in outlier_summary.items():
            print(f"  {col:15}: {summary['count']:5} outliers ({summary['percentage']:5.2f}%)")
        
        return outlier_summary
    
    def train_models(self):
        """Train multiple ML models."""
        print("\n" + "=" * 80)
        print("TRAINING ML MODELS")
        print("=" * 80)
        
        try:
            # Prepare data
            X = self.df[self.feature_cols].fillna(self.df[self.feature_cols].mean())
            y = self.df['Risk_Level']
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            X_scaled = pd.DataFrame(X_scaled, columns=self.feature_cols)
            
            # Train-test split
            split_idx = int(0.8 * len(X))
            self.X_train, self.X_test = X_scaled[:split_idx], X_scaled[split_idx:]
            self.y_train, self.y_test = y[:split_idx], y[split_idx:]
            
            print(f"\n✓ Data prepared: {len(self.X_train)} train, {len(self.X_test)} test")
            
            # Models to train
            model_configs = {
                'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10),
                'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5),
                'Support Vector Machine': SVC(kernel='rbf', random_state=42, probability=True)
            }
            
            for model_name, model in model_configs.items():
                try:
                    print(f"\n🔧 Training {model_name}...")
                    model.fit(self.X_train, self.y_train)
                    self.models[model_name] = model
                    print(f"   ✓ {model_name} trained successfully")
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
        
        except Exception as e:
            print(f"❌ Error in model training: {str(e)}")
    
    def evaluate_models(self):
        """Evaluate trained models."""
        print("\n" + "=" * 80)
        print("MODEL EVALUATION")
        print("=" * 80)
        
        model_results = {}
        
        for model_name, model in self.models.items():
            try:
                print(f"\n📊 Evaluating {model_name}:")
                
                y_pred = model.predict(self.X_test)
                y_pred_proba = model.predict_proba(self.X_test)
                
                train_acc = model.score(self.X_train, self.y_train)
                test_acc = model.score(self.X_test, self.y_test)
                precision = precision_score(self.y_test, y_pred, average='weighted', zero_division=0)
                recall = recall_score(self.y_test, y_pred, average='weighted', zero_division=0)
                f1 = f1_score(self.y_test, y_pred, average='weighted', zero_division=0)
                
                # ROC-AUC for binary classification
                y_test_binary = (self.y_test > 1).astype(int)
                y_pred_proba_binary = y_pred_proba[:, -1]
                
                roc_auc = roc_auc_score(y_test_binary, y_pred_proba_binary) if len(np.unique(y_test_binary)) > 1 else None
                
                model_results[model_name] = {
                    'train_accuracy': train_acc,
                    'test_accuracy': test_acc,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'roc_auc': roc_auc,
                    'confusion_matrix': confusion_matrix(self.y_test, y_pred).tolist()
                }
                
                print(f"  Train Accuracy: {train_acc:.4f}")
                print(f"  Test Accuracy:  {test_acc:.4f}")
                print(f"  Precision:      {precision:.4f}")
                print(f"  Recall:         {recall:.4f}")
                print(f"  F1-Score:       {f1:.4f}")
                if roc_auc:
                    print(f"  ROC-AUC:        {roc_auc:.4f}")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
        
        self.results['models'] = model_results
        return model_results
    
    def feature_importance(self):
        """Extract feature importance from tree models."""
        print("\n" + "=" * 80)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("=" * 80)
        
        importance_data = {}
        
        for model_name in ['Random Forest', 'Gradient Boosting']:
            if model_name in self.models:
                model = self.models[model_name]
                importances = model.feature_importances_
                importance_data[model_name] = dict(zip(self.feature_cols, importances))
                
                print(f"\n🔍 Top Features - {model_name}:")
                sorted_features = sorted(importance_data[model_name].items(), 
                                       key=lambda x: x[1], reverse=True)
                for rank, (feature, importance) in enumerate(sorted_features[:5], 1):
                    bar = '█' * int(importance * 50)
                    print(f"  {rank}. {feature:15} {bar} {importance:.4f}")
        
        return importance_data
    
    def generate_report(self, output_file=None):
        """Generate comprehensive analysis report."""
        print("\n\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "AIRHEALTH AI - COMPREHENSIVE ANALYSIS REPORT" + " " * 14 + "║")
        print("╚" + "=" * 78 + "╝")
        
        # Run all analyses
        self.generate_statistical_summary()
        self.analyze_data_quality()
        self.analyze_risk_distribution()
        self.analyze_cities()
        self.correlation_analysis()
        self.outlier_detection()
        self.train_models()
        self.evaluate_models()
        self.feature_importance()
        
        # Final summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"✓ Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✓ Results exported to: {output_file}")


def main():
    """Main execution for standalone analysis."""
    print("AirHealth AI - Comprehensive Analysis Module")
    print("=" * 80)
    
    # Generate synthetic dataset
    np.random.seed(42)
    cities = ['Delhi', 'Mumbai', 'Bangalore', 'Pune', 'Chennai', 'Hyderabad', 'Kolkata', 'Jaipur']
    date_range = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    data_list = []
    for city in cities:
        city_data = pd.DataFrame({
            'city': city,
            'date': date_range,
            'AQI': np.random.normal(150, 50, len(date_range)).clip(0, 500),
            'PM25': np.random.exponential(35, len(date_range)),
            'PM10': np.random.exponential(60, len(date_range)),
            'NO2': np.random.gamma(2, 20, len(date_range)),
            'O3': np.random.gamma(2, 15, len(date_range)),
            'SO2': np.random.exponential(8, len(date_range)),
            'Temperature': np.random.normal(28, 8, len(date_range)),
            'Humidity': np.random.normal(65, 15, len(date_range)).clip(20, 95),
            'Pressure': np.random.normal(1013, 5, len(date_range)),
            'Wind_Speed': np.random.exponential(3, len(date_range)),
        })
        city_data['Risk_Level'] = pd.cut(city_data['AQI'], 
                                        bins=[0, 100, 150, 500], 
                                        labels=[0, 1, 2]).astype(int)
        data_list.append(city_data)
    
    df = pd.concat(data_list, ignore_index=True)
    
    # Run analysis
    analyzer = AirHealthAnalyzer(df)
    analyzer.generate_report(output_file='analysis_results.json')


if __name__ == "__main__":
    main()
