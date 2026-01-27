# ==============================
# CiviNigrani – Predictions Page
# ==============================

import streamlit as st
import pandas as pd

from src.config import RISK_THRESHOLD_CRITICAL, RISK_THRESHOLD_MODERATE
from src import loaders
from src.prgi import compute_prgi, get_top_high_risk_districts
from src.ui import render_sidebar

st.set_page_config(
    page_title="Predictions | CiviNigrani",
    page_icon="🔮",
    layout="wide"
)

render_sidebar()

# ------------------------------
# Header
# ------------------------------
st.title("Risk Predictions & Alerts")

st.info(
    "**High-Risk Leaderboard**: Districts with consistently high delivery gaps, "
    "ranked by their 3-month average PRGI."
)

# ------------------------------
# Load and Compute Data
# ------------------------------
raw_pds_df = loaders.load_pds_data()
prgi_df = compute_prgi(raw_pds_df)

# ------------------------------
# Controls & Leaderboard
# ------------------------------
col_header, col_ctrl = st.columns([3, 1])

with col_ctrl:
    top_n = st.radio("Show Top:", [10, 25], horizontal=True)

with col_header:
    st.subheader(f"🔥 Top {top_n} High-Risk Districts")

if prgi_df.empty:
    st.warning("Could not compute PRGI metrics. Data unavailable.")
else:
    high_risk_df = get_top_high_risk_districts(prgi_df, n=top_n)
    
    if high_risk_df.empty:
        st.caption("No high-risk data available yet.")
    else:
        # Add Risk Level classification
        high_risk_df["Risk Level"] = high_risk_df["avg_prgi"].apply(
            lambda x: "Critical" if x > RISK_THRESHOLD_CRITICAL 
                      else ("High" if x > RISK_THRESHOLD_MODERATE else "Moderate")
        )
        
        # Convert to percentages
        high_risk_df["Avg Risk %"] = high_risk_df["avg_prgi"] * 100
        high_risk_df["Latest Risk %"] = high_risk_df["latest_prgi"] * 100
        
        # Display Table
        display_df = high_risk_df[["district", "Risk Level", "Avg Risk %", "Latest Risk %"]]
        display_df.columns = ["District", "Risk Level", "Avg Risk % (3mo)", "Latest Risk %"]
        
        st.dataframe(
            display_df.style.format({
                "Avg Risk % (3mo)": "{:.1f}%",
                "Latest Risk %": "{:.1f}%"
            }).applymap(
                lambda x: "color: red; font-weight: bold" if x == "Critical" else "",
                subset=["Risk Level"]
            ),
            use_container_width=True,
            hide_index=True
        )
        
        # Summary Insight
        critical_count = (high_risk_df["Risk Level"] == "Critical").sum()
        if critical_count > 0:
            st.error(f"**{critical_count} district(s)** are in Critical condition with >30% delivery gap.")

# ------------------------------
# Future Features
# ------------------------------
st.markdown("---")
st.subheader("Upcoming Features")

st.markdown(
    """
    - **OGD Data Integration**: Incorporating broader datasets from data.gov.in
    - **Forecasting Models**: Predicting next month's grievance surge based on current patterns
    - **District Comparison**: Side-by-side analysis of multiple districts
    """
)

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.caption(
    "CiviNigrani is a research prototype using public datasets. "
    "It provides evidence-based insights and does not make political claims."
)
