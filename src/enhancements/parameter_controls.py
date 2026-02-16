"""
Enhanced Parameter Controls and Validation System for Smart Bus Dashboard.

This module provides intuitive parameter adjustment interfaces with real-time validation,
preset configurations, and live preview functionality.

Requirements addressed:
- 7.1: Replace basic sidebar controls with intuitive parameter adjustment interfaces
- 7.2: Show real-time preview of changes before applying
- 7.3: Implement parameter validation with clear acceptable ranges
- 7.4: Provide preset configurations for common scenarios
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from src.config.settings import config_manager


class ParameterType(Enum):
    """Types of parameters supported by the system."""
    SPEED = "speed"
    TURNAROUND_TIME = "turnaround_time"
    CAPACITY = "capacity"
    EFFICIENCY = "efficiency"
    FREQUENCY = "frequency"


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ParameterRange:
    """Defines acceptable ranges for parameters."""
    min_value: float
    max_value: float
    optimal_min: Optional[float] = None
    optimal_max: Optional[float] = None
    step: float = 1.0
    unit: str = ""
    
    def is_valid(self, value: float) -> bool:
        """Check if value is within acceptable range."""
        return self.min_value <= value <= self.max_value
    
    def is_optimal(self, value: float) -> bool:
        """Check if value is within optimal range."""
        if self.optimal_min is None or self.optimal_max is None:
            return True
        return self.optimal_min <= value <= self.optimal_max
    
    def get_validation_level(self, value: float) -> ValidationLevel:
        """Get validation level for a value."""
        if not self.is_valid(value):
            return ValidationLevel.ERROR
        elif not self.is_optimal(value):
            return ValidationLevel.WARNING
        else:
            return ValidationLevel.INFO


@dataclass
class ParameterDefinition:
    """Complete definition of a parameter."""
    name: str
    display_name: str
    description: str
    param_type: ParameterType
    range_def: ParameterRange
    default_value: float
    help_text: str
    impact_description: str
    related_parameters: List[str] = field(default_factory=list)


@dataclass
class PresetConfiguration:
    """Predefined parameter configuration for common scenarios."""
    name: str
    description: str
    scenario: str
    parameters: Dict[str, float]
    expected_outcomes: List[str]
    use_cases: List[str]


@dataclass
class ValidationResult:
    """Result of parameter validation."""
    is_valid: bool
    level: ValidationLevel
    message: str
    suggestions: List[str] = field(default_factory=list)


class ParameterValidator:
    """Validates parameter values and provides feedback."""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[ParameterType, Callable]:
        """Initialize validation rules for different parameter types."""
        return {
            ParameterType.SPEED: self._validate_speed,
            ParameterType.TURNAROUND_TIME: self._validate_turnaround_time,
            ParameterType.CAPACITY: self._validate_capacity,
            ParameterType.EFFICIENCY: self._validate_efficiency,
            ParameterType.FREQUENCY: self._validate_frequency
        }
    
    def validate_parameter(self, param_def: ParameterDefinition, value: float) -> ValidationResult:
        """Validate a parameter value against its definition."""
        # Basic range validation
        if not param_def.range_def.is_valid(value):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Value {value} is outside acceptable range ({param_def.range_def.min_value}-{param_def.range_def.max_value} {param_def.range_def.unit})",
                suggestions=[f"Choose a value between {param_def.range_def.min_value} and {param_def.range_def.max_value} {param_def.range_def.unit}"]
            )
        
        # Optimal range validation
        validation_level = param_def.range_def.get_validation_level(value)
        
        # Apply specific validation rules
        if param_def.param_type in self.validation_rules:
            return self.validation_rules[param_def.param_type](param_def, value, validation_level)
        
        # Default validation result
        return ValidationResult(
            is_valid=True,
            level=validation_level,
            message=self._get_default_message(validation_level, value, param_def),
            suggestions=self._get_default_suggestions(validation_level, param_def)
        )
    
    def _validate_speed(self, param_def: ParameterDefinition, value: float, level: ValidationLevel) -> ValidationResult:
        """Validate bus speed parameter."""
        suggestions = []
        
        if value < 35:
            suggestions.append("Lower speeds may reduce efficiency but improve safety in urban areas")
        elif value > 55:
            suggestions.append("Higher speeds may increase fuel consumption and reduce passenger comfort")
        
        if 40 <= value <= 50:
            message = f"Optimal speed setting: {value} km/h provides good balance of efficiency and safety"
        elif value < 40:
            message = f"Conservative speed setting: {value} km/h prioritizes safety over efficiency"
        else:
            message = f"Aggressive speed setting: {value} km/h prioritizes efficiency over comfort"
        
        return ValidationResult(
            is_valid=True,
            level=level,
            message=message,
            suggestions=suggestions
        )
    
    def _validate_turnaround_time(self, param_def: ParameterDefinition, value: float, level: ValidationLevel) -> ValidationResult:
        """Validate turnaround time parameter."""
        suggestions = []
        
        if value < 10:
            suggestions.append("Short turnaround times may cause delays if buses run behind schedule")
        elif value > 20:
            suggestions.append("Long turnaround times reduce overall system efficiency")
        
        if 12 <= value <= 18:
            message = f"Optimal turnaround time: {value} minutes allows adequate buffer time"
        elif value < 12:
            message = f"Tight turnaround time: {value} minutes maximizes efficiency but reduces flexibility"
        else:
            message = f"Conservative turnaround time: {value} minutes provides high reliability"
        
        return ValidationResult(
            is_valid=True,
            level=level,
            message=message,
            suggestions=suggestions
        )
    
    def _validate_capacity(self, param_def: ParameterDefinition, value: float, level: ValidationLevel) -> ValidationResult:
        """Validate capacity parameter."""
        return ValidationResult(
            is_valid=True,
            level=level,
            message=f"Bus capacity set to {value} passengers",
            suggestions=[]
        )
    
    def _validate_efficiency(self, param_def: ParameterDefinition, value: float, level: ValidationLevel) -> ValidationResult:
        """Validate efficiency parameter."""
        return ValidationResult(
            is_valid=True,
            level=level,
            message=f"Target efficiency: {value}%",
            suggestions=[]
        )
    
    def _validate_frequency(self, param_def: ParameterDefinition, value: float, level: ValidationLevel) -> ValidationResult:
        """Validate frequency parameter."""
        return ValidationResult(
            is_valid=True,
            level=level,
            message=f"Service frequency: {value} buses per hour",
            suggestions=[]
        )
    
    def _get_default_message(self, level: ValidationLevel, value: float, param_def: ParameterDefinition) -> str:
        """Get default validation message."""
        if level == ValidationLevel.INFO:
            return f"✅ {param_def.display_name}: {value} {param_def.range_def.unit} (Optimal)"
        elif level == ValidationLevel.WARNING:
            return f"⚠️ {param_def.display_name}: {value} {param_def.range_def.unit} (Acceptable)"
        else:
            return f"❌ {param_def.display_name}: {value} {param_def.range_def.unit} (Invalid)"
    
    def _get_default_suggestions(self, level: ValidationLevel, param_def: ParameterDefinition) -> List[str]:
        """Get default suggestions based on validation level."""
        if level == ValidationLevel.WARNING and param_def.range_def.optimal_min is not None:
            return [f"Consider values between {param_def.range_def.optimal_min} and {param_def.range_def.optimal_max} {param_def.range_def.unit} for optimal performance"]
        return []


class PresetManager:
    """Manages preset configurations for common scenarios."""
    
    def __init__(self):
        self.presets = self._initialize_presets()
    
    def _initialize_presets(self) -> Dict[str, PresetConfiguration]:
        """Initialize predefined configurations."""
        return {
            "urban_efficient": PresetConfiguration(
                name="Urban Efficient",
                description="Optimized for urban routes with frequent stops",
                scenario="Dense urban areas with high passenger demand",
                parameters={
                    "speed": 35.0,
                    "turnaround_time": 12.0,
                    "capacity": 80.0,
                    "efficiency": 85.0
                },
                expected_outcomes=[
                    "Higher passenger throughput",
                    "Reduced waiting times",
                    "Improved fuel efficiency in stop-and-go traffic"
                ],
                use_cases=[
                    "City center routes",
                    "Shopping districts",
                    "Business areas during peak hours"
                ]
            ),
            "suburban_balanced": PresetConfiguration(
                name="Suburban Balanced",
                description="Balanced approach for suburban routes",
                scenario="Mixed suburban areas with moderate demand",
                parameters={
                    "speed": 45.0,
                    "turnaround_time": 15.0,
                    "capacity": 60.0,
                    "efficiency": 80.0
                },
                expected_outcomes=[
                    "Good balance of speed and comfort",
                    "Reliable service with buffer time",
                    "Moderate fuel consumption"
                ],
                use_cases=[
                    "Residential areas",
                    "Mixed-use developments",
                    "School routes"
                ]
            ),
            "express_service": PresetConfiguration(
                name="Express Service",
                description="High-speed service for long-distance routes",
                scenario="Long-distance routes with limited stops",
                parameters={
                    "speed": 55.0,
                    "turnaround_time": 20.0,
                    "capacity": 100.0,
                    "efficiency": 75.0
                },
                expected_outcomes=[
                    "Faster travel times",
                    "Higher passenger capacity",
                    "Suitable for commuter routes"
                ],
                use_cases=[
                    "Highway routes",
                    "Airport connections",
                    "Inter-city services"
                ]
            ),
            "eco_friendly": PresetConfiguration(
                name="Eco-Friendly",
                description="Environmentally optimized settings",
                scenario="Routes prioritizing environmental impact",
                parameters={
                    "speed": 40.0,
                    "turnaround_time": 18.0,
                    "capacity": 70.0,
                    "efficiency": 90.0
                },
                expected_outcomes=[
                    "Reduced emissions",
                    "Lower fuel consumption",
                    "Sustainable operations"
                ],
                use_cases=[
                    "Green initiatives",
                    "Tourist areas",
                    "Environmental zones"
                ]
            ),
            "peak_hour": PresetConfiguration(
                name="Peak Hour",
                description="Optimized for high-demand periods",
                scenario="Rush hour and high-traffic periods",
                parameters={
                    "speed": 30.0,
                    "turnaround_time": 10.0,
                    "capacity": 90.0,
                    "efficiency": 70.0
                },
                expected_outcomes=[
                    "Maximum passenger capacity",
                    "Frequent service",
                    "Reduced congestion impact"
                ],
                use_cases=[
                    "Morning rush hour",
                    "Evening commute",
                    "Special events"
                ]
            )
        }
    
    def get_preset(self, preset_name: str) -> Optional[PresetConfiguration]:
        """Get a preset configuration by name."""
        return self.presets.get(preset_name)
    
    def get_all_presets(self) -> Dict[str, PresetConfiguration]:
        """Get all available presets."""
        return self.presets
    
    def apply_preset(self, preset_name: str) -> Dict[str, float]:
        """Apply a preset and return the parameter values."""
        preset = self.get_preset(preset_name)
        if preset:
            return preset.parameters.copy()
        return {}


class ParameterControlsSystem:
    """Enhanced parameter controls and validation system."""
    
    def __init__(self):
        self.parameters = self._initialize_parameters()
        self.validator = ParameterValidator()
        self.preset_manager = PresetManager()
        self.current_values = {}
        self.validation_results = {}
        self.preview_mode = True
        self.last_update_time = 0
        self.update_debounce_ms = 300  # Debounce updates for 300ms
    
    def _initialize_parameters(self) -> Dict[str, ParameterDefinition]:
        """Initialize parameter definitions."""
        return {
            "speed": ParameterDefinition(
                name="speed",
                display_name="Average Bus Speed",
                description="Average operating speed of buses on routes",
                param_type=ParameterType.SPEED,
                range_def=ParameterRange(
                    min_value=20.0,
                    max_value=80.0,
                    optimal_min=40.0,
                    optimal_max=50.0,
                    step=1.0,
                    unit="km/h"
                ),
                default_value=40.0,
                help_text="Controls the average speed buses maintain on routes. Higher speeds reduce travel time but may increase fuel consumption and reduce passenger comfort.",
                impact_description="Affects trip duration, fuel efficiency, and passenger experience",
                related_parameters=["turnaround_time", "efficiency"]
            ),
            "turnaround_time": ParameterDefinition(
                name="turnaround_time",
                display_name="Turnaround Time",
                description="Time allocated for buses to turn around at route endpoints",
                param_type=ParameterType.TURNAROUND_TIME,
                range_def=ParameterRange(
                    min_value=5.0,
                    max_value=30.0,
                    optimal_min=12.0,
                    optimal_max=18.0,
                    step=1.0,
                    unit="minutes"
                ),
                default_value=15.0,
                help_text="Buffer time for buses to turn around and prepare for the return journey. Longer times improve reliability but reduce overall efficiency.",
                impact_description="Affects schedule reliability, bus utilization, and service frequency",
                related_parameters=["speed", "frequency"]
            ),
            "capacity": ParameterDefinition(
                name="capacity",
                display_name="Bus Capacity",
                description="Maximum passenger capacity per bus",
                param_type=ParameterType.CAPACITY,
                range_def=ParameterRange(
                    min_value=30.0,
                    max_value=120.0,
                    optimal_min=60.0,
                    optimal_max=90.0,
                    step=5.0,
                    unit="passengers"
                ),
                default_value=75.0,
                help_text="Maximum number of passengers each bus can carry. Higher capacity reduces the number of buses needed but may affect comfort.",
                impact_description="Affects fleet size requirements, passenger comfort, and operational costs",
                related_parameters=["frequency", "efficiency"]
            ),
            "efficiency": ParameterDefinition(
                name="efficiency",
                display_name="Target Efficiency",
                description="Target operational efficiency percentage",
                param_type=ParameterType.EFFICIENCY,
                range_def=ParameterRange(
                    min_value=60.0,
                    max_value=95.0,
                    optimal_min=80.0,
                    optimal_max=90.0,
                    step=1.0,
                    unit="%"
                ),
                default_value=85.0,
                help_text="Target efficiency for bus operations. Higher efficiency reduces costs but may require more precise scheduling.",
                impact_description="Affects operational costs, service reliability, and resource utilization",
                related_parameters=["speed", "capacity"]
            )
        }
    
    def render_enhanced_controls(self) -> Dict[str, float]:
        """Render the enhanced parameter control interface."""
        st.markdown("### 🎛️ Enhanced Parameter Controls")
        
        # Control tabs
        control_tab, preset_tab, preview_tab = st.tabs(["🔧 Controls", "📋 Presets", "👁️ Preview"])
        
        with control_tab:
            self._render_parameter_controls()
        
        with preset_tab:
            self._render_preset_controls()
        
        with preview_tab:
            self._render_preview_panel()
        
        return self.current_values.copy()
    
    def _render_parameter_controls(self):
        """Render individual parameter controls with validation."""
        st.markdown("#### Individual Parameter Controls")
        
        # Real-time preview toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            self.preview_mode = st.checkbox(
                "🔄 Real-time Preview",
                value=self.preview_mode,
                help="Show live preview of changes as you adjust parameters"
            )
        with col2:
            if st.button("🔄 Reset All", help="Reset all parameters to default values"):
                self._reset_to_defaults()
                st.rerun()
        
        st.markdown("---")
        
        # Render each parameter control
        for param_name, param_def in self.parameters.items():
            self._render_parameter_control(param_name, param_def)
            st.markdown("---")
        
        # Apply changes button (if not in preview mode)
        if not self.preview_mode:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✅ Apply Changes", type="primary", use_container_width=True):
                    self._apply_changes()
                    st.success("Parameters updated successfully!")
    
    def _render_parameter_control(self, param_name: str, param_def: ParameterDefinition):
        """Render a single parameter control with validation."""
        # Parameter header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{param_def.display_name}**")
            st.caption(param_def.description)
        with col2:
            if st.button("❓", key=f"help_{param_name}", help=param_def.help_text):
                st.info(f"**{param_def.display_name}**\n\n{param_def.help_text}\n\n**Impact:** {param_def.impact_description}")
        
        # Current value display
        current_value = self.current_values.get(param_name, param_def.default_value)
        
        # Parameter control
        col1, col2 = st.columns([2, 1])
        with col1:
            new_value = st.slider(
                f"{param_def.display_name} ({param_def.range_def.unit})",
                min_value=param_def.range_def.min_value,
                max_value=param_def.range_def.max_value,
                value=current_value,
                step=param_def.range_def.step,
                key=f"slider_{param_name}",
                label_visibility="collapsed"
            )
        
        with col2:
            # Numeric input for precise control
            precise_value = st.number_input(
                "Precise value",
                min_value=param_def.range_def.min_value,
                max_value=param_def.range_def.max_value,
                value=new_value,
                step=param_def.range_def.step,
                key=f"number_{param_name}",
                label_visibility="collapsed"
            )
            
            # Use precise value if different from slider
            if abs(precise_value - new_value) > 0.001:
                new_value = precise_value
        
        # Update current value and validate
        if new_value != current_value:
            self.current_values[param_name] = new_value
            if self.preview_mode:
                self._update_preview()
        
        # Validation and feedback
        validation_result = self.validator.validate_parameter(param_def, new_value)
        self.validation_results[param_name] = validation_result
        
        # Display validation feedback
        self._display_validation_feedback(validation_result)
        
        # Range indicator
        self._render_range_indicator(param_def, new_value)
        
        # Impact preview (without expander to avoid nesting issues)
        if param_def.related_parameters:
            st.markdown(f"**📊 Impact on {', '.join(param_def.related_parameters)}**")
            self._render_parameter_impact(param_name, param_def, new_value)
    
    def _display_validation_feedback(self, validation_result: ValidationResult):
        """Display validation feedback to the user."""
        if validation_result.level == ValidationLevel.ERROR:
            st.error(validation_result.message)
        elif validation_result.level == ValidationLevel.WARNING:
            st.warning(validation_result.message)
        else:
            st.success(validation_result.message)
        
        # Display suggestions
        if validation_result.suggestions:
            for suggestion in validation_result.suggestions:
                st.info(f"💡 {suggestion}")
    
    def _render_range_indicator(self, param_def: ParameterDefinition, current_value: float):
        """Render a visual range indicator using Streamlit components."""
        range_def = param_def.range_def
        
        # Display range information in a clean format
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Min: {range_def.min_value} {range_def.unit}")
        with col2:
            st.caption(f"**Current: {current_value} {range_def.unit}**")
        with col3:
            st.caption(f"Max: {range_def.max_value} {range_def.unit}")
        
        # Show optimal range if defined
        if range_def.optimal_min is not None and range_def.optimal_max is not None:
            if range_def.optimal_min <= current_value <= range_def.optimal_max:
                st.success(f"✓ Within optimal range ({range_def.optimal_min}-{range_def.optimal_max} {range_def.unit})")
            else:
                st.info(f"ℹ️ Optimal range: {range_def.optimal_min}-{range_def.optimal_max} {range_def.unit}")
        
        # Visual progress bar using Streamlit's progress
        total_range = range_def.max_value - range_def.min_value
        progress_value = (current_value - range_def.min_value) / total_range
        st.progress(progress_value)
    
    def _render_parameter_impact(self, param_name: str, param_def: ParameterDefinition, value: float):
        """Render parameter impact visualization."""
        # Calculate impact on related parameters
        impacts = self._calculate_parameter_impacts(param_name, value)
        
        for related_param, impact in impacts.items():
            if impact != 0:
                impact_color = "#4CAF50" if impact > 0 else "#F44336"
                impact_symbol = "↗️" if impact > 0 else "↘️"
                impact_text = "increases" if impact > 0 else "decreases"
                
                st.markdown(f"""
                <div style="padding: 8px; margin: 4px 0; border-left: 4px solid {impact_color}; background: rgba(76, 175, 80, 0.1);">
                    {impact_symbol} <strong>{related_param.replace('_', ' ').title()}</strong> {impact_text} by ~{abs(impact):.1f}%
                </div>
                """, unsafe_allow_html=True)
    
    def _calculate_parameter_impacts(self, param_name: str, value: float) -> Dict[str, float]:
        """Calculate impact of parameter changes on related parameters."""
        impacts = {}
        param_def = self.parameters[param_name]
        
        # Simplified impact calculations (in real implementation, these would be based on actual models)
        if param_name == "speed":
            # Higher speed reduces turnaround time needs but may reduce efficiency
            baseline_speed = param_def.default_value
            speed_change = (value - baseline_speed) / baseline_speed * 100
            
            impacts["turnaround_time"] = -speed_change * 0.3  # Inverse relationship
            impacts["efficiency"] = -abs(speed_change) * 0.2  # Efficiency decreases with extreme speeds
        
        elif param_name == "turnaround_time":
            # Longer turnaround time improves reliability but reduces frequency
            baseline_turnaround = param_def.default_value
            turnaround_change = (value - baseline_turnaround) / baseline_turnaround * 100
            
            impacts["frequency"] = -turnaround_change * 0.5  # Inverse relationship
            impacts["efficiency"] = turnaround_change * 0.1  # Slight positive relationship
        
        elif param_name == "capacity":
            # Higher capacity affects efficiency and frequency needs
            baseline_capacity = param_def.default_value
            capacity_change = (value - baseline_capacity) / baseline_capacity * 100
            
            impacts["frequency"] = -capacity_change * 0.4  # Higher capacity = lower frequency needed
            impacts["efficiency"] = capacity_change * 0.2  # Higher capacity can improve efficiency
        
        return impacts
    
    def _render_preset_controls(self):
        """Render preset configuration controls."""
        st.markdown("#### 📋 Preset Configurations")
        st.caption("Quick-apply optimized settings for common scenarios")
        
        # Preset selection
        presets = self.preset_manager.get_all_presets()
        preset_names = list(presets.keys())
        
        selected_preset = st.selectbox(
            "Choose a preset configuration:",
            [""] + preset_names,
            format_func=lambda x: "Select a preset..." if x == "" else presets[x].name if x else ""
        )
        
        if selected_preset:
            preset = presets[selected_preset]
            
            # Display preset information
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{preset.name}**")
                st.markdown(preset.description)
                st.markdown(f"**Scenario:** {preset.scenario}")
                
                # Parameter values
                st.markdown("**Parameter Values:**")
                for param_name, value in preset.parameters.items():
                    param_def = self.parameters.get(param_name)
                    if param_def:
                        st.markdown(f"• {param_def.display_name}: {value} {param_def.range_def.unit}")
            
            with col2:
                # Expected outcomes
                st.markdown("**Expected Outcomes:**")
                for outcome in preset.expected_outcomes:
                    st.markdown(f"✅ {outcome}")
                
                # Use cases
                st.markdown("**Use Cases:**")
                for use_case in preset.use_cases:
                    st.markdown(f"🎯 {use_case}")
            
            # Apply preset button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"Apply {preset.name}", type="primary", use_container_width=True):
                    self._apply_preset(selected_preset)
                    st.success(f"✅ Applied {preset.name} configuration!")
                    st.rerun()
    
    def _render_preview_panel(self):
        """Render real-time preview panel."""
        st.markdown("#### 👁️ Real-time Preview")
        st.caption("Live preview of parameter changes and their impact")
        
        if not self.current_values:
            st.info("🔧 Adjust parameters in the Controls tab to see live preview")
            return
        
        # Current configuration summary
        st.markdown("**Current Configuration:**")
        config_cols = st.columns(2)
        
        for i, (param_name, value) in enumerate(self.current_values.items()):
            param_def = self.parameters.get(param_name)
            if param_def:
                col = config_cols[i % 2]
                with col:
                    validation_result = self.validation_results.get(param_name)
                    if validation_result:
                        status_icon = "✅" if validation_result.level == ValidationLevel.INFO else "⚠️" if validation_result.level == ValidationLevel.WARNING else "❌"
                        col.metric(
                            f"{status_icon} {param_def.display_name}",
                            f"{value} {param_def.range_def.unit}",
                            help=validation_result.message
                        )
        
        st.markdown("---")
        
        # Impact analysis
        st.markdown("**📊 Impact Analysis**")
        self._render_impact_analysis()
        
        # Performance predictions
        st.markdown("**🎯 Performance Predictions**")
        self._render_performance_predictions()
    
    def _render_impact_analysis(self):
        """Render impact analysis of current parameter settings."""
        if not self.current_values:
            return
        
        # Calculate overall system impact
        impacts = {}
        for param_name, value in self.current_values.items():
            param_impacts = self._calculate_parameter_impacts(param_name, value)
            for impact_param, impact_value in param_impacts.items():
                if impact_param not in impacts:
                    impacts[impact_param] = 0
                impacts[impact_param] += impact_value
        
        # Display impact summary
        if impacts:
            impact_cols = st.columns(len(impacts))
            for i, (impact_param, impact_value) in enumerate(impacts.items()):
                with impact_cols[i]:
                    impact_color = "normal" if abs(impact_value) < 5 else "inverse"
                    impact_symbol = "↗️" if impact_value > 0 else "↘️" if impact_value < 0 else "➡️"
                    
                    st.metric(
                        f"{impact_symbol} {impact_param.replace('_', ' ').title()}",
                        f"{impact_value:+.1f}%",
                        delta=f"{impact_value:+.1f}%",
                        delta_color=impact_color
                    )
    
    def _render_performance_predictions(self):
        """Render performance predictions based on current settings."""
        if not self.current_values:
            return
        
        # Calculate performance metrics
        speed = self.current_values.get("speed", 40.0)
        turnaround = self.current_values.get("turnaround_time", 15.0)
        capacity = self.current_values.get("capacity", 75.0)
        efficiency = self.current_values.get("efficiency", 85.0)
        
        # Simple performance calculations (in real implementation, these would use actual models)
        trips_per_day = max(1, 12 - (speed - 40) * 0.05 - (turnaround - 15) * 0.1)
        fuel_efficiency = min(100, speed * 0.8 + (100 - efficiency) * 0.2)
        passenger_satisfaction = min(100, 100 - abs(speed - 45) * 0.5 - max(0, turnaround - 20) * 2)
        operational_cost = max(50, 100 - efficiency + abs(speed - 45) * 0.3)
        
        # Display predictions
        pred_cols = st.columns(4)
        
        with pred_cols[0]:
            st.metric(
                "🚌 Trips/Day",
                f"{trips_per_day:.1f}",
                help="Estimated number of trips per bus per day"
            )
        
        with pred_cols[1]:
            st.metric(
                "⛽ Fuel Efficiency",
                f"{fuel_efficiency:.1f}%",
                help="Predicted fuel efficiency rating"
            )
        
        with pred_cols[2]:
            st.metric(
                "😊 Satisfaction",
                f"{passenger_satisfaction:.1f}%",
                help="Estimated passenger satisfaction score"
            )
        
        with pred_cols[3]:
            st.metric(
                "💰 Op. Cost Index",
                f"{operational_cost:.0f}",
                help="Operational cost index (lower is better)"
            )
        
        # Recommendations
        st.markdown("**💡 Recommendations**")
        recommendations = self._generate_recommendations()
        
        if recommendations:
            for rec in recommendations:
                st.info(f"💡 {rec}")
        else:
            st.success("✅ Current configuration looks optimal!")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on current settings."""
        recommendations = []
        
        if not self.current_values:
            return recommendations
        
        speed = self.current_values.get("speed", 40.0)
        turnaround = self.current_values.get("turnaround_time", 15.0)
        capacity = self.current_values.get("capacity", 75.0)
        efficiency = self.current_values.get("efficiency", 85.0)
        
        # Speed recommendations
        if speed < 35:
            recommendations.append("Consider increasing speed slightly to improve efficiency while maintaining safety")
        elif speed > 55:
            recommendations.append("High speed may impact passenger comfort and fuel efficiency")
        
        # Turnaround time recommendations
        if turnaround < 10:
            recommendations.append("Very short turnaround time may cause delays if buses run behind schedule")
        elif turnaround > 20:
            recommendations.append("Long turnaround time reduces overall system efficiency")
        
        # Capacity recommendations
        if capacity > 100:
            recommendations.append("High capacity buses may be less maneuverable in urban areas")
        elif capacity < 50:
            recommendations.append("Low capacity may require more buses to meet demand")
        
        # Efficiency recommendations
        if efficiency < 75:
            recommendations.append("Target efficiency below 75% may indicate operational issues")
        elif efficiency > 90:
            recommendations.append("Very high efficiency targets may be difficult to maintain consistently")
        
        return recommendations
    
    def _apply_preset(self, preset_name: str):
        """Apply a preset configuration."""
        preset_values = self.preset_manager.apply_preset(preset_name)
        if preset_values:
            self.current_values.update(preset_values)
            # Validate all new values
            for param_name, value in preset_values.items():
                if param_name in self.parameters:
                    validation_result = self.validator.validate_parameter(
                        self.parameters[param_name], value
                    )
                    self.validation_results[param_name] = validation_result
            
            if self.preview_mode:
                self._update_preview()
    
    def _reset_to_defaults(self):
        """Reset all parameters to their default values."""
        self.current_values = {}
        self.validation_results = {}
        
        for param_name, param_def in self.parameters.items():
            self.current_values[param_name] = param_def.default_value
            validation_result = self.validator.validate_parameter(param_def, param_def.default_value)
            self.validation_results[param_name] = validation_result
        
        if self.preview_mode:
            self._update_preview()
    
    def _apply_changes(self):
        """Apply parameter changes to the system."""
        # In a real implementation, this would update the actual system parameters
        # For now, we'll just update the session state
        if 'parameter_values' not in st.session_state:
            st.session_state.parameter_values = {}
        
        st.session_state.parameter_values.update(self.current_values)
        self.last_update_time = time.time()
    
    def _update_preview(self):
        """Update real-time preview (debounced)."""
        current_time = time.time()
        if current_time - self.last_update_time > self.update_debounce_ms / 1000:
            # In a real implementation, this would trigger preview updates
            # For now, we'll just update the timestamp
            self.last_update_time = current_time
    
    def get_current_values(self) -> Dict[str, float]:
        """Get current parameter values."""
        if not self.current_values:
            # Initialize with defaults
            for param_name, param_def in self.parameters.items():
                self.current_values[param_name] = param_def.default_value
        
        return self.current_values.copy()
    
    def validate_all_parameters(self) -> Dict[str, ValidationResult]:
        """Validate all current parameter values."""
        results = {}
        for param_name, value in self.current_values.items():
            if param_name in self.parameters:
                results[param_name] = self.validator.validate_parameter(
                    self.parameters[param_name], value
                )
        return results
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export current configuration for saving or sharing."""
        return {
            'parameters': self.current_values.copy(),
            'validation_results': {
                name: {
                    'is_valid': result.is_valid,
                    'level': result.level.value,
                    'message': result.message
                }
                for name, result in self.validation_results.items()
            },
            'timestamp': time.time(),
            'preview_mode': self.preview_mode
        }
    
    def import_configuration(self, config: Dict[str, Any]) -> bool:
        """Import a configuration."""
        try:
            if 'parameters' in config:
                self.current_values = config['parameters'].copy()
                
                # Re-validate all parameters
                self.validation_results = {}
                for param_name, value in self.current_values.items():
                    if param_name in self.parameters:
                        validation_result = self.validator.validate_parameter(
                            self.parameters[param_name], value
                        )
                        self.validation_results[param_name] = validation_result
                
                if 'preview_mode' in config:
                    self.preview_mode = config['preview_mode']
                
                if self.preview_mode:
                    self._update_preview()
                
                return True
        except Exception as e:
            st.error(f"Failed to import configuration: {str(e)}")
            return False
        
        return False


# Global instance for easy access
parameter_controls_system = ParameterControlsSystem()