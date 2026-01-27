# ==============================
# CiviNigrani – Dashboard Page
# ==============================

import streamlit as st
import pandas as pd

from src.config import SPIKE_SENSITIVITY
from src import loaders
from src.prgi import compute_prgi, generate_narrative
from src.ui import render_sidebar
import textwrap

st.set_page_config(
    page_title="Dashboard | CiviNigrani",
    page_icon="📊",
    layout="wide"
)

# Render Persistent Sidebar
render_sidebar()

# ------------------------------
# Header
# ------------------------------
st.title("Data Status")

# ------------------------------
# Load Data
# ------------------------------
raw_pds_df = loaders.load_pds_data()
raw_grievance_df = loaders.load_grievance_data()

# ------------------------------
# Data Status Section
# ------------------------------
st.subheader("Current Data Status")

col_pds, col_griev = st.columns(2)

with col_pds:
    if raw_pds_df.empty:
        st.error("PDS dataset not found or empty.")
    else:
        st.success(f"PDS: {len(raw_pds_df):,} records loaded")

with col_griev:
    if raw_grievance_df.empty:
        st.warning("Grievance data unavailable.")
    else:
        st.success(f"Grievances: {len(raw_grievance_df):,} records loaded")

# ------------------------------
# PRGI Analysis – Flashy Visual
# ------------------------------
st.markdown("---")
st.subheader("Policy Reality Gap Index (PRGI)")

prgi_df = compute_prgi(raw_pds_df)

if prgi_df.empty:
    st.warning("PRGI metrics unavailable. Check data sources.")
else:
    # District Selector
    district = st.selectbox(
        "Select District",
        sorted(prgi_df["district"].unique()),
        key="dashboard_district"
    )

    district_df = prgi_df[prgi_df["district"] == district].sort_values("month")
    
    if not district_df.empty:
        latest = district_df.iloc[-1]
        
        # ========================================
        # FLASHY METRICS: Allocation vs Delivery
        # ========================================
        st.markdown("#### Allocation vs Delivery")
        
        allocated = latest.get('allocation', 0)
        distributed = latest.get('distribution', 0)
        gap = allocated - distributed
        delivery_pct = (distributed / allocated * 100) if allocated > 0 else 0
        gap_pct = 100 - delivery_pct
        
        # Big Numbers Display
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric(
                label="Allocated (MT)",
                value=f"{allocated:,.0f}"
            )
        
        with metric_col2:
            st.metric(
                label="Delivered (MT)",
                value=f"{distributed:,.0f}",
                delta=f"{delivery_pct:.1f}% of target",
                delta_color="normal"
            )
        
        with metric_col3:
            # Gap Metric with color logic
            delta_color = "inverse" if gap_pct > 15 else "off"
            st.metric(
                label="Delivery Gap",
                value=f"{gap:,.0f} MT",
                delta=f"-{gap_pct:.1f}%",
                delta_color=delta_color
            )
        
        # ========================================
        # PROGRESS BAR: Full Gradient Scale
        # ========================================
        st.markdown("#### Delivery Progress")
        
        # Determine status text based on delivery percentage
        if delivery_pct < 30:
            status_text = "Critical"
            status_color = "#e74c3c"
        elif delivery_pct < 70:
            status_text = "Moderate"
            status_color = "#f39c12"
        else:
            status_text = "Good"
            status_color = "#27ae60"
        
        # Full gradient scale bar with pointer
        pointer_position = min(delivery_pct, 100)
        
        # Custom thick progress bar with HTML/CSS
        progress_html = textwrap.dedent(f"""
        <div style="margin: 40px 0 20px 0;"> <!-- Added top margin for label -->
            <!-- Gradient Scale Bar -->
            <div style="
                background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%);
                border-radius: 15px;
                height: 40px;
                width: 100%;
                position: relative;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            ">
                <!-- Pointer/Marker -->
                <div style="
                    position: absolute;
                    left: calc({pointer_position:.1f}% - 3px);
                    top: -5px; 
                    width: 6px;
                    height: 50px;
                    background: #333;
                    border: 1px solid white;
                    border-radius: 3px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    z-index: 10;
                "></div>
                
                <!-- Percentage Label (Moved Above) -->
                <div style="
                    position: absolute;
                    left: calc({pointer_position:.1f}% - 30px);
                    top: -35px; /* Moved above the bar */
                    background: #333;
                    color: white;
                    padding: 4px 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                    white-space: nowrap;
                    z-index: 11;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                ">
                    {delivery_pct:.1f}%
                    <div style=" /* Little arrow pointing down */
                        position: absolute;
                        bottom: -5px;
                        left: 50%;
                        margin-left: -5px;
                        width: 0; 
                        height: 0; 
                        border-left: 5px solid transparent;
                        border-right: 5px solid transparent;
                        border-top: 5px solid #333;
                    "></div>
                </div>
            </div>
            
            <!-- Scale Labels -->
            <div style="display: flex; justify-content: space-between; margin-top: 15px; color: #666; font-size: 12px;">
                <span>0% (Critical)</span>
                <span>50% (Moderate)</span>
                <span>100% (Good)</span>
            </div>
            
            <!-- Status Summary -->
            <p style="text-align: center; margin-top: 10px; font-size: 16px;">
                <span style="color: {status_color}; font-weight: bold;">{status_text}</span>: 
                {distributed:,.0f} MT delivered of {allocated:,.0f} MT allocated
            </p>
        </div>
        """)
        st.html(progress_html)
        
        # Risk Level Badge
        if gap_pct > 30:
            st.error(f"**Critical Risk**: Over 30% of allocation missing in {district}.")
        elif gap_pct > 15:
            st.warning(f"**High Risk**: {gap_pct:.1f}% delivery gap detected.")
        else:
            st.success(f"**Good Performance**: {district} is operating within acceptable limits.")
        
        # ========================================
        # Plain-English Narrative
        # ========================================
        narrative = generate_narrative(latest)
        st.info(narrative)
        
        # ========================================
        # Trend Chart
        # ========================================
        st.markdown("#### PRGI Trend Over Time")
        st.line_chart(district_df.set_index("month")["prgi"])
        
        # Rolling Spike Detection
        if len(district_df) >= 4:
            last_3_avg = district_df["prgi"].iloc[-4:-1].mean()
            current = district_df["prgi"].iloc[-1]
            if current > last_3_avg * SPIKE_SENSITIVITY and current > 0.1:
                st.error(
                    f"**Spike Alert**: Recent PRGI ({current:.2f}) is significantly "
                    f"higher than the 3-month average ({last_3_avg:.2f})."
                )
        
        # Expandable Data Table
        with st.expander("View Raw Data"):
            st.dataframe(district_df[["month", "district", "allocation", "distribution", "prgi"]])

