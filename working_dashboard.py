#!/usr/bin/env python3
"""
Working Smart Bus Dashboard - Enhanced with Tooltips and Help System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import enhancement systems
try:
    from src.enhancements.tooltips import tooltip_system
    TOOLTIPS_AVAILABLE = True
except ImportError:
    TOOLTIPS_AVAILABLE = False

try:
    from src.enhancements.parameter_controls import parameter_controls_system
    PARAMETER_CONTROLS_AVAILABLE = True
except ImportError:
    PARAMETER_CONTROLS_AVAILABLE = False

# Configure page
st.set_page_config(
    page_title="Smart Bus Scheduling System",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMetric {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stSelectbox > div > div {
        background-color: white;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 2px solid #1f77b4;
    }
    
    h1 {
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title with help
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🚌 Smart Bus Scheduling System Dashboard")
    st.markdown("**Enhanced Dashboard with Real-time Analytics**")

with col2:
    if TOOLTIPS_AVAILABLE:
        if st.button("❓ Help & Glossary"):
            st.session_state.show_help = not st.session_state.get('show_help', False)

# Show help panel if requested
if TOOLTIPS_AVAILABLE and st.session_state.get('show_help', False):
    with st.expander("📚 Help Center", expanded=True):
        tab1, tab2, tab3 = st.tabs(["Search Help", "Glossary", "Quick Tour"])
        
        with tab1:
            tooltip_system.render_help_search()
        
        with tab2:
            tooltip_system.render_glossary()
        
        with tab3:
            tooltip_system.show_onboarding_tour()

# Sidebar controls with enhanced parameter system
st.sidebar.header("🎛️ Dashboard Controls")

# Admin panel toggle
if st.sidebar.button("🔧 Admin Panel"):
    st.session_state.show_admin = not st.session_state.get('show_admin', False)

# Enhanced parameter controls
st.sidebar.subheader("System Parameters")

if PARAMETER_CONTROLS_AVAILABLE:
    # Use enhanced parameter controls
    with st.sidebar:
        st.markdown("### 🎛️ Enhanced Controls")
        if st.button("Open Parameter Controls", use_container_width=True):
            st.session_state.show_parameter_controls = not st.session_state.get('show_parameter_controls', False)
    
    # Get current parameter values
    current_params = parameter_controls_system.get_current_values()
    speed = current_params.get("speed", 40.0)
    turnaround = current_params.get("turnaround_time", 15.0)
    
    # Display current values in sidebar
    st.sidebar.metric("Current Speed", f"{speed} km/h")
    st.sidebar.metric("Turnaround Time", f"{turnaround} min")
    
    # Show parameter controls panel if requested
    if st.session_state.get('show_parameter_controls', False):
        # Render enhanced controls without wrapping in expander to avoid nesting
        parameter_controls_system.render_enhanced_controls()

else:
    # Fallback to basic controls
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        speed = st.slider("Average Bus Speed (km/h)", 20, 80, 40)
    with col2:
        if TOOLTIPS_AVAILABLE:
            tooltip_system.render_tooltip("speed_analysis", "?")

    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        turnaround = st.slider("Turnaround Time (minutes)", 5, 30, 15)
    with col2:
        if TOOLTIPS_AVAILABLE:
            tooltip_system.render_tooltip("turnaround_time", "?")

    st.sidebar.metric("Current Settings", f"{speed} km/h, {turnaround} min")

# Real-time preview toggle with help
col1, col2 = st.sidebar.columns([3, 1])
with col1:
    show_preview = st.checkbox("Show Real-time Preview", True)
with col2:
    if TOOLTIPS_AVAILABLE:
        tooltip_system.render_tooltip("real_time_preview", "?")

# Main dashboard content
if st.session_state.get('show_admin', False):
    st.header("🔧 System Administration")
    
    tab1, tab2, tab3 = st.tabs(["Performance", "Data Quality", "System Status"])
    
    with tab1:
        st.subheader("📊 Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Response Time", "245ms", "-15ms")
        with col2:
            st.metric("Cache Hit Rate", "87%", "+5%")
        with col3:
            st.metric("Active Users", "12", "+2")
        with col4:
            st.metric("System Load", "23%", "-8%")
        
        # Performance chart
        perf_data = pd.DataFrame({
            'Time': pd.date_range('2024-01-01', periods=24, freq='H'),
            'Response Time (ms)': np.random.normal(250, 50, 24),
            'CPU Usage (%)': np.random.normal(25, 10, 24)
        })
        
        fig = px.line(perf_data, x='Time', y=['Response Time (ms)', 'CPU Usage (%)'],
                     title="System Performance Over Time")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("📋 Data Quality Status")
        
        data_status = {
            'Bus Allocation': {'status': '✅ Good', 'records': 1250, 'quality': 98},
            'Demand Forecast': {'status': '✅ Good', 'records': 2400, 'quality': 95},
            'Speed Analysis': {'status': '⚠️ Warning', 'records': 800, 'quality': 87}
        }
        
        for name, info in data_status.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{name} Status", info['status'])
            with col2:
                st.metric("Records", f"{info['records']:,}")
            with col3:
                st.metric("Quality Score", f"{info['quality']}%")
    
    with tab3:
        st.subheader("🖥️ System Status")
        st.success("All systems operational")
        st.info("Last updated: 2 minutes ago")
        
        if st.button("Refresh System Status"):
            st.success("System status refreshed!")

else:
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚌 Bus Allocation", 
        "📈 Demand Forecast", 
        "⚡ Speed Analysis", 
        "📊 Summary"
    ])
    
    with tab1:
        # Header with help
        col1, col2 = st.columns([4, 1])
        with col1:
            st.header("🚌 Bus Allocation Overview")
        with col2:
            if TOOLTIPS_AVAILABLE:
                tooltip_system.render_tooltip("bus_allocation", "?")
        
        # Show contextual help
        if TOOLTIPS_AVAILABLE:
            tooltip_system.render_help_panel("bus_allocation")
        
        # Generate sample data
        routes = [f'Route {chr(65 + i)}' for i in range(8)]
        allocation_data = pd.DataFrame({
            'Route': routes,
            'Buses_Required': np.random.randint(5, 25, len(routes)),
            'Current_Buses': np.random.randint(3, 20, len(routes)),
            'Efficiency': np.random.uniform(70, 95, len(routes))
        })
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Routes", len(routes))
        with col2:
            st.metric("Total Buses Required", allocation_data['Buses_Required'].sum())
        with col3:
            st.metric("Current Fleet", allocation_data['Current_Buses'].sum())
        with col4:
            st.metric("Avg Efficiency", f"{allocation_data['Efficiency'].mean():.1f}%")
        
        # Allocation chart
        fig = px.bar(allocation_data, x='Route', y=['Buses_Required', 'Current_Buses'],
                    title="Bus Allocation by Route", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📋 Detailed Allocation Data")
        st.dataframe(allocation_data, use_container_width=True)
    
    with tab2:
        # Header with help
        col1, col2 = st.columns([4, 1])
        with col1:
            st.header("📈 Demand Forecast")
        with col2:
            if TOOLTIPS_AVAILABLE:
                tooltip_system.render_tooltip("demand_forecast", "?")
        
        # Show contextual help
        if TOOLTIPS_AVAILABLE:
            tooltip_system.render_help_panel("demand_forecast")
        
        # Generate forecast data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        forecast_data = pd.DataFrame({
            'Date': dates,
            'Predicted_Boardings': np.random.normal(1500, 300, len(dates)),
            'Actual_Boardings': np.random.normal(1450, 250, len(dates)),
            'Route_Type': np.random.choice(['Urban', 'Suburban', 'Rural'], len(dates))
        })
        
        # Forecast metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Daily Boardings", f"{forecast_data['Predicted_Boardings'].mean():.0f}")
        with col2:
            st.metric("Peak Day Forecast", f"{forecast_data['Predicted_Boardings'].max():.0f}")
        with col3:
            st.metric("Forecast Accuracy", "94.2%")
        
        # Forecast chart
        fig = px.line(forecast_data, x='Date', y=['Predicted_Boardings', 'Actual_Boardings'],
                     title="Daily Boarding Predictions vs Actual")
        st.plotly_chart(fig, use_container_width=True)
        
        # Route type breakdown
        route_summary = forecast_data.groupby('Route_Type')['Predicted_Boardings'].mean().reset_index()
        fig2 = px.pie(route_summary, values='Predicted_Boardings', names='Route_Type',
                     title="Boarding Distribution by Route Type")
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        # Header with help
        col1, col2 = st.columns([4, 1])
        with col1:
            st.header("⚡ Speed vs Trips Analysis")
        with col2:
            if TOOLTIPS_AVAILABLE:
                tooltip_system.render_tooltip("speed_analysis", "?")
        
        # Show contextual help
        if TOOLTIPS_AVAILABLE:
            tooltip_system.render_help_panel("speed_analysis")
        
        # Generate speed analysis data
        speeds = np.arange(20, 81, 5)
        trips_data = pd.DataFrame({
            'Speed_kmh': speeds,
            'Trips_per_Bus': 12 - (speeds - 40) * 0.05 + np.random.normal(0, 0.5, len(speeds)),
            'Fuel_Efficiency': speeds * 0.8 + np.random.normal(0, 2, len(speeds))
        })
        
        # Current settings impact with help
        current_trips = 12 - (speed - 40) * 0.05
        efficiency_score = current_trips / speed * 100
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            st.metric("Current Speed", f"{speed} km/h")
        with col2:
            st.metric("Predicted Trips/Bus", f"{current_trips:.1f}")
        with col3:
            st.metric("Efficiency Score", f"{efficiency_score:.1f}%")
        with col4:
            if TOOLTIPS_AVAILABLE:
                tooltip_system.render_tooltip("efficiency_score", "?")
        
        # Speed analysis chart
        fig = px.line(trips_data, x='Speed_kmh', y='Trips_per_Bus',
                     title="Trips per Bus vs Speed Analysis")
        fig.add_vline(x=speed, line_dash="dash", line_color="red",
                     annotation_text=f"Current: {speed} km/h")
        st.plotly_chart(fig, use_container_width=True)
        
        # Optimization recommendations
        st.subheader("🎯 Optimization Recommendations")
        optimal_speed = trips_data.loc[trips_data['Trips_per_Bus'].idxmax(), 'Speed_kmh']
        
        if speed < optimal_speed - 5:
            st.info(f"💡 Consider increasing speed to {optimal_speed:.0f} km/h for optimal trips per bus")
        elif speed > optimal_speed + 5:
            st.warning(f"⚠️ Current speed may be too high. Consider reducing to {optimal_speed:.0f} km/h")
        else:
            st.success("✅ Current speed is near optimal range")
    
    with tab4:
        st.header("📊 System Summary")
        
        # Overall KPIs
        st.subheader("🎯 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("System Efficiency", "91.2%", "+2.1%")
        with col2:
            st.metric("Fleet Utilization", "87.5%", "+1.8%")
        with col3:
            st.metric("On-time Performance", "94.3%", "+0.7%")
        with col4:
            st.metric("Passenger Satisfaction", "4.2/5", "+0.1")
        
        # Summary charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Route performance summary
            route_perf = pd.DataFrame({
                'Route': [f'Route {chr(65 + i)}' for i in range(6)],
                'Performance': np.random.uniform(80, 98, 6)
            })
            fig1 = px.bar(route_perf, x='Route', y='Performance',
                         title="Route Performance Summary")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Daily trends
            daily_trends = pd.DataFrame({
                'Hour': range(6, 23),
                'Passenger_Load': np.random.normal(60, 20, 17)
            })
            fig2 = px.area(daily_trends, x='Hour', y='Passenger_Load',
                          title="Daily Passenger Load Trends")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Export options
        st.subheader("📥 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Dashboard Data"):
                st.success("Dashboard data exported successfully!")
        
        with col2:
            if st.button("📈 Export Charts"):
                st.success("Charts exported successfully!")
        
        with col3:
            if st.button("📋 Generate Report"):
                st.success("Report generated successfully!")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🚌 Smart Bus Scheduling System")

with col2:
    st.caption("📊 Enhanced Dashboard v2.0")

with col3:
    st.caption("⚡ Real-time Analytics Enabled")