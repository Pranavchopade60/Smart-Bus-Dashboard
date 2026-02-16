"""
Core configuration settings for the Smart Bus Dashboard Enhancement.

This module provides centralized configuration management for themes,
user preferences, performance settings, and system configuration.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class Theme(Enum):
    """Available theme options."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ChartTheme(Enum):
    """Available chart theme options."""
    DEFAULT = "plotly"
    DARK = "plotly_dark"
    WHITE = "plotly_white"
    ACCESSIBLE = "accessible"


@dataclass
class AccessibilitySettings:
    """Accessibility configuration settings."""
    high_contrast: bool = False
    large_text: bool = False
    keyboard_navigation: bool = True
    screen_reader_support: bool = True
    reduced_motion: bool = False
    focus_indicators: bool = True


@dataclass
class PerformanceSettings:
    """Performance optimization settings."""
    cache_enabled: bool = True
    cache_size_mb: int = 100
    max_response_time_ms: int = 500
    ui_feedback_time_ms: int = 200
    section_transition_time_ms: int = 1000
    chunk_size_rows: int = 10000
    enable_lazy_loading: bool = True


@dataclass
class ExportPreferences:
    """Export functionality preferences."""
    default_format: str = "csv"
    include_metadata: bool = True
    compress_large_files: bool = True
    max_file_size_mb: int = 50


@dataclass
class VisualizationSettings:
    """Visualization configuration settings."""
    chart_theme: ChartTheme = ChartTheme.DEFAULT
    color_palette: str = "viridis"
    animation_enabled: bool = True
    accessibility_mode: bool = False
    default_chart_types: Dict[str, str] = field(default_factory=lambda: {
        "allocation": "bar",
        "forecast": "bar",
        "sensitivity": "line",
        "distribution": "pie"
    })
    show_legends: bool = True
    show_axis_labels: bool = True


@dataclass
class UserPreferences:
    """User-specific preferences and settings."""
    theme: Theme = Theme.LIGHT
    default_section: str = "Bus Allocation Overview"
    saved_filters: Dict[str, Any] = field(default_factory=dict)
    accessibility_settings: AccessibilitySettings = field(default_factory=AccessibilitySettings)
    export_preferences: ExportPreferences = field(default_factory=ExportPreferences)
    visualization_settings: VisualizationSettings = field(default_factory=VisualizationSettings)
    onboarding_completed: bool = False
    language: str = "en"


@dataclass
class SystemConfig:
    """System-wide configuration settings."""
    app_name: str = "Smart Bus Scheduling System"
    version: str = "1.0.0"
    data_directory: str = "outputs"
    cache_directory: str = ".cache"
    config_file: str = "config.json"
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)
    
    # File paths
    allocation_file: str = "bus_allocation_plan.csv"
    forecast_file: str = "predicted_daily_boardings_example_wed.csv"
    sensitivity_file: str = "sensitivity_trips_per_bus.csv"
    
    # UI Configuration
    page_title: str = "Smart Bus Scheduling System"
    page_icon: str = "🚌"
    layout: str = "wide"
    
    # Navigation sections
    sections: List[str] = field(default_factory=lambda: [
        "Bus Allocation Overview",
        "Demand Forecast", 
        "Trips vs Speed Analysis",
        "Equitable Resource Allocation Summary"
    ])


