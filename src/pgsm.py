import pandas as pd
import numpy as np

def load_grievance_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parses grievance data (pre-loaded DataFrame) into time-series signal data.
    Expects dataframe with either 'month' (YYYY-MM) + 'grievance_signals' columns 
    OR 'source_file' column (legacy format).
    """
    if df.empty:
        return pd.DataFrame()

    try:
        # Standardize columns
        df.columns = [c.lower().strip() for c in df.columns]

        # 1. New Format Support (pgsm_grievance_signals_*.csv)
        if "month" in df.columns and "grievance_signals" in df.columns:
             df["month"] = pd.to_datetime(df["month"], errors='coerce')
             df["grievance_signals"] = pd.to_numeric(df["grievance_signals"], errors='coerce')
             return df[["month", "grievance_signals"]].dropna().sort_values("month")

        # 2. Legacy Format Support (up_aggregated_matches_*.csv)
        # Tries to extract dates from filenames if preserved in 'source_file'
        if "source_file" in df.columns:
            # Regex to find date pattern in 'source_file' column
            # Example filename: "01-12-2025.pdf"
            df["extracted_date"] = df["source_file"].str.extract(r'(\d{2}-\d{2}-\d{4})')
            df["month"] = pd.to_datetime(df["extracted_date"], format="%d-%m-%Y", errors='coerce')
            
            # Count rows per month as a proxy for signal volume in the old format
            monthly_counts = df.groupby("month").size().reset_index(name="grievance_signals")
            return monthly_counts.sort_values("month")

    except Exception as e:
        print(f"Error parsing grievance signals: {e}")
        return pd.DataFrame()

    return pd.DataFrame()

def get_pds_grievance_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts PDS-specific grievance summaries if available.
    """
    # Placeholder for future logic if we want specific textual signals
    return pd.DataFrame()
