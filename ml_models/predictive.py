#!/usr/bin/env python3
"""
Predictive Models for Hiring Trend Forecasting
Time series analysis and trend prediction for job market intelligence
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta
import joblib
from collections import defaultdict

class HiringTrendPredictor:
    """Predict future hiring trends using time series analysis and ML"""
    
    def __init__(self):
        self.models = {
            'volume': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'urgency': RandomForestRegressor(n_estimators=100, random_state=42),
            'tech_adoption': LinearRegression()
        }
        self.scalers = {
            'volume': StandardScaler(),
            'urgency': StandardScaler(),
            'tech_adoption': StandardScaler()
        }
        self.is_fitted = False
        self.feature_names = []
        
    def _prepare_time_series_data(self, jobs: List[Dict]) -> pd.DataFrame:
        """Convert job data into time series format"""
        # Convert job data to DataFrame
        job_records = []
        
        for job in jobs:
            scraped_date = job.get('scraped_date', '')
            
            # Parse date (handle different formats)
            try:
                if '-' in scraped_date:
                    date = datetime.strptime(scraped_date.split()[0], '%Y-%m-%d')
                else:
                    date = datetime.now()  # Fallback to current date
            except:
                date = datetime.now()
            
            record = {
                'date': date,
                'company': job.get('company', 'Unknown'),
                'urgency_score': 1 if job.get('urgent_hiring_language', []) else 0,
                'tech_count': len(job.get('technology_adoption', [])),
                'pain_points_count': len(job.get('pain_points', [])),
                'has_salary': 1 if job.get('budget_signals', {}).get('salary_ranges', []) else 0,
                'description_length': len(job.get('description', '')),
                'department': job.get('department', 'Unknown')
            }
            job_records.append(record)
        
        return pd.DataFrame(job_records)
    
    def _create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features for prediction"""
        df = df.copy()
        
        # Sort by date
        df = df.sort_values('date')
        
        # Create time-based features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_year'] = df['date'].dt.dayofyear
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        # Create rolling averages (7-day windows)
        df['volume_7d'] = df.groupby('company').size().rolling(window=7, min_periods=1).mean()
        df['urgency_7d'] = df.groupby('company')['urgency_score'].rolling(window=7, min_periods=1).mean()
        df['tech_adoption_7d'] = df.groupby('company')['tech_count'].rolling(window=7, min_periods=1).mean()
        
        # Lag features (previous week's data)
        df['volume_lag1'] = df.groupby('company').size().shift(1)
        df['urgency_lag1'] = df.groupby('company')['urgency_score'].shift(1)
        df['tech_lag1'] = df.groupby('company')['tech_count'].shift(1)
        
        # Fill NaN values
        df = df.fillna(df.mean())
        
        return df
    
    def _aggregate_daily_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate job data by day for time series analysis"""
        daily_agg = df.groupby(df['date'].dt.date).agg({
            'company': 'count',  # Total jobs per day
            'urgency_score': 'mean',  # Average urgency
            'tech_count': 'mean',  # Average tech mentions
            'pain_points_count': 'mean',
            'has_salary': 'mean',
            'description_length': 'mean'
        }).reset_index()
        
        daily_agg.columns = ['date', 'job_volume', 'avg_urgency', 'avg_tech_adoption', 
                           'avg_pain_points', 'salary_transparency', 'avg_desc_length']
        
        # Convert date back to datetime
        daily_agg['date'] = pd.to_datetime(daily_agg['date'])
        
        return daily_agg
    
    def fit(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Train predictive models on historical job data"""
        if len(jobs) < 10:
            return {'error': 'Insufficient data for training (minimum 10 jobs required)'}
        
        # Prepare data
        df = self._prepare_time_series_data(jobs)
        daily_df = self._aggregate_daily_data(df)
        
        if len(daily_df) < 3:
            return {'error': 'Insufficient time series data (minimum 3 days required)'}
        
        # Create features
        daily_df = self._create_time_features(daily_df)
        
        # Prepare feature matrix
        feature_cols = ['year', 'month', 'day_of_year', 'week_of_year', 
                       'avg_tech_adoption', 'avg_pain_points', 'salary_transparency', 'avg_desc_length']
        
        X = daily_df[feature_cols].values
        self.feature_names = feature_cols
        
        # Prepare targets
        targets = {
            'volume': daily_df['job_volume'].values,
            'urgency': daily_df['avg_urgency'].values,
            'tech_adoption': daily_df['avg_tech_adoption'].values
        }
        
        results = {}
        
        # Train each model
        for model_name, model in self.models.items():
            y = targets[model_name]
            
            # Scale features
            X_scaled = self.scalers[model_name].fit_transform(X)
            
            # Train model
            model.fit(X_scaled, y)
            
            # Evaluate (using training data for simplicity)
            y_pred = model.predict(X_scaled)
            
            results[model_name] = {
                'mae': mean_absolute_error(y, y_pred),
                'mse': mean_squared_error(y, y_pred),
                'r2': r2_score(y, y_pred)
            }
        
        self.is_fitted = True
        
        results['training_summary'] = {
            'n_days': len(daily_df),
            'n_jobs': len(jobs),
            'date_range': f"{daily_df['date'].min()} to {daily_df['date'].max()}"
        }
        
        return results
    
    def predict_trends(self, days_ahead: int = 7) -> Dict[str, List[float]]:
        """Predict hiring trends for the next N days"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Generate future dates
        current_date = datetime.now()
        future_dates = [current_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
        
        predictions = {
            'dates': [date.strftime('%Y-%m-%d') for date in future_dates],
            'volume': [],
            'urgency': [],
            'tech_adoption': []
        }
        
        for date in future_dates:
            # Create features for future date
            features = np.array([
                date.year,
                date.month,
                date.timetuple().tm_yday,  # day of year
                date.isocalendar()[1],     # week of year
                5.0,  # avg_tech_adoption (baseline)
                1.5,  # avg_pain_points (baseline)
                0.3,  # salary_transparency (baseline)
                2000  # avg_desc_length (baseline)
            ]).reshape(1, -1)
            
            # Make predictions
            for model_name, model in self.models.items():
                X_scaled = self.scalers[model_name].transform(features)
                pred = model.predict(X_scaled)[0]
                predictions[model_name].append(max(0, pred))  # Ensure non-negative
        
        return predictions
    
    def analyze_trend_patterns(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Analyze current hiring patterns and trends"""
        df = self._prepare_time_series_data(jobs)
        
        # Company-level analysis
        company_trends = {}
        
        for company in df['company'].unique():
            if company == 'Unknown':
                continue
                
            company_data = df[df['company'] == company]
            
            if len(company_data) < 2:
                continue
            
            # Calculate trends
            job_count = len(company_data)
            avg_urgency = company_data['urgency_score'].mean()
            avg_tech_adoption = company_data['tech_count'].mean()
            
            # Determine trend direction (if we have time series data)
            if len(company_data) >= 3:
                # Simple linear trend
                dates_numeric = pd.to_numeric(company_data['date'])
                volume_trend = np.polyfit(dates_numeric, [1] * len(company_data), 1)[0]
                urgency_trend = np.polyfit(dates_numeric, company_data['urgency_score'], 1)[0]
            else:
                volume_trend = 0
                urgency_trend = 0
            
            company_trends[company] = {
                'job_count': job_count,
                'avg_urgency': round(avg_urgency, 3),
                'avg_tech_adoption': round(avg_tech_adoption, 1),
                'volume_trend': 'increasing' if volume_trend > 0 else 'stable',
                'urgency_trend': 'increasing' if urgency_trend > 0 else 'stable'
            }
        
        # Overall market analysis
        total_jobs = len(df)
        overall_urgency = df['urgency_score'].mean()
        top_companies = df['company'].value_counts().head(5).to_dict()
        
        # Technology trend analysis
        all_tech = []
        for job in jobs:
            all_tech.extend(job.get('technology_adoption', []))
        
        tech_trends = pd.Series(all_tech).value_counts().head(10).to_dict()
        
        return {
            'market_overview': {
                'total_jobs_analyzed': total_jobs,
                'average_urgency': round(overall_urgency, 3),
                'active_companies': len(df['company'].unique()),
                'top_hiring_companies': top_companies
            },
            'company_trends': company_trends,
            'technology_trends': tech_trends,
            'analysis_date': datetime.now().isoformat()
        }
    
    def get_feature_importance(self) -> Dict[str, List[Tuple[str, float]]]:
        """Get feature importance for each model"""
        if not self.is_fitted:
            return {}
        
        importance_data = {}
        
        for model_name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                feature_importance = list(zip(self.feature_names, importances))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                importance_data[model_name] = feature_importance
            elif hasattr(model, 'coef_'):
                # For linear models
                importances = np.abs(model.coef_)
                feature_importance = list(zip(self.feature_names, importances))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                importance_data[model_name] = feature_importance
        
        return importance_data