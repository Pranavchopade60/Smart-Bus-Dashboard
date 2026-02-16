# 🚌 Smart Bus Scheduling & Optimization Dashboard

A modern, interactive dashboard for bus scheduling optimization with enhanced UI/UX, accessibility features, and comprehensive data analysis capabilities.

## 🌟 Features

- **📊 Interactive Visualizations** - Real-time charts with zoom, pan, and drill-down
- **🎛️ Enhanced Parameter Controls** - Intuitive controls with validation and feedback
- **♿ Accessibility Compliant** - WCAG 2.1 AA standards
- **📥 Multi-Format Export** - CSV, PDF, and Excel export options
- **🔍 Advanced Filtering** - Date ranges, routes, and performance metrics
- **⚡ Performance Optimized** - Caching and efficient data loading
- **📱 Responsive Design** - Works on desktop, tablet, and mobile

## 🚀 Live Demo

**Dashboard URL:** [Your Streamlit Cloud URL will go here]

## 📋 Requirements

- Python 3.8+
- Streamlit 1.30.0+
- See `requirements.txt` for full dependencies

## 🏃 Running Locally

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/smart-bus-dashboard.git
cd smart-bus-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run working_dashboard.py
```

4. Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
smart-bus-dashboard/
├── working_dashboard.py      # Main dashboard application
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── outputs/                  # Data files
│   ├── bus_allocation_plan.csv
│   ├── predicted_daily_boardings_example_wed.csv
│   └── sensitivity_trips_per_bus.csv
└── src/                      # Source code
    ├── config/              # Configuration management
    ├── data/                # Data loading and filtering
    ├── ui/                  # UI components
    ├── enhancements/        # Enhanced features
    └── compatibility/       # Backward compatibility
```

## 🎯 Key Sections

1. **Bus Allocation Overview** - View current bus allocation across routes
2. **Demand Forecast** - Analyze predicted passenger demand
3. **Trips vs Speed Analysis** - Performance optimization insights
4. **Resource Allocation Summary** - Equitable distribution analysis

## 🔧 Configuration

Edit `config.json` to customize:
- System parameters
- Theme settings
- Data file paths
- Feature toggles

## 📊 Data Format

The dashboard expects CSV files with the following structure:

**bus_allocation_plan.csv:**
- Route_Name
- Baseline_Trips_per_Day
- Forecast_Multiplier
- Forecast_Trips_per_Day
- Trips_per_Bus_per_Day
- Recommended_Buses

## 🧪 Testing

All features are tested with 275+ test cases:
```bash
pytest tests/
```

## 📝 License

This project was developed for the BMS Project 2024.

## 👥 Credits

**Developed by:** Pranav Chopade and Team  
**Project:** BMS 2024  
**Institution:** [Your Institution]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please contact: [your.email@example.com]

## 🙏 Acknowledgments

- Streamlit for the amazing framework
- The open-source community for various libraries used

---

**⭐ If you find this project useful, please give it a star!**
