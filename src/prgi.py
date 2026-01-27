import pandas as pd
from src.config import TARGET_STATE

def compute_prgi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Policy Reality Gap Index (PRGI) from PDS data.
    PRGI = 1 - (Total Distributed / Total Allocated)
    
    Args:
        df: Raw PDS DataFrame loaded by loaders.py
        
    Returns:
        DataFrame with ['month', 'district', 'prgi', 'allocation', 'distribution']
        Returns empty DataFrame on failure or empty input.
    """
    if df.empty:
        return pd.DataFrame()

    try:
        # 1. Standardize Columns (Case-insensitive)
        df.columns = [c.lower().strip() for c in df.columns]
        
        # 2. Filter for Target State
        state_col = next((c for c in df.columns if 'state' in c and 'name' in c), 
                         next((c for c in df.columns if 'state' in c), None))
        
        if state_col:
            mask = df[state_col].astype(str).str.strip().str.lower() == TARGET_STATE.lower()
            df = df[mask].copy()
        
        if df.empty:
            return pd.DataFrame()

        # 3. Parse Dates
        # The raw CSV 'month' column seems to be a date string like '2017-01-01'
        if 'month' in df.columns:
            df["month_idx"] = pd.to_datetime(df["month"], errors='coerce')
        elif 'year' in df.columns and 'month' in df.columns:
             df["month_idx"] = pd.to_datetime(
                df["year"].astype(str) + "-" + df["month"].astype(str) + "-01", 
                format="%Y-%m-%d", 
                errors='coerce'
            )
        else:
            return pd.DataFrame()

        df = df.dropna(subset=["month_idx"])

        # 4. Aggregate Allocation vs Distribution
        # The CSV has specific commodities: 'total_rice_allocated', 'total_wheat_distributed', etc.
        # We need to sum ALL allocated vs ALL distributed columns.
        
        alloc_cols = [c for c in df.columns if 'alloc' in c and 'total' in c]
        dist_cols = [c for c in df.columns if 'distrib' in c and 'total' in c]
        
        if not alloc_cols or not dist_cols:
             # Fallback to looser match
             alloc_cols = [c for c in df.columns if 'alloc' in c]
             dist_cols = [c for c in df.columns if 'distrib' in c]

        # Ensure numeric and sum
        df['total_allocation'] = 0
        for c in alloc_cols:
            df['total_allocation'] += pd.to_numeric(df[c], errors='coerce').fillna(0)
            
        df['total_distribution'] = 0
        for c in dist_cols:
            df['total_distribution'] += pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Group by Month and District
        dist_name_col = next((c for c in df.columns if 'district' in c and 'name' in c), 
                             next((c for c in df.columns if 'district' in c), 'district_name'))
        
        grouped = df.groupby(["month_idx", dist_name_col])[['total_allocation', 'total_distribution']].sum().reset_index()

        # 5. Calculate PRGI
        grouped = grouped[grouped['total_allocation'] > 0].copy()
        grouped["prgi"] = 1 - (grouped['total_distribution'] / grouped['total_allocation'])
        grouped["prgi"] = grouped["prgi"].clip(0, 1)

        # Standardize Output Columns
        grouped = grouped.rename(columns={
            dist_name_col: "district", 
            "month_idx": "month",
            "total_allocation": "allocation",
            "total_distribution": "distribution"
        })

        return grouped

    except Exception as e:
        print(f"Error computing PRGI: {e}")
        return pd.DataFrame()

def get_top_high_risk_districts(prgi_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Identifies the top N districts with the highest average PRGI over the last 3 months.
    """
    if prgi_df.empty:
        return pd.DataFrame()

    try:
        # Filter for the last 3 available months
        available_months = sorted(prgi_df["month"].unique())
        last_3_months = available_months[-3:]
        
        recent_df = prgi_df[prgi_df["month"].isin(last_3_months)].copy()
        
        # Calculate average PRGI per district
        district_risk = recent_df.groupby("district")["prgi"].mean().reset_index()
        district_risk = district_risk.rename(columns={"prgi": "avg_prgi"})
        
        # Get latest PRGI for context
        latest_month = available_months[-1]
        latest_df = prgi_df[prgi_df["month"] == latest_month][["district", "prgi"]]
        latest_df = latest_df.rename(columns={"prgi": "latest_prgi"})
        
        # Merge and Sort
        merged = pd.merge(district_risk, latest_df, on="district", how="left")
        merged = merged.sort_values("avg_prgi", ascending=False).head(n)
        
        return merged
        
    except Exception as e:
        print(f"Error finding high risk districts: {e}")
        return pd.DataFrame()

def generate_narrative(row: pd.Series) -> str:
    """
    Generates a plain-English explanation of the PRGI status.
    """
    try:
        prgi = row['prgi']
        district = row['district']
        
        if prgi > 0.3:
            return f"{district}: Critical failure. Over 30% of allocated grain did not reach the distribution point."
        elif prgi > 0.15:
            return f"{district}: High leakage detected. {prgi:.1%} of allocation is unaccounted for."
        else:
            return f"{district}: Good performance with a minor delivery gap of {prgi:.1%}."
    except Exception:
        return "Data unavailable for narrative."
