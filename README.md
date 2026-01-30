# CiviNigrani

**Jahan Policy khatam hoti hai, wahan _Nigrani_ shuru hoti hai**

CiviNigrani is an AI-powered governance intelligence platform that measures whether public policy promises — specifically the Public Distribution System (PDS) in Uttar Pradesh — are delivered on the ground. It combines delivery gap analysis, ML-powered forecasting, and grievance signal mining to provide **actionable insights** for policymakers, researchers, and civil society.

---

## 📌 Why This Matters

The **Public Distribution System (PDS)** is a cornerstone of food security in India, distributing foodgrains at subsidized prices to eligible beneficiaries under the National Food Security Act (NFSA). Publicly available PDS allocation and distribution data provide structured information on delivery outcomes.

At the same time, **citizen grievance data** — such as monthly complaints and their resolution status — signal where implementation is failing or under stress. By correlating delivery gaps with spikes in complaints and forecasting future risks using machine learning, CiviNigrani acts as an early warning system for governance failures.

---

## 🎯 Key Features

### 📊 Overview Dashboard

- **Policy Reality Gap Index (PRGI)**: Quantifies promise vs delivery (Allocation - Distribution)
- **Interactive Risk Map**: Geospatial visualization of district-level delivery gaps across UP
- **High-Risk Alerts**: Districts ranked by 3-month average PRGI with risk classification
- **Grievance Analytics**: Multi-line trend charts showing receipts, disposal, and pending complaints
- **Disposal Efficiency Gauge**: Animated gauge showing grievance resolution performance

### 🤖 AI Intelligence Center

- **ML Forecasts**: Prophet-based 3-month ahead PRGI predictions with confidence intervals
- **Risk Distribution Charts**: State-wide forecast risk breakdown (Critical/High/Low)
- **PGSM Validation**: Accuracy metrics for grievance spike predictions
- **News Intelligence**: Automated root cause analysis using NewsAPI (when configured)

### 🛡️ ArmorIQ Verified Agent
- **Verified Tool Execution**: Implements the **Plan → Token → Invoke** pattern for secure tool usage.
- **Role-Based Access Control (RBAC)**:
  - **Analyst (Read-Only)**: Can query data but is blocked from making changes.
  - **Admin (Read/Write)**: Authorized to update sensitive data (e.g., PRGI corrections).
- **Safety Guardrails**: Real-time scanning for PII (Personally Identifiable Information) and toxicity in both queries and responses.
- **Audit Support**: Verification badges indicate safe, authorized responses.

---

## 🔒 ArmorIQ Implementation

CiviNigrani integrates **ArmorIQ SDK** to transform a standard AI assistant into a **Verified Agent** suitable for government use.

### Architecture
The system uses a **Model Context Protocol (MCP)** server architecture wrapped with ArmorIQ verification:

1.  **Plan Generation**: The agent (Gemini 2.0 Flash) analyzes the user query and proposes a tool execution plan.
2.  **Policy Check**: ArmorIQ intercepts the plan.
    -   *If User is Analyst*: Write operations (e.g., `update_district_prgi`) are **BLOCKED**.
    -   *If User is Admin*: Write operations are **ALLOWED** (verified token issued).
3.  **Secure Invocation**: The MCP server only executes the tool if a valid verification token is present.
4.  **Output Scanning**: The final response is scanned for sensitive data before being shown to the user.

### Usage
- **Select Role**: Use the sidebar "User Identity" selector to switch between `Analyst` and `Admin`.
- **Try it out**:
    -   *As Analyst*: Ask "Update Lucknow PRGI to 0.9". **Result**: Blocked.
    -   *As Admin*: Ask "Update Lucknow PRGI to 0.9". **Result**: Success.

### 📚 About Page

- **Methodology Documentation**: Clear explanations of PRGI, PGSM, and risk frameworks
- **Interactive Examples**: Step-by-step stories showing how the system detects failures
- **Verified Links**: Official government sources and trusted news coverage

---

## 💻 Tech Stack

### Core Technologies

- **Language**: Python 3.8+
- **Framework**: Streamlit (multi-page dashboard)
- **Data Processing**: pandas, numpy, scipy, statsmodels
- **Visualization**: Plotly, Folium, Seaborn, Matplotlib
- **ML/AI**: Prophet (time-series forecasting)
- **Geospatial**: GeoPandas, Streamlit-Folium
- **APIs**: NewsAPI (optional), BeautifulSoup4 (web scraping)

### Key Libraries

- `streamlit` - Interactive web dashboard
- `prophet` - ML forecasting engine
- `plotly` - Interactive charts and gauges
- `folium` - Geographic risk maps
- `geopandas` - Spatial data processing
- `python-dotenv` - Secure API key management

---

## 🚀 Installation Guide

### Prerequisites

- **Python 3.8+** (Check with `python3 --version` or `python --version`)
- **pip** (Python package installer)
- **Git** (to clone the repository)

### Quick Start (Recommended)

The installation script now automatically **sets up the environment** and **fetches all required data sources**, so you are ready to run immediately.

#### **Linux / macOS**

```bash
# Clone the repository
git clone https://github.com/aaryanmax/civinigrani.git
cd civinigrani

# Run the automated installer
chmod +x install.sh
./install.sh
```

#### **Windows PowerShell**

```powershell
# Clone the repository
git clone https://github.com/aaryanmax/civinigrani.git
cd civinigrani

# Run the automated installer
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install.ps1
```

The installer will:

1. ✅ Check Python version
2. ✅ Create a virtual environment & install dependencies
3. 🔄 **Auto-fetch PDS Data**: Downloads the latest allocation datasets
4. 🔄 **Auto-extract Grievance Data**: Crawls and processes government reports

