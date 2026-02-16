"""
Enhanced layout manager for the Smart Bus Dashboard.

This module provides responsive layout management, navigation components,
and modern UI structure for the dashboard application.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING
from dataclasses import dataclass
from src.config.settings import config_manager, Theme
from src.ui.styles import style_manager
from src.ui.javascript import javascript_manager
from src.ui.navigation import navigation_controller

if TYPE_CHECKING:
    from src.data.filters import FilterSet


@dataclass
class LayoutConfig:
    """Configuration for dashboard layout."""
    show_sidebar: bool = True
    show_header: bool = True
    show_footer: bool = True
    responsive: bool = True
    theme: Theme = Theme.LIGHT
    custom_css: Optional[str] = None
    javascript_features: List[str] = None


@dataclass
class GridBreakpoint:
    """Responsive grid breakpoint configuration."""
    name: str
    min_width: int
    max_width: Optional[int]
    columns: int
    gutter: int


class ResponsiveGridSystem:
    """Advanced responsive grid system for dashboard layout."""
    
    def __init__(self):
        self.breakpoints = [
            GridBreakpoint("xs", 0, 575, 1, 16),
            GridBreakpoint("sm", 576, 767, 2, 16),
            GridBreakpoint("md", 768, 991, 2, 20),
            GridBreakpoint("lg", 992, 1199, 3, 24),
            GridBreakpoint("xl", 1200, 1399, 3, 24),
            GridBreakpoint("xxl", 1400, None, 4, 32)
        ]
    
    def get_current_breakpoint(self, width: int) -> GridBreakpoint:
        """Get the current breakpoint based on screen width."""
        for breakpoint in reversed(self.breakpoints):
            if width >= breakpoint.min_width:
                if breakpoint.max_width is None or width <= breakpoint.max_width:
                    return breakpoint
        return self.breakpoints[0]  # Default to xs
    
    def generate_grid_css(self) -> str:
        """Generate CSS for responsive grid system."""
        css = """
        <style>
        /* Enhanced Responsive Grid System */
        .dashboard-grid {
            display: grid;
            gap: var(--grid-gutter, 1rem);
            width: 100%;
            margin: 0 auto;
        }
        
        .grid-item {
            min-width: 0; /* Prevent grid blowout */
        }
        
        .grid-item-full { grid-column: 1 / -1; }
        .grid-item-half { grid-column: span 2; }
        .grid-item-third { grid-column: span 1; }
        
        /* Responsive Grid Classes */
        """
        
        for bp in self.breakpoints:
            if bp.max_width:
                media_query = f"@media (min-width: {bp.min_width}px) and (max-width: {bp.max_width}px)"
            else:
                media_query = f"@media (min-width: {bp.min_width}px)"
            
            css += f"""
        {media_query} {{
            .dashboard-grid {{
                grid-template-columns: repeat({bp.columns}, 1fr);
                --grid-gutter: {bp.gutter}px;
            }}
            
            .grid-{bp.name}-1 {{ grid-column: span 1; }}
            .grid-{bp.name}-2 {{ grid-column: span 2; }}
            .grid-{bp.name}-3 {{ grid-column: span 3; }}
            .grid-{bp.name}-4 {{ grid-column: span 4; }}
            .grid-{bp.name}-full {{ grid-column: 1 / -1; }}
        }}
        """
        
        css += """
        /* Container Max Widths */
        .container {
            width: 100%;
            padding-left: var(--spacing-md);
            padding-right: var(--spacing-md);
            margin-left: auto;
            margin-right: auto;
        }
        
        @media (min-width: 576px) { .container { max-width: 540px; } }
        @media (min-width: 768px) { .container { max-width: 720px; } }
        @media (min-width: 992px) { .container { max-width: 960px; } }
        @media (min-width: 1200px) { .container { max-width: 1140px; } }
        @media (min-width: 1400px) { .container { max-width: 1320px; } }
        
        /* Fluid Container */
        .container-fluid {
            width: 100%;
            padding-left: var(--spacing-md);
            padding-right: var(--spacing-md);
        }
        </style>
        """
        
        return css


class DashboardLayout:
    """Enhanced layout manager for the Smart Bus Dashboard."""
    
    def __init__(self, config: Optional[LayoutConfig] = None):
        self.config = config or LayoutConfig()
        self.current_section = None
        self.breadcrumbs = []
        self.grid_system = ResponsiveGridSystem()
        # Remove automatic page config setup - handled by main dashboard
    
    def _setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=config_manager.system_config.page_title,
            page_icon=config_manager.system_config.page_icon,
            layout=config_manager.system_config.layout,
            initial_sidebar_state="expanded" if self.config.show_sidebar else "collapsed",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': f"{config_manager.system_config.app_name} v{config_manager.system_config.version}"
            }
        )
    
    def render_complete_layout(self, content_func: Callable, section: str = None) -> None:
        """Render the complete dashboard layout with all components."""
        # Apply styles and JavaScript
        self._inject_styles_and_scripts()
        
        # Apply responsive layout adjustments
        self.apply_responsive_layout()
        
        # Set current section
        if section:
            self.current_section = section
            navigation_controller.current_section = section
        
        # Render layout components
        if self.config.show_header:
            self.render_header()
        
        # Create main layout structure with responsive container
        main_container = st.container()
        with main_container:
            st.markdown('<div class="container-responsive">', unsafe_allow_html=True)
            
            # Add skip links for accessibility
            self._render_skip_links()
            
            # Render enhanced navigation system
            self.render_enhanced_navigation()
            
            # Render breadcrumbs if available
            if section:
                navigation_controller.render_breadcrumbs(section)
            
            # Main content area with responsive grid
            st.markdown('<main id="main-content" role="main">', unsafe_allow_html=True)
            
            # Render main content
            content_func()
            
            st.markdown('</main>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Sidebar with responsive behavior
        if self.config.show_sidebar:
            with st.sidebar:
                self.render_adaptive_sidebar()
        
        # Footer
        if self.config.show_footer:
            self.render_footer()
    
    def _inject_styles_and_scripts(self):
        """Inject custom CSS and JavaScript."""
        # Get user preferences
        user_prefs = config_manager.user_preferences
        
        # Generate and inject CSS
        css = style_manager.get_complete_css(
            theme=user_prefs.theme,
            accessibility=user_prefs.accessibility_settings
        )
        
        # Add responsive grid system CSS
        css += self.grid_system.generate_grid_css()
        
        if self.config.custom_css:
            css += f"\n<style>{self.config.custom_css}</style>"
        
        st.markdown(css, unsafe_allow_html=True)
        
        # Generate and inject JavaScript
        js_features = self.config.javascript_features or ['base', 'tooltips', 'accessibility', 'animations', 'responsive']
        javascript = javascript_manager.get_complete_javascript(js_features)
        st.markdown(javascript, unsafe_allow_html=True)
        
        # Inject navigation-specific styles and JavaScript
        navigation_controller.inject_navigation_styles()
        navigation_controller.inject_navigation_javascript()
    
    def _render_skip_links(self):
        """Render accessibility skip links."""
        skip_links_html = """
        <div class="skip-links" role="navigation" aria-label="Skip links">
            <a href="#main-content" class="skip-link">Skip to main content</a>
            <a href="#navigation" class="skip-link">Skip to navigation</a>
            <a href="#sidebar" class="skip-link">Skip to sidebar</a>
        </div>
        """
        st.markdown(skip_links_html, unsafe_allow_html=True)
    
    def render_header(self):
        """Render the enhanced dashboard header."""
        header_html = f"""
        <div class="main-header" role="banner">
            <h1>{config_manager.system_config.app_name}</h1>
            <div class="subtitle">
                <span class="location-info">📍 Starting Point: Shirpur</span>
                <span class="user-role">👤 Administrator View</span>
            </div>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the enhanced sidebar with controls and navigation."""
        st.markdown('<div id="sidebar" class="sidebar-enhanced">', unsafe_allow_html=True)
        
        # Admin Controls Section
        with st.expander("🎛️ Admin Controls", expanded=True):
            self._render_admin_controls()
        
        # Quick Actions Section
        with st.expander("⚡ Quick Actions", expanded=False):
            self._render_quick_actions()
        
        # Settings Section
        with st.expander("⚙️ Settings", expanded=False):
            self._render_settings()
        
        # Help Section
        with st.expander("❓ Help & Info", expanded=False):
            self._render_help_section()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_admin_controls(self):
        """Render admin control widgets."""
        # Speed control with enhanced UI
        st.markdown("**🚌 Bus Speed Configuration**")
        speed = st.slider(
            "Average Bus Speed (km/h)",
            min_value=30,
            max_value=60,
            value=40,
            step=1,
            help="Adjust the average speed of buses for route calculations"
        )
        
        # Turnaround time control
        st.markdown("**🔄 Turnaround Time Settings**")
        turnaround = st.slider(
            "Turnaround Time (minutes)",
            min_value=5,
            max_value=30,
            value=15,
            step=1,
            help="Time required for buses to turn around at route endpoints"
        )
        
        # Store values in session state
        st.session_state['admin_speed'] = speed
        st.session_state['admin_turnaround'] = turnaround
        
        # Real-time preview
        if st.checkbox("Show Real-time Preview", value=True):
            st.info(f"Current Settings: {speed} km/h, {turnaround} min turnaround")
    
    def _render_quick_actions(self):
        """Render quick action buttons."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
            
            if st.button("📊 Export Report", use_container_width=True):
                st.info("Export functionality will be implemented in task 7")
        
        with col2:
            if st.button("🎯 Reset Filters", use_container_width=True):
                # Clear filter session state
                for key in list(st.session_state.keys()):
                    if key.startswith('filter_'):
                        del st.session_state[key]
                # Reset filter system
                from src.data.filters import filter_system, FilterSet
                st.session_state['active_filters'] = FilterSet()
                st.rerun()
            
            if st.button("💾 Save Settings", use_container_width=True):
                config_manager.save_config()
                st.success("Settings saved!")
    
    def render_filter_panel(self, data: pd.DataFrame, data_type: str = "general") -> 'FilterSet':
        """
        Render comprehensive filter panel with all filter types.
        
        Args:
            data: DataFrame to create filters for
            data_type: Type of data being filtered
            
        Returns:
            FilterSet with current filter configuration
        """
        from src.data.filters import (
            filter_system, FilterSet, DateRangeFilter, RouteFilter, 
            PerformanceFilter, TextSearchFilter, NumericRangeFilter, CategoricalFilter
        )
        
        st.markdown("### 🔍 Data Filters")
        
        # Initialize filter set
        if 'active_filters' not in st.session_state:
            st.session_state['active_filters'] = FilterSet()
        
        current_filters = st.session_state['active_filters']
        
        # Create filter tabs
        filter_tabs = st.tabs(["🔍 Search", "📅 Date Range", "🚌 Routes", "⚡ Performance", "📊 Advanced"])
        
        # Text Search Filter
        with filter_tabs[0]:
            st.markdown("#### Global Search")
            
            search_term = st.text_input(
                "Search across all data",
                value=current_filters.text_search.search_term if current_filters.text_search else "",
                placeholder="Enter search term...",
                help="Search for specific values across all text columns"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                case_sensitive = st.checkbox(
                    "Case sensitive",
                    value=current_filters.text_search.case_sensitive if current_filters.text_search else False
                )
            with col2:
                exact_match = st.checkbox(
                    "Exact match",
                    value=current_filters.text_search.exact_match if current_filters.text_search else False
                )
            
            # Smart search suggestions
            if search_term:
                smart_filter = filter_system.create_smart_filter(data, search_term)
                if not smart_filter.is_empty():
                    st.info("💡 Smart filter suggestions detected! Check other tabs for auto-configured filters.")
            
            # Update text search filter
            if search_term.strip():
                current_filters.text_search = TextSearchFilter(
                    search_term=search_term,
                    case_sensitive=case_sensitive,
                    exact_match=exact_match
                )
            else:
                current_filters.text_search = None
        
        # Date Range Filter
        with filter_tabs[1]:
            st.markdown("#### Date Range Filter")
            
            # Get available date range
            date_columns = [col for col in data.columns if 'date' in col.lower() or 'day' in col.lower()]
            
            if date_columns:
                date_column = st.selectbox(
                    "Date Column",
                    date_columns,
                    help="Select the column to use for date filtering"
                )
                
                min_date, max_date = filter_system.get_date_range(data, date_column)
                
                if min_date and max_date:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        start_date = st.date_input(
                            "Start Date",
                            value=current_filters.date_range.start_date if current_filters.date_range else min_date,
                            min_value=min_date,
                            max_value=max_date,
                            help="Select the start date for filtering"
                        )
                    
                    with col2:
                        end_date = st.date_input(
                            "End Date",
                            value=current_filters.date_range.end_date if current_filters.date_range else max_date,
                            min_value=min_date,
                            max_value=max_date,
                            help="Select the end date for filtering"
                        )
                    
                    # Update date range filter
                    current_filters.date_range = DateRangeFilter(
                        start_date=start_date,
                        end_date=end_date,
                        date_column=date_column
                    )
                    
                    # Show date range summary
                    filtered_data = current_filters.date_range.apply(data)
                    st.info(f"📊 Date filter will show {len(filtered_data)} of {len(data)} records")
                else:
                    st.warning("No valid dates found in the selected column")
            else:
                st.info("No date columns detected in the data")
                current_filters.date_range = None
        
        # Route Filter
        with filter_tabs[2]:
            st.markdown("#### Route Filter")
            
            available_routes = filter_system.get_available_routes(data)
            
            if available_routes:
                include_all = st.checkbox(
                    "Include all routes",
                    value=current_filters.routes.include_all if current_filters.routes else True,
                    help="Check to include all routes, uncheck to select specific routes"
                )
                
                selected_routes = []
                if not include_all:
                    selected_routes = st.multiselect(
                        "Select Routes",
                        available_routes,
                        default=current_filters.routes.selected_routes if current_filters.routes else [],
                        help="Select specific routes to include in the analysis"
                    )
                
                # Update route filter
                current_filters.routes = RouteFilter(
                    selected_routes=selected_routes,
                    include_all=include_all
                )
                
                # Show route filter summary
                if not include_all and selected_routes:
                    filtered_data = current_filters.routes.apply(data)
                    st.info(f"🚌 Route filter will show {len(filtered_data)} of {len(data)} records")
            else:
                st.info("No route information detected in the data")
                current_filters.routes = None
        
        # Performance Filter
        with filter_tabs[3]:
            st.markdown("#### Performance Metrics Filter")
            
            # Speed filters
            if 'Speed_kmh' in data.columns:
                st.markdown("**Speed Range (km/h)**")
                speed_min, speed_max = data['Speed_kmh'].min(), data['Speed_kmh'].max()
                
                speed_range = st.slider(
                    "Speed Range",
                    min_value=float(speed_min),
                    max_value=float(speed_max),
                    value=(
                        current_filters.performance.min_speed if current_filters.performance and current_filters.performance.min_speed else float(speed_min),
                        current_filters.performance.max_speed if current_filters.performance and current_filters.performance.max_speed else float(speed_max)
                    ),
                    help="Filter data by speed range"
                )
                
                min_speed, max_speed = speed_range
            else:
                min_speed = max_speed = None
            
            # Boarding filters
            boarding_cols = [col for col in data.columns if 'boarding' in col.lower()]
            min_boardings = max_boardings = None
            
            if boarding_cols:
                boarding_col = boarding_cols[0]
                st.markdown(f"**{boarding_col} Range**")
                
                boarding_min, boarding_max = data[boarding_col].min(), data[boarding_col].max()
                
                boarding_range = st.slider(
                    f"{boarding_col} Range",
                    min_value=int(boarding_min),
                    max_value=int(boarding_max),
                    value=(
                        current_filters.performance.min_boardings if current_filters.performance and current_filters.performance.min_boardings else int(boarding_min),
                        current_filters.performance.max_boardings if current_filters.performance and current_filters.performance.max_boardings else int(boarding_max)
                    ),
                    help=f"Filter data by {boarding_col.lower()} range"
                )
                
                min_boardings, max_boardings = boarding_range
            
            # Update performance filter
            if min_speed is not None or min_boardings is not None:
                current_filters.performance = PerformanceFilter(
                    min_speed=min_speed,
                    max_speed=max_speed,
                    min_boardings=min_boardings,
                    max_boardings=max_boardings
                )
            else:
                current_filters.performance = None
        
        # Advanced Filters
        with filter_tabs[4]:
            st.markdown("#### Advanced Filters")
            
            # Numeric range filters
            numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
            # Remove columns already handled in performance
            numeric_columns = [col for col in numeric_columns if col not in ['Speed_kmh'] and 'boarding' not in col.lower()]
            
            if numeric_columns:
                st.markdown("**Numeric Range Filters**")
                
                # Clear existing numeric filters if not in current selection
                current_filters.numeric_ranges = []
                
                for col in numeric_columns[:3]:  # Limit to 3 for UI space
                    col_min, col_max = data[col].min(), data[col].max()
                    
                    if col_min != col_max:  # Only show if there's variation
                        col_range = st.slider(
                            f"{col} Range",
                            min_value=float(col_min),
                            max_value=float(col_max),
                            value=(float(col_min), float(col_max)),
                            help=f"Filter data by {col} range"
                        )
                        
                        if col_range != (float(col_min), float(col_max)):
                            current_filters.numeric_ranges.append(
                                NumericRangeFilter(
                                    column=col,
                                    min_value=col_range[0],
                                    max_value=col_range[1]
                                )
                            )
            
            # Categorical filters
            categorical_values = filter_system.get_categorical_values(data)
            
            if categorical_values:
                st.markdown("**Categorical Filters**")
                
                # Clear existing categorical filters
                current_filters.categorical = []
                
                for col, values in list(categorical_values.items())[:2]:  # Limit to 2 for UI space
                    if len(values) > 1 and len(values) <= 20:  # Only show if reasonable number of options
                        selected_values = st.multiselect(
                            f"Filter by {col}",
                            values,
                            help=f"Select specific values for {col}"
                        )
                        
                        if selected_values:
                            current_filters.categorical.append(
                                CategoricalFilter(
                                    column=col,
                                    selected_values=selected_values
                                )
                            )
        
        # Filter Summary and Actions
        st.markdown("---")
        
        # Show filter summary
        filter_summary = current_filters.get_summary()
        
        if filter_summary['total_filters'] > 0:
            st.markdown("#### 📋 Active Filters")
            
            for filter_info in filter_summary['active_filters']:
                st.info(f"**{filter_info['type'].replace('_', ' ').title()}**: {filter_info['description']}")
            
            # Show filtered data count
            try:
                filtered_data = current_filters.apply_all(data)
                st.success(f"✅ Filters will show **{len(filtered_data)}** of **{len(data)}** records ({len(filtered_data)/len(data)*100:.1f}%)")
            except Exception as e:
                st.error(f"Error applying filters: {str(e)}")
        else:
            st.info("No filters currently active")
        
        # Filter Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Filter Set", use_container_width=True):
                self._save_filter_set_dialog(current_filters)
        
        with col2:
            if st.button("📂 Load Filter Set", use_container_width=True):
                self._load_filter_set_dialog()
        
        with col3:
            if st.button("🗑️ Clear All Filters", use_container_width=True):
                st.session_state['active_filters'] = FilterSet()
                st.rerun()
        
        # Update session state
        st.session_state['active_filters'] = current_filters
        
        return current_filters
    
    def _save_filter_set_dialog(self, filter_set: 'FilterSet'):
        """Show dialog to save current filter set."""
        from src.data.filters import filter_system
        
        with st.form("save_filter_form"):
            st.markdown("#### Save Filter Set")
            
            filter_name = st.text_input(
                "Filter Set Name",
                placeholder="Enter a name for this filter set...",
                help="Give your filter set a descriptive name"
            )
            
            if st.form_submit_button("Save Filter Set"):
                if filter_name.strip():
                    filter_system.save_filter_set(filter_name.strip(), filter_set)
                    
                    # Also save to user preferences for persistence
                    config_manager.user_preferences.saved_filters[filter_name.strip()] = {
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
                    st.success(f"Filter set '{filter_name}' saved successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a name for the filter set")
    
    def _load_filter_set_dialog(self):
        """Show dialog to load a saved filter set."""
        from src.data.filters import filter_system, FilterSet, DateRangeFilter, RouteFilter, PerformanceFilter, TextSearchFilter
        from datetime import date
        
        saved_filters = list(config_manager.user_preferences.saved_filters.keys())
        
        if saved_filters:
            with st.form("load_filter_form"):
                st.markdown("#### Load Filter Set")
                
                selected_filter = st.selectbox(
                    "Select Filter Set",
                    saved_filters,
                    help="Choose a saved filter set to load"
                )
                
                if st.form_submit_button("Load Filter Set"):
                    if selected_filter:
                        try:
                            # Load from user preferences
                            filter_data = config_manager.user_preferences.saved_filters[selected_filter]
                            
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
                            st.session_state['active_filters'] = loaded_filter_set
                            st.success(f"Filter set '{selected_filter}' loaded successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error loading filter set: {str(e)}")
        else:
            st.info("No saved filter sets found. Save a filter set first to load it later.")
    
    def render_filter_summary_bar(self, filter_set: 'FilterSet') -> None:
        """Render a compact filter summary bar."""
        if not filter_set or filter_set.is_empty():
            return
        
        summary = filter_set.get_summary()
        
        if summary['total_filters'] > 0:
            with st.container():
                st.markdown("---")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**🔍 Active Filters ({summary['total_filters']}):**")
                    
                    filter_chips = []
                    for filter_info in summary['active_filters']:
                        filter_chips.append(f"`{filter_info['type'].replace('_', ' ').title()}`")
                    
                    st.markdown(" • ".join(filter_chips))
                
                with col2:
                    if st.button("🗑️ Clear", key="clear_filters_summary"):
                        st.session_state['active_filters'] = FilterSet()
                        st.rerun()
    
    def _render_settings(self):
        """Render settings controls."""
        # Theme selection
        theme_options = ["Light", "Dark", "Auto"]
        current_theme = config_manager.user_preferences.theme.value.title()
        
        selected_theme = st.selectbox(
            "🎨 Theme",
            theme_options,
            index=theme_options.index(current_theme) if current_theme in theme_options else 0,
            help="Choose your preferred color theme"
        )
        
        # Update theme if changed
        if selected_theme.lower() != config_manager.user_preferences.theme.value:
            config_manager.user_preferences.theme = Theme(selected_theme.lower())
            config_manager.save_config()
            st.rerun()
        
        # Accessibility settings
        st.markdown("**♿ Accessibility**")
        
        high_contrast = st.checkbox(
            "High Contrast Mode",
            value=config_manager.user_preferences.accessibility_settings.high_contrast,
            help="Increase contrast for better visibility"
        )
        
        large_text = st.checkbox(
            "Large Text Mode",
            value=config_manager.user_preferences.accessibility_settings.large_text,
            help="Increase text size for better readability"
        )
        
        reduced_motion = st.checkbox(
            "Reduce Motion",
            value=config_manager.user_preferences.accessibility_settings.reduced_motion,
            help="Minimize animations and transitions"
        )
        
        # Update accessibility settings
        config_manager.user_preferences.accessibility_settings.high_contrast = high_contrast
        config_manager.user_preferences.accessibility_settings.large_text = large_text
        config_manager.user_preferences.accessibility_settings.reduced_motion = reduced_motion
    
    def _render_help_section(self):
        """Render help and information section."""
        st.markdown("**📚 Documentation**")
        
        if st.button("🎯 Take Tour", use_container_width=True):
            navigation_controller._start_onboarding_tour()
        
        if st.button("📖 User Guide", use_container_width=True):
            if navigation_controller.current_section:
                navigation_controller._show_user_guide(navigation_controller.current_section.lower().replace(' ', '_'))
            else:
                st.info("User guide will be implemented in task 5")
        
        if st.button("🔍 Glossary", use_container_width=True):
            navigation_controller._show_glossary()
        
        # Navigation history
        if navigation_controller.can_go_back():
            if st.button("⬅️ Go Back", use_container_width=True):
                previous_section = navigation_controller.go_back()
                if previous_section:
                    st.rerun()
        
        # System information
        st.markdown("**ℹ️ System Info**")
        st.caption(f"Version: {config_manager.system_config.version}")
        st.caption("Status: ✅ Online")
        
        # Current section info
        if navigation_controller.current_section:
            st.caption(f"Current: {navigation_controller.current_section}")
    
    def render_enhanced_navigation(self) -> str:
        """Render the enhanced navigation system with breadcrumbs and help integration."""
        # Render main navigation
        selected_section = navigation_controller.render_main_navigation(self.current_section)
        
        # Handle section changes
        if selected_section != self.current_section:
            navigation_controller.handle_section_change(selected_section)
            self.current_section = selected_section
        
        # Render help panel for current section
        if self.current_section:
            navigation_controller.render_help_panel(self.current_section)
            
            # Render section information
            navigation_controller.render_section_info(self.current_section)
        
        return selected_section
    
    def render_navigation_tabs(self, sections: List[str], current_section: str = None) -> str:
        """Render enhanced navigation tabs."""
        if not current_section:
            current_section = sections[0]
        
        # Create navigation HTML
        nav_html = '<div id="navigation" class="nav-tabs" role="navigation" aria-label="Main navigation">'
        
        for i, section in enumerate(sections):
            active_class = "active" if section == current_section else ""
            nav_html += f'''
            <button class="nav-tab {active_class}" 
                    data-section="{section}"
                    data-tooltip="Navigate to {section}"
                    aria-pressed="{str(section == current_section).lower()}"
                    role="tab">
                {self._get_section_icon(section)} {section}
            </button>
            '''
        
        nav_html += '</div>'
        st.markdown(nav_html, unsafe_allow_html=True)
        
        # Use Streamlit's built-in tab functionality for actual navigation
        selected_section = st.selectbox(
            "Select Section",
            sections,
            index=sections.index(current_section) if current_section in sections else 0,
            label_visibility="collapsed"
        )
        
        return selected_section
    
    def _get_section_icon(self, section: str) -> str:
        """Get icon for a section."""
        icons = {
            "Bus Allocation Overview": "🚌",
            "Demand Forecast": "📈",
            "Trips vs Speed Analysis": "⚡",
            "Equitable Resource Allocation Summary": "⚖️"
        }
        return icons.get(section, "📊")
    
    def render_breadcrumbs(self):
        """Render breadcrumb navigation."""
        if not self.breadcrumbs:
            return
        
        breadcrumb_html = '<nav class="breadcrumb" aria-label="Breadcrumb navigation">'
        
        for i, crumb in enumerate(self.breadcrumbs):
            if i > 0:
                breadcrumb_html += '<span class="breadcrumb-separator" aria-hidden="true">›</span>'
            
            if i == len(self.breadcrumbs) - 1:
                # Current page
                breadcrumb_html += f'<span class="breadcrumb-item current" aria-current="page">{crumb}</span>'
            else:
                # Clickable breadcrumb
                breadcrumb_html += f'<span class="breadcrumb-item"><a href="#" data-section="{crumb}">{crumb}</a></span>'
        
        breadcrumb_html += '</nav>'
        st.markdown(breadcrumb_html, unsafe_allow_html=True)
    
    def add_breadcrumb(self, item: str):
        """Add an item to the breadcrumb trail."""
        if item not in self.breadcrumbs:
            self.breadcrumbs.append(item)
    
    def clear_breadcrumbs(self):
        """Clear the breadcrumb trail."""
        self.breadcrumbs = []
    
    def render_card(self, title: str, content_func: Callable, 
                   actions: Optional[List[Dict[str, Any]]] = None,
                   help_text: Optional[str] = None) -> None:
        """Render a dashboard card with enhanced styling."""
        card_html = f'''
        <div class="dashboard-card" role="region" aria-labelledby="card-{title.lower().replace(' ', '-')}">
            <div class="card-header">
                <h3 class="card-title" id="card-{title.lower().replace(' ', '-')}">{title}</h3>
        '''
        
        if actions or help_text:
            card_html += '<div class="card-actions">'
            
            if help_text:
                card_html += f'<span data-tooltip="{help_text}" class="help-icon">❓</span>'
            
            if actions:
                for action in actions:
                    card_html += f'''
                    <button class="btn btn-secondary" 
                            onclick="{action.get('onclick', '')}"
                            data-tooltip="{action.get('tooltip', '')}">
                        {action.get('icon', '')} {action.get('label', '')}
                    </button>
                    '''
            
            card_html += '</div>'
        
        card_html += '</div>'
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Render card content
        content_func()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_footer(self):
        """Render the dashboard footer."""
        footer_html = f"""
        <footer class="dashboard-footer" role="contentinfo">
            <div class="footer-content">
                <div class="footer-section">
                    <span class="footer-text">
                        Developed by Pranav Chopade and Team | BMS Project 2024
                    </span>
                </div>
                <div class="footer-section">
                    <span class="footer-text">
                        Version {config_manager.system_config.version} | 
                        <span class="status-indicator status-success">
                            ● Online
                        </span>
                    </span>
                </div>
            </div>
        </footer>
        """
        st.markdown(footer_html, unsafe_allow_html=True)
    
    def show_loading_indicator(self, message: str = "Loading..."):
        """Show a loading indicator."""
        loading_html = f"""
        <div class="loading-container" role="status" aria-live="polite">
            <div class="loading-spinner"></div>
            <span class="loading-text">{message}</span>
        </div>
        """
        return st.markdown(loading_html, unsafe_allow_html=True)
    
    def render_responsive_grid(self, items: List[Dict[str, Any]], container_class: str = "container") -> None:
        """Render items in a responsive grid layout."""
        grid_html = f'<div class="{container_class}"><div class="dashboard-grid">'
        st.markdown(grid_html, unsafe_allow_html=True)
        
        for item in items:
            grid_classes = item.get('grid_classes', 'grid-item')
            item_html = f'<div class="grid-item {grid_classes}">'
            st.markdown(item_html, unsafe_allow_html=True)
            
            # Render item content
            if 'content_func' in item:
                item['content_func']()
            elif 'content' in item:
                st.markdown(item['content'])
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    def create_responsive_columns(self, ratios: List[int], gap: str = "md") -> List:
        """Create responsive columns with specified ratios."""
        # Use Streamlit's column system with responsive enhancements
        cols = st.columns(ratios, gap=gap)
        
        # Add responsive classes to columns
        for i, col in enumerate(cols):
            with col:
                st.markdown(f'<div class="responsive-column col-{i}">', unsafe_allow_html=True)
        
        return cols
    
    def apply_responsive_layout(self) -> None:
        """Apply responsive layout adjustments based on screen size."""
        responsive_js = """
        <script>
        function applyResponsiveLayout() {
            const width = window.innerWidth;
            const body = document.body;
            
            // Remove existing responsive classes
            body.classList.remove('layout-xs', 'layout-sm', 'layout-md', 'layout-lg', 'layout-xl', 'layout-xxl');
            
            // Add appropriate responsive class
            if (width < 576) {
                body.classList.add('layout-xs');
            } else if (width < 768) {
                body.classList.add('layout-sm');
            } else if (width < 992) {
                body.classList.add('layout-md');
            } else if (width < 1200) {
                body.classList.add('layout-lg');
            } else if (width < 1400) {
                body.classList.add('layout-xl');
            } else {
                body.classList.add('layout-xxl');
            }
            
            // Trigger custom responsive event
            window.dispatchEvent(new CustomEvent('responsiveLayoutChange', {
                detail: { width: width }
            }));
        }
        
        // Apply on load and resize
        window.addEventListener('load', applyResponsiveLayout);
        window.addEventListener('resize', applyResponsiveLayout);
        
        // Apply immediately
        applyResponsiveLayout();
        </script>
        """
        st.markdown(responsive_js, unsafe_allow_html=True)
    
    def show_notification(self, message: str, type: str = "info", duration: int = 5000):
        """Show a notification message."""
        notification_html = f"""
        <div class="notification notification-{type}" 
             role="alert" 
             aria-live="assertive"
             style="animation: slideIn 0.3s ease-out;">
            {message}
        </div>
        <script>
        setTimeout(() => {{
            const notification = document.querySelector('.notification');
            if (notification) {{
                notification.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }}
        }}, {duration});
        </script>
        """
        st.markdown(notification_html, unsafe_allow_html=True)
    
    def render_adaptive_sidebar(self):
        """Render sidebar that adapts to screen size."""
        # Check if we should show sidebar based on screen size
        adaptive_sidebar_js = """
        <script>
        function adaptSidebar() {
            const width = window.innerWidth;
            const sidebar = document.querySelector('.css-1d391kg'); // Streamlit sidebar class
            
            if (sidebar) {
                if (width < 768) {
                    sidebar.classList.add('sidebar-mobile');
                } else {
                    sidebar.classList.remove('sidebar-mobile');
                }
            }
        }
        
        window.addEventListener('resize', adaptSidebar);
        adaptSidebar();
        </script>
        """
        st.markdown(adaptive_sidebar_js, unsafe_allow_html=True)
        
        # Render the enhanced sidebar
        self.render_sidebar()


# Global layout manager instance
layout_manager = DashboardLayout()