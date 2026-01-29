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
#     1_Overview.py      <- Dashboard + Risk Map + Alerts
#     2_AI_Intelligence.py <- AI Forecasts + PGSM Validation
#     3_About.py         <- Technical Documentation
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
        **Overview**  
        View delivery gap analysis with interactive visuals and real-time metrics.
        """
    )
    st.page_link("pages/1_Overview.py", label="Open Overview", icon="📊")

with col2:
    st.markdown(
        """
        **AI Intelligence**  
        AI-powered forecasts, PGSM validation, and news analysis.
        """
    )
    st.page_link("pages/2_AI_Intelligence.py", label="Open AI Intelligence", icon="🤖")

with col3:
    st.markdown(
        """
        **About**  
        Understand how PRGI, PGSM, and risk levels are calculated.
        """
    )
    st.page_link("pages/3_About.py", label="Open About", icon="📚")

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.caption(
    "CiviNigrani is a research prototype using public datasets. "
    "It provides evidence-based insights and does not make political claims."
)
