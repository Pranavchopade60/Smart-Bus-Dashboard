"""
Advanced filtering system for the Smart Bus Dashboard.

This module provides comprehensive filtering capabilities including
date ranges, route filtering, performance metrics, and search functionality.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
import re
from enum import Enum


class FilterType(Enum):
    """Types of filters available."""
    DATE_RANGE = "date_range"
    ROUTE = "route"
    PERFORMANCE = "performance"
    TEXT_SEARCH = "text_search"
    NUMERIC_RANGE = "numeric_range"
    CATEGORICAL = "categorical"


@dataclass
class DateRangeFilter:
    """Date range filter configuration."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    date_column: str = "Date"
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply date range filter to data."""
        if self.date_column not in data.columns:
            return data
        
        filtered_data = data.copy()
        
        # Convert date column to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(filtered_data[self.date_column]):
            filtered_data[self.date_column] = pd.to_datetime(filtered_data[self.date_column], errors='coerce')
        
        # Apply date filters
        if self.start_date:
            filtered_data = filtered_data[filtered_data[self.date_column] >= pd.Timestamp(self.start_date)]
        
        if self.end_date:
            filtered_data = filtered_data[filtered_data[self.date_column] <= pd.Timestamp(self.end_date)]
        
        return filtered_data


@dataclass
class RouteFilter:
    """Route-based filter configuration."""
    selected_routes: List[str] = field(default_factory=list)
    route_column: str = "Route"
    include_all: bool = True
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply route filter to data."""
        if self.route_column not in data.columns or self.include_all or not self.selected_routes:
            return data
        
        return data[data[self.route_column].isin(self.selected_routes)]


@dataclass
class PerformanceFilter:
    """Performance metrics filter configuration."""
    min_speed: Optional[float] = None
    max_speed: Optional[float] = None
    min_efficiency: Optional[float] = None
    max_efficiency: Optional[float] = None
    min_boardings: Optional[int] = None
    max_boardings: Optional[int] = None
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply performance filters to data."""
        filtered_data = data.copy()
        
        # Speed filters
        if 'Speed_kmh' in data.columns:
            if self.min_speed is not None:
                filtered_data = filtered_data[filtered_data['Speed_kmh'] >= self.min_speed]
            if self.max_speed is not None:
                filtered_data = filtered_data[filtered_data['Speed_kmh'] <= self.max_speed]
        
        # Efficiency filters (if available)
        efficiency_cols = [col for col in data.columns if 'efficiency' in col.lower()]
        if efficiency_cols:
            eff_col = efficiency_cols[0]
            if self.min_efficiency is not None:
                filtered_data = filtered_data[filtered_data[eff_col] >= self.min_efficiency]
            if self.max_efficiency is not None:
                filtered_data = filtered_data[filtered_data[eff_col] <= self.max_efficiency]
        
        # Boarding filters
        boarding_cols = [col for col in data.columns if 'boarding' in col.lower()]
        if boarding_cols:
            boarding_col = boarding_cols[0]
            if self.min_boardings is not None:
                filtered_data = filtered_data[filtered_data[boarding_col] >= self.min_boardings]
            if self.max_boardings is not None:
                filtered_data = filtered_data[filtered_data[boarding_col] <= self.max_boardings]
        
        return filtered_data


@dataclass
class TextSearchFilter:
    """Text search filter configuration."""
    search_term: str = ""
    search_columns: List[str] = field(default_factory=list)
    case_sensitive: bool = False
    exact_match: bool = False
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply text search filter to data."""
        if not self.search_term.strip():
            return data
        
        # Determine columns to search
        search_cols = self.search_columns if self.search_columns else data.select_dtypes(include=['object']).columns.tolist()
        
        if not search_cols:
            return data
        
        search_term = self.search_term if self.case_sensitive else self.search_term.lower()
        
        # Create search mask
        mask = pd.Series([False] * len(data), index=data.index)
        
        for col in search_cols:
            if col in data.columns:
                col_data = data[col].astype(str)
                if not self.case_sensitive:
                    col_data = col_data.str.lower()
                
                if self.exact_match:
                    mask |= (col_data == search_term)
                else:
                    mask |= col_data.str.contains(search_term, na=False, regex=False)
        
        return data[mask]