class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.json"
        self.system_config = SystemConfig()
        self.user_preferences = UserPreferences()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Load user preferences
                if 'user_preferences' in config_data:
                    prefs_data = config_data['user_preferences']
                    if isinstance(prefs_data, dict):
                        self.user_preferences = self._dict_to_user_preferences(prefs_data)
                
                # Load system config overrides
                if 'system_config' in config_data:
                    sys_data = config_data['system_config']
                    if isinstance(sys_data, dict):
                        self._update_system_config(sys_data)
                    
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Warning: Could not load config file {self.config_path}: {e}")
                # Use defaults
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        config_data = {
            'user_preferences': self._user_preferences_to_dict(),
            'system_config': self._system_config_to_dict()
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_path) or '.', exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file {self.config_path}: {e}")
    
    def _dict_to_user_preferences(self, data: Dict[str, Any]) -> UserPreferences:
        """Convert dictionary to UserPreferences object."""
        # Handle nested objects with error handling
        try:
            accessibility = AccessibilitySettings(**data.get('accessibility_settings', {}))
        except (TypeError, ValueError):
            accessibility = AccessibilitySettings()
        
        try:
            export_prefs = ExportPreferences(**data.get('export_preferences', {}))
        except (TypeError, ValueError):
            export_prefs = ExportPreferences()
        
        try:
            viz_settings = VisualizationSettings(**data.get('visualization_settings', {}))
        except (TypeError, ValueError):
            viz_settings = VisualizationSettings()
        
        # Handle theme with fallback
        try:
            theme = Theme(data.get('theme', Theme.LIGHT.value))
        except (ValueError, TypeError):
            theme = Theme.LIGHT
        
        return UserPreferences(
            theme=theme,
            default_section=data.get('default_section', "Bus Allocation Overview"),
            saved_filters=data.get('saved_filters', {}) if isinstance(data.get('saved_filters'), dict) else {},
            accessibility_settings=accessibility,
            export_preferences=export_prefs,
            visualization_settings=viz_settings,
            onboarding_completed=bool(data.get('onboarding_completed', False)),
            language=str(data.get('language', 'en'))
        )
    
    def _user_preferences_to_dict(self) -> Dict[str, Any]:
        """Convert UserPreferences object to dictionary."""
        return {
            'theme': self.user_preferences.theme.value,
            'default_section': self.user_preferences.default_section,
            'saved_filters': self.user_preferences.saved_filters,
            'accessibility_settings': {
                'high_contrast': self.user_preferences.accessibility_settings.high_contrast,
                'large_text': self.user_preferences.accessibility_settings.large_text,
                'keyboard_navigation': self.user_preferences.accessibility_settings.keyboard_navigation,
                'screen_reader_support': self.user_preferences.accessibility_settings.screen_reader_support,
                'reduced_motion': self.user_preferences.accessibility_settings.reduced_motion,
                'focus_indicators': self.user_preferences.accessibility_settings.focus_indicators
            },
            'export_preferences': {
                'default_format': self.user_preferences.export_preferences.default_format,
                'include_metadata': self.user_preferences.export_preferences.include_metadata,
                'compress_large_files': self.user_preferences.export_preferences.compress_large_files,
                'max_file_size_mb': self.user_preferences.export_preferences.max_file_size_mb
            },
            'visualization_settings': {
                'chart_theme': self.user_preferences.visualization_settings.chart_theme.value if hasattr(self.user_preferences.visualization_settings.chart_theme, 'value') else str(self.user_preferences.visualization_settings.chart_theme),
                'color_palette': self.user_preferences.visualization_settings.color_palette,
                'animation_enabled': self.user_preferences.visualization_settings.animation_enabled,
                'accessibility_mode': self.user_preferences.visualization_settings.accessibility_mode,
                'default_chart_types': self.user_preferences.visualization_settings.default_chart_types,
                'show_legends': self.user_preferences.visualization_settings.show_legends,
                'show_axis_labels': self.user_preferences.visualization_settings.show_axis_labels
            },
            'onboarding_completed': self.user_preferences.onboarding_completed,
            'language': self.user_preferences.language
        }
    
    def _update_system_config(self, data: Dict[str, Any]) -> None:
        """Update system configuration with provided data."""
        for key, value in data.items():
            if hasattr(self.system_config, key):
                setattr(self.system_config, key, value)
    
    def _system_config_to_dict(self) -> Dict[str, Any]:
        """Convert SystemConfig object to dictionary."""
        return {
            'app_name': self.system_config.app_name,
            'version': self.system_config.version,
            'data_directory': self.system_config.data_directory,
            'cache_directory': self.system_config.cache_directory
        }
    
    def get_file_path(self, file_type: str) -> str:
        """Get full path for a data file."""
        file_mapping = {
            'allocation': self.system_config.allocation_file,
            'forecast': self.system_config.forecast_file,
            'sensitivity': self.system_config.sensitivity_file
        }
        
        filename = file_mapping.get(file_type)
        if not filename:
            raise ValueError(f"Unknown file type: {file_type}")
        
        return os.path.join(self.system_config.data_directory, filename)
    
    def update_user_preference(self, key: str, value: Any) -> None:
        """Update a specific user preference."""
        if hasattr(self.user_preferences, key):
            setattr(self.user_preferences, key, value)
            self.save_config()
        else:
            raise ValueError(f"Unknown preference key: {key}")
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.user_preferences = UserPreferences()
        self.system_config = SystemConfig()
        self.save_config()


# Global configuration instance
config_manager = ConfigManager()