# ------------------------------
# PGSM Section (Enhanced)
# ------------------------------
st.markdown("---")
st.subheader("Grievance Signal Monitoring (PGSM)")

from src.pgsm import load_grievance_signals
pgsm_df = load_grievance_signals(raw_grievance_df)

if pgsm_df.empty:
    st.info("Grievance signal analysis unavailable.")
else:
    # Aggregate by month (sum all signals)
    pgsm_summary = pgsm_df.groupby("month")["grievance_signals"].sum().reset_index()
    pgsm_summary = pgsm_summary.sort_values("month")
    
    # Show metrics
    total_signals = pgsm_summary["grievance_signals"].sum()
    latest_month = pgsm_summary["month"].max() if not pgsm_summary.empty else "N/A"
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Grievance Signals", f"{total_signals:,}")
    with col2:
        st.metric("Latest Data Month", str(latest_month))
    
    # Enhanced Visualization - Always show chart
    st.markdown("#### Monthly Trend")
    
    # Always show bar chart (even for single month)
    st.bar_chart(pgsm_summary, x="month", y="grievance_signals", color="#e74c3c")
    
    if len(pgsm_summary) == 1:
        st.caption("Only 1 month of data available. More months will appear as additional CPGRAMS reports are processed.")
    
    # Breakdown by Source (if available)
    if "source" in pgsm_df.columns and pgsm_df["source"].nunique() > 1:
        st.markdown("#### Signal Breakdown by Source")
        source_summary = pgsm_df.groupby(["month", "source"])["grievance_signals"].sum().unstack(fill_value=0)
        st.bar_chart(source_summary)
    
    st.caption("Data extracted from CPGRAMS Monthly Progress Reports published by DARPG.")

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.caption(
    "CiviNigrani is a research prototype using public datasets. "
    "It provides evidence-based insights and does not make political claims."
)
