"""
Compatibility module for Smart Bus Dashboard Enhancement.

This module provides backward compatibility with the original dashboard
and migration tools for data and configuration files.
"""

from src.compatibility.compatibility_layer import (
    CompatibilityLayer,
    CompatibilityReport,
    MigrationResult,
    LegacyDataLoader,
    ConfigurationMigrator,
    compatibility_layer,
    configuration_migrator
)

__all__ = [
    'CompatibilityLayer',
    'CompatibilityReport',
    'MigrationResult',
    'LegacyDataLoader',
    'ConfigurationMigrator',
    'compatibility_layer',
    'configuration_migrator'
]
