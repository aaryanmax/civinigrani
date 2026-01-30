"""
Data Query Tools for ArmorIQ Agent
===================================

Read-only data access tools for PRGI and PGSM data.
All tools enforce read-only access with data citations.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class DataTools:
    """Read-only data access tools for the agent."""
    
    def __init__(self, prgi_df: pd.DataFrame, pgsm_df: Optional[pd.DataFrame] = None):
        """
        Initialize with data sources.
        
        Args:
            prgi_df: PRGI DataFrame with columns: district, prgi, allocation, distribution, month
            pgsm_df: PGSM DataFrame with grievance data (optional)
        """
        self.prgi_df = prgi_df.copy() if not prgi_df.empty else pd.DataFrame()
        self.pgsm_df = pgsm_df.copy() if pgsm_df is not None and not pgsm_df.empty else pd.DataFrame()
    
    def get_top_prgi_districts(self, n: int = 5, time_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Get top N districts with highest PRGI (worst delivery gap).
        
        Args:
            n: Number of districts to return
            time_period: Optional period filter (e.g., "2024-Q4", "2024-10")
            
        Returns:
            Dict with results and citation
        """
        if self.prgi_df.empty:
            return {"error": "No PRGI data available", "citation": None}
        
        df = self.prgi_df.copy()
        
        # Filter by time period if specified
        if time_period and 'month' in df.columns:
            # Simple filtering logic
            df = df[df['month'].astype(str).str.contains(time_period, na=False)]
        
        # Get latest data for each district
        if 'month' in df.columns:
            latest = df.sort_values('month').groupby('district').tail(1)
        else:
            latest = df
        
        # Sort by PRGI descending
        top_districts = latest.nlargest(n, 'prgi')[['district', 'prgi', 'allocation', 'distribution']]
        
        results = []
        for _, row in top_districts.iterrows():
            results.append({
                "district": row['district'].title(),
                "prgi": round(float(row['prgi']), 3),
                "allocation": float(row.get('allocation', 0)),
                "distribution": float(row.get('distribution', 0))
            })
        
        citation = {
            "source": "PDS Distribution Data",
            "period": time_period if time_period else "Latest available",
            "districts_analyzed": len(df['district'].unique()),
            "data_points": len(df)
        }
        
        return {"results": results, "citation": citation}
    
    def get_grievance_spikes(self, threshold_pct: float = 30.0) -> Dict[str, Any]:
        """
        Identify months with significant grievance spikes.
        
        Args:
            threshold_pct: Percentage increase threshold to flag as spike
            
        Returns:
            Dict with spike months and citation
        """
        if self.pgsm_df.empty:
            return {"error": "No grievance data available", "citation": None}
        
        df = self.pgsm_df.copy()
        
        # Aggregate by month if we have receipts column
        if 'receipts' in df.columns and 'month' in df.columns:
            monthly = df.groupby('month')['receipts'].sum().reset_index()
            monthly = monthly.sort_values('month')
            
            # Calculate percentage change
            monthly['pct_change'] = monthly['receipts'].pct_change() * 100
            
            # Find spikes
            spikes = monthly[monthly['pct_change'] > threshold_pct]
            
            results = []
            for _, row in spikes.iterrows():
                results.append({
                    "month": str(row['month']),
                    "receipts": int(row['receipts']),
                    "increase_pct": round(float(row['pct_change']), 1)
                })
            
            citation = {
                "source": "PGSM Grievance Data",
                "months_analyzed": len(monthly),
                "threshold": f"{threshold_pct}% increase"
            }
            
            return {"results": results, "citation": citation}
        
        return {"error": "Insufficient grievance data", "citation": None}
    
    def explain_prgi_change(self, district: str, month: Optional[str] = None) -> Dict[str, Any]:
        """
        Explain PRGI trends for a specific district.
        
        Args:
            district: Name of the district
            month: Optional specific month
            
        Returns:
            Dict with trend explanation
        """
        district_data = self.prgi_df[self.prgi_df['district'].str.lower() == district.lower()].copy()
        
        if district_data.empty:
            return {"error": f"No data found for district: {district}", "citation": None}
        
        # Sort by time
        if 'month' in district_data.columns:
            district_data = district_data.sort_values('month')
            
            # Filter by month if specified
            if month:
                current = district_data[district_data['month'].astype(str).str.contains(month, na=False)]
            else:
                current = district_data.tail(1)
        else:
            current = district_data
            
        if current.empty:
             return {"error": f"No data for {month} in {district}", "citation": None}
            
        current_prgi = float(current.iloc[0]['prgi'])
        
        # Calculate trend
        trend = "stable"
        change = 0.0
        
        if len(district_data) > 1:
            prev_prgi = float(district_data.iloc[-2]['prgi'])
            change = current_prgi - prev_prgi
            if change > 0.01:
                trend = "increasing (worsening)"
            elif change < -0.01:
                trend = "decreasing (improving)"
                
        # Get recent history
        recent = district_data.tail(3)[['month', 'prgi']].to_dict('records')
        
        explanation = {
            "district": district.title(),
            "current_prgi": round(current_prgi, 3),
            "trend": trend,
            "change": round(change, 3),
            "recent_months": recent
        }
        
        citation = {
            "source": "PDS Distribution Data",
            "district": district.title(),
            "period": str(current.iloc[0].get('month', 'Latest')),
            "metric": "PRGI (Policy Reality Gap Index)"
        }
        
        return {"explanation": explanation, "citation": citation}
    
    def summarize_state_performance(self, year: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate state-level performance summary.
        
        Args:
            year: Optional year filter (e.g., "2024")
            
        Returns:
            Dict with state summary and citation
        """
        if self.prgi_df.empty:
            return {"error": "No PRGI data available", "citation": None}
        
        df = self.prgi_df.copy()
        
        # Filter by year if specified
        if year and 'month' in df.columns:
            df = df[df['month'].astype(str).str.contains(year, na=False)]
        
        if df.empty:
            return {"error": f"No data for year {year}", "citation": None}
        
        # State-level metrics
        summary = {
            "total_districts": len(df['district'].unique()),
            "avg_prgi": round(float(df['prgi'].mean()), 3),
            "median_prgi": round(float(df['prgi'].median()), 3),
            "worst_prgi": round(float(df['prgi'].max()), 3),
            "best_prgi": round(float(df['prgi'].min()), 3),
            "total_allocation": float(df['allocation'].sum()) if 'allocation' in df.columns else 0,
            "total_distribution": float(df['distribution'].sum()) if 'distribution' in df.columns else 0
        }
        
        # Risk classification
        high_risk = len(df[df['prgi'] > 0.3])
        medium_risk = len(df[(df['prgi'] > 0.15) & (df['prgi'] <= 0.3)])
        low_risk = len(df[df['prgi'] <= 0.15])
        
        summary['risk_classification'] = {
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk
        }
        
        citation = {
            "source": "PDS Distribution Data",
            "year": year if year else "All available",
            "data_points": len(df)
        }
        
        return {"summary": summary, "citation": citation}
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """Return list of available tool descriptions for the agent."""
        return [
            {
                "name": "get_top_prgi_districts",
                "description": "Get top N districts with highest PRGI (worst delivery gap). Supports time filtering.",
                "parameters": "n (int), time_period (optional str)"
            },
            {
                "name": "get_grievance_spikes",
                "description": "Identify months with significant grievance increases above threshold.",
                "parameters": "threshold_pct (float)"
            },
            {
                "name": "explain_prgi_change",
                "description": "Explain PRGI trends and changes for a specific district over time.",
                "parameters": "district (str), month (optional str)"
            },
            {
                "name": "summarize_state_performance",
                "description": "Generate comprehensive state-level performance summary with risk classification.",
                "parameters": "year (optional str)"
            }
        ]
