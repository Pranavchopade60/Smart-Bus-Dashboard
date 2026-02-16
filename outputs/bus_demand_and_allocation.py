# Reproducible script: bus_demand_and_allocation.py
# This script expects the CSV /mnt/data/bus_system_schedule_summary.csv as input and recreates:
# - bus allocation plan (heuristic)
# - simulated historical demand and a GradientBoosting model
# - sensitivity analysis plots
# Run in an environment with pandas, scikit-learn, joblib, matplotlib.