@dataclass
class NumericRangeFilter:
    """Numeric range filter configuration."""
    column: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply numeric range filter to data."""
        if self.column not in data.columns:
            return data
        
        filtered_data = data.copy()
        
        if self.min_value is not None:
            filtered_data = filtered_data[filtered_data[self.column] >= self.min_value]
        
        if self.max_value is not None:
            filtered_data = filtered_data[filtered_data[self.column] <= self.max_value]
        
        return filtered_data


@dataclass
class CategoricalFilter:
    """Categorical filter configuration."""
    column: str
    selected_values: List[str] = field(default_factory=list)
    exclude_values: List[str] = field(default_factory=list)
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply categorical filter to data."""
        if self.column not in data.columns:
            return data
        
        filtered_data = data.copy()
        
        # Include filter
        if self.selected_values:
            filtered_data = filtered_data[filtered_data[self.column].isin(self.selected_values)]
        
        # Exclude filter
        if self.exclude_values:
            filtered_data = filtered_data[~filtered_data[self.column].isin(self.exclude_values)]
        
        return filtered_data


@dataclass
class FilterSet:
    """Complete set of filters to apply."""
    date_range: Optional[DateRangeFilter] = None
    routes: Optional[RouteFilter] = None
    performance: Optional[PerformanceFilter] = None
    text_search: Optional[TextSearchFilter] = None
    numeric_ranges: List[NumericRangeFilter] = field(default_factory=list)
    categorical: List[CategoricalFilter] = field(default_factory=list)
    custom_filters: Dict[str, Any] = field(default_factory=dict)
    
    def apply_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply all filters to the data."""
        filtered_data = data.copy()
        
        # Apply each filter type
        if self.date_range:
            filtered_data = self.date_range.apply(filtered_data)
        
        if self.routes:
            filtered_data = self.routes.apply(filtered_data)
        
        if self.performance:
            filtered_data = self.performance.apply(filtered_data)
        
        if self.text_search:
            filtered_data = self.text_search.apply(filtered_data)
        
        # Apply numeric range filters
        for numeric_filter in self.numeric_ranges:
            filtered_data = numeric_filter.apply(filtered_data)
        
        # Apply categorical filters
        for categorical_filter in self.categorical:
            filtered_data = categorical_filter.apply(filtered_data)
        
        return filtered_data
    
    def is_empty(self) -> bool:
        """Check if filter set is empty."""
        return (
            self.date_range is None and
            self.routes is None and
            self.performance is None and
            self.text_search is None and
            not self.numeric_ranges and
            not self.categorical and
            not self.custom_filters
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of active filters."""
        summary = {
            'total_filters': 0,
            'active_filters': []
        }
        
        if self.date_range and (self.date_range.start_date or self.date_range.end_date):
            summary['total_filters'] += 1
            summary['active_filters'].append({
                'type': 'date_range',
                'description': f"Date: {self.date_range.start_date or 'Any'} to {self.date_range.end_date or 'Any'}"
            })
        
        if self.routes and self.routes.selected_routes and not self.routes.include_all:
            summary['total_filters'] += 1
            summary['active_filters'].append({
                'type': 'routes',
                'description': f"Routes: {', '.join(self.routes.selected_routes[:3])}{'...' if len(self.routes.selected_routes) > 3 else ''}"
            })
        
        if self.performance:
            perf_filters = []
            if self.performance.min_speed is not None or self.performance.max_speed is not None:
                perf_filters.append(f"Speed: {self.performance.min_speed or 'Any'}-{self.performance.max_speed or 'Any'} km/h")
            if self.performance.min_boardings is not None or self.performance.max_boardings is not None:
                perf_filters.append(f"Boardings: {self.performance.min_boardings or 'Any'}-{self.performance.max_boardings or 'Any'}")
            
            if perf_filters:
                summary['total_filters'] += 1
                summary['active_filters'].append({
                    'type': 'performance',
                    'description': '; '.join(perf_filters)
                })
        
        if self.text_search and self.text_search.search_term.strip():
            summary['total_filters'] += 1
            summary['active_filters'].append({
                'type': 'text_search',
                'description': f"Search: '{self.text_search.search_term}'"
            })
        
        summary['total_filters'] += len(self.numeric_ranges) + len(self.categorical)
        
        return summary


