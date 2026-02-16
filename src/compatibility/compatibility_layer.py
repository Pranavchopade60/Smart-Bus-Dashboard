"""
Compatibility Layer for Smart Bus Dashboard Enhancement

This module ensures backward compatibility with the original dashboard
while adding enhanced features. It provides:
- Legacy data format support
- Configuration migration tools
- Fallback mechanisms for missing features
- Compatibility testing utilities
"""

import os
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import shutil
from datetime import datetime
import warnings


@dataclass
class CompatibilityReport:
    """Report on compatibility status."""
    is_compatible: bool
    version: str
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    migration_required: bool


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    success: bool
    files_migrated: List[str]
    errors: List[str]
    backup_location: Optional[str]


class CompatibilityLayer:
    """
    Ensures backward compatibility with original dashboard functionality.
    
    This class provides:
    - CSV format validation and conversion
    - Configuration file migration
    - Legacy function wrappers
    - Fallback mechanisms
    """
    
    # Original dashboard expected CSV columns
    LEGACY_FORMATS = {
        'allocation': [
            'Route Name', 'Baseline_Trips_per_Day', 'Forecast_Multiplier',
            'Forecast_Trips_per_Day', 'Trips_per_Bus_per_Day', 
            'Required_Buses_exact', 'Required_Buses_floor', 'Required_Buses_ceil',
            'Fractional_need', 'Allocated_Buses', 'Achieved_Trips_per_Day',
            'Unmet_Trips', 'Surplus_Trips'
        ],
        'forecast': [
            'route', 'Predicted_Daily_Boardings'
        ],
        'sensitivity': [
            'Route Name', 'Final Destination', 'Speed_kmh', 
            'Turnaround_min', 'Trips_per_Bus_per_Day'
        ]
    }
    
    # Column name mappings for enhanced dashboard
    COLUMN_MAPPINGS = {
        'Route Name': 'Route',
        'route': 'Route',
        'Predicted_Daily_Boardings': 'Predicted_Boardings',
        'Trips_per_Bus_per_Day': 'Trips_per_Bus',
        'Allocated_Buses': 'Buses_Required'
    }
    
    def __init__(self, data_directory: str = "outputs"):
        self.data_directory = Path(data_directory)
        self.backup_directory = Path(".backups")
        self.backup_directory.mkdir(exist_ok=True)
        
    def check_compatibility(self) -> CompatibilityReport:
        """
        Check compatibility with existing data and configuration.
        
        Returns:
            CompatibilityReport with detailed compatibility status
        """
        issues = []
        warnings_list = []
        recommendations = []
        migration_required = False
        
        # Check data files
        for data_type, expected_columns in self.LEGACY_FORMATS.items():
            file_path = self._get_data_file_path(data_type)
            
            if not file_path.exists():
                warnings_list.append(f"Data file not found: {file_path}")
                continue
            
            try:
                # Read CSV and check columns
                df = pd.read_csv(file_path)
                
                # Check for required columns
                missing_columns = set(expected_columns) - set(df.columns)
                extra_columns = set(df.columns) - set(expected_columns)
                
                if missing_columns:
                    issues.append(f"{data_type}: Missing columns {missing_columns}")
                    migration_required = True
                
                if extra_columns:
                    warnings_list.append(f"{data_type}: Extra columns {extra_columns}")
                
                # Check data types
                type_issues = self._check_data_types(df, data_type)
                if type_issues:
                    warnings_list.extend(type_issues)
                
            except Exception as e:
                issues.append(f"Error reading {data_type} file: {str(e)}")
        
        # Check configuration files
        config_issues = self._check_configuration_compatibility()
        if config_issues:
            warnings_list.extend(config_issues)
        
        # Generate recommendations
        if migration_required:
            recommendations.append("Run migration tool to update data formats")
        
        if warnings_list:
            recommendations.append("Review warnings and consider data cleanup")
        
        is_compatible = len(issues) == 0
        
        return CompatibilityReport(
            is_compatible=is_compatible,
            version="1.0.0",
            issues=issues,
            warnings=warnings_list,
            recommendations=recommendations,
            migration_required=migration_required
        )
    
    def _get_data_file_path(self, data_type: str) -> Path:
        """Get path to data file based on type."""
        file_mapping = {
            'allocation': 'bus_allocation_plan.csv',
            'forecast': 'predicted_daily_boardings_example_wed.csv',
            'sensitivity': 'sensitivity_trips_per_bus.csv'
        }
        
        filename = file_mapping.get(data_type, f"{data_type}.csv")
        return self.data_directory / filename
    
    def _check_data_types(self, df: pd.DataFrame, data_type: str) -> List[str]:
        """Check if data types are appropriate."""
        issues = []
        
        # Define expected numeric columns
        numeric_columns = {
            'allocation': [
                'Baseline_Trips_per_Day', 'Forecast_Multiplier', 
                'Forecast_Trips_per_Day', 'Trips_per_Bus_per_Day',
                'Required_Buses_exact', 'Required_Buses_floor', 
                'Required_Buses_ceil', 'Fractional_need',
                'Allocated_Buses', 'Achieved_Trips_per_Day',
                'Unmet_Trips', 'Surplus_Trips'
            ],
            'forecast': ['Predicted_Daily_Boardings'],
            'sensitivity': ['Speed_kmh', 'Turnaround_min', 'Trips_per_Bus_per_Day']
        }
        
        expected_numeric = numeric_columns.get(data_type, [])
        
        for col in expected_numeric:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                issues.append(f"{data_type}: Column '{col}' should be numeric")
        
        return issues
    
    def _check_configuration_compatibility(self) -> List[str]:
        """Check configuration file compatibility."""
        issues = []
        
        config_file = Path("config.json")
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Check for required configuration sections
                if 'user_preferences' not in config:
                    issues.append("Configuration missing 'user_preferences' section")
                
                if 'system_config' not in config:
                    issues.append("Configuration missing 'system_config' section")
                
            except json.JSONDecodeError:
                issues.append("Configuration file is not valid JSON")
            except Exception as e:
                issues.append(f"Error reading configuration: {str(e)}")
        
        return issues
    
    def migrate_data_formats(self, backup: bool = True) -> MigrationResult:
        """
        Migrate data formats to enhanced dashboard format.
        
        Args:
            backup: Whether to create backups before migration
            
        Returns:
            MigrationResult with migration status
        """
        files_migrated = []
        errors = []
        backup_location = None
        
        # Create backup if requested
        if backup:
            backup_location = self._create_backup()
        
        # Migrate each data file
        for data_type in self.LEGACY_FORMATS.keys():
            file_path = self._get_data_file_path(data_type)
            
            if not file_path.exists():
                continue
            
            try:
                # Read original data
                df = pd.read_csv(file_path)
                
                # Apply column mappings
                df_migrated = self._apply_column_mappings(df)
                
                # Validate migrated data
                if self._validate_migrated_data(df_migrated, data_type):
                    # Save migrated data (overwrites original)
                    df_migrated.to_csv(file_path, index=False)
                    files_migrated.append(str(file_path))
                else:
                    errors.append(f"Validation failed for {data_type}")
                
            except Exception as e:
                errors.append(f"Error migrating {data_type}: {str(e)}")
        
        success = len(errors) == 0
        
        return MigrationResult(
            success=success,
            files_migrated=files_migrated,
            errors=errors,
            backup_location=backup_location
        )
    
    def _create_backup(self) -> str:
        """Create backup of data files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_directory / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all CSV files
        for csv_file in self.data_directory.glob("*.csv"):
            shutil.copy2(csv_file, backup_dir / csv_file.name)
        
        # Copy configuration if exists
        config_file = Path("config.json")
        if config_file.exists():
            shutil.copy2(config_file, backup_dir / "config.json")
        
        return str(backup_dir)
    
    def _apply_column_mappings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply column name mappings to DataFrame."""
        df_copy = df.copy()
        
        # Rename columns based on mapping
        rename_dict = {}
        for old_name, new_name in self.COLUMN_MAPPINGS.items():
            if old_name in df_copy.columns:
                rename_dict[old_name] = new_name
        
        if rename_dict:
            df_copy = df_copy.rename(columns=rename_dict)
        
        return df_copy
    
    def _validate_migrated_data(self, df: pd.DataFrame, data_type: str) -> bool:
        """Validate migrated data."""
        # Basic validation - ensure data is not empty
        if df.empty:
            return False
        
        # Ensure no critical columns were lost
        if len(df.columns) == 0:
            return False
        
        # Ensure numeric columns are still numeric
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return False
        
        return True
    
    def restore_from_backup(self, backup_location: str) -> bool:
        """
        Restore data from backup.
        
        Args:
            backup_location: Path to backup directory
            
        Returns:
            True if restore successful, False otherwise
        """
        backup_dir = Path(backup_location)
        
        if not backup_dir.exists():
            return False
        
        try:
            # Restore all CSV files
            for csv_file in backup_dir.glob("*.csv"):
                target_path = self.data_directory / csv_file.name
                shutil.copy2(csv_file, target_path)
            
            # Restore configuration if exists
            backup_config = backup_dir / "config.json"
            if backup_config.exists():
                shutil.copy2(backup_config, "config.json")
            
            return True
            
        except Exception as e:
            warnings.warn(f"Error restoring from backup: {str(e)}")
            return False
    
    def get_legacy_data_loader(self) -> 'LegacyDataLoader':
        """Get a data loader that maintains legacy interface."""
        return LegacyDataLoader(self.data_directory)
    
    def ensure_streamlit_compatibility(self) -> Dict[str, Any]:
        """
        Ensure compatibility with Streamlit infrastructure.
        
        Returns:
            Dictionary with compatibility status
        """
        compatibility_status = {
            'streamlit_version': 'unknown',
            'compatible': True,
            'issues': [],
            'features_available': {}
        }
        
        # Check Streamlit version
        try:
            # Import streamlit locally to avoid issues
            import streamlit as st_local
            compatibility_status['streamlit_version'] = st_local.__version__
            
            version_parts = st_local.__version__.split('.')
            major_version = int(version_parts[0])
            
            if major_version < 1:
                compatibility_status['issues'].append(
                    f"Streamlit version {st_local.__version__} is outdated. Recommend 1.0.0+"
                )
                compatibility_status['compatible'] = False
        except Exception as e:
            compatibility_status['issues'].append(f"Error checking Streamlit version: {str(e)}")
        
        # Check for required Streamlit features
        required_features = [
            'session_state',
            'tabs',
            'columns',
            'expander',
            'sidebar'
        ]
        
        try:
            import streamlit as st_local
            for feature in required_features:
                try:
                    has_feature = hasattr(st_local, feature)
                    compatibility_status['features_available'][feature] = has_feature
                    
                    if not has_feature:
                        compatibility_status['issues'].append(f"Missing Streamlit feature: {feature}")
                        compatibility_status['compatible'] = False
                except Exception:
                    compatibility_status['features_available'][feature] = False
        except ImportError:
            compatibility_status['issues'].append("Streamlit is not installed")
            compatibility_status['compatible'] = False
        
        return compatibility_status


