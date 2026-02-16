"""
Integration module for the Smart Bus Dashboard Enhancement.

This module provides the main integration point that ties together
all the enhanced components and provides a unified interface.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import time

# Import all enhanced components
from src.config.settings import config_manager
from src.ui.layout import layout_manager
from src.ui.styles import style_manager
from src.ui.javascript import javascript_manager
from src.ui.visualization import visualization_engine, ChartConfig, ChartType
from src.data.controller import data_controller
from src.data.filters import filter_system, FilterSet
from src.enhancements.tooltips import tooltip_system
from src.enhancements.exports import export_controller
from src.enhancements.accessibility import accessibility_manager


@dataclass
class DashboardState:
    """Current state of the dashboard."""
    current_section: str
    active_filters: FilterSet
    user_preferences: Dict[str, Any]
    data_cache: Dict[str, pd.DataFrame]
    performance_metrics: Dict[str, float]


class EnhancedDashboard:
    """Main enhanced dashboard integration class."""
    
    def __init__(self):
        self.state = self._initialize_state()
        self.sections = config_manager.system_config.sections
        self.data_cache = {}
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_state(self) -> DashboardState:
        """Initialize dashboard state."""
        return DashboardState(
            current_section=config_manager.user_preferences.default_section,
            active_filters=FilterSet(),
            user_preferences=config_manager._user_preferences_to_dict(),
            data_cache={},
            performance_metrics={}
        )
    
    def _initialize_session_state(self) -> None:
        """Initialize Streamlit session state."""
        if 'dashboard_initialized' not in st.session_state:
            st.session_state.dashboard_initialized = True
            st.session_state.current_section = self.state.current_section
            st.session_state.filters_applied = False
            st.session_state.onboarding_completed = config_manager.user_preferences.onboarding_completed
            
            # Initialize filter system with empty filter set
            from src.data.filters import FilterSet
            st.session_state.active_filters = FilterSet()
            
            # Load last used filters if available
            self._load_last_used_filters()
    
    def _load_last_used_filters(self) -> None:
        """Load the last used filter set from user preferences."""
        from src.data.filters import FilterSet, DateRangeFilter, RouteFilter, PerformanceFilter, TextSearchFilter
        from datetime import date
        
        # Check if there's a "last_used" filter set
        if 'last_used' in config_manager.user_preferences.saved_filters:
            try:
                filter_data = config_manager.user_preferences.saved_filters['last_used']
                
                # Reconstruct FilterSet
                loaded_filter_set = FilterSet()
                
                # Date range filter
                if filter_data.get('date_range'):
                    dr_data = filter_data['date_range']
                    loaded_filter_set.date_range = DateRangeFilter(
                        start_date=date.fromisoformat(dr_data['start_date']) if dr_data['start_date'] else None,
                        end_date=date.fromisoformat(dr_data['end_date']) if dr_data['end_date'] else None,
                        date_column=dr_data['date_column'] or "Date"
                    )
                
                # Route filter
                if filter_data.get('routes'):
                    r_data = filter_data['routes']
                    loaded_filter_set.routes = RouteFilter(
                        selected_routes=r_data['selected_routes'],
                        include_all=r_data['include_all']
                    )
                
                # Performance filter
                if filter_data.get('performance'):
                    p_data = filter_data['performance']
                    loaded_filter_set.performance = PerformanceFilter(
                        min_speed=p_data['min_speed'],
                        max_speed=p_data['max_speed'],
                        min_boardings=p_data['min_boardings'],
                        max_boardings=p_data['max_boardings']
                    )
                
                # Text search filter
                if filter_data.get('text_search'):
                    ts_data = filter_data['text_search']
                    loaded_filter_set.text_search = TextSearchFilter(
                        search_term=ts_data['search_term'],
                        case_sensitive=ts_data['case_sensitive'],
                        exact_match=ts_data['exact_match']
                    )
                
                # Update session state
                st.session_state.active_filters = loaded_filter_set
                
            except Exception as e:
                # If loading fails, just use empty filter set
                pass
    
    def _save_current_filters_as_last_used(self) -> None:
        """Save current filters as last used for session persistence."""
        if 'active_filters' in st.session_state:
            filter_set = st.session_state.active_filters
            
            if not filter_set.is_empty():
                # Save to user preferences as "last_used"
                config_manager.user_preferences.saved_filters['last_used'] = {
                    'date_range': {
                        'start_date': filter_set.date_range.start_date.isoformat() if filter_set.date_range and filter_set.date_range.start_date else None,
                        'end_date': filter_set.date_range.end_date.isoformat() if filter_set.date_range and filter_set.date_range.end_date else None,
                        'date_column': filter_set.date_range.date_column if filter_set.date_range else None
                    } if filter_set.date_range else None,
                    'routes': {
                        'selected_routes': filter_set.routes.selected_routes if filter_set.routes else [],
                        'include_all': filter_set.routes.include_all if filter_set.routes else True
                    } if filter_set.routes else None,
                    'performance': {
                        'min_speed': filter_set.performance.min_speed if filter_set.performance else None,
                        'max_speed': filter_set.performance.max_speed if filter_set.performance else None,
                        'min_boardings': filter_set.performance.min_boardings if filter_set.performance else None,
                        'max_boardings': filter_set.performance.max_boardings if filter_set.performance else None
                    } if filter_set.performance else None,
                    'text_search': {
                        'search_term': filter_set.text_search.search_term if filter_set.text_search else "",
                        'case_sensitive': filter_set.text_search.case_sensitive if filter_set.text_search else False,
                        'exact_match': filter_set.text_search.exact_match if filter_set.text_search else False
                    } if filter_set.text_search else None
                }
                
                config_manager.save_config()
    
    def run(self) -> None:
        """Run the enhanced dashboard."""
        # Apply accessibility enhancements
        accessibility_css = accessibility_manager.apply_accessibility_enhancements()
        if accessibility_css:
            st.markdown(accessibility_css, unsafe_allow_html=True)
        
        # Render complete layout
        layout_manager.render_complete_layout(
            content_func=self._render_main_content,
            section=st.session_state.get('current_section', self.state.current_section)
        )
        
        # Show onboarding tour for new users
        if not st.session_state.get('onboarding_completed', False):
            self._show_onboarding()
        
        # Save current filters for session persistence (on every run to capture changes)
        self._save_current_filters_as_last_used()
    
    def _render_main_content(self) -> None:
        """Render main dashboard content."""
        # Navigation
        selected_section = layout_manager.render_navigation_tabs(
            self.sections,
            st.session_state.get('current_section', self.sections[0])
        )
        
        # Update current section
        if selected_section != st.session_state.get('current_section'):
            st.session_state.current_section = selected_section
            st.rerun()
        
        # Add breadcrumbs
        layout_manager.clear_breadcrumbs()
        layout_manager.add_breadcrumb("Dashboard")
        layout_manager.add_breadcrumb(selected_section)
        
        # Render filter panel in sidebar
        with st.sidebar:
            st.markdown("## 🔍 Data Filters")
            
            # Load appropriate data for filter configuration
            current_data = None
            if selected_section == "Bus Allocation Overview":
                current_data = self._load_data_with_caching('allocation')
            elif selected_section == "Demand Forecast":
                current_data = self._load_data_with_caching('forecast')
            elif selected_section == "Trips vs Speed Analysis":
                current_data = self._load_data_with_caching('sensitivity')
            else:
                # For summary section, use allocation data as default
                current_data = self._load_data_with_caching('allocation')
            
            # Render filter panel if data is available
            if current_data is not None and not current_data.empty:
                active_filters = layout_manager.render_filter_panel(current_data, selected_section.lower().replace(' ', '_'))
                
                # Render filter summary bar in main content
                layout_manager.render_filter_summary_bar(active_filters)
            else:
                st.warning("No data available for filtering")
        
        # Render section content
        if selected_section == "Bus Allocation Overview":
            self._render_bus_allocation_section()
        elif selected_section == "Demand Forecast":
            self._render_demand_forecast_section()
        elif selected_section == "Trips vs Speed Analysis":
            self._render_speed_analysis_section()
        elif selected_section == "Equitable Resource Allocation Summary":
            self._render_resource_summary_section()
    
    def _render_bus_allocation_section(self) -> None:
        """Render bus allocation overview section."""
        layout_manager.render_card(
            title="🚌 Bus Allocation Overview",
            content_func=self._render_allocation_content,
            help_text="Optimal bus allocation based on demand forecasting and operational constraints"
        )
        
        # Contextual help
        tooltip_system.render_contextual_help("bus_allocation")
    
    def _render_allocation_content(self) -> None:
        """Render bus allocation content."""
        try:
            # Load allocation data
            allocation_data = self._load_data_with_caching('allocation')
            
            if allocation_data is not None and not allocation_data.empty:
                # Apply filters
                filtered_data = self._apply_current_filters(allocation_data)
                
                # Create visualization
                chart_config = ChartConfig(
                    title="Bus Allocation by Route",
                    chart_type=ChartType.BAR,
                    x_column="Route" if "Route" in filtered_data.columns else filtered_data.columns[0],
                    y_column="Buses_Required" if "Buses_Required" in filtered_data.columns else filtered_data.select_dtypes(include=['number']).columns[0],
                    height=400,
                    accessibility_mode=accessibility_manager.settings.accessibility_mode
                )
                
                # Render chart with controls
                fig = visualization_engine.render_chart_with_controls(filtered_data, chart_config)
                st.plotly_chart(fig, use_container_width=True)
                
                # Data summary
                self._render_data_summary(filtered_data, "Bus Allocation")
                
                # Export options
                export_controller.render_export_controls(filtered_data, "Bus Allocation")
                
            else:
                st.warning("No bus allocation data available. Please check data files.")
                
        except Exception as e:
            st.error(f"Error loading bus allocation data: {str(e)}")
    
    def _render_demand_forecast_section(self) -> None:
        """Render demand forecast section."""
        layout_manager.render_card(
            title="📈 Demand Forecast",
            content_func=self._render_forecast_content,
            help_text="Machine learning predictions of passenger boarding numbers"
        )
        
        # Contextual help
        tooltip_system.render_contextual_help("demand_forecast")
    
    def _render_forecast_content(self) -> None:
        """Render demand forecast content."""
        try:
            # Load forecast data
            forecast_data = self._load_data_with_caching('forecast')
            
            if forecast_data is not None and not forecast_data.empty:
                # Apply filters
                filtered_data = self._apply_current_filters(forecast_data)
                
                # Create visualization
                chart_config = ChartConfig(
                    title="Predicted Daily Boardings",
                    chart_type=ChartType.LINE,
                    x_column="Day" if "Day" in filtered_data.columns else filtered_data.columns[0],
                    y_column="Predicted_Boardings" if "Predicted_Boardings" in filtered_data.columns else filtered_data.select_dtypes(include=['number']).columns[0],
                    height=400,
                    accessibility_mode=accessibility_manager.settings.accessibility_mode
                )
                
                # Render chart
                fig = visualization_engine.render_chart_with_controls(filtered_data, chart_config)
                st.plotly_chart(fig, use_container_width=True)
                
                # Data summary
                self._render_data_summary(filtered_data, "Demand Forecast")
                
                # Export options
                export_controller.render_export_controls(filtered_data, "Demand Forecast")
                
            else:
                st.warning("No demand forecast data available. Please check data files.")
                
        except Exception as e:
            st.error(f"Error loading demand forecast data: {str(e)}")
    
    def _render_speed_analysis_section(self) -> None:
        """Render speed analysis section."""
        layout_manager.render_card(
            title="⚡ Trips vs Speed Analysis",
            content_func=self._render_speed_content,
            help_text="Analysis of how bus speed affects trip capacity and efficiency"
        )
        
        # Contextual help
        tooltip_system.render_contextual_help("speed_analysis")
    
    def _render_speed_content(self) -> None:
        """Render speed analysis content."""
        try:
            # Load sensitivity data
            sensitivity_data = self._load_data_with_caching('sensitivity')
            
            if sensitivity_data is not None and not sensitivity_data.empty:
                # Apply filters
                filtered_data = self._apply_current_filters(sensitivity_data)
                
                # Create visualization
                chart_config = ChartConfig(
                    title="Trips per Bus vs Speed",
                    chart_type=ChartType.LINE,
                    x_column="Speed_kmh" if "Speed_kmh" in filtered_data.columns else filtered_data.columns[0],
                    y_column="Trips_per_Bus" if "Trips_per_Bus" in filtered_data.columns else filtered_data.select_dtypes(include=['number']).columns[0],
                    height=400,
                    accessibility_mode=accessibility_manager.settings.accessibility_mode
                )
                
                # Render chart
                fig = visualization_engine.render_chart_with_controls(filtered_data, chart_config)
                st.plotly_chart(fig, use_container_width=True)
                
                # Interactive speed analysis
                self._render_speed_controls(filtered_data)
                
                # Data summary
                self._render_data_summary(filtered_data, "Speed Analysis")
                
                # Export options
                export_controller.render_export_controls(filtered_data, "Speed Analysis")
                
            else:
                st.warning("No speed analysis data available. Please check data files.")
                
        except Exception as e:
            st.error(f"Error loading speed analysis data: {str(e)}")
    
    def _render_resource_summary_section(self) -> None:
        """Render resource allocation summary section."""
        layout_manager.render_card(
            title="⚖️ Equitable Resource Allocation Summary",
            content_func=self._render_summary_content,
            help_text="Summary of resource allocation across all routes and performance metrics"
        )
    
    def _render_summary_content(self) -> None:
        """Render resource summary content."""
        try:
            # Load all data types
            all_data = {}
            for data_type in ['allocation', 'forecast', 'sensitivity']:
                data = self._load_data_with_caching(data_type)
                if data is not None and not data.empty:
                    all_data[data_type] = data
            
            if all_data:
                # Create summary metrics
                self._render_summary_metrics(all_data)
                
                # Create combined visualization
                self._render_combined_analysis(all_data)
                
                # Export all data
                export_controller.render_export_controls(all_data, "Complete Dashboard")
                
            else:
                st.warning("No data available for summary. Please check data files.")
                
        except Exception as e:
            st.error(f"Error creating resource summary: {str(e)}")
    
    def _render_speed_controls(self, data: pd.DataFrame) -> None:
        """Render interactive speed controls."""
        st.markdown("### 🎛️ Interactive Speed Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get current admin settings
            current_speed = st.session_state.get('admin_speed', 40)
            current_turnaround = st.session_state.get('admin_turnaround', 15)
            
            st.metric("Current Speed Setting", f"{current_speed} km/h")
            st.metric("Current Turnaround Time", f"{current_turnaround} min")
        
        with col2:
            # Calculate impact
            if 'Speed_kmh' in data.columns and 'Trips_per_Bus' in data.columns:
                # Find closest speed in data
                closest_speed_idx = (data['Speed_kmh'] - current_speed).abs().idxmin()
                predicted_trips = data.loc[closest_speed_idx, 'Trips_per_Bus']
                
                st.metric("Predicted Trips per Bus", f"{predicted_trips:.1f}")
                
                # Calculate efficiency
                efficiency = predicted_trips / current_speed * 100
                st.metric("Speed Efficiency", f"{efficiency:.1f}%")
    
    def _render_summary_metrics(self, all_data: Dict[str, pd.DataFrame]) -> None:
        """Render summary metrics."""
        st.markdown("### 📊 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'allocation' in all_data:
                total_buses = all_data['allocation']['Buses_Required'].sum() if 'Buses_Required' in all_data['allocation'].columns else 0
                st.metric("Total Buses Required", int(total_buses))
        
        with col2:
            if 'forecast' in all_data:
                total_boardings = all_data['forecast']['Predicted_Boardings'].sum() if 'Predicted_Boardings' in all_data['forecast'].columns else 0
                st.metric("Total Predicted Boardings", f"{int(total_boardings):,}")
        
        with col3:
            if 'allocation' in all_data:
                total_routes = len(all_data['allocation'])
                st.metric("Total Routes", total_routes)
        
        with col4:
            # Calculate average efficiency
            current_speed = st.session_state.get('admin_speed', 40)
            if 'sensitivity' in all_data and 'Trips_per_Bus' in all_data['sensitivity'].columns:
                avg_trips = all_data['sensitivity']['Trips_per_Bus'].mean()
                efficiency = avg_trips / current_speed * 100
                st.metric("System Efficiency", f"{efficiency:.1f}%")
    
    def _render_combined_analysis(self, all_data: Dict[str, pd.DataFrame]) -> None:
        """Render combined analysis visualization."""
        st.markdown("### 🔄 Integrated Analysis")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Resource Distribution", "Performance Trends", "Optimization Opportunities"])
        
        with tab1:
            if 'allocation' in all_data:
                # Resource distribution pie chart
                allocation_data = all_data['allocation']
                if 'Route' in allocation_data.columns and 'Buses_Required' in allocation_data.columns:
                    chart_config = ChartConfig(
                        title="Bus Allocation Distribution",
                        chart_type=ChartType.PIE,
                        x_column="Route",
                        y_column="Buses_Required",
                        height=400
                    )
                    
                    fig = visualization_engine.render_interactive_chart(allocation_data, chart_config)
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if 'forecast' in all_data:
                # Performance trends
                forecast_data = all_data['forecast']
                if 'Day' in forecast_data.columns and 'Predicted_Boardings' in forecast_data.columns:
                    chart_config = ChartConfig(
                        title="Boarding Trends",
                        chart_type=ChartType.AREA,
                        x_column="Day",
                        y_column="Predicted_Boardings",
                        height=400
                    )
                    
                    fig = visualization_engine.render_interactive_chart(forecast_data, chart_config)
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            if 'sensitivity' in all_data:
                # Optimization opportunities
                sensitivity_data = all_data['sensitivity']
                if 'Speed_kmh' in sensitivity_data.columns and 'Trips_per_Bus' in sensitivity_data.columns:
                    chart_config = ChartConfig(
                        title="Speed Optimization Opportunities",
                        chart_type=ChartType.SCATTER,
                        x_column="Speed_kmh",
                        y_column="Trips_per_Bus",
                        height=400
                    )
                    
                    fig = visualization_engine.render_interactive_chart(sensitivity_data, chart_config)
                    st.plotly_chart(fig, use_container_width=True)
    
    def _load_data_with_caching(self, data_type: str) -> Optional[pd.DataFrame]:
        """Load data with caching."""
        if data_type in self.data_cache:
            return self.data_cache[data_type]
        
        try:
            data = data_controller.load_csv_data(
                data_controller.data_files[data_type],
                use_cache=True
            )
            self.data_cache[data_type] = data
            return data
        except Exception as e:
            st.error(f"Failed to load {data_type} data: {str(e)}")
            return None
    
    def _apply_current_filters(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply current filter set to data."""
        from src.data.filters import FilterSet
        
        # Get active filters from session state
        if 'active_filters' in st.session_state:
            active_filters = st.session_state['active_filters']
            if isinstance(active_filters, FilterSet) and not active_filters.is_empty():
                try:
                    filtered_data = filter_system.apply_filters(data, active_filters)
                    
                    # Show filter impact if data was filtered
                    if len(filtered_data) != len(data):
                        st.info(f"🔍 Filters applied: Showing {len(filtered_data)} of {len(data)} records ({len(filtered_data)/len(data)*100:.1f}%)")
                    
                    return filtered_data
                except Exception as e:
                    st.warning(f"Error applying filters: {str(e)}. Showing unfiltered data.")
                    return data
        
        return data
    
    def _render_data_summary(self, data: pd.DataFrame, section_name: str) -> None:
        """Render data summary information."""
        with st.expander(f"📋 {section_name} Data Summary"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", len(data))
            
            with col2:
                st.metric("Columns", len(data.columns))
            
            with col3:
                missing_values = data.isnull().sum().sum()
                st.metric("Missing Values", missing_values)
            
            # Show data preview
            st.markdown("**Data Preview:**")
            st.dataframe(data.head(), use_container_width=True)
    
    def _show_onboarding(self) -> None:
        """Show onboarding tour."""
        with st.container():
            tooltip_system.show_onboarding_tour()
    
    def render_admin_panel(self) -> None:
        """Render admin panel for system management."""
        st.markdown("## 🔧 System Administration")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Data Quality", "Accessibility", "Export"])
        
        with tab1:
            visualization_engine.render_performance_dashboard()
        
        with tab2:
            self._render_data_quality_panel()
        
        with tab3:
            accessibility_manager.render_accessibility_controls()
            accessibility_manager.render_accessibility_report()
        
        with tab4:
            self._render_export_management()
    
    def _render_data_quality_panel(self) -> None:
        """Render data quality management panel."""
        st.markdown("### 📊 Data Quality Management")
        
        summaries = data_controller.get_all_data_summaries()
        
        for data_type, summary in summaries.items():
            with st.expander(f"{data_type.title()} Data Quality"):
                if 'error' in summary:
                    st.error(f"Error: {summary['error']}")
                else:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Rows", summary.get('shape', [0, 0])[0])
                    
                    with col2:
                        st.metric("Columns", summary.get('shape', [0, 0])[1])
                    
                    with col3:
                        quality_score = summary.get('quality_score', 0)
                        st.metric("Quality Score", f"{quality_score:.1%}")
    
    def _render_export_management(self) -> None:
        """Render export management interface."""
        st.markdown("### 📥 Export Management")
        
        # Dashboard state export
        if st.button("Export Dashboard State"):
            dashboard_state = {
                'current_section': st.session_state.get('current_section'),
                'user_preferences': config_manager._user_preferences_to_dict(),
                'timestamp': time.time()
            }
            
            result = export_controller.export_dashboard_state(dashboard_state)
            
            if result.success:
                st.download_button(
                    label="Download Dashboard State",
                    data=result.download_data,
                    file_name=result.filename,
                    mime="application/json"
                )
            else:
                st.error(f"Export failed: {result.error_message}")


# Global enhanced dashboard instance
enhanced_dashboard = EnhancedDashboard()