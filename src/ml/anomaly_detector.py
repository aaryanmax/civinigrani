"""
Anomaly Detection Module for CiviNigrani
Uses Isolation Forest to detect suspicious data patterns and outliers
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class AnomalyDetector:
    """
    Detects anomalies in PDS delivery data using Isolation Forest algorithm.
    
    Flags suspicious patterns like:
    - 100% delivery gaps (possible data corruption)
    - Unusual spikes or drops
    - Inconsistent temporal patterns
    """
    
    def __init__(self, contamination: float = 0.05):
        """
        Initialize the anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies (default 5%)
        """
        self.contamination = contamination
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for anomaly detection from PDS data.
        
        Args:
            df: DataFrame with PDS data (allocation, distribution, PRGI, etc.)
            
        Returns:
            DataFrame with engineered features
        """
        features = pd.DataFrame()
        
        # Basic features
        features['allocation'] = df['allocation']
        features['distribution'] = df['distribution']
        features['prgi'] = df['prgi']
        
        # Additional features if available
        if 'delivery_gap_pct' in df.columns:
            features['delivery_gap_pct'] = df['delivery_gap_pct']
        
        # Temporal features (if month is available)
        if 'month' in df.columns:
            # Convert month to numeric (assumes YYYY-MM format)
            try:
                df['month_numeric'] = pd.to_datetime(df['month']).apply(lambda x: x.year * 12 + x.month)
                features['month_numeric'] = df['month_numeric']
            except:
                pass
        
        # Lag features (previous month's PRGI by district)
        if 'district_name' in df.columns and 'month' in df.columns:
            df_sorted = df.sort_values(['district_name', 'month'])
            features['prgi_lag1'] = df_sorted.groupby('district_name')['prgi'].shift(1)
            features['prgi_lag2'] = df_sorted.groupby('district_name')['prgi'].shift(2)
            
            # Rolling statistics
            features['prgi_rolling_mean'] = df_sorted.groupby('district_name')['prgi'].transform(
                lambda x: x.rolling(window=3, min_periods=1).mean()
            )
            features['prgi_rolling_std'] = df_sorted.groupby('district_name')['prgi'].transform(
                lambda x: x.rolling(window=3, min_periods=1).std()
            )
        
        # Fill NaN values
        features = features.fillna(0)
        
        self.feature_names = features.columns.tolist()
        return features
    
    def fit(self, df: pd.DataFrame):
        """
        Train the anomaly detector on historical data.
        
        Args:
            df: PDS DataFrame with allocation, distribution, prgi columns
        """
        # Engineer features
        X = self._engineer_features(df)
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled)
        
        print(f"✅ Anomaly detector trained on {len(df)} records")
        print(f"   Features used: {', '.join(self.feature_names)}")
    
    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in the dataset.
        
        Args:
            df: PDS DataFrame to check for anomalies
            
        Returns:
            DataFrame with added 'is_anomaly' and 'anomaly_score' columns
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        # Engineer features
        X = self._engineer_features(df)
        
        # Standardize
        X_scaled = self.scaler.transform(X)
        
        # Predict anomalies
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        # Add results to dataframe
        result_df = df.copy()
        result_df['is_anomaly'] = (predictions == -1)
        result_df['anomaly_score'] = scores
        
        # Add anomaly reasons
        result_df['anomaly_reason'] = result_df.apply(
            lambda row: self._explain_anomaly(row), axis=1
        )
        
        return result_df
    
    def _explain_anomaly(self, row: pd.Series) -> str:
        """
        Generate human-readable explanation for why a record is anomalous.
        
        Args:
            row: DataFrame row
            
        Returns:
            Explanation string
        """
        if not row.get('is_anomaly', False):
            return ""
        
        reasons = []
        
        # Check for 100% gap
        if row.get('prgi', 0) >= 0.99:
            reasons.append("100% delivery gap (possible data error)")
        
        # Check for zero distribution with allocation
        if row.get('allocation', 0) > 0 and row.get('distribution', 0) == 0:
            reasons.append("Zero distribution despite allocation")
        
        # Check for unusual PRGI values
        prgi = row.get('prgi', 0)
        if prgi > 0.5:
            reasons.append(f"Unusually high gap ({prgi*100:.1f}%)")
        
        # Check for large variance from rolling mean
        if 'prgi_rolling_mean' in row and 'prgi_rolling_std' in row:
            rolling_mean = row.get('prgi_rolling_mean', 0)
            rolling_std = row.get('prgi_rolling_std', 0)
            if rolling_std > 0:
                z_score = abs((prgi - rolling_mean) / rolling_std)
                if z_score > 2:
                    reasons.append(f"Large deviation from trend (Z={z_score:.1f})")
        
        if not reasons:
            reasons.append("Statistical outlier (Isolation Forest)")
        
        return "; ".join(reasons)
    
    def get_anomaly_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics about detected anomalies.
        
        Args:
            df: DataFrame with anomaly detection results
            
        Returns:
            Dictionary with summary statistics
        """
        anomalies = df[df['is_anomaly'] == True]
        
        summary = {
            'total_records': len(df),
            'total_anomalies': len(anomalies),
            'anomaly_rate': len(anomalies) / len(df) * 100 if len(df) > 0 else 0,
            'avg_anomaly_score': anomalies['anomaly_score'].mean() if len(anomalies) > 0 else 0,
        }
        
        # Breakdown by district
        if 'district_name' in df.columns:
            district_anomalies = anomalies.groupby('district_name').size().sort_values(ascending=False)
            summary['top_anomalous_districts'] = district_anomalies.head(5).to_dict()
        
        # Breakdown by month
        if 'month' in df.columns:
            month_anomalies = anomalies.groupby('month').size().sort_values(ascending=False)
            summary['top_anomalous_months'] = month_anomalies.head(5).to_dict()
        
        return summary


def detect_simple_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Quick rule-based anomaly detection without ML training.
    Useful for immediate flagging of obvious issues.
    
    Args:
        df: PDS DataFrame
        
    Returns:
        DataFrame with 'simple_anomaly' and 'simple_reason' columns
    """
    result_df = df.copy()
    
    def check_simple_anomalies(row):
        reasons = []
        
        # 100% gap
        if row.get('prgi', 0) >= 0.99:
            reasons.append("100% delivery gap")
        
        # Zero distribution with allocation
        if row.get('allocation', 0) > 0 and row.get('distribution', 0) == 0:
            reasons.append("No distribution")
        
        # Extremely high allocation (possible data entry error)
        if row.get('allocation', 0) > 1e6:  # More than 1 million quintals
            reasons.append("Unusually high allocation")
        
        # Negative values (impossible)
        if row.get('allocation', 0) < 0 or row.get('distribution', 0) < 0:
            reasons.append("Negative values")
        
        # Distribution > allocation (impossible)
        if row.get('distribution', 0) > row.get('allocation', 0):
            reasons.append("Distribution exceeds allocation")
        
        return "; ".join(reasons) if reasons else ""
    
    result_df['simple_anomaly'] = result_df.apply(check_simple_anomalies, axis=1)
    result_df['is_simple_anomaly'] = result_df['simple_anomaly'] != ""
    
    return result_df
