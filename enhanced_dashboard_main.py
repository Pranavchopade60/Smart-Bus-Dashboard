"""
Enhanced Smart Bus Scheduling System Dashboard - Main Entry Point

This is the main entry point for the enhanced dashboard that integrates
all the new features including modern UI, accessibility, tooltips,
export functionality, and advanced data management.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import enhanced dashboard components
try:
    from src.integration import enhanced_dashboard
    from src.config.settings import config_manager
    from src.enhancements.accessibility import accessibility_manager
    from src.ui.layout import layout_manager
    
    ENHANCED_COMPONENTS_AVAILABLE = True
except ImportError as e:
    st.error(f"Enhanced components not available: {e}")
    ENHANCED_COMPONENTS_AVAILABLE = False

def main():
    """Main function to run the enhanced dashboard."""
    
    if not ENHANCED_COMPONENTS_AVAILABLE:
        st.error("Enhanced dashboard components are not available. Please check the installation.")
        st.stop()
    
    # Configure Streamlit page
    st.set_page_config(
        page_title=config_manager.system_config.page_title,
        page_icon=config_manager.system_config.page_icon,
        layout=config_manager.system_config.layout,
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': f"""
            # {config_manager.system_config.app_name}
            
            **Version:** {config_manager.system_config.version}
            
            Enhanced dashboard with modern UI/UX, accessibility features,
            advanced data management, and comprehensive export capabilities.
            
            **Features:**
            - 🎨 Modern, responsive design
            - ♿ WCAG 2.1 AA accessibility compliance
            - 📊 Interactive data visualizations
            - 🔍 Advanced filtering and search
            - 📥 Multi-format data export
            - 🎯 Contextual help and tooltips
            - ⚡ Performance optimization
            
            **Developed by:** Pranav Chopade and Team
            **Project:** BMS 2024
            """
        }
    )
    
    # Initialize dashboard
    try:
        # Check if this is an admin session
        if st.sidebar.button("🔧 Admin Panel"):
            st.session_state.show_admin = not st.session_state.get('show_admin', False)
        
        # Show admin panel if requested
        if st.session_state.get('show_admin', False):
            enhanced_dashboard.render_admin_panel()
        else:
            # Run main dashboard
            enhanced_dashboard.run()
        
        # Add footer with system status
        render_system_status()
        
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")
        st.exception(e)
        
        # Fallback to basic dashboard
        st.warning("Falling back to basic dashboard...")
        render_fallback_dashboard()

def render_system_status():
    """Render system status in footer."""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.caption(f"🚌 {config_manager.system_config.app_name}")
    
    with col2:
        st.caption(f"📊 Version {config_manager.system_config.version}")
    
    with col3:
        # Check data availability
        try:
            summaries = enhanced_dashboard.data_controller.get_all_data_summaries()
            data_status = "✅ Data Available" if any('error' not in s for s in summaries.values()) else "❌ Data Issues"
        except:
            data_status = "❓ Data Status Unknown"
        
        st.caption(data_status)
    
    with col4:
        # Performance status
        try:
            perf_summary = enhanced_dashboard.visualization_engine.get_performance_summary()
            if isinstance(perf_summary, dict) and 'avg_render_time' in perf_summary:
                avg_time = perf_summary['avg_render_time']
                perf_status = "🟢 Good" if avg_time < 200 else "🟡 Fair" if avg_time < 500 else "🔴 Slow"
            else:
                perf_status = "📊 No Data"
        except:
            perf_status = "❓ Unknown"
        
        st.caption(f"⚡ Performance: {perf_status}")

def render_fallback_dashboard():
    """Render a basic fallback dashboard if enhanced components fail."""
    st.title("🚌 Smart Bus Scheduling System")
    st.markdown("*Basic Dashboard Mode*")
    
    st.warning("""
    The enhanced dashboard features are not available. This is a basic fallback version.
    
    **Missing Features:**
    - Enhanced UI styling
    - Accessibility features
    - Advanced data management
    - Export functionality
    - Interactive tooltips
    """)
    
    # Basic data display
    try:
        import pandas as pd
        
        # Try to load basic data
        data_files = {
            'Bus Allocation': 'outputs/bus_allocation_plan.csv',
            'Demand Forecast': 'outputs/predicted_daily_boardings_example_wed.csv',
            'Speed Analysis': 'outputs/sensitivity_trips_per_bus.csv'
        }
        
        for name, file_path in data_files.items():
            if os.path.exists(file_path):
                st.subheader(name)
                try:
                    data = pd.read_csv(file_path)
                    st.dataframe(data)
                    
                    # Basic chart
                    if len(data.columns) >= 2:
                        numeric_cols = data.select_dtypes(include=['number']).columns
                        if len(numeric_cols) > 0:
                            st.bar_chart(data.set_index(data.columns[0])[numeric_cols[0]])
                
                except Exception as e:
                    st.error(f"Error loading {name}: {e}")
            else:
                st.warning(f"{name} data file not found: {file_path}")
    
    except ImportError:
        st.error("Pandas not available. Cannot display data.")

def check_dependencies():
    """Check if all required dependencies are available."""
    required_packages = [
        'streamlit',
        'pandas',
        'plotly',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        st.error(f"Missing required packages: {', '.join(missing_packages)}")
        st.markdown("Please install missing packages using:")
        st.code(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

if __name__ == "__main__":
    # Check dependencies first
    if check_dependencies():
        main()
    else:
        st.stop()