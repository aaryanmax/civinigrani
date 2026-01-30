"""
Population Data Fetcher
=======================

Provides district-wise population data for PeerLens peer comparison.
Uses Census 2011 data stored locally with caching for performance.
"""

import json
import pandas as pd
import streamlit as st
from pathlib import Path

# Path to population data cache
POPULATION_CACHE_PATH = Path(__file__).parent.parent / "data" / "cache" / "population_census_2011.json"


@st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours
def load_population_data() -> pd.DataFrame:
    """
    Load district population data from Census 2011 cache.
    
    Returns:
        DataFrame with columns: ['district', 'population']
        Empty DataFrame if data unavailable.
    """
    try:
        if not POPULATION_CACHE_PATH.exists():
            print(f"⚠️ Population data not found at {POPULATION_CACHE_PATH}")
            return pd.DataFrame()
        
        with open(POPULATION_CACHE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        districts = data.get('districts', [])
        if not districts:
            return pd.DataFrame()
        
        df = pd.DataFrame(districts)
        
        # Normalize district names for matching
        df['district'] = df['district'].str.lower().str.strip()
        
        print(f"✅ Loaded population data for {len(df)} districts")
        return df
        
    except Exception as e:
        print(f"❌ Error loading population data: {e}")
        return pd.DataFrame()


def get_district_population(district: str) -> int:
    """
    Get population for a specific district.
    
    Args:
        district: District name (case-insensitive)
        
    Returns:
        Population count or 0 if not found.
    """
    df = load_population_data()
    if df.empty:
        return 0
    
    normalized = district.lower().strip()
    match = df[df['district'] == normalized]
    
    if match.empty:
        return 0
    
    return int(match.iloc[0]['population'])
