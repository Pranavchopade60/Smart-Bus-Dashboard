import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Smart Bus Scheduling System", layout="wide")
st.title("🚌 Smart Bus Scheduling & Optimization Dashboard")
st.markdown("**Starting Point:** Shirpur | **Administrator View**")

# Paths
OUT_DIR = "outputs"
ALLOC_P = os.path.join(OUT_DIR, "bus_allocation_plan.csv")
FORECAST_P = os.path.join(OUT_DIR, "predicted_daily_boardings_example_wed.csv")
SENS_P = os.path.join(OUT_DIR, "sensitivity_trips_per_bus.csv")

if not os.path.exists(ALLOC_P):
    st.error("Missing outputs. Please run backend scripts to populate the 'outputs' folder.\n\nExpected files: bus_allocation_plan.csv, predicted_daily_boardings_example_wed.csv, sensitivity_trips_per_bus.csv")
    st.stop()

alloc = pd.read_csv(ALLOC_P)
forecast = pd.read_csv(FORECAST_P) if os.path.exists(FORECAST_P) else pd.DataFrame()
sensitivity = pd.read_csv(SENS_P) if os.path.exists(SENS_P) else pd.DataFrame()

# Sidebar controls
st.sidebar.header("Admin Controls ")
speed = st.sidebar.slider("Average Bus Speed (km/h)", 30, 60, 40, 1)
turnaround = st.sidebar.slider("Turnaround Time (min)", 5, 30, 15, 1)
view_choice = st.sidebar.radio("Select View", [
    "Bus Allocation Overview",
    "Demand Forecast",
    "Trips vs Speed Analysis",
    "Equitable Resource Allocation Summary"
])

if view_choice == "Bus Allocation Overview":
    st.header(" Bus Allocation Plan")
    st.dataframe(alloc, use_container_width=True)
    fig1 = px.bar(alloc, x="Route Name", y="Allocated_Buses", title="Allocated Buses per Route", color="Allocated_Buses")
    st.plotly_chart(fig1, use_container_width=True)
    fig2 = px.bar(alloc, x="Route Name", y="Achieved_Trips_per_Day", title="Achieved Trips per Day")
    st.plotly_chart(fig2, use_container_width=True)

elif view_choice == "Demand Forecast":
    st.header(" Predicted Passenger Demand ")
    if forecast.empty:
        st.info("No forecast CSV found in outputs folder.")
    else:
        st.dataframe(forecast, use_container_width=True)
        fig3 = px.bar(forecast, x="route", y="Predicted_Daily_Boardings", color="route", title="Predicted Daily Boardings per Route")
        st.plotly_chart(fig3, use_container_width=True)

elif view_choice == "Trips vs Speed Analysis":
    st.header(" Sensitivity: Trips per Bus vs Speed")
    if sensitivity.empty:
        st.info("No sensitivity CSV found in outputs folder.")
    else:
        route_select = st.selectbox("Select Route", sensitivity['Route Name'].unique())
        sub = sensitivity[sensitivity['Route Name'] == route_select]
        fig4 = px.line(sub, x="Speed_kmh", y="Trips_per_Bus_per_Day", color="Turnaround_min", markers=True,
                       title=f"Trips per Bus/day vs Speed for {route_select}")
        st.plotly_chart(fig4, use_container_width=True)
        st.info(f"Adjust sidebar parameters: Speed = {speed} km/h, Turnaround = {turnaround} min")

elif view_choice == "Equitable Resource Allocation Summary":
    st.header(" Equity and Efficiency Overview")
    alloc_summary = alloc[['Route Name', 'Allocated_Buses', 'Unmet_Trips', 'Surplus_Trips']].copy()
    alloc_summary['Efficiency (%)'] = (alloc_summary['Allocated_Buses'] / alloc_summary['Allocated_Buses'].sum() * 100).round(2)
    st.dataframe(alloc_summary, use_container_width=True)
    fig5 = px.pie(alloc_summary, values='Allocated_Buses', names='Route Name', title="Bus Distribution by Route")
    st.plotly_chart(fig5, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Developed by Pranav Chopade and Team | BMS Project 2024")