### Manual Installation (Advanced)

If you prefer to run steps manually:

```bash
# 1. Environment Setup
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Data Pipeline (Crucial Step)
# You MUST run these to populate the data/ folder
python scripts/scrape_data.py
python scripts/extract_cpgrams.py
```

---

## 🎯 Running the App

After installation, activate the virtual environment and run:

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Start the dashboard
streamlit run Home.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

### Optional: NewsAPI Configuration

For live news analysis (optional):

1. Get a free API key from [NewsAPI.org](https://newsapi.org/)
2. Create a `.env` file in the project root:
   ```
   NEWS_API_KEY=your_api_key_here
   ```
3. Restart the app - news intelligence will now show live articles

**Note**: The app works fully without NewsAPI - it will use demo data as fallback.

---

## 📱 Application Pages

### 1. 📊 Overview

**Unified dashboard combining:**

- **Dashboard Tab**: PRGI analysis, delivery progress bars, trend charts
- **Risk Map Tab**: Interactive choropleth map of Uttar Pradesh districts
- **Alerts Tab**: Top high-risk districts ranked by severity
- **Grievances Tab**: PGSM analytics with animated trend charts and disposal gauge

### 2. 🤖 AI Intelligence

**Machine learning and validation:**

- **AI Forecasts Tab**: Prophet-based 3-month predictions with district selector
- **PGSM Validation Tab**: Historical accuracy of grievance spike predictions

### 3. 📚 About

**Methodology and documentation:**

- PRGI calculation formulas
- PGSM signal detection logic
- Risk assessment framework
- Interactive example walkthrough
- Official data source links

---

## 📂 Data Sources (Public & Open)

All data used is from official government sources:

### PDS Data

- **Source**: India Data Portal - Public Distribution System
- **URL**: [ckandev.indiadataportal.com](https://ckandev.indiadataportal.com/en_GB/dataset/public-distribution-system-pds)
- **Contains**: District-wise monthly wheat and rice allocation and distribution

### Grievance Data

- **Source**: CPGRAMS (Centralized Public Grievance Redress and Monitoring System)
- **URL**: [cpgrams.gov.in](https://www.cpgrams.gov.in/)
- **Contains**: Monthly receipts, disposal, and pending counts

### Geographic Data

- **Source**: Gist - UP District Boundaries (GeoJSON)
- **URL**: Community-maintained shapefiles
- **Contains**: District polygons for choropleth mapping

---

## 🧠 AI & ML Features

### Prophet Forecasting

- Trains separate models for each district
- Uses historical PRGI data (2024-2025)
- Generates 3-month ahead predictions
- Includes confidence intervals (upper/lower bounds)
- **Model Caching**: Trained models saved to `data/cache/` for fast reloading

### PGSM Validation

- Correlates grievance spikes with delivery gaps
- Tests predictive accuracy with lag analysis
- Generates validation reports in `reports/`

### ArmorIQ Local Guard

- Regex-based PII detection (no external API)
- Keyword-based toxicity filtering
- Runs completely on-device for privacy

---

## 📊 Core Metrics

### PRGI (Policy Reality Gap Index)

```
PRGI = (Allocated - Distributed) / Allocated
```

- **0%**: Perfect delivery
- **15-30%**: High risk
- **>30%**: Critical risk

### PGSM (Public Grievance Signal Mining)

- Detects anomalous spikes in monthly complaints
- Spike threshold: Current month > 1.5× of 3-month average
- Correlates with PRGI changes in subsequent months

---

## 🛠️ Development

### Project Structure

```
civinigrani/
├── Home.py                    # Entry point
├── pages/                     # Streamlit pages
│   ├── 1_Overview.py         # Main dashboard + map + alerts + PGSM
│   ├── 2_AI_Intelligence.py  # Forecasts + validation
│   └── 3_About.py            # Documentation
├── src/                       # Core modules
│   ├── ai_engine.py          # AI assistant with dynamic data analysis
│   ├── armoriq_guard.py      # Local PII/toxicity filter
│   ├── config.py             # Configuration and constants
│   ├── loaders.py            # Data loading utilities
│   ├── prgi.py               # PRGI calculation engine
│   ├── ui.py                 # Reusable UI components
│   ├── intelligence/
│   │   └── news_analyzer.py # NewsAPI integration
│   ├── ml/
│   │   └── forecaster.py    # Prophet ML pipeline
│   └── validation/
│       └── pgsm_validator.py # PGSM spike detection & validation
├── scripts/                   # Data scraping utilities
├── data/                      # Data directory
│   ├── raw/                  # Original CSV files
│   ├── cache/                # Cached ML models
│   └── processed/            # Generated datasets
└── reports/                   # Generated markdown reports
```

### Running Scripts

```bash
# Data scraping (if source URLs change)
python scripts/scrape_data.py

# CPGRAMS extraction
python scripts/extract_cpgrams.py
```

---

## ⚠️ Disclaimer

This project uses public data for research and demonstration purposes. It does not make political claims or judgments. All interpretations are based on evidence available in open government datasets. The system is designed to support evidence-based governance, not to replace human decision-making.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

**Areas for contribution:**

- Additional data sources
- Enhanced ML models
- New visualization types
- Documentation improvements
- Bug fixes and optimizations

---

## 🙏 Acknowledgments

- **NFSA** for maintaining open PDS data
- **CPGRAMS** for public grievance statistics
- **India Data Portal** for structured datasets
- **Prophet** by Meta for time-series forecasting
- **Streamlit** for the amazing dashboard framework

---

**Built with ❤️ for better governance through data transparency**
**Team CogniThread**