class LegacyDataLoader:
    """
    Data loader that maintains the original dashboard's interface.
    
    This class provides the same data loading interface as the original
    dashboard while using the enhanced data controller internally.
    """
    
    def __init__(self, data_directory: str = "outputs"):
        self.data_directory = Path(data_directory)
        self.OUT_DIR = str(data_directory)
        
        # Legacy file paths (matching original dashboard)
        self.ALLOC_P = str(self.data_directory / "bus_allocation_plan.csv")
        self.FORECAST_P = str(self.data_directory / "predicted_daily_boardings_example_wed.csv")
        self.SENS_P = str(self.data_directory / "sensitivity_trips_per_bus.csv")
    
    def load_allocation_data(self) -> pd.DataFrame:
        """Load allocation data (legacy interface)."""
        if not os.path.exists(self.ALLOC_P):
            raise FileNotFoundError(f"Allocation file not found: {self.ALLOC_P}")
        return pd.read_csv(self.ALLOC_P)
    
    def load_forecast_data(self) -> pd.DataFrame:
        """Load forecast data (legacy interface)."""
        if not os.path.exists(self.FORECAST_P):
            return pd.DataFrame()  # Return empty DataFrame like original
        return pd.read_csv(self.FORECAST_P)
    
    def load_sensitivity_data(self) -> pd.DataFrame:
        """Load sensitivity data (legacy interface)."""
        if not os.path.exists(self.SENS_P):
            return pd.DataFrame()  # Return empty DataFrame like original
        return pd.read_csv(self.SENS_P)
    
    def check_data_availability(self) -> Dict[str, bool]:
        """Check which data files are available."""
        return {
            'allocation': os.path.exists(self.ALLOC_P),
            'forecast': os.path.exists(self.FORECAST_P),
            'sensitivity': os.path.exists(self.SENS_P)
        }


