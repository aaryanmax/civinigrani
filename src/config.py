from pathlib import Path

# -----------------------------------------------------------------------------
# Filesystem Layout
# -----------------------------------------------------------------------------
SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------
# Public Distribution System (PDS)
PDS_FILE_NAME = "pds_district_monthly_wheat_rice.csv"
PDS_RAW_PATH = RAW_DIR / PDS_FILE_NAME

# Grievance Data Patterns (PGSM)
# We prefer the new structured format, but fall back to the old one if needed
PGSM_NEW_PATTERN = "pgsm_grievance_signals_*.csv"
PGSM_OLD_PATTERN = "up_aggregated_matches_*.csv"

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
TARGET_STATE = "Uttar Pradesh"

# -----------------------------------------------------------------------------
# Risk Intelligence Thresholds
# -----------------------------------------------------------------------------
# PRGI (Policy Reality Gap Index) Thresholds
# Calculated as: 1 - (Distributed / Allocated)
RISK_THRESHOLD_MODERATE = 0.15  # > 15% Gap
RISK_THRESHOLD_CRITICAL = 0.30  # > 30% Gap

# Rolling Spike Detection
SPIKE_SENSITIVITY = 1.5  # Current month > 1.5x of 3-month average
