# ==============================
# CiviNigrani – Main Entry Point
# ==============================
# 
# This is the home page of the multi-page Streamlit app.
# Individual pages are located in the `pages/` directory and
# are auto-discovered by Streamlit.
#
# Structure:
#   Home.py              <- You are here (Home)
#   pages/
#     1_Dashboard.py    <- PRGI Analysis & Visuals
#     2_Predictions.py  <- High-Risk Districts
#     3_Methodology.py  <- Technical Documentation
# ==============================

import streamlit as st

from src.ui import render_sidebar

st.set_page_config(
    page_title="CiviNigrani | Governance Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# Sidebar Branding (Persistent)
# ------------------------------
render_sidebar()

# ------------------------------
# Home Page Content
# ------------------------------
st.title("CiviNigrani")
st.markdown("### *Jahan Policy khatam hoti hai, wahan Nigrani shuru hoti hai*")

st.markdown("---")

st.markdown(
    """
    **CiviNigrani** is a governance intelligence platform that measures policy delivery gaps 
    and detects early citizen distress signals using publicly available data.
    
    ### How It Works
    
    1. **Policy Reality Gap Index (PRGI)**  
       Calculates the difference between what was sanctioned vs. what was actually delivered.
       
    2. **Public Grievance Signal Mining (PGSM)**  
       Analyzes volume patterns in CPGRAMS grievance reports to detect emerging issues.
       
    3. **Risk Intelligence**  
       Identifies high-risk districts for proactive intervention.
    """
)

st.markdown("---")

# Quick Navigation Cards
st.subheader("Navigate")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        **Dashboard**  
        View delivery gap analysis with interactive visuals and real-time metrics.
        """
    )
    st.page_link("pages/1_Dashboard.py", label="Open Dashboard", icon="📊")

with col2:
    st.markdown(
        """
        **Predictions**  
        See the top high-risk districts ranked by delivery gap severity.
        """
    )
    st.page_link("pages/2_Predictions.py", label="Open Predictions", icon="🔮")

with col3:
    st.markdown(
        """
        **Methodology**  
        Understand how PRGI, PGSM, and risk levels are calculated.
        """
    )
    st.page_link("pages/3_Methodology.py", label="Open Methodology", icon="📚")

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.caption(
    "CiviNigrani is a research prototype using public datasets. "
    "It provides evidence-based insights and does not make political claims."
)
