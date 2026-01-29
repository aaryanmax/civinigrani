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
# Rolling Spike Detection
SPIKE_SENSITIVITY = 1.5  # Current month > 1.5x of 3-month average

# -----------------------------------------------------------------------------
# Policy Configuration
# -----------------------------------------------------------------------------
SELECTED_POLICY = "PDS"  # Current active policy

POLICY_RESOURCES = {
    "PDS": {
        "official": [
            {
                "title": "UP Food & Civil Supplies Dept", 
                "url": "https://fcs.up.gov.in",
                "icon": "🏛️"
            },
            {
                "title": "National Food Security Portal", 
                "url": "https://nfsa.gov.in",
                "icon": "🇮🇳"
            },
            {
                "title": "Ration Card Search (UP)", 
                "url": "https://fcs.up.gov.in/Important/AmritMahotsav.aspx",
                "icon": "🔍"
            }
        ],
        "news": [
            {
                "title": "UP Saves ₹1,200 Cr via Digital PDS (Economic Times)", 
                "url": "https://economictimes.indiatimes.com/news/india/up-saving-rs-1200-crore-annually-with-digital-public-distribution-system-cm-yogi-adityanath/articleshow/97880998.cms",
                "icon": "📰" 
            },
            {
                "title": "One Nation One Ration Card Reform (PIB)", 
                "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=1661642",
                "icon": "📢"
            },
            {
                "title": "NFSA Decade Review & Impact (Mint)", 
                "url": "https://www.livemint.com/news/india",
                "icon": "🗞️"
            }
        ]
    }
}
