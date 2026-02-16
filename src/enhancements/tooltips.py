"""
Comprehensive tooltip and help system for the Smart Bus Dashboard.

This module provides contextual tooltips, help panels, glossary,
and progressive disclosure functionality.
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class TooltipType(Enum):
    """Types of tooltips available."""
    INFO = "info"
    HELP = "help"
    WARNING = "warning"
    ERROR = "error"
    DEFINITION = "definition"


@dataclass
class TooltipContent:
    """Content for a tooltip."""
    title: str
    description: str
    tooltip_type: TooltipType = TooltipType.INFO
    examples: List[str] = field(default_factory=list)
    related_links: List[Dict[str, str]] = field(default_factory=list)
    show_icon: bool = True


@dataclass
class GlossaryEntry:
    """Entry in the glossary."""
    term: str
    definition: str
    category: str
    examples: List[str] = field(default_factory=list)
    related_terms: List[str] = field(default_factory=list)


class TooltipSystem:
    """Comprehensive tooltip and help system."""
    
    def __init__(self):
        self.tooltips: Dict[str, TooltipContent] = {}
        self.glossary: Dict[str, GlossaryEntry] = {}
        self.help_panels: Dict[str, Dict[str, Any]] = {}
        self.onboarding_steps: List[Dict[str, Any]] = []
        
        # Initialize default content
        self._initialize_default_tooltips()
        self._initialize_glossary()
        self._initialize_help_panels()
        self._initialize_onboarding()
    
    def _initialize_default_tooltips(self) -> None:
        """Initialize default tooltip content."""
        self.tooltips = {
            "bus_allocation": TooltipContent(
                title="Bus Allocation",
                description="Optimal distribution of buses across routes based on demand forecasting and operational constraints.",
                tooltip_type=TooltipType.INFO,
                examples=[
                    "Route A requires 12 buses during peak hours",
                    "Route B can operate efficiently with 8 buses"
                ],
                related_links=[
                    {"text": "Learn about demand forecasting", "url": "#demand_forecast"},
                    {"text": "View optimization algorithms", "url": "#optimization"}
                ]
            ),
            "demand_forecast": TooltipContent(
                title="Demand Forecasting",
                description="Machine learning predictions of passenger boarding numbers based on historical data and patterns.",
                tooltip_type=TooltipType.INFO,
                examples=[
                    "Monday morning peak: 1,500 expected boardings",
                    "Weekend evening: 800 expected boardings"
                ]
            ),
            "speed_analysis": TooltipContent(
                title="Speed vs Trips Analysis",
                description="Analysis of how bus operating speed affects the number of trips per bus and overall system efficiency.",
                tooltip_type=TooltipType.INFO,
                examples=[
                    "At 40 km/h: 12 trips per bus per day",
                    "At 60 km/h: 10 trips per bus per day"
                ]
            ),
            "efficiency_score": TooltipContent(
                title="Efficiency Score",
                description="A composite metric measuring system performance based on speed, utilization, and passenger satisfaction.",
                tooltip_type=TooltipType.DEFINITION,
                examples=[
                    "Score of 90%+ indicates excellent performance",
                    "Score below 70% suggests optimization needed"
                ]
            ),
            "turnaround_time": TooltipContent(
                title="Turnaround Time",
                description="Time required for a bus to complete a route and return to the starting point, including stops and delays.",
                tooltip_type=TooltipType.DEFINITION,
                examples=[
                    "Urban routes: typically 15-25 minutes",
                    "Suburban routes: typically 30-45 minutes"
                ]
            ),
            "real_time_preview": TooltipContent(
                title="Real-time Preview",
                description="Live updates showing the impact of parameter changes on system performance and resource allocation.",
                tooltip_type=TooltipType.HELP,
                examples=[
                    "Adjust speed slider to see trip count changes",
                    "Modify turnaround time to see efficiency impact"
                ]
            )
        }
    
    def _initialize_glossary(self) -> None:
        """Initialize glossary with technical terms."""
        self.glossary = {
            "bus_allocation": GlossaryEntry(
                term="Bus Allocation",
                definition="The process of distributing available buses across different routes to maximize efficiency and meet passenger demand.",
                category="Operations",
                examples=[
                    "Allocating 15 buses to Route A during peak hours",
                    "Redistributing buses based on real-time demand"
                ],
                related_terms=["demand_forecasting", "route_optimization", "fleet_management"]
            ),
            "demand_forecasting": GlossaryEntry(
                term="Demand Forecasting",
                definition="Using historical data and machine learning to predict future passenger boarding patterns and route usage.",
                category="Analytics",
                examples=[
                    "Predicting 20% increase in ridership during holidays",
                    "Forecasting peak hour demand for route planning"
                ],
                related_terms=["machine_learning", "passenger_analytics", "route_planning"]
            ),
            "route_optimization": GlossaryEntry(
                term="Route Optimization",
                definition="The process of finding the most efficient paths and schedules for bus routes to minimize travel time and maximize coverage.",
                category="Planning",
                examples=[
                    "Reducing route overlap to improve efficiency",
                    "Adjusting stop locations based on passenger density"
                ],
                related_terms=["bus_allocation", "schedule_optimization", "network_design"]
            ),
            "fleet_management": GlossaryEntry(
                term="Fleet Management",
                definition="Comprehensive management of bus fleet including maintenance, allocation, scheduling, and performance monitoring.",
                category="Operations",
                examples=[
                    "Tracking bus utilization across all routes",
                    "Scheduling maintenance based on usage patterns"
                ],
                related_terms=["bus_allocation", "maintenance_scheduling", "performance_monitoring"]
            ),
            "performance_metrics": GlossaryEntry(
                term="Performance Metrics",
                definition="Key indicators used to measure the effectiveness and efficiency of the bus transportation system.",
                category="Analytics",
                examples=[
                    "On-time performance: 94.3%",
                    "Fleet utilization: 87.5%",
                    "Passenger satisfaction: 4.2/5"
                ],
                related_terms=["kpi", "system_efficiency", "service_quality"]
            )
        }
    
    def _initialize_help_panels(self) -> None:
        """Initialize help panel content for each section."""
        self.help_panels = {
            "bus_allocation": {
                "title": "Bus Allocation Help",
                "sections": [
                    {
                        "title": "Understanding Bus Allocation",
                        "content": "Bus allocation determines how many buses are assigned to each route based on passenger demand, route characteristics, and operational constraints."
                    },
                    {
                        "title": "Key Metrics",
                        "content": "• **Buses Required**: Optimal number of buses for the route\n• **Current Buses**: Currently allocated buses\n• **Efficiency**: Route performance score (70-100%)"
                    },
                    {
                        "title": "Interpreting Charts",
                        "content": "The bar chart compares required vs. current bus allocation. Red bars indicate under-allocation, green bars show optimal allocation."
                    },
                    {
                        "title": "Taking Action",
                        "content": "Use the insights to redistribute buses from over-allocated to under-allocated routes for better system efficiency."
                    }
                ]
            },
            "demand_forecast": {
                "title": "Demand Forecasting Help",
                "sections": [
                    {
                        "title": "Understanding Forecasts",
                        "content": "Demand forecasting uses machine learning to predict passenger boarding patterns based on historical data, weather, events, and seasonal trends."
                    },
                    {
                        "title": "Forecast Accuracy",
                        "content": "• **Predicted vs Actual**: Compare forecasted and actual boardings\n• **Accuracy Rate**: Typically 90-95% for short-term forecasts\n• **Confidence Intervals**: Range of expected values"
                    },
                    {
                        "title": "Using Forecasts",
                        "content": "Use forecasts for:\n• Planning bus allocation\n• Adjusting schedules\n• Preparing for peak demand\n• Resource planning"
                    }
                ]
            },
            "speed_analysis": {
                "title": "Speed Analysis Help",
                "sections": [
                    {
                        "title": "Speed vs Trips Relationship",
                        "content": "Higher speeds allow more trips per day but may reduce passenger comfort and increase fuel consumption. The optimal speed balances efficiency with service quality."
                    },
                    {
                        "title": "Optimization Recommendations",
                        "content": "The system provides recommendations based on:\n• Current performance data\n• Route characteristics\n• Passenger feedback\n• Operational constraints"
                    },
                    {
                        "title": "Real-time Adjustments",
                        "content": "Use the speed and turnaround time controls to see immediate impact on:\n• Trips per bus\n• System efficiency\n• Resource utilization"
                    }
                ]
            }
        }
    
    def _initialize_onboarding(self) -> None:
        """Initialize onboarding tour steps."""
        self.onboarding_steps = [
            {
                "step": 1,
                "title": "Welcome to Smart Bus Dashboard",
                "content": "This enhanced dashboard provides real-time analytics and optimization tools for bus fleet management.",
                "target": "main",
                "action": "highlight"
            },
            {
                "step": 2,
                "title": "Navigation Tabs",
                "content": "Use these tabs to explore different aspects of your bus system: allocation, forecasting, speed analysis, and summary.",
                "target": "tabs",
                "action": "highlight"
            },
            {
                "step": 3,
                "title": "Interactive Controls",
                "content": "Adjust system parameters using the sidebar controls to see real-time impact on performance metrics.",
                "target": "sidebar",
                "action": "highlight"
            },
            {
                "step": 4,
                "title": "Admin Panel",
                "content": "Access advanced system management features including performance monitoring and data quality checks.",
                "target": "admin_button",
                "action": "highlight"
            },
            {
                "step": 5,
                "title": "Help System",
                "content": "Look for help icons (?) throughout the dashboard for contextual assistance and detailed explanations.",
                "target": "help_icons",
                "action": "highlight"
            }
        ]
    
    def render_tooltip(self, key: str, trigger_text: str = "?", position: str = "top") -> None:
        """Render a tooltip for a specific key."""
        if key not in self.tooltips:
            return
        
        tooltip = self.tooltips[key]
        
        # Create tooltip HTML
        tooltip_html = f"""
        <div class="tooltip-container" style="display: inline-block; position: relative;">
            <span class="tooltip-trigger" style="
                display: inline-block;
                width: 20px;
                height: 20px;
                background-color: #1f77b4;
                color: white;
                border-radius: 50%;
                text-align: center;
                line-height: 20px;
                font-size: 12px;
                cursor: help;
                margin-left: 5px;
            " title="{tooltip.description}">
                {trigger_text}
            </span>
        </div>
        """
        
        st.markdown(tooltip_html, unsafe_allow_html=True)
    
    def render_help_panel(self, section: str) -> None:
        """Render help panel for a specific section."""
        if section not in self.help_panels:
            return
        
        help_content = self.help_panels[section]
        
        with st.expander(f"❓ {help_content['title']}", expanded=False):
            for section_content in help_content['sections']:
                st.markdown(f"### {section_content['title']}")
                st.markdown(section_content['content'])
                st.markdown("---")
    
    def render_contextual_help(self, context: str) -> None:
        """Render contextual help based on current context."""
        if context in self.help_panels:
            self.render_help_panel(context)
        
        # Also show relevant tooltips
        relevant_tooltips = [key for key in self.tooltips.keys() if context in key or key in context]
        
        if relevant_tooltips:
            st.markdown("**Quick Help:**")
            for tooltip_key in relevant_tooltips[:3]:  # Show max 3 relevant tooltips
                tooltip = self.tooltips[tooltip_key]
                st.info(f"**{tooltip.title}**: {tooltip.description}")
    
    def render_glossary(self, category: Optional[str] = None) -> None:
        """Render glossary of terms."""
        st.markdown("## 📚 Glossary")
        
        # Filter by category if specified
        entries = self.glossary.values()
        if category:
            entries = [entry for entry in entries if entry.category == category]
        
        # Group by category
        categories = {}
        for entry in entries:
            if entry.category not in categories:
                categories[entry.category] = []
            categories[entry.category].append(entry)
        
        # Render by category
        for cat_name, cat_entries in categories.items():
            st.markdown(f"### {cat_name}")
            
            for entry in sorted(cat_entries, key=lambda x: x.term):
                with st.expander(f"**{entry.term}**"):
                    st.markdown(entry.definition)
                    
                    if entry.examples:
                        st.markdown("**Examples:**")
                        for example in entry.examples:
                            st.markdown(f"• {example}")
                    
                    if entry.related_terms:
                        st.markdown("**Related Terms:**")
                        st.markdown(", ".join(entry.related_terms))
    
    def show_onboarding_tour(self) -> None:
        """Show onboarding tour for new users."""
        if st.session_state.get('onboarding_completed', False):
            return
        
        st.info("👋 Welcome! Take a quick tour to learn about the dashboard features.")
        
        if st.button("Start Tour"):
            st.session_state.onboarding_step = 1
        
        if st.session_state.get('onboarding_step', 0) > 0:
            current_step = st.session_state.onboarding_step
            
            if current_step <= len(self.onboarding_steps):
                step_info = self.onboarding_steps[current_step - 1]
                
                st.markdown(f"### Step {step_info['step']}: {step_info['title']}")
                st.markdown(step_info['content'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if current_step > 1 and st.button("Previous"):
                        st.session_state.onboarding_step -= 1
                        st.rerun()
                
                with col2:
                    if st.button("Skip Tour"):
                        st.session_state.onboarding_completed = True
                        st.session_state.onboarding_step = 0
                        st.rerun()
                
                with col3:
                    if current_step < len(self.onboarding_steps):
                        if st.button("Next"):
                            st.session_state.onboarding_step += 1
                            st.rerun()
                    else:
                        if st.button("Complete Tour"):
                            st.session_state.onboarding_completed = True
                            st.session_state.onboarding_step = 0
                            st.success("Tour completed! You can always access help using the ? icons.")
                            st.rerun()
    
    def add_tooltip(self, key: str, content: TooltipContent) -> None:
        """Add a new tooltip."""
        self.tooltips[key] = content
    
    def add_glossary_entry(self, entry: GlossaryEntry) -> None:
        """Add a new glossary entry."""
        self.glossary[entry.term.lower()] = entry
    
    def search_help(self, query: str) -> List[Dict[str, Any]]:
        """Search help content and return relevant results."""
        results = []
        query_lower = query.lower()
        
        # Search tooltips
        for key, tooltip in self.tooltips.items():
            if (query_lower in tooltip.title.lower() or 
                query_lower in tooltip.description.lower()):
                results.append({
                    'type': 'tooltip',
                    'key': key,
                    'title': tooltip.title,
                    'description': tooltip.description,
                    'relevance': 'high' if query_lower in tooltip.title.lower() else 'medium'
                })
        
        # Search glossary
        for key, entry in self.glossary.items():
            if (query_lower in entry.term.lower() or 
                query_lower in entry.definition.lower()):
                results.append({
                    'type': 'glossary',
                    'key': key,
                    'title': entry.term,
                    'description': entry.definition,
                    'relevance': 'high' if query_lower in entry.term.lower() else 'medium'
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results
    
    def render_help_search(self) -> None:
        """Render help search interface."""
        st.markdown("### 🔍 Search Help")
        
        query = st.text_input("Search for help topics, terms, or concepts:")
        
        if query:
            results = self.search_help(query)
            
            if results:
                st.markdown(f"Found {len(results)} results for '{query}':")
                
                for result in results[:10]:  # Show top 10 results
                    with st.expander(f"{result['title']} ({result['type']})"):
                        st.markdown(result['description'])
            else:
                st.warning(f"No results found for '{query}'. Try different keywords.")


# Global tooltip system instance
tooltip_system = TooltipSystem()