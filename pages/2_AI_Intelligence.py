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
tab_forecast, tab_validation = st.tabs(["🔮 AI Forecasts", "📊 PGSM Validation"])


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
                st.plotly_chart(fig, key=f"forecast_chart_{selected_district}", use_container_width=True)
                
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
            st.plotly_chart(fig_pie, key="risk_pie", use_container_width=True)
            
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


# ==============================
# Footer
# ==============================
st.markdown("---")
st.caption(
    "CiviNigrani AI Intelligence • Powered by Prophet ML and News Analysis"
)
