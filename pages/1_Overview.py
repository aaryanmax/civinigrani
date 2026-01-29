# ==============================
# CiviNigrani – Overview Page (Merged Dashboard + Predictions + Risk Map)
# ==============================

import streamlit as st
import pandas as pd
import textwrap
import folium
from streamlit_folium import st_folium
import geopandas as gpd

from src.config import SPIKE_SENSITIVITY, RISK_THRESHOLD_CRITICAL, RISK_THRESHOLD_MODERATE
from src import loaders
from src.prgi import compute_prgi, generate_narrative, get_top_high_risk_districts
from src.ui import render_sidebar, ai_engine

st.set_page_config(
    page_title="Overview | CiviNigrani",
    page_icon="📊",
    layout="wide"
)

render_sidebar()

# ==============================
# Load Data (Shared)
# ==============================
raw_pds_df = loaders.load_pds_data()
raw_grievance_df = loaders.load_grievance_data()
prgi_df = compute_prgi(raw_pds_df)
ai_engine.update_data(prgi_df)

# ==============================
# Page Header
# ==============================
st.title("📊 CiviNigrani Overview")
st.markdown("Unified view of PDS data, risk analysis, and geographic insights.")

# ==============================
# Tabs
# ==============================
tab_dashboard, tab_map, tab_alerts, tab_pgsm = st.tabs(["📈 Dashboard", "🗺️ Risk Map", "🚨 Alerts", "📋 Grievances"])

