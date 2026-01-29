import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional
import requests

from src.config import (
    PDS_RAW_PATH, 
    PROCESSED_DIR, 
    PGSM_NEW_PATTERN, 
    PGSM_OLD_PATTERN, 
    TARGET_STATE
)

# PDS data source URL
PDS_CSV_URL = "https://ckandev.indiadataportal.com/dataset/f00b1bbb-7483-4607-b566-7f5d5a1527f4/resource/45ad7278-f4b1-4472-9351-1f7caf147ee0/download/pds-district-wise-monthly-wheat-and-rice.csv"

def _fetch_pds_data():
    """
    Download PDS CSV from official government data portal if not present.
    This ensures fresh data on new deployments (e.g., Streamlit Cloud).
    """
    if PDS_RAW_PATH.exists():
        return True
    
    try:
        print(f"📥 PDS data not found. Downloading from official source...")
        print(f"   Source: {PDS_CSV_URL}")
        
        # Ensure directory exists
        PDS_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Download with streaming for large files
        response = requests.get(PDS_CSV_URL, stream=True, timeout=60)
        response.raise_for_status()
        
        # Write to file
        with open(PDS_RAW_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ PDS data downloaded successfully to {PDS_RAW_PATH}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download PDS data: {e}")
        print(f"   The app will continue but PDS features will be unavailable.")
        return False

@st.cache_data(ttl=3600, show_spinner=False)
def load_pds_data() -> pd.DataFrame:
    """
    Loads PDS distribution data safely.
    Auto-fetches from official source if file doesn't exist.
    Returns: DataFrame with data or Empty DataFrame on error.
    """
    # Resolve to absolute path for cross-platform compatibility
    pds_path = PDS_RAW_PATH.resolve()
    
    # Debug: Print path information
    print(f"🔍 PDS Data Loader Debug:")
    print(f"   Expected path: {pds_path}")
    print(f"   File exists: {pds_path.exists()}")
    print(f"   Is file: {pds_path.is_file() if pds_path.exists() else 'N/A'}")
    if pds_path.exists():
        print(f"   File size: {pds_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Auto-fetch if not present
    if not pds_path.exists():
        print(f"   Attempting auto-fetch...")
        _fetch_pds_data()
    
    # If still not present after fetch attempt, return empty
    if not pds_path.exists():
        print(f"   ❌ File not found after fetch attempt")
        return pd.DataFrame()

    try:
        # Load with explicit encoding for cross-platform compatibility
        print(f"   📖 Reading CSV file...")
        df = pd.read_csv(pds_path, encoding='utf-8', low_memory=False)
        print(f"   ✅ Loaded {len(df)} rows successfully")
        return df
    except UnicodeDecodeError:
        # Try alternative encoding if UTF-8 fails
        print(f"   ⚠️  UTF-8 failed, trying latin-1 encoding...")
        try:
            df = pd.read_csv(pds_path, encoding='latin-1', low_memory=False)
            print(f"   ✅ Loaded {len(df)} rows with latin-1 encoding")
            return df
        except Exception as e:
            print(f"   ❌ Error with latin-1: {e}")
            return pd.DataFrame()
    except Exception as e:
        print(f"   ❌ Error loading PDS data: {e}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def load_grievance_data() -> pd.DataFrame:
    """
    Auto-detects and loads the latest available grievance signal data.
    Prioritizes the new 'pgsm_' format over the old 'up_aggregated_' format.
    """
    try:
        # 1. Try New Format
        files = sorted(PROCESSED_DIR.glob(PGSM_NEW_PATTERN))
        
        # 2. Fallback to Old Format
        if not files:
            files = sorted(PROCESSED_DIR.glob(PGSM_OLD_PATTERN))
        
        if not files:
            return pd.DataFrame()
        
        latest_file = files[-1]
        
        # Load with string type to avoid parsing errors initially
        df = pd.read_csv(latest_file, dtype=str)
        return df
        
    except Exception as e:
        print(f"Error loading grievance data: {e}")
        return pd.DataFrame()