class ConfigurationMigrator:
    """
    Migrates configuration files from legacy format to enhanced format.
    """
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.legacy_config_file = Path("config_legacy.json")
    
    def migrate_configuration(self, backup: bool = True) -> MigrationResult:
        """
        Migrate configuration to enhanced format.
        
        Args:
            backup: Whether to backup existing configuration
            
        Returns:
            MigrationResult with migration status
        """
        files_migrated = []
        errors = []
        backup_location = None
        
        if not self.config_file.exists():
            # No configuration to migrate - create default
            return self._create_default_configuration()
        
        try:
            # Backup existing configuration
            if backup:
                backup_location = str(self.config_file.with_suffix('.json.bak'))
                shutil.copy2(self.config_file, backup_location)
            
            # Load existing configuration
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Migrate to enhanced format
            enhanced_config = self._convert_to_enhanced_format(config)
            
            # Save enhanced configuration
            with open(self.config_file, 'w') as f:
                json.dump(enhanced_config, f, indent=2)
            
            files_migrated.append(str(self.config_file))
            
        except Exception as e:
            errors.append(f"Error migrating configuration: {str(e)}")
        
        success = len(errors) == 0
        
        return MigrationResult(
            success=success,
            files_migrated=files_migrated,
            errors=errors,
            backup_location=backup_location
        )
    
    def _create_default_configuration(self) -> MigrationResult:
        """Create default enhanced configuration."""
        default_config = {
            'user_preferences': {
                'theme': 'light',
                'default_section': 'Bus Allocation Overview',
                'saved_filters': {},
                'accessibility_settings': {
                    'high_contrast': False,
                    'large_text': False,
                    'keyboard_navigation': True,
                    'screen_reader_support': True,
                    'reduced_motion': False,
                    'focus_indicators': True
                },
                'export_preferences': {
                    'default_format': 'csv',
                    'include_metadata': True,
                    'compress_large_files': True,
                    'max_file_size_mb': 50
                },
                'visualization_settings': {
                    'chart_theme': 'plotly',
                    'color_palette': 'viridis',
                    'animation_enabled': True,
                    'accessibility_mode': False,
                    'default_chart_types': {
                        'allocation': 'bar',
                        'forecast': 'bar',
                        'sensitivity': 'line',
                        'distribution': 'pie'
                    },
                    'show_legends': True,
                    'show_axis_labels': True
                },
                'onboarding_completed': False,
                'language': 'en'
            },
            'system_config': {
                'app_name': 'Smart Bus Scheduling System',
                'version': '1.0.0',
                'data_directory': 'outputs',
                'cache_directory': '.cache'
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return MigrationResult(
                success=True,
                files_migrated=[str(self.config_file)],
                errors=[],
                backup_location=None
            )
        except Exception as e:
            return MigrationResult(
                success=False,
                files_migrated=[],
                errors=[f"Error creating default configuration: {str(e)}"],
                backup_location=None
            )
    
    def _convert_to_enhanced_format(self, legacy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy configuration to enhanced format."""
        # Start with default structure
        enhanced_config = {
            'user_preferences': {},
            'system_config': {}
        }
        
        # Migrate user preferences if they exist
        if 'user_preferences' in legacy_config:
            enhanced_config['user_preferences'] = legacy_config['user_preferences']
        else:
            # Create default user preferences
            enhanced_config['user_preferences'] = {
                'theme': 'light',
                'default_section': 'Bus Allocation Overview',
                'saved_filters': {},
                'onboarding_completed': False
            }
        
        # Ensure all required fields exist
        if 'accessibility_settings' not in enhanced_config['user_preferences']:
            enhanced_config['user_preferences']['accessibility_settings'] = {
                'high_contrast': False,
                'large_text': False,
                'keyboard_navigation': True,
                'screen_reader_support': True,
                'reduced_motion': False,
                'focus_indicators': True
            }
        
        if 'export_preferences' not in enhanced_config['user_preferences']:
            enhanced_config['user_preferences']['export_preferences'] = {
                'default_format': 'csv',
                'include_metadata': True,
                'compress_large_files': True,
                'max_file_size_mb': 50
            }
        
        if 'visualization_settings' not in enhanced_config['user_preferences']:
            enhanced_config['user_preferences']['visualization_settings'] = {
                'chart_theme': 'plotly',
                'color_palette': 'viridis',
                'animation_enabled': True,
                'accessibility_mode': False,
                'default_chart_types': {
                    'allocation': 'bar',
                    'forecast': 'bar',
                    'sensitivity': 'line',
                    'distribution': 'pie'
                },
                'show_legends': True,
                'show_axis_labels': True
            }
        
        # Migrate system configuration
        if 'system_config' in legacy_config:
            enhanced_config['system_config'] = legacy_config['system_config']
        else:
            enhanced_config['system_config'] = {
                'app_name': 'Smart Bus Scheduling System',
                'version': '1.0.0',
                'data_directory': 'outputs',
                'cache_directory': '.cache'
            }
        
        return enhanced_config


# Global compatibility layer instance
compatibility_layer = CompatibilityLayer()
configuration_migrator = ConfigurationMigrator()