# ──────────────────────────────────────────
# TAB 1: Dashboard
# ──────────────────────────────────────────
with tab_dashboard:
    # Data Status
    st.subheader("Data Status")
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
    
    st.markdown("---")
    
    # PRGI Analysis
    st.subheader("Policy Reality Gap Index (PRGI)")
    
    if prgi_df.empty:
        st.warning("PRGI metrics unavailable. Check data sources.")
    else:
        district = st.selectbox(
            "Select District",
            sorted(prgi_df["district"].unique()),
            key="overview_district"
        )
        
        district_df = prgi_df[prgi_df["district"] == district].sort_values("month")
        
        if not district_df.empty:
            latest = district_df.iloc[-1]
            
            # Allocation vs Delivery Metrics
            st.markdown("#### Allocation vs Delivery")
            allocated = latest.get('allocation', 0)
            distributed = latest.get('distribution', 0)
            gap = allocated - distributed
            delivery_pct = (distributed / allocated * 100) if allocated > 0 else 0
            gap_pct = 100 - delivery_pct
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric(label="Allocated (MT)", value=f"{allocated:,.0f}")
            with metric_col2:
                st.metric(label="Delivered (MT)", value=f"{distributed:,.0f}", delta=f"{delivery_pct:.1f}% of target")
            with metric_col3:
                delta_color = "inverse" if gap_pct > 15 else "off"
                st.metric(label="Delivery Gap", value=f"{gap:,.0f} MT", delta=f"-{gap_pct:.1f}%", delta_color=delta_color)
            
            # Progress Bar
            st.markdown("#### Delivery Progress")
            if delivery_pct < 30:
                status_text, status_color = "Critical", "#e74c3c"
            elif delivery_pct < 70:
                status_text, status_color = "Moderate", "#f39c12"
            else:
                status_text, status_color = "Good", "#27ae60"
            
            pointer_position = min(delivery_pct, 100)
            progress_html = textwrap.dedent(f"""
            <div style="margin: 40px 0 20px 0;">
                <div style="background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%); border-radius: 15px; height: 40px; width: 100%; position: relative; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
                    <div style="position: absolute; left: calc({pointer_position:.1f}% - 3px); top: -5px; width: 6px; height: 50px; background: #333; border: 1px solid white; border-radius: 3px; z-index: 10;"></div>
                    <div style="position: absolute; left: calc({pointer_position:.1f}% - 30px); top: -35px; background: #333; color: white; padding: 4px 10px; border-radius: 5px; font-weight: bold; font-size: 14px; z-index: 11;">
                        {delivery_pct:.1f}%
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 15px; color: #666; font-size: 12px;">
                    <span>0% (Critical)</span><span>50% (Moderate)</span><span>100% (Good)</span>
                </div>
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
            
            # Narrative
            narrative = generate_narrative(latest)
            st.info(narrative)
            
            # Trend Chart
            st.markdown("#### PRGI Trend Over Time")
            st.line_chart(district_df.set_index("month")["prgi"])

# ──────────────────────────────────────────
# TAB 2: Risk Map
# ──────────────────────────────────────────
with tab_map:
    st.subheader("Geospatial Risk Map")
    st.markdown("Visualize PDS delivery gaps across Uttar Pradesh districts.")
    
    @st.cache_data(ttl=3600)
    def load_geojson():
        url = "https://gist.githubusercontent.com/GauravSahu/6705332/raw/UttarPradesh.geojson"
        try:
            gdf = gpd.read_file(url)
            possible_cols = ['district', 'District', 'DISTRICT', 'dtname', 'DTNAME', 'Name', 'NAME']
            target_col = next((c for c in gdf.columns if c in possible_cols), None)
            if target_col:
                gdf = gdf.rename(columns={target_col: 'district'})
            gdf['district'] = gdf['district'].astype(str).str.lower().str.strip()
            return gdf
        except Exception as e:
            st.error(f"Failed to load map data: {e}")
            return gpd.GeoDataFrame()

    def get_risk_data():
        if prgi_df.empty:
            return pd.DataFrame()
        latest_month = prgi_df['month'].max()
        latest_df = prgi_df[prgi_df['month'] == latest_month].copy()
        latest_df['district'] = latest_df['district'].str.lower().str.strip()
        if 'month' in latest_df.columns:
            latest_df['month'] = latest_df['month'].astype(str)
        return latest_df

    def color_producer(prgi):
        if pd.isna(prgi):
            return '#808080'
        if prgi > 0.3:
            return '#e74c3c'
        elif prgi > 0.15:
            return '#f39c12'
        else:
            return '#27ae60'

    with st.spinner("Loading Map Data..."):
        gdf = load_geojson()
        data_df = get_risk_data()

    if not gdf.empty and not data_df.empty:
        merged = gdf.merge(data_df, on='district', how='left')
        
        col1, col2, col3 = st.columns(3)
        avg_gap = data_df['prgi'].mean() * 100
        critical_count = len(data_df[data_df['prgi'] > 0.3])
        col1.metric("State Average Gap", f"{avg_gap:.1f}%")
        col2.metric("Critical Districts", f"{critical_count}")
        col3.metric("Map Data", "Uttar Pradesh")
        
        m = folium.Map(location=[27.0, 80.0], zoom_start=6, tiles="CartoDB positron", scrollWheelZoom=False)
        folium.GeoJson(
            merged,
            style_function=lambda feature: {
                'fillColor': color_producer(feature['properties'].get('prgi', None)),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['district', 'prgi', 'allocation'],
                aliases=['District:', 'Gap Index:', 'Allocated (MT):'],
                localize=True
            )
        ).add_to(m)
        st_folium(m, width="100%", height=500)
        
        st.markdown("""
        <div style="display: flex; gap: 20px; font-weight: bold; justify-content: center;">
            <span style="color: #e74c3c">■ Critical Risk (>30%)</span>
            <span style="color: #f39c12">■ High Risk (15-30%)</span>
            <span style="color: #27ae60">■ Good (<15%)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Could not load map or PDS data.")

# ──────────────────────────────────────────
# TAB 3: Alerts (Predictions)
# ──────────────────────────────────────────
with tab_alerts:
    st.subheader("🔥 High-Risk Alerts")
    st.info("Districts with consistently high delivery gaps, ranked by 3-month average PRGI.")
    
    if prgi_df.empty:
        st.warning("PRGI data unavailable.")
    else:
        top_n = st.radio("Show Top:", [10, 25], horizontal=True, key="alerts_top_n")
        high_risk_df = get_top_high_risk_districts(prgi_df, n=top_n)
        
        if high_risk_df.empty:
            st.caption("No high-risk data available yet.")
        else:
            high_risk_df["Risk Level"] = high_risk_df["avg_prgi"].apply(
                lambda x: "Critical" if x > RISK_THRESHOLD_CRITICAL 
                          else ("High" if x > RISK_THRESHOLD_MODERATE else "Moderate")
            )
            high_risk_df["Avg Risk %"] = high_risk_df["avg_prgi"] * 100
            high_risk_df["Latest Risk %"] = high_risk_df["latest_prgi"] * 100
            
            display_df = high_risk_df[["district", "Risk Level", "Avg Risk %", "Latest Risk %"]]
            display_df.columns = ["District", "Risk Level", "Avg Risk % (3mo)", "Latest Risk %"]
            
            st.dataframe(
                display_df.style.format({
                    "Avg Risk % (3mo)": "{:.1f}%",
                    "Latest Risk %": "{:.1f}%"
                }).map(
                    lambda x: "color: red; font-weight: bold" if x == "Critical" else "",
                    subset=["Risk Level"]
                ),
                width="stretch",
                hide_index=True
            )
            
            critical_count = (high_risk_df["Risk Level"] == "Critical").sum()
            if critical_count > 0:
                st.error(f"**{critical_count} district(s)** are in Critical condition with >30% delivery gap.")

# ──────────────────────────────────────────
# TAB 4: PGSM Grievances
# ──────────────────────────────────────────
with tab_pgsm:
    st.subheader("📋 Public Grievance Signal Mining (PGSM)")
    st.info("Analyzing citizen grievance patterns to detect early warning signs of policy failures.")
    
    if raw_grievance_df.empty:
        st.warning("Grievance data not available.")
    else:
        # Convert numeric columns
        for col in ['receipts', 'disposal', 'pending']:
            if col in raw_grievance_df.columns:
                raw_grievance_df[col] = pd.to_numeric(raw_grievance_df[col], errors='coerce').fillna(0)
        
        # Summary Stats with animated metrics
        st.markdown("### 📊 Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        total_receipts = raw_grievance_df['receipts'].sum() if 'receipts' in raw_grievance_df.columns else 0
        total_disposed = raw_grievance_df['disposal'].sum() if 'disposal' in raw_grievance_df.columns else 0
        total_pending = raw_grievance_df['pending'].sum() if 'pending' in raw_grievance_df.columns else 0
        disposal_rate = (total_disposed / total_receipts * 100) if total_receipts > 0 else 0
        
        col1.metric("📥 Total Received", f"{total_receipts:,.0f}")
        col2.metric("✅ Disposed", f"{total_disposed:,.0f}")
        col3.metric("⏳ Pending", f"{total_pending:,.0f}")
        col4.metric("📈 Disposal Rate", f"{disposal_rate:.1f}%")
        
        st.markdown("---")
        
        # Animated Trend Chart
        st.markdown("### 📈 Grievance Trends Over Time")
        
        if 'month' in raw_grievance_df.columns and 'receipts' in raw_grievance_df.columns:
            import plotly.graph_objects as go
            
            monthly = raw_grievance_df.groupby('month').agg({
                'receipts': 'sum',
                'disposal': 'sum',
                'pending': 'sum'
            }).reset_index().sort_values('month')
            
            fig = go.Figure()
            
            # Add animated traces
            fig.add_trace(go.Scatter(
                x=monthly['month'], y=monthly['receipts'],
                mode='lines+markers',
                name='📥 Receipts',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            ))
            fig.add_trace(go.Scatter(
                x=monthly['month'], y=monthly['disposal'],
                mode='lines+markers', 
                name='✅ Disposed',
                line=dict(color='#27ae60', width=3),
                marker=dict(size=8)
            ))
            fig.add_trace(go.Scatter(
                x=monthly['month'], y=monthly['pending'],
                mode='lines+markers',
                name='⏳ Pending',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.1)'
            ))
            
            fig.update_layout(
                title="Monthly Grievance Flow",
                xaxis_title="Month",
                yaxis_title="Count",
                height=400,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            st.plotly_chart(fig, key="pgsm_trend", use_container_width=True)
        else:
            st.caption("Trend data unavailable.")
        
        # Animated Gauge for Disposal Efficiency
        st.markdown("### 🎯 Disposal Efficiency")
        
        import plotly.graph_objects as go
        
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=disposal_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Grievance Disposal Rate", 'font': {'size': 20}},
            delta={'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [0, 100], 'ticksuffix': '%'},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 50], 'color': '#ffebee'},
                    {'range': [50, 75], 'color': '#fff3e0'},
                    {'range': [75, 100], 'color': '#e8f5e9'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        gauge_fig.update_layout(height=300)
        st.plotly_chart(gauge_fig, key="disposal_gauge", use_container_width=True)
        
        # Data Table
        st.markdown("### 📋 Recent Records")
        display_cols = [c for c in ['month', 'ministry', 'receipts', 'disposal', 'pending'] if c in raw_grievance_df.columns]
        st.dataframe(raw_grievance_df[display_cols].head(15), width="stretch", hide_index=True)

# ==============================
# Footer
# ==============================
st.markdown("---")
st.caption(
    "CiviNigrani is a research prototype using public datasets. "
    "It provides evidence-based insights and does not make political claims."
)
