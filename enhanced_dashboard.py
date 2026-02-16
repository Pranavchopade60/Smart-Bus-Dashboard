"""
Enhanced Smart Bus Scheduling System Dashboard

This is the main application file that integrates all the enhanced components
including modern UI, accessibility features, and improved user experience.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from typing import Optional

# Import enhanced components
from src.config.settings import config_manager
from src.ui.layout import layout_manager, LayoutConfig
from src.ui.styles import style_manager


class EnhancedDashboard:
    """Main enhanced dashboard application."""
    
    def __init__(self):
        self.config = config_manager
        self.layout = layout_manager
        self.data = {}
        self._initialize_session_state()
        self._load_data()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'current_section' not in st.session_state:
            st.session_state.current_section = self.config.user_preferences.default_section
        
        if 'admin_speed' not in st.session_state:
            st.session_state.admin_speed = 40
        
        if 'admin_turnaround' not in st.session_state:
            st.session_state.admin_turnaround = 15
        
        if 'onboarding_shown' not in st.session_state:
            st.session_state.onboarding_shown = self.config.user_preferences.onboarding_completed
    
    def _load_data(self):
        """Load CSV data files with enhanced error handling."""
        try:
            # Check if data directory exists
            data_dir = self.config.system_config.data_directory
            if not os.path.exists(data_dir):
                st.error(f"Data directory '{data_dir}' not found. Please ensure the outputs folder exists.")
                st.stop()
            
            # Load allocation data
            alloc_path = self.config.get_file_path('allocation')
            if os.path.exists(alloc_path):
                self.data['allocation'] = pd.read_csv(alloc_path)
            else:
                st.error(f"Missing allocation data: {alloc_path}")
                st.info("Please run the backend scripts to generate the required data files.")
                st.stop()
            
            # Load forecast data (optional)
            forecast_path = self.config.get_file_path('forecast')
            if os.path.exists(forecast_path):
                self.data['forecast'] = pd.read_csv(forecast_path)
            else:
                self.data['forecast'] = pd.DataFrame()
                st.warning("Forecast data not available. Some features may be limited.")
            
            # Load sensitivity data (optional)
            sensitivity_path = self.config.get_file_path('sensitivity')
            if os.path.exists(sensitivity_path):
                self.data['sensitivity'] = pd.read_csv(sensitivity_path)
            else:
                self.data['sensitivity'] = pd.DataFrame()
                st.warning("Sensitivity analysis data not available. Some features may be limited.")
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.info("Please check that all required CSV files are present in the outputs directory.")
            st.stop()
    
    def run(self):
        """Run the enhanced dashboard application."""
        # Setup layout configuration
        layout_config = LayoutConfig(
            show_sidebar=True,
            show_header=True,
            show_footer=True,
            responsive=True,
            theme=self.config.user_preferences.theme,
            javascript_features=['base', 'tooltips', 'accessibility', 'animations']
        )
        
        # Update layout configuration
        self.layout.config = layout_config
        
        # Render complete layout
        self.layout.render_complete_layout(
            content_func=self._render_main_content,
            section=st.session_state.current_section
        )
        
        # Show onboarding if not completed
        if not st.session_state.onboarding_shown:
            self._show_onboarding()
    
    def _render_main_content(self):
        """Render the main dashboard content."""
        # Add main content container
        st.markdown('<div id="main-content" role="main">', unsafe_allow_html=True)
        
        # Navigation tabs
        sections = self.config.system_config.sections
        selected_section = self.layout.render_navigation_tabs(
            sections, 
            st.session_state.current_section
        )
        
        # Update current section if changed
        if selected_section != st.session_state.current_section:
            st.session_state.current_section = selected_section
            st.rerun()
        
        # Render section content
        if selected_section == "Bus Allocation Overview":
            self._render_allocation_overview()
        elif selected_section == "Demand Forecast":
            self._render_demand_forecast()
        elif selected_section == "Trips vs Speed Analysis":
            self._render_trips_analysis()
        elif selected_section == "Equitable Resource Allocation Summary":
            self._render_equity_summary()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_allocation_overview(self):
        """Render the bus allocation overview section."""
        self.layout.add_breadcrumb("Bus Allocation Overview")
        
        # Data table card
        def render_allocation_table():
            if not self.data['allocation'].empty:
                st.dataframe(
                    self.data['allocation'], 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No allocation data available.")
        
        self.layout.render_card(
            title="📊 Bus Allocation Plan",
            content_func=render_allocation_table,
            help_text="This table shows the current bus allocation plan for all routes"
        )
        
        # Charts
        if not self.data['allocation'].empty:
            col1, col2 = st.columns(2)
            
            with col1:
                def render_allocation_chart():
                    fig = px.bar(
                        self.data['allocation'], 
                        x="Route Name", 
                        y="Allocated_Buses",
                        title="Allocated Buses per Route",
                        color="Allocated_Buses",
                        color_continuous_scale="viridis"
                    )
                    fig.update_layout(
                        showlegend=True,
                        xaxis_title="Route Name",
                        yaxis_title="Number of Buses",
                        font=dict(size=12)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                self.layout.render_card(
                    title="🚌 Bus Distribution",
                    content_func=render_allocation_chart,
                    help_text="Visual representation of bus allocation across routes"
                )
            
            with col2:
                def render_trips_chart():
                    fig = px.bar(
                        self.data['allocation'], 
                        x="Route Name", 
                        y="Achieved_Trips_per_Day",
                        title="Achieved Trips per Day",
                        color="Achieved_Trips_per_Day",
                        color_continuous_scale="plasma"
                    )
                    fig.update_layout(
                        showlegend=True,
                        xaxis_title="Route Name",
                        yaxis_title="Trips per Day",
                        font=dict(size=12)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                self.layout.render_card(
                    title="🔄 Daily Trips",
                    content_func=render_trips_chart,
                    help_text="Number of trips achieved per day for each route"
                )
    
    def _render_demand_forecast(self):
        """Render the demand forecast section."""
        self.layout.add_breadcrumb("Demand Forecast")
        
        if self.data['forecast'].empty:
            st.info("📈 Forecast data is not available. Please run the demand forecasting model to generate predictions.")
            return
        
        # Forecast data table
        def render_forecast_table():
            st.dataframe(
                self.data['forecast'], 
                use_container_width=True,
                hide_index=True
            )
        
        self.layout.render_card(
            title="📈 Predicted Passenger Demand",
            content_func=render_forecast_table,
            help_text="Forecasted passenger demand based on historical data and trends"
        )
        
        # Forecast chart
        def render_forecast_chart():
            fig = px.bar(
                self.data['forecast'], 
                x="route", 
                y="Predicted_Daily_Boardings",
                color="route",
                title="Predicted Daily Boardings per Route"
            )
            fig.update_layout(
                showlegend=True,
                xaxis_title="Route",
                yaxis_title="Predicted Daily Boardings",
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        self.layout.render_card(
            title="📊 Demand Visualization",
            content_func=render_forecast_chart,
            help_text="Visual representation of predicted passenger demand"
        )
    
    def _render_trips_analysis(self):
        """Render the trips vs speed analysis section."""
        self.layout.add_breadcrumb("Trips vs Speed Analysis")
        
        if self.data['sensitivity'].empty:
            st.info("⚡ Sensitivity analysis data is not available. Please run the sensitivity analysis to generate this data.")
            return
        
        # Route selection
        routes = self.data['sensitivity']['Route Name'].unique()
        selected_route = st.selectbox(
            "🛣️ Select Route for Analysis",
            routes,
            help="Choose a route to analyze the relationship between speed and trips per bus"
        )
        
        # Filter data for selected route
        route_data = self.data['sensitivity'][self.data['sensitivity']['Route Name'] == selected_route]
        
        # Analysis chart
        def render_sensitivity_chart():
            fig = px.line(
                route_data, 
                x="Speed_kmh", 
                y="Trips_per_Bus_per_Day",
                color="Turnaround_min",
                markers=True,
                title=f"Trips per Bus/Day vs Speed for {selected_route}"
            )
            fig.update_layout(
                showlegend=True,
                xaxis_title="Speed (km/h)",
                yaxis_title="Trips per Bus per Day",
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        self.layout.render_card(
            title="⚡ Speed vs Performance Analysis",
            content_func=render_sensitivity_chart,
            help_text="Analysis of how bus speed affects the number of trips per bus per day"
        )
        
        # Current settings info
        current_speed = st.session_state.get('admin_speed', 40)
        current_turnaround = st.session_state.get('admin_turnaround', 15)
        
        st.info(f"📊 Current Settings: Speed = {current_speed} km/h, Turnaround = {current_turnaround} min")
    
    def _render_equity_summary(self):
        """Render the equitable resource allocation summary."""
        self.layout.add_breadcrumb("Equitable Resource Allocation Summary")
        
        if self.data['allocation'].empty:
            st.info("⚖️ Allocation data is not available.")
            return
        
        # Calculate equity metrics
        allocation_summary = self.data['allocation'][['Route Name', 'Allocated_Buses', 'Unmet_Trips', 'Surplus_Trips']].copy()
        total_buses = allocation_summary['Allocated_Buses'].sum()
        allocation_summary['Efficiency (%)'] = (allocation_summary['Allocated_Buses'] / total_buses * 100).round(2)
        
        # Summary table
        def render_equity_table():
            st.dataframe(
                allocation_summary, 
                use_container_width=True,
                hide_index=True
            )
        
        self.layout.render_card(
            title="⚖️ Equity and Efficiency Overview",
            content_func=render_equity_table,
            help_text="Summary of resource allocation efficiency and equity across routes"
        )
        
        # Distribution chart
        def render_distribution_chart():
            fig = px.pie(
                allocation_summary, 
                values='Allocated_Buses', 
                names='Route Name',
                title="Bus Distribution by Route"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(font=dict(size=12))
            st.plotly_chart(fig, use_container_width=True)
        
        self.layout.render_card(
            title="🥧 Resource Distribution",
            content_func=render_distribution_chart,
            help_text="Proportional distribution of buses across all routes"
        )
        
        # Equity metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_unmet = allocation_summary['Unmet_Trips'].sum()
            st.metric(
                label="🔴 Total Unmet Trips",
                value=f"{total_unmet:,}",
                help="Total number of trips that could not be served"
            )
        
        with col2:
            total_surplus = allocation_summary['Surplus_Trips'].sum()
            st.metric(
                label="🟢 Total Surplus Trips",
                value=f"{total_surplus:,}",
                help="Total number of additional trips that could be served"
            )
        
        with col3:
            efficiency_score = ((total_surplus - total_unmet) / (total_surplus + total_unmet) * 100) if (total_surplus + total_unmet) > 0 else 0
            st.metric(
                label="📊 Efficiency Score",
                value=f"{efficiency_score:.1f}%",
                help="Overall efficiency of the current allocation"
            )
    
    def _show_onboarding(self):
        """Show onboarding tour for new users."""
        with st.expander("🎯 Welcome to the Enhanced Smart Bus Dashboard!", expanded=True):
            st.markdown("""
            ### Welcome! 👋
            
            This enhanced dashboard provides a modern, accessible interface for managing your Smart Bus Scheduling System.
            
            **Key Features:**
            - 🎨 **Modern Design**: Clean, professional interface with responsive layout
            - ♿ **Accessibility**: Full keyboard navigation and screen reader support
            - 📊 **Interactive Charts**: Hover, zoom, and explore your data
            - 🎛️ **Enhanced Controls**: Intuitive parameter adjustment with real-time feedback
            - 📱 **Mobile Friendly**: Works seamlessly on all device sizes
            
            **Navigation:**
            - Use the tabs above to switch between different sections
            - Access admin controls in the sidebar
            - Hover over elements for helpful tooltips
            - Use keyboard shortcuts: Ctrl+H for help, Ctrl+F for search
            
            **Getting Started:**
            1. Explore the **Bus Allocation Overview** to see current allocations
            2. Check **Demand Forecast** for passenger predictions
            3. Analyze **Trips vs Speed** to optimize performance
            4. Review **Equity Summary** for resource distribution
            
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Start Using Dashboard", type="primary", use_container_width=True):
                    st.session_state.onboarding_shown = True
                    self.config.user_preferences.onboarding_completed = True
                    self.config.save_config()
                    st.rerun()
            
            with col2:
                if st.button("📖 View Full Documentation", use_container_width=True):
                    st.info("Full documentation will be available in task 5")


def main():
    """Main application entry point."""
    try:
        dashboard = EnhancedDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please check the console for detailed error information.")
        # Log error for debugging
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()