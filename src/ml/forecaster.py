"""
═══════════════════════════════════════════════════════════════════════════════
AI FORECASTING MODULE
═══════════════════════════════════════════════════════════════════════════════

This module uses Prophet (Facebook's time-series forecasting library) to predict
future PRGI (delivery gaps) for the next 3 months.

Key Features:
    - District-level 3-month ahead predictions
    - Confidence intervals (upper/lower bounds)
    - Anomaly detection for sudden changes
    
Author: CiviNigrani Team
Created: January 2026
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import pickle
import os
import logging
from typing import Dict, List, Tuple, TYPE_CHECKING, Any
import warnings
warnings.filterwarnings('ignore')

# Try importing Prophet (may not be installed yet)
if TYPE_CHECKING:
    from prophet import Prophet

try:
    from prophet import Prophet as ProphetModel
    PROPHET_AVAILABLE = True
except ImportError:
    ProphetModel = None
    PROPHET_AVAILABLE = False
    print("⚠️  Prophet not installed. Run: pip install prophet")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Number of months to forecast ahead
FORECAST_HORIZON = 3

# Minimum historical months required for training
MIN_TRAINING_MONTHS = 6

# Risk thresholds for PRGI predictions
PRGI_CRITICAL = 0.30  # 30% delivery gap
PRGI_HIGH = 0.15      # 15% delivery gap


# ═══════════════════════════════════════════════════════════════════════════════
# DATA PREPARATION
# ═══════════════════════════════════════════════════════════════════════════════

def prepare_forecast_data(pds_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Convert PDS data into Prophet-compatible format for each district.
    
    Prophet requires columns: ds (datestamp), y (value to predict)
    
    Args:
        pds_data (pd.DataFrame): Historical PDS data with columns:
            - month (datetime)
            - district_name (str)
            - prgi (float)
    
    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping district names to Prophet datasets
            Each dataset has columns: ds (date), y (PRGI value)
    """
    
    print(f"\n{' PREPARING FORECAST DATA ':═^80}")
    
    district_datasets = {}
    
    for district in pds_data['district_name'].unique():
        # Filter to district and sort by time
        district_data = pds_data[
            pds_data['district_name'] == district
        ].sort_values('month').copy()
        
        # Check minimum data requirement
        if len(district_data) < MIN_TRAINING_MONTHS:
            continue
        
        # Convert to Prophet format
        prophet_df = pd.DataFrame({
            'ds': district_data['month'],
            'y': district_data['prgi']
        })
        
        district_datasets[district] = prophet_df
    
    print(f"✅ Prepared data for {len(district_datasets)} districts")
    print(f"📊 Avg months/district: {np.mean([len(df) for df in district_datasets.values()]):.1f}")
    
    return district_datasets


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL TRAINING
# ═══════════════════════════════════════════════════════════════════════════════

def train_district_forecasters(
    district_datasets: Dict[str, pd.DataFrame]
) -> Dict[str, Prophet]:
    """
    Train a Prophet model for each district.
    
    Args:
        district_datasets: Output from prepare_forecast_data()
        
    Returns:
        Dict[str, Prophet]: Trained Prophet models for each district
    """
    
    if not PROPHET_AVAILABLE:
        print("❌ Prophet not available. Cannot train models.")
        return {}
    
    print(f"\n{' TRAINING FORECAST MODELS ':═^80}")
    
    # Check cache
    cache_dir = "data/cache"
    cache_file = os.path.join(cache_dir, "forecast_models.pkl")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Simple cache invalidation: Re-train if cache is older than 24 hours
    import time
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < 86400: # 24 hours
            try:
                with open(cache_file, 'rb') as f:
                    print(f"⚡ Loading cached models from {cache_file}...")
                    return pickle.load(f)
            except Exception as e:
                print(f"⚠️ Cache load failed: {e}. Retraining...")
    
    models = {}
    failed_districts = []
    
    for district, data in district_datasets.items():
        try:
            # Initialize Prophet with custom parameters
            model = ProphetModel(
                yearly_seasonality=True,  # Capture seasonal patterns
                weekly_seasonality=False,  # Not relevant for monthly data
                daily_seasonality=False,
                changepoint_prior_scale=0.05,  # Detect sudden changes
                interval_width=0.80  # 80% confidence intervals
            )
            
            # Train model
            model.fit(data)
            models[district] = model
            
        except Exception as e:
            print(f"❌ Error training {district}: {str(e)}")
            failed_districts.append(district)
            continue
    
    print(f"✅ Trained {len(models)} models successfully")
    
    # Save to cache
    if models:
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(models, f)
            print(f"💾 Saved models to cache: {cache_file}")
        except Exception as e:
            print(f"⚠️ Failed to save cache: {e}")
            
    if failed_districts:
        print(f"⚠️  Failed: {len(failed_districts)} districts")
    
    return models


