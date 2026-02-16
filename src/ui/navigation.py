"""
Navigation system with breadcrumbs and help integration for the Smart Bus Dashboard.

This module provides comprehensive navigation functionality including tabbed interfaces,
breadcrumb navigation, help panels, and onboarding tour capabilities.
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from src.config.settings import config_manager
from src.ui.styles import style_manager
from src.ui.javascript import javascript_manager


@dataclass
class NavigationItem:
    """Represents a navigation item with metadata."""
    id: str
    label: str
    icon: str = "📊"
    description: str = ""
    tooltip: str = ""
    url: Optional[str] = None
    children: List['NavigationItem'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BreadcrumbItem:
    """Represents a breadcrumb navigation item."""
    label: str
    section: str
    subsection: Optional[str] = None
    url: Optional[str] = None
    clickable: bool = True


@dataclass
class HelpContent:
    """Represents help content for a section."""
    title: str
    content: str
    type: str = "info"  # info, tip, warning, tutorial
    icon: str = "❓"
    links: List[Dict[str, str]] = field(default_factory=list)


class NavigationController:
    """Enhanced navigation system with breadcrumbs and help integration."""
    
    def __init__(self):
        self.current_section = None
        self.current_subsection = None
        self.breadcrumbs: List[BreadcrumbItem] = []
        self.navigation_history: List[str] = []
        self.help_content: Dict[str, HelpContent] = {}
        self.onboarding_steps: List[Dict[str, Any]] = []
        self._initialize_navigation_data()
        self._initialize_help_content()
        self._initialize_onboarding()
    
    def _initialize_navigation_data(self):
        """Initialize navigation structure and metadata."""
        self.sections = [
            NavigationItem(
                id="bus_allocation",
                label="Bus Allocation Overview",
                icon="🚌",
                description="Comprehensive view of bus allocation across routes",
                tooltip="View current bus allocation plans and optimization results",
                metadata={
                    "requirements": ["2.1", "2.2", "2.3"],
                    "data_files": ["allocation"],
                    "chart_types": ["bar", "pie"]
                }
            ),
            NavigationItem(
                id="demand_forecast",
                label="Demand Forecast",
                icon="📈",
                description="Passenger demand predictions and analysis",
                tooltip="Analyze predicted passenger demand patterns",
                metadata={
                    "requirements": ["2.1", "2.2"],
                    "data_files": ["forecast"],
                    "chart_types": ["bar", "line"]
                }
            ),
            NavigationItem(
                id="trips_analysis",
                label="Trips vs Speed Analysis",
                icon="⚡",
                description="Performance analysis of trips versus speed metrics",
                tooltip="Examine the relationship between trip frequency and bus speed",
                metadata={
                    "requirements": ["2.1", "2.3"],
                    "data_files": ["sensitivity"],
                    "chart_types": ["line", "scatter"]
                }
            ),
            NavigationItem(
                id="resource_allocation",
                label="Equitable Resource Allocation Summary",
                icon="⚖️",
                description="Summary of equitable resource distribution",
                tooltip="Review resource allocation for equitable service distribution",
                metadata={
                    "requirements": ["2.1", "2.2", "2.3"],
                    "data_files": ["allocation", "forecast"],
                    "chart_types": ["bar", "pie", "heatmap"]
                }
            )
        ]
    
    def _initialize_help_content(self):
        """Initialize help content for each section."""
        self.help_content = {
            "bus_allocation": HelpContent(
                title="Bus Allocation Overview Help",
                content="""
                This section displays the current bus allocation plan across different routes.
                
                **Key Features:**
                - View total buses allocated per route
                - Analyze allocation efficiency metrics
                - Compare planned vs actual allocations
                
                **How to Use:**
                1. Review the allocation chart to see distribution
                2. Use filters to focus on specific routes
                3. Check efficiency metrics in the summary table
                
                **Understanding the Data:**
                - Each bar represents buses allocated to a route
                - Colors indicate allocation efficiency levels
                - Hover over charts for detailed information
                """,
                type="tutorial",
                icon="🚌",
                links=[
                    {"label": "Bus Allocation Guide", "url": "#allocation-guide"},
                    {"label": "Route Planning Best Practices", "url": "#route-planning"}
                ]
            ),
            "demand_forecast": HelpContent(
                title="Demand Forecast Help",
                content="""
                This section shows predicted passenger demand for different routes and times.
                
                **Key Features:**
                - View demand predictions by route
                - Analyze peak and off-peak patterns
                - Compare historical vs predicted demand
                
                **How to Use:**
                1. Select time periods using the date controls
                2. Filter by specific routes of interest
                3. Review demand patterns in the charts
                
                **Understanding Predictions:**
                - Higher bars indicate higher expected demand
                - Color coding shows confidence levels
                - Trends help identify capacity needs
                """,
                type="tutorial",
                icon="📈",
                links=[
                    {"label": "Demand Forecasting Methods", "url": "#forecasting"},
                    {"label": "Interpreting Predictions", "url": "#predictions"}
                ]
            ),
            "trips_analysis": HelpContent(
                title="Trips vs Speed Analysis Help",
                content="""
                This section analyzes the relationship between trip frequency and bus speeds.
                
                **Key Features:**
                - Sensitivity analysis of speed vs trips
                - Performance optimization insights
                - Speed impact on service frequency
                
                **How to Use:**
                1. Adjust speed parameters using the controls
                2. Observe changes in trip frequency
                3. Find optimal speed-trip combinations
                
                **Key Insights:**
                - Higher speeds may reduce trip times but affect safety
                - Lower speeds increase reliability but reduce frequency
                - Find the balance for your route requirements
                """,
                type="tutorial",
                icon="⚡",
                links=[
                    {"label": "Speed Optimization Guide", "url": "#speed-optimization"},
                    {"label": "Safety Considerations", "url": "#safety"}
                ]
            ),
            "resource_allocation": HelpContent(
                title="Resource Allocation Summary Help",
                content="""
                This section provides a comprehensive summary of resource allocation equity.
                
                **Key Features:**
                - Equity metrics across all routes
                - Resource distribution analysis
                - Service level comparisons
                
                **How to Use:**
                1. Review equity scores for each area
                2. Identify underserved regions
                3. Plan resource reallocation strategies
                
                **Equity Principles:**
                - Equal access to public transportation
                - Fair distribution based on population density
                - Consideration of socioeconomic factors
                """,
                type="tutorial",
                icon="⚖️",
                links=[
                    {"label": "Equity Guidelines", "url": "#equity"},
                    {"label": "Resource Planning", "url": "#resource-planning"}
                ]
            )
        }
    
    def _initialize_onboarding(self):
        """Initialize onboarding tour steps."""
        self.onboarding_steps = [
            {
                "id": "welcome",
                "title": "Welcome to Smart Bus Dashboard",
                "content": "This enhanced dashboard helps you manage bus scheduling with modern tools and insights.",
                "target": ".main-header",
                "position": "bottom"
            },
            {
                "id": "navigation",
                "title": "Navigation Tabs",
                "content": "Use these tabs to switch between different analysis sections. Each section provides unique insights.",
                "target": ".nav-tabs",
                "position": "bottom"
            },
            {
                "id": "controls",
                "title": "Admin Controls",
                "content": "Adjust bus speed and turnaround time parameters to see real-time impacts on your analysis.",
                "target": ".sidebar-enhanced",
                "position": "left"
            },
            {
                "id": "charts",
                "title": "Interactive Charts",
                "content": "All charts are interactive. Hover for details, zoom to focus, and use the toolbar for more options.",
                "target": ".chart-container",
                "position": "top"
            },
            {
                "id": "help",
                "title": "Help System",
                "content": "Click the help button anytime for contextual assistance and detailed explanations.",
                "target": ".help-button",
                "position": "left"
            }
        ]
    
    def render_main_navigation(self, current_section: Optional[str] = None) -> str:
        """Render the main tabbed navigation interface."""
        if current_section:
            self.current_section = current_section
            self._add_to_history(current_section)
        
        # Generate navigation HTML with enhanced accessibility
        nav_html = '''
        <nav class="main-navigation" role="navigation" aria-label="Main navigation">
            <div class="nav-container">
                <div class="nav-tabs" role="tablist">
        '''
        
        for section in self.sections:
            is_active = section.label == self.current_section
            active_class = "active" if is_active else ""
            
            nav_html += f'''
                <button class="nav-tab {active_class}" 
                        role="tab"
                        aria-selected="{str(is_active).lower()}"
                        aria-controls="panel-{section.id}"
                        data-section="{section.label}"
                        data-tooltip="{section.tooltip}"
                        data-tooltip-position="bottom"
                        onclick="window.dashboardManager?.handleSectionChange('{section.label}')">
                    <span class="nav-icon" aria-hidden="true">{section.icon}</span>
                    <span class="nav-label">{section.label}</span>
                    <span class="nav-description sr-only">{section.description}</span>
                </button>
            '''
        
        nav_html += '''
                </div>
                <div class="nav-actions">
                    <button class="help-button btn btn-secondary" 
                            onclick="window.navigationController?.toggleHelp()"
                            data-tooltip="Get help for current section"
                            aria-label="Open help panel">
                        <span aria-hidden="true">❓</span>
                        <span class="sr-only">Help</span>
                    </button>
                </div>
            </div>
        </nav>
        '''
        
        st.markdown(nav_html, unsafe_allow_html=True)
        
        # Use Streamlit's selectbox for actual navigation (hidden)
        section_labels = [section.label for section in self.sections]
        current_index = 0
        if self.current_section and self.current_section in section_labels:
            current_index = section_labels.index(self.current_section)
        
        selected_section = st.selectbox(
            "Navigate to section",
            section_labels,
            index=current_index,
            key="main_navigation",
            label_visibility="collapsed"
        )
        
        return selected_section
    
    def render_breadcrumbs(self, current_section: str, subsection: Optional[str] = None) -> None:
        """Render breadcrumb navigation."""
        self.current_section = current_section
        self.current_subsection = subsection
        
        # Build breadcrumb trail
        breadcrumbs = [
            BreadcrumbItem("Dashboard", "home", clickable=True),
            BreadcrumbItem(current_section, current_section, clickable=False)
        ]
        
        if subsection:
            breadcrumbs.append(BreadcrumbItem(subsection, current_section, subsection, clickable=False))
        
        self.breadcrumbs = breadcrumbs
        
        # Render breadcrumb HTML
        breadcrumb_html = '''
        <nav class="breadcrumb-navigation" aria-label="Breadcrumb navigation">
            <ol class="breadcrumb-list">
        '''
        
        for i, crumb in enumerate(breadcrumbs):
            is_current = i == len(breadcrumbs) - 1
            
            if is_current:
                breadcrumb_html += f'''
                    <li class="breadcrumb-item current" aria-current="page">
                        <span class="breadcrumb-text">{crumb.label}</span>
                    </li>
                '''
            elif crumb.clickable:
                breadcrumb_html += f'''
                    <li class="breadcrumb-item">
                        <a href="#" class="breadcrumb-link" 
                           data-section="{crumb.section}"
                           onclick="window.navigationController?.navigateToSection('{crumb.section}')">
                            {crumb.label}
                        </a>
                        <span class="breadcrumb-separator" aria-hidden="true">›</span>
                    </li>
                '''
            else:
                breadcrumb_html += f'''
                    <li class="breadcrumb-item">
                        <span class="breadcrumb-text">{crumb.label}</span>
                        <span class="breadcrumb-separator" aria-hidden="true">›</span>
                    </li>
                '''
        
        breadcrumb_html += '''
            </ol>
        </nav>
        '''
        
        st.markdown(breadcrumb_html, unsafe_allow_html=True)
    
    def render_help_panel(self, section: Optional[str] = None) -> None:
        """Render contextual help panel."""
        target_section = section or self.current_section
        
        if not target_section:
            return
        
        # Find section ID from label
        section_id = None
        for nav_section in self.sections:
            if nav_section.label == target_section:
                section_id = nav_section.id
                break
        
        if not section_id or section_id not in self.help_content:
            return
        
        help_data = self.help_content[section_id]
        
        # Create help panel container
        with st.expander(f"{help_data.icon} {help_data.title}", expanded=False):
            # Help content
            st.markdown(help_data.content)
            
            # Help links if available
            if help_data.links:
                st.markdown("**Additional Resources:**")
                for link in help_data.links:
                    st.markdown(f"- [{link['label']}]({link['url']})")
            
            # Quick actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📖 User Guide", key=f"guide_{section_id}"):
                    self._show_user_guide(section_id)
            
            with col2:
                if st.button("🎯 Take Tour", key=f"tour_{section_id}"):
                    self._start_onboarding_tour()
            
            with col3:
                if st.button("🔍 Glossary", key=f"glossary_{section_id}"):
                    self._show_glossary()
    
    def handle_section_change(self, new_section: str) -> None:
        """Handle navigation between sections with smooth transitions."""
        if new_section == self.current_section:
            return
        
        old_section = self.current_section
        self.current_section = new_section
        self._add_to_history(new_section)
        
        # Clear subsection when changing main sections
        self.current_subsection = None
        
        # Trigger transition animation
        transition_js = f"""
        <script>
        if (window.animationManager) {{
            window.animationManager.animatePageTransition('{old_section}', '{new_section}');
        }}
        
        if (window.accessibilityManager) {{
            window.accessibilityManager.announcePageChange('{new_section}');
        }}
        
        // Dispatch custom event for section change
        window.dispatchEvent(new CustomEvent('sectionChange', {{
            detail: {{ from: '{old_section}', to: '{new_section}' }}
        }}));
        </script>
        """
        
        st.markdown(transition_js, unsafe_allow_html=True)
    
    def _add_to_history(self, section: str) -> None:
        """Add section to navigation history."""
        if not self.navigation_history or self.navigation_history[-1] != section:
            self.navigation_history.append(section)
            
            # Keep history to reasonable size
            if len(self.navigation_history) > 10:
                self.navigation_history = self.navigation_history[-10:]
    
    def get_navigation_history(self) -> List[str]:
        """Get navigation history for back/forward functionality."""
        return self.navigation_history.copy()
    
    def can_go_back(self) -> bool:
        """Check if back navigation is possible."""
        return len(self.navigation_history) > 1
    
    def go_back(self) -> Optional[str]:
        """Navigate back to previous section."""
        if self.can_go_back():
            # Remove current section
            self.navigation_history.pop()
            # Get previous section
            previous_section = self.navigation_history[-1]
            self.current_section = previous_section
            return previous_section
        return None
    
    def _show_user_guide(self, section_id: str) -> None:
        """Display detailed user guide for a section."""
        st.info(f"📖 Detailed user guide for {section_id} will be implemented in task 5.1")
    
    def _start_onboarding_tour(self) -> None:
        """Start the interactive onboarding tour."""
        if not config_manager.user_preferences.onboarding_completed:
            # Show onboarding tour
            tour_js = """
            <script>
            if (window.dashboardManager) {
                window.dashboardManager.showNotification('Starting onboarding tour...', 'info');
            }
            
            // Tour implementation will be enhanced in task 5.1
            console.log('Onboarding tour started');
            </script>
            """
            st.markdown(tour_js, unsafe_allow_html=True)
            st.info("🎯 Interactive onboarding tour will be fully implemented in task 5.1")
        else:
            st.success("✅ You've already completed the onboarding tour!")
    
    def _show_glossary(self) -> None:
        """Display glossary of terms."""
        st.info("🔍 Interactive glossary will be implemented in task 5.1")
    
    def get_section_metadata(self, section: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific section."""
        for nav_section in self.sections:
            if nav_section.label == section:
                return nav_section.metadata
        return None
    
    def render_section_info(self, section: str) -> None:
        """Render information panel for current section."""
        metadata = self.get_section_metadata(section)
        if not metadata:
            return
        
        info_html = f'''
        <div class="section-info" role="complementary" aria-label="Section information">
            <div class="info-content">
                <h4 class="info-title">📋 Section Information</h4>
                <div class="info-details">
                    <span class="info-item">
                        <strong>Requirements:</strong> {", ".join(metadata.get("requirements", []))}
                    </span>
                    <span class="info-item">
                        <strong>Data Sources:</strong> {", ".join(metadata.get("data_files", []))}
                    </span>
                    <span class="info-item">
                        <strong>Chart Types:</strong> {", ".join(metadata.get("chart_types", []))}
                    </span>
                </div>
            </div>
        </div>
        '''
        
        st.markdown(info_html, unsafe_allow_html=True)
    
    def inject_navigation_styles(self) -> None:
        """Inject CSS styles for navigation components."""
        nav_css = """
        <style>
        /* Enhanced Navigation Styles */
        .main-navigation {
            background: var(--bg-primary);
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow-sm);
            margin-bottom: var(--spacing-lg);
            border: 1px solid var(--border-color);
        }
        
        .nav-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--spacing-sm);
        }
        
        .nav-tabs {
            display: flex;
            flex: 1;
            gap: var(--spacing-xs);
        }
        
        .nav-tab {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: var(--spacing-md);
            background: transparent;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            transition: all var(--transition-fast);
            color: var(--text-secondary);
            text-decoration: none;
            min-height: 60px;
        }
        
        .nav-tab:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            transform: translateY(-2px);
        }
        
        .nav-tab.active {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            box-shadow: var(--shadow-md);
        }
        
        .nav-tab:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        .nav-icon {
            font-size: 1.5rem;
            margin-bottom: var(--spacing-xs);
        }
        
        .nav-label {
            font-size: var(--font-size-sm);
            font-weight: 500;
            text-align: center;
            line-height: 1.2;
        }
        
        .nav-actions {
            display: flex;
            gap: var(--spacing-sm);
            margin-left: var(--spacing-md);
        }
        
        .help-button {
            min-width: 44px;
            min-height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Breadcrumb Navigation */
        .breadcrumb-navigation {
            margin-bottom: var(--spacing-md);
        }
        
        .breadcrumb-list {
            display: flex;
            align-items: center;
            list-style: none;
            margin: 0;
            padding: 0;
            font-size: var(--font-size-sm);
        }
        
        .breadcrumb-item {
            display: flex;
            align-items: center;
        }
        
        .breadcrumb-link {
            color: var(--primary-color);
            text-decoration: none;
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--border-radius);
            transition: all var(--transition-fast);
        }
        
        .breadcrumb-link:hover {
            background: var(--bg-tertiary);
            text-decoration: underline;
        }
        
        .breadcrumb-link:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        .breadcrumb-text {
            padding: var(--spacing-xs) var(--spacing-sm);
        }
        
        .breadcrumb-item.current .breadcrumb-text {
            color: var(--text-primary);
            font-weight: 500;
        }
        
        .breadcrumb-separator {
            margin: 0 var(--spacing-sm);
            color: var(--text-muted);
        }
        
        /* Section Information Panel */
        .section-info {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-lg);
        }
        
        .info-title {
            margin: 0 0 var(--spacing-sm) 0;
            color: var(--text-primary);
            font-size: var(--font-size-base);
        }
        
        .info-details {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-xs);
        }
        
        .info-item {
            font-size: var(--font-size-sm);
            color: var(--text-secondary);
        }
        
        /* Responsive Navigation */
        @media (max-width: 768px) {
            .nav-container {
                flex-direction: column;
                gap: var(--spacing-md);
            }
            
            .nav-tabs {
                width: 100%;
                flex-direction: column;
            }
            
            .nav-tab {
                flex-direction: row;
                justify-content: flex-start;
                text-align: left;
                min-height: 44px;
            }
            
            .nav-icon {
                margin-bottom: 0;
                margin-right: var(--spacing-sm);
                font-size: 1.25rem;
            }
            
            .nav-actions {
                width: 100%;
                justify-content: center;
                margin-left: 0;
            }
            
            .breadcrumb-list {
                flex-wrap: wrap;
                gap: var(--spacing-xs);
            }
        }
        
        @media (max-width: 480px) {
            .nav-tab .nav-label {
                font-size: var(--font-size-xs);
            }
            
            .breadcrumb-item {
                font-size: var(--font-size-xs);
            }
        }
        </style>
        """
        
        st.markdown(nav_css, unsafe_allow_html=True)
    
    def inject_navigation_javascript(self) -> None:
        """Inject JavaScript for navigation functionality."""
        nav_js = """
        <script>
        // Navigation Controller JavaScript
        class NavigationControllerJS {
            constructor() {
                this.currentSection = null;
                this.helpPanelOpen = false;
                this.init();
            }
            
            init() {
                this.setupEventListeners();
                this.initializeTooltips();
            }
            
            setupEventListeners() {
                // Handle section changes
                document.addEventListener('click', (e) => {
                    if (e.target.matches('.nav-tab, .nav-tab *')) {
                        const tab = e.target.closest('.nav-tab');
                        if (tab) {
                            this.handleTabClick(tab);
                        }
                    }
                    
                    if (e.target.matches('.breadcrumb-link')) {
                        e.preventDefault();
                        const section = e.target.getAttribute('data-section');
                        this.navigateToSection(section);
                    }
                });
                
                // Keyboard navigation
                document.addEventListener('keydown', (e) => {
                    if (e.target.matches('.nav-tab')) {
                        this.handleTabKeyboard(e);
                    }
                });
            }
            
            handleTabClick(tab) {
                const section = tab.getAttribute('data-section');
                if (section) {
                    this.navigateToSection(section);
                }
            }
            
            handleTabKeyboard(event) {
                const tabs = Array.from(document.querySelectorAll('.nav-tab'));
                const currentIndex = tabs.indexOf(event.target);
                
                let newIndex = currentIndex;
                
                switch(event.key) {
                    case 'ArrowLeft':
                        event.preventDefault();
                        newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
                        break;
                    case 'ArrowRight':
                        event.preventDefault();
                        newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
                        break;
                    case 'Home':
                        event.preventDefault();
                        newIndex = 0;
                        break;
                    case 'End':
                        event.preventDefault();
                        newIndex = tabs.length - 1;
                        break;
                    case 'Enter':
                    case ' ':
                        event.preventDefault();
                        this.handleTabClick(event.target);
                        return;
                }
                
                if (newIndex !== currentIndex) {
                    tabs[newIndex].focus();
                }
            }
            
            navigateToSection(section) {
                this.currentSection = section;
                
                // Update active tab
                document.querySelectorAll('.nav-tab').forEach(tab => {
                    tab.classList.remove('active');
                    tab.setAttribute('aria-selected', 'false');
                });
                
                const activeTab = document.querySelector(`[data-section="${section}"]`);
                if (activeTab) {
                    activeTab.classList.add('active');
                    activeTab.setAttribute('aria-selected', 'true');
                }
                
                // Announce navigation change
                if (window.accessibilityManager) {
                    window.accessibilityManager.announcePageChange(section);
                }
                
                // Trigger Streamlit update
                this.triggerStreamlitUpdate(section);
            }
            
            triggerStreamlitUpdate(section) {
                // Find the hidden selectbox and update it
                const selectbox = document.querySelector('select[aria-label="Navigate to section"]');
                if (selectbox) {
                    const options = Array.from(selectbox.options);
                    const targetOption = options.find(opt => opt.text === section);
                    if (targetOption) {
                        selectbox.value = targetOption.value;
                        selectbox.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            }
            
            toggleHelp() {
                this.helpPanelOpen = !this.helpPanelOpen;
                
                const helpPanel = document.querySelector('.help-panel');
                if (helpPanel) {
                    helpPanel.classList.toggle('active', this.helpPanelOpen);
                }
                
                // Announce help panel state
                if (window.accessibilityManager) {
                    const message = this.helpPanelOpen ? 'Help panel opened' : 'Help panel closed';
                    window.accessibilityManager.announce(message, 'polite');
                }
            }
            
            initializeTooltips() {
                // Initialize tooltips for navigation elements
                const tooltipElements = document.querySelectorAll('.nav-tab[data-tooltip], .help-button[data-tooltip]');
                tooltipElements.forEach(el => {
                    if (window.tooltipManager) {
                        window.tooltipManager.initializeTooltip(el);
                    }
                });
            }
            
            handleSectionChange(section) {
                // Performance monitoring
                const startTime = performance.now();
                
                this.navigateToSection(section);
                
                // Record navigation performance
                setTimeout(() => {
                    const endTime = performance.now();
                    if (window.dashboardManager) {
                        window.dashboardManager.recordPerformance('navigation', endTime - startTime);
                    }
                }, 0);
            }
        }
        
        // Initialize navigation controller
        window.navigationController = new NavigationControllerJS();
        </script>
        """
        
        st.markdown(nav_js, unsafe_allow_html=True)


# Global navigation controller instance
navigation_controller = NavigationController()