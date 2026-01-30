"""
PeerLens — Transparent Peer Comparison Engine
=============================================

Core Question Answered:
"Is this district underperforming relative to structurally similar districts?"

PeerLens avoids global rankings and compares only against comparable peers
based on population scale and budget allocation.

Key Principles:
- No machine learning
- No opaque scores
- Explicit ratios and formulas
- Population-normalized signals
- Confidence-aware outputs
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class PeerLens:
    """
    Peer-based relative performance analysis for governance metrics.
    
    Uses existing PRGI data + population data for peer comparison.
    """

    # Thresholds for interpretation (kept explicit & configurable)
    GOOD_THRESHOLD = 0.90
    BAD_THRESHOLD = 1.10

    def __init__(
        self,
        prgi_df: pd.DataFrame,
        population_df: pd.DataFrame,
        grievance_df: Optional[pd.DataFrame] = None,
        alpha: float = 0.15,
        beta: float = 0.15,
        min_peers: int = 3
    ):
        """
        Parameters
        ----------
        prgi_df : pd.DataFrame
            PRGI data with columns: district, prgi, allocation, distribution, month
            
        population_df : pd.DataFrame
            Population data with columns: district, population
            
        grievance_df : pd.DataFrame, optional
            Grievance data with columns: receipts, disposal (for resolution_rate)

        alpha : float
            Population similarity tolerance (± fraction)

        beta : float
            Allocation similarity tolerance (± fraction)

        min_peers : int
            Minimum peers required for reliable comparison
        """
        self.alpha = alpha
        self.beta = beta
        self.min_peers = min_peers

        self.prgi_df = prgi_df.copy() if not prgi_df.empty else pd.DataFrame()
        self.population_df = population_df.copy() if not population_df.empty else pd.DataFrame()
        self.grievance_df = grievance_df.copy() if grievance_df is not None and not grievance_df.empty else pd.DataFrame()

        self.df = self._prepare_dataframe()

    # ─────────────────────────────────────────────
    # Data preparation
    # ─────────────────────────────────────────────

    def _prepare_dataframe(self) -> pd.DataFrame:
        """
        Merge PRGI, population, and grievance data.
        Computes metrics needed for peer comparison.
        """
        if self.prgi_df.empty:
            return pd.DataFrame()
        
        # Get latest month data for each district
        if 'month' in self.prgi_df.columns:
            latest_month = self.prgi_df['month'].max()
            df = self.prgi_df[self.prgi_df['month'] == latest_month].copy()
        else:
            df = self.prgi_df.copy()
        
        # Normalize district names
        df['district'] = df['district'].astype(str).str.lower().str.strip()
        
        # Merge population data
        if not self.population_df.empty:
            pop_df = self.population_df.copy()
            pop_df['district'] = pop_df['district'].astype(str).str.lower().str.strip()
            df = df.merge(pop_df, on='district', how='left')
        else:
            df['population'] = np.nan
        
        # Calculate grievance metrics if available
        if not self.grievance_df.empty:
            # Aggregate grievance data by any available grouping
            griev = self.grievance_df.copy()
            if 'receipts' in griev.columns:
                griev['receipts'] = pd.to_numeric(griev['receipts'], errors='coerce').fillna(0)
            if 'disposal' in griev.columns:
                griev['disposal'] = pd.to_numeric(griev['disposal'], errors='coerce').fillna(0)
            
            total_receipts = griev['receipts'].sum() if 'receipts' in griev.columns else 0
            total_disposal = griev['disposal'].sum() if 'disposal' in griev.columns else 0
            
            # Use state-level resolution rate as proxy
            df['resolution_rate'] = total_disposal / total_receipts if total_receipts > 0 else 0.5
            df['receipts'] = total_receipts / len(df) if len(df) > 0 else 0  # Distribute evenly as estimate
        else:
            df['resolution_rate'] = 0.5  # Default
            df['receipts'] = 0
        
        # Grievance density (receipts per capita)
        df['grievance_density'] = np.where(
            (df['population'] > 0) & (df['receipts'] >= 0),
            df['receipts'] / df['population'],
            np.nan
        )
        
        return df

    # ─────────────────────────────────────────────
    # Peer selection logic
    # ─────────────────────────────────────────────

    def _select_peers(self, target: pd.Series) -> pd.DataFrame:
        """
        Select structurally similar districts.

        Conditions:
        |population_i - population_target| / population_target ≤ alpha
        |allocation_i - allocation_target| / allocation_target ≤ beta
        """
        pop = target.get("population", 0)
        alloc = target.get("allocation", 0)

        if pd.isna(pop) or pop <= 0 or pd.isna(alloc) or alloc <= 0:
            # Fall back to allocation-only matching if no population
            if pd.isna(alloc) or alloc <= 0:
                return pd.DataFrame()
            
            peers = self.df[
                (self.df["district"] != target["district"]) &
                (abs(self.df["allocation"] - alloc) / alloc <= self.beta)
            ]
            return peers

        peers = self.df[
            (self.df["district"] != target["district"]) &
            (abs(self.df["population"] - pop) / pop <= self.alpha) &
            (abs(self.df["allocation"] - alloc) / alloc <= self.beta)
        ]

        return peers

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    def get_districts(self) -> list:
        """Return list of available districts."""
        if self.df.empty:
            return []
        return sorted(self.df["district"].unique().tolist())

    def analyze_district(self, district: str) -> Dict:
        """
        Perform peer-relative analysis for a single district.

        Output is safe, interpretable, and demo-ready.
        """
        if self.df.empty:
            return {"error": "No data available"}
        
        normalized = district.lower().strip()
        
        if normalized not in self.df["district"].values:
            return {"error": f"District '{district}' not found"}

        target = self.df[self.df["district"] == normalized].iloc[0]
        peers = self._select_peers(target)

        peer_count = len(peers)

        if peer_count < self.min_peers:
            return {
                "district": district,
                "peer_count": peer_count,
                "comparison_valid": False,
                "note": f"Only {peer_count} comparable peers found. Adjust tolerances or reduce minimum peers."
            }

        # Median peer benchmarks (robust to outliers)
        peer_prgi = peers["prgi"].median()
        peer_grievance = peers["grievance_density"].median() if "grievance_density" in peers.columns else np.nan
        peer_resolution = peers["resolution_rate"].median() if "resolution_rate" in peers.columns else np.nan

        # Defensive division
        prgi_rel = target["prgi"] / peer_prgi if peer_prgi > 0 else np.nan
        grievance_rel = (
            target.get("grievance_density", np.nan) / peer_grievance
            if not pd.isna(peer_grievance) and peer_grievance > 0 else np.nan
        )
        resolution_rel = (
            target.get("resolution_rate", np.nan) / peer_resolution
            if not pd.isna(peer_resolution) and peer_resolution > 0 else np.nan
        )

        interpretation = self._interpret(
            prgi_rel, grievance_rel, resolution_rel)

        return {
            "district": district,
            "peer_count": peer_count,
            "comparison_valid": True,

            # Explicit ratios (transparent math)
            "prgi_relative": prgi_rel,
            "grievance_relative": grievance_rel,
            "resolution_relative": resolution_rel,

            # Who were the peers (for auditability)
            "peer_districts": peers["district"].str.title().tolist(),

            # Human-readable insight
            "interpretation": interpretation
        }

    def analyze_all(self) -> pd.DataFrame:
        """
        Run PeerLens for all districts.
        """
        results = [
            self.analyze_district(d)
            for d in self.df["district"].unique()
        ]

        return pd.DataFrame(results)

    # ─────────────────────────────────────────────
    # Interpretation layer
    # ─────────────────────────────────────────────

    @classmethod
    def _interpret(
        cls,
        prgi_rel: float,
        grievance_rel: float,
        resolution_rel: float
    ) -> Dict:
        """
        Convert ratios into governance insights.

        Rules are explicit and symmetric.
        """

        def classify(value, lower_is_better: bool):
            if pd.isna(value):
                return "Insufficient data"

            if lower_is_better:
                if value < cls.GOOD_THRESHOLD:
                    return "Better than peers"
                elif value > cls.BAD_THRESHOLD:
                    return "Worse than peers"
            else:
                if value > cls.BAD_THRESHOLD:
                    return "Better than peers"
                elif value < cls.GOOD_THRESHOLD:
                    return "Worse than peers"

            return "Comparable to peers"

        return {
            "delivery_gap": classify(prgi_rel, lower_is_better=True),
            "grievance_pressure": classify(grievance_rel, lower_is_better=True),
            "resolution_capacity": classify(resolution_rel, lower_is_better=False)
        }