# ═══════════════════════════════════════════════════════════════════════════════
# FORECASTING
# ═══════════════════════════════════════════════════════════════════════════════

def generate_forecasts(
    models: Dict[str, Prophet],
    months_ahead: int = FORECAST_HORIZON
) -> pd.DataFrame:
    """
    Generate 3-month ahead forecasts for all districts.
    
    Args:
        models: Trained Prophet models from train_district_forecasters()
        months_ahead: Number of months to forecast (default: 3)
        
    Returns:
        pd.DataFrame: Forecast results with columns:
            - district_name
            - forecast_month (datetime)
            - predicted_prgi (float)
            - lower_bound (float)
            - upper_bound (float)
            - risk_level (str): 'Critical', 'High', 'Moderate', 'Low'
    """
    
    print(f"\n{' GENERATING {months_ahead}-MONTH FORECASTS ':═^80}")
    
    all_forecasts = []
    
    for district, model in models.items():
        # Create future dataframe
        future = model.make_future_dataframe(periods=months_ahead, freq='MS')  # MS = month start
        
        # Generate predictions
        forecast = model.predict(future)
        
        # Extract only future predictions (last N rows)
        future_forecast = forecast.tail(months_ahead)
        
        for _, row in future_forecast.iterrows():
            # Determine risk level based on predicted PRGI
            predicted_prgi = max(0, min(1, row['yhat']))  # Clip to [0, 1]
            
            if predicted_prgi >= PRGI_CRITICAL:
                risk_level = "🔴 Critical"
            elif predicted_prgi >= PRGI_HIGH:
                risk_level = "🟡 High"
            else:
                risk_level = "🟢 Low"
            
            all_forecasts.append({
                'district_name': district,
                'forecast_month': row['ds'],
                'predicted_prgi': predicted_prgi,
                'lower_bound': max(0, row['yhat_lower']),
                'upper_bound': min(1, row['yhat_upper']),
                'risk_level': risk_level
            })
    
    result = pd.DataFrame(all_forecasts)
    
    print(f"✅ Generated {len(result)} district-month forecasts")
    print(f"🔴 Critical risk: {(result['risk_level'] == '🔴 Critical').sum()} predictions")
    print(f"🟡 High risk: {(result['risk_level'] == '🟡 High').sum()} predictions")
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# FULL PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_forecasting_pipeline(
    pds_data: pd.DataFrame,
    months_ahead: int = 3
) -> pd.DataFrame:
    """
    Execute complete forecasting pipeline.
    
    Args:
        pds_data: Historical PDS data (from validation module)
        months_ahead: Number of months to forecast
        
    Returns:
        pd.DataFrame: Forecast results for all districts
    """
    
    print(f"\n{'═' * 80}")
    print(f"{'AI FORECASTING PIPELINE':^80}")
    print(f"{'═' * 80}\n")
    
    if not PROPHET_AVAILABLE:
        print("❌ Cannot run pipeline without Prophet. Install with: pip install prophet")
        return pd.DataFrame()
    
    # Step 1: Prepare data
    datasets = prepare_forecast_data(pds_data)
    
    if not datasets:
        print("❌ No valid districts to forecast (insufficient data)")
        return pd.DataFrame()
    
    # Step 2: Train models
    models = train_district_forecasters(datasets)
    
    if not models:
        print("❌ Model training failed")
        return pd.DataFrame()
    
    # Step 3: Generate forecasts
    forecasts = generate_forecasts(models, months_ahead)
    
    print(f"\n{'═' * 80}")
    print(f"{'FORECASTING COMPLETE':^80}")
    print(f"{'═' * 80}\n")
    
    return forecasts


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO / TESTING
# ═══════================================================================════════

if __name__ == "__main__":
    # Load sample historical data
    from src.validation.pgsm_validator import load_pds_historical_data
    
    pds_data = load_pds_historical_data("2019-01", "2020-12")
    
    # Run forecasting
    forecasts = run_forecasting_pipeline(pds_data, months_ahead=3)
    
    if not forecasts.empty:
        print("\n📊 Sample Forecasts:")
        print(forecasts.head(10))
        
        # Show high-risk districts
        high_risk = forecasts[forecasts['predicted_prgi'] >= PRGI_HIGH].sort_values(
            'predicted_prgi', ascending=False
        )
        
        print(f"\n🚨 High-Risk Districts (Next 3 Months):")
        print(high_risk[['district_name', 'forecast_month', 'predicted_prgi', 'risk_level']].head(10))
