# ==============================
# CiviNigrani – About Page
# ==============================

import streamlit as st

from src.config import (
    RISK_THRESHOLD_CRITICAL, 
    RISK_THRESHOLD_MODERATE, 
    SELECTED_POLICY, 
    POLICY_RESOURCES
)
from src.ui import render_sidebar

st.set_page_config(
    page_title="About | CiviNigrani",
    page_icon="📚",
    layout="wide"
)

render_sidebar()

# ==============================
# Header
# ==============================
st.title("📚 About CiviNigrani")
st.markdown("Understanding the methodology behind governance intelligence.")

# ==============================
# Section 1: PRGI
# ==============================
st.markdown("---")
st.markdown("## 📊 Policy Reality Gap Index (PRGI)")

st.markdown(
    """
    **What is it?**  
    PRGI measures the "leakage" or logistical failure in public service delivery. 
    It compares what was officially sanctioned (policy) vs. what was actually received (reality).

    **Formula:**
    ```
    PRGI = (Allocated - Distributed) / Allocated × 100
    ```
    
    - **0%**: Perfect delivery – 100% of sanctioned goods reached beneficiaries.
    - **30%+**: Critical failure – Major leakage detected.

    **Example:**  
    If a district was allocated 1000 MT of wheat but only 700 MT was distributed, PRGI = 30%.
    """
)

# ==============================
# Section 2: PGSM
# ==============================
st.markdown("---")
st.markdown("## 📈 Public Grievance Signal Mining (PGSM)")

st.markdown(
    """
    **What is it?**  
    PGSM analyzes grievance volumes from CPGRAMS (Centralized Public Grievance Redress and Monitoring System) 
    to detect early warning signs of policy failures.

    **How it works:**
    1. **Ingestion**: Collects monthly grievance data for all states and ministries.
    2. **Extraction**: Mines unstructured text and tables for state/ministry-specific data.
    3. **Signal Detection**: Flags months with anomalous spikes in grievance receipts.
    
    **Insight**: A sudden spike in grievances often precedes official reports of delivery failures.
    """
)

# ==============================
# Section 3: Risk Framework
# ==============================
st.markdown("---")
st.markdown("## 🚨 Risk Assessment Framework")

st.markdown(
    f"""
    Districts are classified into risk tiers based on their **Avg PRGI** (3-month rolling average).

    | Risk Level | PRGI Range | Action Required |
    |------------|------------|-----------------|
    | 🔴 **Critical** | > {RISK_THRESHOLD_CRITICAL*100:.0f}% | Immediate audit, supply chain investigation |
    | 🟡 **High** | {RISK_THRESHOLD_MODERATE*100:.0f}% - {RISK_THRESHOLD_CRITICAL*100:.0f}% | Enhanced monitoring, local verification |
    | 🟢 **Moderate** | < {RISK_THRESHOLD_MODERATE*100:.0f}% | Routine monitoring |

    **Why 3-month average?**  
    Single-month data can be noisy. A rolling average smooths out reporting delays 
    and captures persistent (not transient) delivery issues.
    """
)

# ==============================
# Section 4: Interactive Example
# ==============================
st.markdown("---")
st.markdown("## 📖 See It In Action")
st.caption("A step-by-step story showing how CiviNigrani detects delivery gaps.")

with st.expander("🎬 Click to see example story", expanded=False):
    st.markdown("""
    ### 🏛️ Step 1: Scheme Announced
    Government announces NFSA entitlement: Every AAY cardholder gets 5kg wheat + 3kg rice per month.
    
    ---
    
    ### 👤 Step 2: Beneficiary Visits Shop
    Ramesh, a daily-wage worker, goes to collect his family's ration at Fair Price Shop #247 in Agra.
    
    ---
    
    ### ❌ Step 3: Problem Encountered
    Shop owner says: "Only 2kg wheat available today. Rice finished."
    Ramesh receives only 40% of his entitlement.
    
    ---
    
    ### 📊 Step 4: CiviNigrani Detects
    The system compares allocation vs. distribution data:
    - **Allocated**: 500 MT
    - **Distributed**: 312 MT  
    - **Gap**: 37.6% (🔴 Critical)
    
    ---
    
    ### 🔔 Step 5: Authorities Alerted
    District Supply Officer receives automated report flagging Agra district for immediate audit.
    """)

# ==============================
# Section 5: External Links
# ==============================
st.markdown("---")
st.markdown(f"## 🔗 Verify Scheme Details: {SELECTED_POLICY}")
st.caption("Official data sources and trusted news coverage.")

resources = POLICY_RESOURCES.get(SELECTED_POLICY, {})

if resources:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏛️ Official Sources")
        for link in resources.get("official", []):
            st.markdown(f"- [{link['title']}]({link['url']})")
            
    with col2:
        st.markdown("### 📰 In The News")
        for link in resources.get("news", []):
            st.markdown(f"- [{link['title']}]({link['url']})")

# ==============================
# Footer
# ==============================
st.markdown("---")
st.caption(
    "CiviNigrani is a research prototype using public datasets. "
    "It provides evidence-based insights and does not make political claims."
)
