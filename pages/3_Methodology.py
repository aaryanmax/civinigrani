# ==============================
# CiviNigrani – Methodology Page
# ==============================

import streamlit as st

from src.config import RISK_THRESHOLD_CRITICAL, RISK_THRESHOLD_MODERATE
from src.ui import render_sidebar

st.set_page_config(
    page_title="Methodology | CiviNigrani",
    page_icon="📚",
    layout="wide"
)

render_sidebar()

# ------------------------------
# Header
# ------------------------------
st.title("Methodology & Interpretation Guide")

st.info("Technical documentation for CiviNigrani's metrics and data sources.")

# ------------------------------
# Tabs for Organization
# ------------------------------
tab1, tab2, tab3 = st.tabs(["PRGI (Delivery Gap)", "PGSM (Grievance Signals)", "Risk Calculation"])

with tab1:
    st.markdown("### Policy Reality Gap Index (PRGI)")
    st.markdown(
        """
        **What is it?**  
        PRGI measures the "leakage" or logistical failure in public service delivery. 
        It answers the question: *How much of the government's promise actually reached the people?*
        
        **Data Source:**  
        Monthly Food Grain Bulletins (NFSA) from the Department of Food & Civil Supplies.
        """
    )
    st.warning(
        r"""
        **Formula:**
        
        $$
        \text{PRGI} = 1 - \left( \frac{\text{Total Distributed}}{\text{Total Allocated}} \right)
        $$
        
        *A PRGI of 0.20 means 20% of the allocated resource did not reach the distribution point.*
        """
    )

with tab2:
    st.markdown("### Public Grievance Signal Mining (PGSM)")
    st.markdown(
        """
        **What is it?**  
        PGSM detects distress signals by extracting and analyzing volume patterns in public grievance reports.
        
        **Data Source:**  
        Monthly Progress Reports from CPGRAMS (DARPG).
        
        **Process:**
        1. **Ingestion**: Scrapes standardized PDF reports.
        2. **Extraction**: Mines unstructured text and tables for state/ministry-specific data.
        3. **Signal Detection**: Flags months with anomalous spikes in grievance receipts.
        """
    )

with tab3:
    st.markdown("### Risk Assessment Framework")
    st.markdown(
        """
        Districts are classified into risk tiers based on their **Avg PRGI** (3-month rolling average).
        This logic drives the alerts on the Dashboard and the Predictions leaderboard.
        """
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.error("**Critical Risk**")
        st.markdown(
            f"""
            **Threshold:** Risk > {RISK_THRESHOLD_CRITICAL*100:.0f}%  
            **Meaning:** Severe failure. More than 1/3rd of allocation is missing.
            """
        )
        
        st.warning("**High Risk**")
        st.markdown(
            f"""
            **Threshold:** Risk > {RISK_THRESHOLD_MODERATE*100:.0f}%  
            **Meaning:** Significant leakage or supply chain issues.
            """
        )

    with col2:
        st.success("**Moderate / Low Risk**")
        st.markdown(
            f"""
            **Threshold:** Risk < {RISK_THRESHOLD_MODERATE*100:.0f}%  
            **Meaning:** Acceptable operational variance.
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
