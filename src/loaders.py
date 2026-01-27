import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional

from src.config import (
    PDS_RAW_PATH, 
    PROCESSED_DIR, 
    PGSM_NEW_PATTERN, 
    PGSM_OLD_PATTERN, 
    TARGET_STATE
)

@st.cache_data(ttl=3600, show_spinner=False)
def load_pds_data() -> pd.DataFrame:
    """
    Loads PDS distribution data safely.
    Returns: DataFrame with data or Empty DataFrame on error.
    """
    if not PDS_RAW_PATH.exists():
        return pd.DataFrame()

    try:
        # Load and preliminary filter for target state if column exists
        # We don't filter here strictly to allow the PRGI logic to handle specifics,
        # but robust reading is key.
        df = pd.read_csv(PDS_RAW_PATH)
        return df
    except Exception as e:
        print(f"Error loading PDS data: {e}")
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