class FilterSystem:
    """Advanced filtering system for dashboard data."""
    
    def __init__(self):
        self.saved_filters: Dict[str, FilterSet] = {}
        self.filter_history: List[FilterSet] = []
        self.max_history = 10
    
    def create_date_range_filter(self, start_date: Optional[date] = None, 
                                end_date: Optional[date] = None,
                                date_column: str = "Date") -> DateRangeFilter:
        """Create a date range filter."""
        return DateRangeFilter(start_date, end_date, date_column)
    
    def create_route_filter(self, selected_routes: List[str] = None,
                           route_column: str = "Route",
                           include_all: bool = True) -> RouteFilter:
        """Create a route filter."""
        return RouteFilter(selected_routes or [], route_column, include_all)
    
    def create_performance_filter(self, **kwargs) -> PerformanceFilter:
        """Create a performance filter."""
        return PerformanceFilter(**kwargs)
    
    def create_text_search_filter(self, search_term: str,
                                 search_columns: List[str] = None,
                                 case_sensitive: bool = False,
                                 exact_match: bool = False) -> TextSearchFilter:
        """Create a text search filter."""
        return TextSearchFilter(search_term, search_columns or [], case_sensitive, exact_match)
    
    def apply_filters(self, data: pd.DataFrame, filter_set: FilterSet) -> pd.DataFrame:
        """Apply a complete filter set to data."""
        # Add to history
        self._add_to_history(filter_set)
        
        return filter_set.apply_all(data)
    
    def get_available_routes(self, data: pd.DataFrame, route_column: str = "Route") -> List[str]:
        """Get list of available routes from data."""
        if route_column not in data.columns:
            return []
        
        return sorted(data[route_column].dropna().unique().tolist())
    
    def get_date_range(self, data: pd.DataFrame, date_column: str = "Date") -> Tuple[Optional[date], Optional[date]]:
        """Get the available date range from data."""
        if date_column not in data.columns:
            return None, None
        
        try:
            date_series = pd.to_datetime(data[date_column], errors='coerce').dropna()
            if date_series.empty:
                return None, None
            
            return date_series.min().date(), date_series.max().date()
        except Exception:
            return None, None
    
    def get_numeric_ranges(self, data: pd.DataFrame) -> Dict[str, Tuple[float, float]]:
        """Get numeric ranges for all numeric columns."""
        ranges = {}
        
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            col_data = data[col].dropna()
            if not col_data.empty:
                ranges[col] = (float(col_data.min()), float(col_data.max()))
        
        return ranges
    
    def get_categorical_values(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """Get unique values for categorical columns."""
        values = {}
        
        categorical_columns = data.select_dtypes(include=['object']).columns
        
        for col in categorical_columns:
            unique_vals = data[col].dropna().unique()
            if len(unique_vals) <= 50:  # Only include if not too many unique values
                values[col] = sorted(unique_vals.tolist())
        
        return values
    
    def save_filter_set(self, name: str, filter_set: FilterSet) -> None:
        """Save a filter set for later use."""
        self.saved_filters[name] = filter_set
    
    def load_filter_set(self, name: str) -> Optional[FilterSet]:
        """Load a saved filter set."""
        return self.saved_filters.get(name)
    
    def get_saved_filter_names(self) -> List[str]:
        """Get list of saved filter names."""
        return list(self.saved_filters.keys())
    
    def delete_saved_filter(self, name: str) -> bool:
        """Delete a saved filter set."""
        if name in self.saved_filters:
            del self.saved_filters[name]
            return True
        return False
    
    def _add_to_history(self, filter_set: FilterSet) -> None:
        """Add filter set to history."""
        # Don't add empty filter sets
        if filter_set.is_empty():
            return
        
        # Add to beginning of history
        self.filter_history.insert(0, filter_set)
        
        # Limit history size
        if len(self.filter_history) > self.max_history:
            self.filter_history = self.filter_history[:self.max_history]
    
    def get_filter_history(self) -> List[FilterSet]:
        """Get filter history."""
        return self.filter_history.copy()
    
    def clear_history(self) -> None:
        """Clear filter history."""
        self.filter_history.clear()
    
    def create_smart_filter(self, data: pd.DataFrame, query: str) -> FilterSet:
        """Create a smart filter based on natural language query."""
        filter_set = FilterSet()
        
        # Simple natural language processing for common patterns
        query_lower = query.lower()
        
        # Date patterns
        if 'today' in query_lower:
            filter_set.date_range = DateRangeFilter(start_date=date.today(), end_date=date.today())
        elif 'yesterday' in query_lower:
            yesterday = date.today() - timedelta(days=1)
            filter_set.date_range = DateRangeFilter(start_date=yesterday, end_date=yesterday)
        elif 'last week' in query_lower:
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
            filter_set.date_range = DateRangeFilter(start_date=start_date, end_date=end_date)
        
        # Route patterns
        route_matches = re.findall(r'route\s+(\w+)', query_lower)
        if route_matches:
            available_routes = self.get_available_routes(data)
            matching_routes = [route for route in available_routes if any(match in route.lower() for match in route_matches)]
            if matching_routes:
                filter_set.routes = RouteFilter(selected_routes=matching_routes, include_all=False)
        
        # Performance patterns
        speed_matches = re.findall(r'speed\s*[><=]+\s*(\d+)', query_lower)
        if speed_matches:
            speed_val = float(speed_matches[0])
            if '>' in query_lower:
                filter_set.performance = PerformanceFilter(min_speed=speed_val)
            elif '<' in query_lower:
                filter_set.performance = PerformanceFilter(max_speed=speed_val)
        
        # Text search fallback
        if filter_set.is_empty():
            filter_set.text_search = TextSearchFilter(search_term=query)
        
        return filter_set


# Global filter system instance
filter_system = FilterSystem()