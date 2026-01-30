# ==============================
# CiviNigrani – AI Intelligence (Merged PGSM Validation + AI Forecasts)
# ==============================

"""
This page combines:
    1. PGSM Validation - Grievance signal analysis
    2. AI Forecasts - Prophet ML predictions + News Intelligence
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.ui import render_sidebar
from src.validation.pgsm_validator import load_pds_historical_data, run_validation

# Check ML modules
try:
    from src.ml.forecaster import run_forecasting_pipeline, PROPHET_AVAILABLE
    from src.intelligence.news_analyzer import get_district_intelligence
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    error_msg = str(e)

# PeerLens imports
from src.intelligence.peerlens import PeerLens
from src.population_fetcher import load_population_data
from src.prgi import compute_prgi
from src import loaders


st.set_page_config(
    page_title="AI Intelligence | CiviNigrani",
    page_icon="🤖",
    layout="wide"
)

render_sidebar()

# ==============================
# Page Header
# ==============================
st.title("🤖 AI Intelligence Center")
st.markdown("Advanced analytics combining ML forecasts, validation, and news intelligence.")

# ==============================
# Tabs
# ==============================
tab_forecast, tab_validation, tab_peerlens = st.tabs(["🔮 AI Forecasts", "📊 PGSM Validation", "🔍 PeerLens"])


# ──────────────────────────────────────────
# TAB 1: AI Forecasts
# ──────────────────────────────────────────
with tab_forecast:
    st.subheader("3-Month Ahead PRGI Forecasts")
    
    if not MODULES_AVAILABLE:
        st.error(f"ML modules not available. Please install Prophet: `pip install prophet`")
    else:
        @st.cache_data(ttl=7200)
        def load_forecast_data():
            try:
                pds_data = load_pds_historical_data("2024-01", "2025-12")
                # Returns DataFrame with: district_name, forecast_month, predicted_prgi, lower_bound, upper_bound, risk_level
                forecasts_df = run_forecasting_pipeline(pds_data, months_ahead=3)
                return forecasts_df, None
            except Exception as e:
                return pd.DataFrame(), str(e)
        
        with st.spinner("🔮 Training AI Models... This may take a moment on first load."):
            forecasts_df, error = load_forecast_data()
        
        if error:
            st.error(f"Forecast Error: {error}")
        elif not forecasts_df.empty:
            # Metrics Row
            col1, col2, col3 = st.columns(3)
            
            total_districts = forecasts_df['district_name'].nunique()
            avg_prgi = forecasts_df['predicted_prgi'].mean() * 100
            critical_count = (forecasts_df['risk_level'] == '🔴 Critical').sum()
            
            col1.metric("Districts Forecasted", total_districts)
            col2.metric("Avg Predicted Gap", f"{avg_prgi:.1f}%")
            col3.metric("🔴 Critical Predictions", critical_count)
            
            st.markdown("---")
            
            # District Selector
            districts = sorted(forecasts_df['district_name'].unique())
            selected_district = st.selectbox(
                "Select District to Analyze",
                districts,
                key="forecast_district"
            )
            
            if selected_district:
                district_df = forecasts_df[forecasts_df['district_name'] == selected_district]
                
                # Plot forecast
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=district_df['forecast_month'],
                    y=district_df['predicted_prgi'],
                    mode='lines+markers',
                    name='Predicted PRGI',
                    line=dict(color='#3498db', width=3),
                    marker=dict(size=10)
                ))
                
                # Add confidence bands
                if 'lower_bound' in district_df.columns and 'upper_bound' in district_df.columns:
                    fig.add_trace(go.Scatter(
                        x=district_df['forecast_month'],
                        y=district_df['upper_bound'],
                        mode='lines',
                        name='Upper Bound',
                        line=dict(dash='dash', color='rgba(52, 152, 219, 0.4)')
                    ))
                    fig.add_trace(go.Scatter(
                        x=district_df['forecast_month'],
                        y=district_df['lower_bound'],
                        mode='lines',
                        name='Lower Bound',
                        fill='tonexty',
                        line=dict(dash='dash', color='rgba(52, 152, 219, 0.4)')
                    ))
                
                # Add risk threshold lines
                fig.add_hline(y=0.3, line_dash="dash", line_color="red", 
                              annotation_text="Critical (30%)")
                fig.add_hline(y=0.15, line_dash="dash", line_color="orange",
                              annotation_text="High (15%)")
                
                fig.update_layout(
                    title=f"PRGI Forecast: {selected_district}",
                    xaxis_title="Forecast Month",
                    yaxis_title="Predicted Gap Index",
                    yaxis=dict(tickformat='.0%'),
                    height=400,
                    showlegend=True
                )
                st.plotly_chart(fig, key=f"forecast_chart_{selected_district}", width="stretch")
                
                # District Risk Summary Table
                st.markdown("#### Forecast Details")
                display_cols = ['forecast_month', 'predicted_prgi', 'risk_level']
                display_df = district_df[display_cols].copy()
                display_df['predicted_prgi'] = (display_df['predicted_prgi'] * 100).round(1).astype(str) + '%'
                display_df.columns = ['Month', 'Predicted Gap', 'Risk Level']
                st.dataframe(display_df, width="stretch", hide_index=True)
            
            # State-wide Summary
            st.markdown("---")
            st.markdown("### 📊 State-wide Risk Distribution")
            
            risk_counts = forecasts_df['risk_level'].value_counts()
            fig_pie = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                color=risk_counts.index,
                color_discrete_map={
                    '🔴 Critical': '#e74c3c',
                    '🟡 High': '#f39c12',
                    '🟢 Low': '#27ae60'
                }
            )
            fig_pie.update_layout(title="Forecast Risk Distribution", height=350)
            st.plotly_chart(fig_pie, key="risk_pie", width="stretch")
            
        else:
            st.warning("No forecast data available. The ML pipeline may still be training.")


# ──────────────────────────────────────────
# TAB 2: PGSM Validation
# ──────────────────────────────────────────
with tab_validation:
    st.subheader("PGSM Validation Dashboard")
    st.markdown("Analyze and validate Grievance Signal predictions against outcomes.")
    
    @st.cache_data(ttl=3600)
    def load_validation_results():
        try:
            # run_validation returns (DataFrame, report_path)
            validation_df, report_path = run_validation()
            return validation_df
        except Exception as e:
            st.error(f"Validation Error: {e}")
            return pd.DataFrame()
    
    with st.spinner("Loading validation results..."):
        validation_df = load_validation_results()
    
    if validation_df.empty:
        st.info("No validation data available. Run the validation pipeline first.")
    else:
        # Summary Stats
        col1, col2, col3, col4 = st.columns(4)
        total_predictions = len(validation_df)
        
        col1.metric("Total Predictions", total_predictions)
        
        if 'correct' in validation_df.columns:
            accuracy = validation_df['correct'].mean() * 100
            col2.metric("Accuracy", f"{accuracy:.1f}%")
        
        if 'district_name' in validation_df.columns:
            col3.metric("Districts", validation_df['district_name'].nunique())
        
        if 'month' in validation_df.columns:
            col4.metric("Time Range", f"{validation_df['month'].min()} to {validation_df['month'].max()}")
        
        st.markdown("---")
        
        # Data Table
        st.markdown("### Validation Results")
        st.dataframe(validation_df.head(50), width="stretch", hide_index=True)


# ──────────────────────────────────────────
# TAB 3: PeerLens
# ──────────────────────────────────────────
with tab_peerlens:
    st.subheader("🔍 Fair Peer Comparison")
    st.markdown(
        "Districts are compared only against structurally similar peers. "
        "No rankings. No predictions. Fully explainable."
    )
    
    # Load data
    @st.cache_data(ttl=3600)
    def load_peerlens_data():
        raw_pds = loaders.load_pds_data()
        prgi = compute_prgi(raw_pds)
        population = load_population_data()
        grievance = loaders.load_grievance_data()
        return prgi, population, grievance
    
    with st.spinner("Loading peer comparison data..."):
        prgi_data, pop_data, griev_data = load_peerlens_data()
    
    if prgi_data.empty:
        st.warning("PDS/PRGI data not available for peer comparison.")
    else:
        st.markdown("---")
        
        # Controls
        st.markdown("### ⚙️ Peer Matching Controls")
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
        
        with col_ctrl1:
            alpha = st.slider(
                "Population tolerance (%)",
                min_value=5,
                max_value=50,
                value=25,
                help="How similar the population of peer districts must be",
                key="peerlens_alpha"
            ) / 100
        
        with col_ctrl2:
            beta = st.slider(
                "Allocation tolerance (%)",
                min_value=5,
                max_value=50,
                value=25,
                help="How similar the budget allocation must be",
                key="peerlens_beta"
            ) / 100
        
        with col_ctrl3:
            min_peers = st.number_input(
                "Minimum peers",
                min_value=1,
                max_value=10,
                value=2,
                help="Minimum peers for reliable comparison",
                key="peerlens_min_peers"
            )
        
        # Initialize PeerLens engine
        engine = PeerLens(
            prgi_df=prgi_data,
            population_df=pop_data,
            grievance_df=griev_data,
            alpha=alpha,
            beta=beta,
            min_peers=min_peers
        )
        
        districts = engine.get_districts()
        
        if not districts:
            st.warning("No districts available for comparison.")
        else:
            st.markdown("---")
            st.markdown("### 📊 District Analysis")
            
            district = st.selectbox(
                "Select District",
                [d.title() for d in districts],
                key="peerlens_district"
            )
            
            if district:
                result = engine.analyze_district(district)
                
                if "error" in result:
                    st.error(result["error"])
                elif not result.get("comparison_valid", False):
                    st.warning(f"⚠️ {result.get('note', 'Insufficient peers')}")
                    st.info("Try increasing the tolerance sliders to find more peers.")
                else:
                    st.success(f"✅ Comparison based on **{result['peer_count']} peer districts**")
                    
                    # Metric Cards
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        prgi_val = result.get('prgi_relative')
                        if prgi_val is not None and not pd.isna(prgi_val):
                            st.metric(
                                "Delivery Gap (PRGI)",
                                f"{prgi_val:.2f}",
                                result["interpretation"]["delivery_gap"],
                                delta_color="inverse" if prgi_val > 1.0 else "normal"
                            )
                        else:
                            st.metric("Delivery Gap", "N/A")
                    
                    with col2:
                        grievance_val = result.get('grievance_relative')
                        if grievance_val is not None and not pd.isna(grievance_val):
                            st.metric(
                                "Grievance Pressure",
                                f"{grievance_val:.2f}",
                                result["interpretation"]["grievance_pressure"],
                                delta_color="inverse" if grievance_val > 1.0 else "normal"
                            )
                        else:
                            st.metric("Grievance Pressure", "N/A")
                    
                    with col3:
                        resolution_val = result.get('resolution_relative')
                        if resolution_val is not None and not pd.isna(resolution_val):
                            st.metric(
                                "Resolution Capacity",
                                f"{resolution_val:.2f}",
                                result["interpretation"]["resolution_capacity"],
                                delta_color="normal" if resolution_val > 1.0 else "inverse"
                            )
                        else:
                            st.metric("Resolution Capacity", "N/A")
                    
                    # Peer Districts
                    st.markdown("---")
                    st.markdown("### 🏘️ Peer Districts Used")
                    peer_list = result.get("peer_districts", [])
                    if peer_list:
                        st.info(f"Compared against: **{', '.join(peer_list[:10])}**" + 
                                (f" and {len(peer_list)-10} more" if len(peer_list) > 10 else ""))
                    
                    # Methodology
                    with st.expander("ℹ️ How PeerLens Works"):
                        st.markdown("""
                        **PeerLens** compares districts only against structurally similar peers:
                        
                        1. **Population Matching**: Districts with similar population (±tolerance%)
                        2. **Allocation Matching**: Districts with similar budget allocation (±tolerance%)
                        3. **Relative Comparison**: Your district's metrics vs median of peers
                        
                        **Metrics Explained:**
                        - **Delivery Gap Ratio**: Your PRGI ÷ Peer median PRGI (lower is better)
                        - **Grievance Pressure**: Your complaints/capita ÷ Peer median (lower is better)
                        - **Resolution Capacity**: Your resolution rate ÷ Peer median (higher is better)
                        
                        A ratio of 1.0 means you're exactly at the peer average.
                        """)


# ==============================
# Footer
# ==============================
st.markdown("---")
st.caption(
    "CiviNigrani AI Intelligence • Powered by Prophet ML, PeerLens, and News Analysis"
)
