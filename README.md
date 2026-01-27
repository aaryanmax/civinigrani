# CiviNigrani

**Jahan Policy khatam hoti hai, wahan _Nigrani_ shuru hoti hai**

CiviNigrani is a governance intelligence platform that measures whether public policy promises — specifically the Public Distribution System (PDS) in Uttar Pradesh — are delivered on the ground, and detects early citizen distress signals using public data. It combines delivery gap analysis with grievance signal mining to provide **actionable insights** for policymakers, researchers, and civil society.

---

## 📌 Why This Matters

The **Public Distribution System (PDS)** is a cornerstone of food security in India, distributing foodgrains at subsidized prices to eligible beneficiaries under the National Food Security Act (NFSA). Publicly available PDS allocation and distribution data (e.g., district-wise wheat and rice distribution) provide structured information on delivery outcomes.

At the same time, **citizen grievance data** — such as monthly complaints and their resolution status — signal where implementation is failing or under stress. By correlating delivery gaps with spikes in complaints, CiviNigrani acts as an early warning system for governance failures.

---

## 🔍 Core Plan & Pipeline

1. **Policy & Geography Locked**

   * Policy: Public Distribution System (PDS) under NFSA
   * Region: Uttar Pradesh
   * Time window: Latest available (2025 data where possible)

2. **Data Collection**

   * PDS allocation/offtake data (state/district/month) from NFSA dashboards and open CSVs (e.g., PDS District Wise Monthly Wheat and Rice).
   * Citizen grievance data from CPGRAMS and monthly reports (receipt/disposal counts) for PDS-related complaints.

3. **Data Ingestion & Cleaning**

   * Convert raw datasets (CSV, PDF) into standardized tables
   * Normalize district names and date formats
   * Add provenance metadata (source, URL, extraction date)

4. **Feature Engineering**

   * Compute **Policy Reality Gap Index (PRGI)**: delivery gap = 1 − (offtake/allocation)
   * Compute **Public Grievance Signal Mining (PGSM)**: monthly grievance counts, pendency, spike detection

5. **Correlation & Risk Flagging**

   * Link PRGI with grievance spikes in lag windows
   * Generate risk flags for districts/months requiring attention

6. **Visualization & Dashboard**

   * Streamlit UI showing heatmaps, time series, risk lists, and source-linked data tables

---

## Key Features

* 📈 **PRGI (Policy Reality Gap Index):** Quantifies promise vs delivery
* 🔔 **Grievance Signal Mining:** Detects stress in citizen complaint trends
* 🔄 **Correlation Engine:** Flags potential governance risk signals
* 📌 **Evidence Traceability:** All figures link back to public data sources
* 🌍 **User Friendly Dashboard:** Intuitive UI without black-box AI
* ⚖️ **Non-partisan, neutral analysis:** Focused on delivery, not politics

---

## 💻 Tech Stack

* **Language:** Python
* **Framework:** Streamlit (dashboard)
* **Data Processing:** pandas, numpy, scipy, statsmodels
* **Visualization:** matplotlib, seaborn, plotly, folium
* **Data Storage:** CSV / SQLite (MVP)
* **Environment:** Ubuntu / Mac / Windows

---

## 🚀 Installation Guide

### Prerequisites

- **Python 3.8+** (Check with `python3 --version` or `python --version`)
- **pip** (Python package installer)

### One-Click Install

#### **Linux / macOS**

```bash
chmod +x install.sh
./install.sh
```

The script will:
- Create a virtual environment
- Install all dependencies
- Provide instructions to run the app

#### **Windows PowerShell**

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install.ps1
```

The script will:
- Create a virtual environment
- Install all dependencies
- Provide instructions to run the app

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🎯 Running the App

After installation, activate the virtual environment and run:

```bash
streamlit run Home.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

### Features Available:
- **Dashboard**: PRGI analysis with delivery progress visualization
- **Predictions**: High-risk district identification  
- **Methodology**: Technical documentation and formulas
- **Accessibility**: Dark mode, font sizing, and language options

---

## 📂 Data Sources (Public & Open)

Links you can populate into **data/samples/links.txt**:

* Public Distribution System (PDS) District Monthly Data CSV — district-wise wheat/rice distribution (open data). ([ckandev.indiadataportal.com][1])
* NFSA official portal (policy & allocation context). ([NFSA][2])
* CPGRAMS public grievance portal (complaints & statistics).

Use these to build real datasets for PRGI and PGSM.

---

## Disclaimer

This project uses public data for research and demonstration. It does not make political claims or judgments. All interpretations are based on evidence available in open datasets.


[1]: https://ckandev.indiadataportal.com/en_GB/dataset/public-distribution-system-pds/resource/45ad7278-f4b1-4472-9351-1f7caf147ee0 "Public Distribution System (PDS) - PDS District Wise Monthly Wheat and Rice - India Data portal"
[2]: https://nfsa.gov.in/portal/PDS_page "NFSA"
