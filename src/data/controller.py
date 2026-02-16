"""
Enhanced data controller for the Smart Bus Dashboard.

This module provides comprehensive data loading, validation, caching,
and filtering functionality with performance optimization.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import joblib
from pathlib import Path
import hashlib
import json
import time

from src.config.settings import config_manager


@dataclass
class LoadingProgress:
    """Progress information for data loading operations."""
    current_chunk: int
    total_chunks: int
    rows_processed: int
    total_rows_estimate: int
    elapsed_time: float
    estimated_remaining: float
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (self.current_chunk / self.total_chunks) * 100
    
    @property
    def rows_per_second(self) -> float:
        """Calculate processing rate."""
        if self.elapsed_time == 0:
            return 0.0
        return self.rows_processed / self.elapsed_time


@dataclass
class DataQualityReport:
    """Data quality assessment report."""
    completeness_score: float
    consistency_score: float
    validity_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    total_rows: int
    total_columns: int


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_report: Optional[DataQualityReport] = None


class DataController:
    """Enhanced data controller with caching, validation, and filtering."""
    
    def __init__(self):
        self.cache_dir = Path(config_manager.system_config.cache_directory)
        self.cache_dir.mkdir(exist_ok=True)
        self.data_cache = {}
        self.cache_metadata = {}
        
        # Performance settings
        self.performance = config_manager.system_config.performance
        
        # Initialize data file paths
        self.data_files = {
            'allocation': config_manager.get_file_path('allocation'),
            'forecast': config_manager.get_file_path('forecast'),
            'sensitivity': config_manager.get_file_path('sensitivity')
        }
    
    def load_csv_data(self, file_path: str, use_cache: bool = True, 
                     progress_callback: Optional[Callable[[LoadingProgress], None]] = None) -> pd.DataFrame:
        """
        Load CSV data with caching, validation, and progress tracking.
        
        Args:
            file_path: Path to the CSV file
            use_cache: Whether to use cached data if available
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If data validation fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        # Generate cache key
        cache_key = self._generate_cache_key(file_path)
        
        # Check cache first
        if use_cache and self._is_cache_valid(cache_key, file_path):
            return self._load_from_cache(cache_key)
        
        try:
            # Load data with chunking for large files
            file_size = os.path.getsize(file_path)
            
            if file_size > 50 * 1024 * 1024:  # 50MB threshold
                data = self._load_large_file(file_path, progress_callback)
            else:
                data = pd.read_csv(file_path)
                
                # Report progress for small files too
                if progress_callback:
                    progress = LoadingProgress(
                        current_chunk=1,
                        total_chunks=1,
                        rows_processed=len(data),
                        total_rows_estimate=len(data),
                        elapsed_time=0.1,
                        estimated_remaining=0.0
                    )
                    progress_callback(progress)
            
            # Validate data
            validation_result = self.validate_data_quality(data)
            if not validation_result.is_valid:
                raise ValueError(f"Data validation failed: {validation_result.errors}")
            
            # Cache the data
            if use_cache:
                self._save_to_cache(cache_key, data, file_path)
            
            return data
            
        except Exception as e:
            raise ValueError(f"Failed to load data from {file_path}: {str(e)}")
    
    def _load_large_file(self, file_path: str, 
                        progress_callback: Optional[Callable[[LoadingProgress], None]] = None) -> pd.DataFrame:
        """Load large CSV files in chunks with progress tracking."""
        chunk_size = self.performance.chunk_size_rows
        chunks = []
        start_time = time.time()
        
        try:
            # First, estimate total rows for better progress tracking
            total_rows_estimate = self._estimate_file_rows(file_path)
            total_chunks_estimate = max(1, total_rows_estimate // chunk_size)
            
            chunk_num = 0
            rows_processed = 0
            
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunks.append(chunk)
                chunk_num += 1
                rows_processed += len(chunk)
                
                # Report progress
                if progress_callback:
                    elapsed_time = time.time() - start_time
                    remaining_chunks = max(0, total_chunks_estimate - chunk_num)
                    estimated_remaining = (elapsed_time / chunk_num) * remaining_chunks if chunk_num > 0 else 0
                    
                    progress = LoadingProgress(
                        current_chunk=chunk_num,
                        total_chunks=total_chunks_estimate,
                        rows_processed=rows_processed,
                        total_rows_estimate=total_rows_estimate,
                        elapsed_time=elapsed_time,
                        estimated_remaining=estimated_remaining
                    )
                    progress_callback(progress)
            
            return pd.concat(chunks, ignore_index=True)
            
        except Exception as e:
            raise ValueError(f"Failed to load large file {file_path}: {str(e)}")
    
    def _estimate_file_rows(self, file_path: str) -> int:
        """Estimate the number of rows in a CSV file."""
        try:
            # Read a small sample to estimate average line length
            sample_size = min(1024 * 1024, os.path.getsize(file_path))  # 1MB sample
            
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(sample_size)
                sample_lines = sample.count('\n')
            
            if sample_lines == 0:
                return 1
            
            # Estimate total rows based on file size
            file_size = os.path.getsize(file_path)
            estimated_rows = int((file_size / sample_size) * sample_lines)
            
            return max(1, estimated_rows - 1)  # Subtract 1 for header
            
        except Exception:
            # Fallback estimate
            return max(1, os.path.getsize(file_path) // 100)  # Rough estimate
    
    def validate_data_quality(self, data: pd.DataFrame) -> ValidationResult:
        """
        Comprehensive data quality validation.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            ValidationResult with quality assessment
        """
        errors = []
        warnings = []
        
        # Basic validation
        if data.empty:
            errors.append("Dataset is empty")
            return ValidationResult(False, errors, warnings)
        
        # Check for required columns based on data type
        required_columns = self._get_required_columns(data)
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Data type validation
        type_issues = self._validate_data_types(data)
        if type_issues:
            warnings.extend(type_issues)
        
        # Generate quality report
        quality_report = self._generate_quality_report(data)
        
        # Check quality thresholds
        if quality_report.completeness_score < 0.8:
            warnings.append(f"Low data completeness: {quality_report.completeness_score:.2%}")
        
        if quality_report.consistency_score < 0.9:
            warnings.append(f"Data consistency issues: {quality_report.consistency_score:.2%}")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(is_valid, errors, warnings, quality_report)
    
    def _get_required_columns(self, data: pd.DataFrame) -> List[str]:
        """Determine required columns based on data characteristics."""
        # Basic heuristics to identify data type
        columns = data.columns.tolist()
        
        # Bus allocation data
        if any('bus' in col.lower() for col in columns):
            return ['Route', 'Buses_Required'] if 'Route' in columns else []
        
        # Forecast data
        if any('boarding' in col.lower() for col in columns):
            return ['Day', 'Predicted_Boardings'] if 'Day' in columns else []
        
        # Sensitivity data
        if any('speed' in col.lower() for col in columns):
            return ['Speed_kmh', 'Trips_per_Bus'] if 'Speed_kmh' in columns else []
        
        return []
    
    def _validate_data_types(self, data: pd.DataFrame) -> List[str]:
        """Validate data types and identify issues."""
        issues = []
        
        for column in data.columns:
            col_data = data[column]
            
            # Check for mixed types
            if col_data.dtype == 'object':
                # Try to identify if it should be numeric
                numeric_count = sum(pd.to_numeric(col_data, errors='coerce').notna())
                total_count = len(col_data.dropna())
                
                if total_count > 0 and numeric_count / total_count > 0.8:
                    issues.append(f"Column '{column}' appears to be numeric but stored as text")
            
            # Check for negative values where they shouldn't exist
            if pd.api.types.is_numeric_dtype(col_data):
                if 'count' in column.lower() or 'number' in column.lower():
                    if (col_data < 0).any():
                        issues.append(f"Column '{column}' contains negative values")
        
        return issues
    
    def _generate_quality_report(self, data: pd.DataFrame) -> DataQualityReport:
        """Generate comprehensive data quality report."""
        total_cells = data.size
        missing_cells = data.isnull().sum().sum()
        
        # Completeness score
        completeness_score = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
        
        # Consistency score (based on data type consistency)
        consistency_issues = 0
        for column in data.columns:
            if data[column].dtype == 'object':
                # Check for inconsistent formatting
                unique_values = data[column].dropna().unique()
                if len(unique_values) > 1:
                    # Simple heuristic for consistency
                    formats = set()
                    for value in unique_values[:10]:  # Sample first 10
                        if isinstance(value, str):
                            formats.add(type(value).__name__)
                    if len(formats) > 1:
                        consistency_issues += 1
        
        consistency_score = 1 - (consistency_issues / len(data.columns)) if len(data.columns) > 0 else 1
        
        # Validity score (based on data range validation)
        validity_issues = 0
        for column in data.columns:
            if pd.api.types.is_numeric_dtype(data[column]):
                # Check for outliers using IQR method
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((data[column] < lower_bound) | (data[column] > upper_bound)).sum()
                if outliers > len(data) * 0.05:  # More than 5% outliers
                    validity_issues += 1
        
        validity_score = 1 - (validity_issues / len(data.select_dtypes(include=[np.number]).columns)) if len(data.select_dtypes(include=[np.number]).columns) > 0 else 1
        
        # Generate issues list
        issues = []
        if completeness_score < 0.9:
            issues.append({
                'type': 'completeness',
                'severity': 'warning' if completeness_score > 0.7 else 'error',
                'description': f'Missing data: {missing_cells} cells ({(1-completeness_score):.1%})',
                'affected_columns': data.columns[data.isnull().any()].tolist()
            })
        
        # Generate recommendations
        recommendations = []
        if completeness_score < 0.8:
            recommendations.append("Consider data imputation for missing values")
        if consistency_score < 0.9:
            recommendations.append("Standardize data formats across columns")
        if validity_score < 0.9:
            recommendations.append("Review and handle outliers in numeric columns")
        
        return DataQualityReport(
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            validity_score=validity_score,
            issues=issues,
            recommendations=recommendations,
            total_rows=len(data),
            total_columns=len(data.columns)
        )
    
    def _generate_cache_key(self, file_path: str) -> str:
        """Generate cache key for file."""
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str, file_path: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.cache_metadata:
            return False
        
        cache_info = self.cache_metadata[cache_key]
        file_mtime = os.path.getmtime(file_path)
        
        return cache_info['file_mtime'] >= file_mtime
    
    def _load_from_cache(self, cache_key: str) -> pd.DataFrame:
        """Load data from cache."""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            return joblib.load(cache_file)
        
        raise FileNotFoundError(f"Cache file not found: {cache_file}")
    
    def _save_to_cache(self, cache_key: str, data: pd.DataFrame, file_path: str) -> None:
        """Save data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Save data
        joblib.dump(data, cache_file)
        
        # Save metadata
        self.cache_metadata[cache_key] = {
            'file_path': file_path,
            'file_mtime': os.path.getmtime(file_path),
            'cached_at': datetime.now().isoformat(),
            'data_shape': data.shape
        }
        
        # Save metadata to file
        metadata_file = self.cache_dir / "cache_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.cache_metadata, f, indent=2)
    
    def get_cached_data(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Get cached data if available."""
        try:
            return self._load_from_cache(cache_key)
        except FileNotFoundError:
            return None
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        
        self.cache_metadata.clear()
        
        metadata_file = self.cache_dir / "cache_metadata.json"
        if metadata_file.exists():
            metadata_file.unlink()
    
    def load_data_with_progress(self, data_type: str, 
                               progress_callback: Optional[Callable[[LoadingProgress], None]] = None) -> pd.DataFrame:
        """
        Load data with progress tracking for UI integration.
        
        Args:
            data_type: Type of data to load ('allocation', 'forecast', 'sensitivity')
            progress_callback: Callback function for progress updates
            
        Returns:
            Loaded DataFrame
        """
        if data_type not in self.data_files:
            raise ValueError(f"Unknown data type: {data_type}")
        
        file_path = self.data_files[data_type]
        return self.load_csv_data(file_path, use_cache=True, progress_callback=progress_callback)
    
    def get_data_summary(self, data_type: str) -> Dict[str, Any]:
        """Get summary statistics for a data type."""
        if data_type not in self.data_files:
            raise ValueError(f"Unknown data type: {data_type}")
        
        file_path = self.data_files[data_type]
        
        try:
            data = self.load_csv_data(file_path)
            
            return {
                'file_path': file_path,
                'shape': data.shape,
                'columns': data.columns.tolist(),
                'dtypes': data.dtypes.to_dict(),
                'memory_usage': data.memory_usage(deep=True).sum(),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                'quality_score': self.validate_data_quality(data).quality_report.completeness_score if self.validate_data_quality(data).quality_report else 0
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'exists': os.path.exists(file_path)
            }
    
    def get_all_data_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get summaries for all data types."""
        summaries = {}
        
        for data_type in self.data_files.keys():
            summaries[data_type] = self.get_data_summary(data_type)
        
        return summaries
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache usage statistics."""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_cache_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'cache_directory': str(self.cache_dir),
            'cached_files': len(cache_files),
            'total_cache_size_mb': total_cache_size / (1024 * 1024),
            'cache_enabled': self.performance.cache_enabled,
            'cache_limit_mb': self.performance.cache_size_mb,
            'cache_utilization': min(100, (total_cache_size / (1024 * 1024)) / self.performance.cache_size_mb * 100)
        }
    
    def validate_all_data_files(self) -> Dict[str, ValidationResult]:
        """Validate all configured data files."""
        results = {}
        
        for data_type, file_path in self.data_files.items():
            try:
                if os.path.exists(file_path):
                    data = self.load_csv_data(file_path, use_cache=True)
                    results[data_type] = self.validate_data_quality(data)
                else:
                    results[data_type] = ValidationResult(
                        is_valid=False,
                        errors=[f"File not found: {file_path}"],
                        warnings=[]
                    )
            except Exception as e:
                results[data_type] = ValidationResult(
                    is_valid=False,
                    errors=[f"Failed to load {file_path}: {str(e)}"],
                    warnings=[]
                )
        
        return results
    
    def cleanup_old_cache(self, max_age_days: int = 7) -> int:
        """Clean up old cache files."""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        cleaned_files = 0
        
        for cache_file in self.cache_dir.glob("*.pkl"):
            if cache_file.stat().st_mtime < cutoff_time:
                cache_file.unlink()
                cleaned_files += 1
        
        # Update metadata
        self.cache_metadata = {
            k: v for k, v in self.cache_metadata.items()
            if os.path.exists(self.cache_dir / f"{k}.pkl")
        }
        
        # Save updated metadata
        metadata_file = self.cache_dir / "cache_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.cache_metadata, f, indent=2)
        
        return cleaned_files


# Global data controller instance
data_controller = DataController()