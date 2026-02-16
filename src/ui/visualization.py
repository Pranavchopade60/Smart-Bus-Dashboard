"""
Enhanced visualization engine for the Smart Bus Dashboard.

This module provides interactive charts with accessibility features,
drill-down capabilities, and performance optimization.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
import hashlib
import json
from datetime import datetime, timedelta

from src.config.settings import config_manager
from src.enhancements.accessibility import accessibility_manager


class ChartType(Enum):
    """Available chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    AREA = "area"


@dataclass
class ChartConfig:
    """Configuration for chart rendering."""
    title: str
    chart_type: ChartType
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    hover_data: List[str] = field(default_factory=list)
    custom_colors: Optional[List[str]] = None
    height: int = 400
    width: Optional[int] = None
    show_legend: bool = True
    interactive: bool = True
    accessibility_mode: bool = False


@dataclass
class ChartPerformance:
    """Performance metrics for chart rendering."""
    render_time: float
    data_points: int
    chart_type: str
    optimization_applied: bool = False
    cache_hit: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CacheEntry:
    """Cache entry for visualization data."""
    data_hash: str
    config_hash: str
    figure: go.Figure
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)


@dataclass
class RealTimeConfig:
    """Configuration for real-time updates."""
    enabled: bool = True
    update_interval: float = 1.0  # seconds
    auto_refresh: bool = True
    performance_monitoring: bool = True
    cache_enabled: bool = True
    max_cache_size: int = 100


class VisualizationEngine:
    """Enhanced visualization engine with accessibility and performance features."""
    
    def __init__(self):
        self.performance_metrics: List[ChartPerformance] = []
        self.chart_cache: Dict[str, CacheEntry] = {}
        self.accessibility_settings = config_manager.user_preferences.accessibility_settings
        self.viz_settings = config_manager.user_preferences.visualization_settings
        
        # Performance thresholds
        self.max_data_points = 10000
        self.performance_threshold_ms = 500
        
        # Real-time configuration
        self.realtime_config = RealTimeConfig()
        
        # Performance monitoring
        self.performance_monitor_active = False
        self.performance_alerts: List[str] = []
        
        # Cache management
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
        
        # Auto-refresh tracking
        self.auto_refresh_callbacks: Dict[str, Callable] = {}
        self.last_update_times: Dict[str, datetime] = {}
    
    def render_interactive_chart(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """
        Render an interactive chart with accessibility features and caching.
        
        Args:
            data: DataFrame containing the data
            config: Chart configuration
            
        Returns:
            Plotly figure object
        """
        start_time = time.time()
        
        # Generate cache keys
        data_hash = self._generate_data_hash(data)
        config_hash = self._generate_config_hash(config)
        cache_key = f"{data_hash}_{config_hash}"
        
        # Check cache first
        if self.realtime_config.cache_enabled and cache_key in self.chart_cache:
            cache_entry = self.chart_cache[cache_key]
            cache_entry.access_count += 1
            cache_entry.last_accessed = datetime.now()
            
            # Record cache hit
            self.cache_stats['hits'] += 1
            self.cache_stats['total_requests'] += 1
            
            # Record performance with cache hit
            render_time = (time.time() - start_time) * 1000
            self._record_performance(render_time, len(data), config.chart_type.value, False, True)
            
            return cache_entry.figure
        
        # Cache miss - create new chart
        self.cache_stats['misses'] += 1
        self.cache_stats['total_requests'] += 1
        
        # Apply accessibility settings
        if self.accessibility_settings.high_contrast or config.accessibility_mode:
            config = self._apply_accessibility_config(config)
        
        # Optimize data if needed
        optimized_data, optimization_applied = self._optimize_data_for_performance(data)
        
        # Create chart based on type
        fig = self._create_chart(optimized_data, config)
        
        # Apply styling and accessibility features
        fig = self._apply_chart_styling(fig, config)
        fig = self._add_accessibility_features(fig, config)
        
        # Add interactivity
        if config.interactive:
            fig = self._add_interactivity(fig, config)
        
        # Add real-time update capabilities
        if self.realtime_config.enabled:
            fig = self._add_realtime_features(fig, config)
        
        # Cache the result
        if self.realtime_config.cache_enabled:
            self._cache_figure(cache_key, data_hash, config_hash, fig)
        
        # Record performance
        render_time = (time.time() - start_time) * 1000
        self._record_performance(render_time, len(data), config.chart_type.value, optimization_applied, False)
        
        return fig
    
    def _create_chart(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create chart based on configuration."""
        if config.chart_type == ChartType.BAR:
            return self._create_bar_chart(data, config)
        elif config.chart_type == ChartType.LINE:
            return self._create_line_chart(data, config)
        elif config.chart_type == ChartType.PIE:
            return self._create_pie_chart(data, config)
        elif config.chart_type == ChartType.SCATTER:
            return self._create_scatter_chart(data, config)
        elif config.chart_type == ChartType.HISTOGRAM:
            return self._create_histogram(data, config)
        elif config.chart_type == ChartType.BOX:
            return self._create_box_plot(data, config)
        elif config.chart_type == ChartType.HEATMAP:
            return self._create_heatmap(data, config)
        elif config.chart_type == ChartType.AREA:
            return self._create_area_chart(data, config)
        else:
            raise ValueError(f"Unsupported chart type: {config.chart_type}")
    
    def _create_bar_chart(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create bar chart."""
        fig = px.bar(
            data,
            x=config.x_column,
            y=config.y_column,
            color=config.color_column,
            title=config.title,
            hover_data=config.hover_data,
            color_discrete_sequence=config.custom_colors,
            height=config.height,
            width=config.width
        )
        return fig
    
    def _create_line_chart(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create line chart."""
        fig = px.line(
            data,
            x=config.x_column,
            y=config.y_column,
            color=config.color_column,
            title=config.title,
            hover_data=config.hover_data,
            color_discrete_sequence=config.custom_colors,
            height=config.height,
            width=config.width
        )
        return fig
    
    def _create_pie_chart(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create pie chart."""
        fig = px.pie(
            data,
            values=config.y_column,
            names=config.x_column,
            title=config.title,
            color_discrete_sequence=config.custom_colors,
            height=config.height,
            width=config.width
        )
        return fig
    
    def _create_scatter_chart(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create scatter plot."""
        fig = px.scatter(
            data,
            x=config.x_column,
            y=config.y_column,
            color=config.color_column,
            size=config.size_column,
            title=config.title,
            hover_data=config.hover_data,
            color_discrete_sequence=config.custom_colors,
            height=config.height,
            width=config.width
        )
        return fig
    
    def _create_histogram(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create histogram."""
        fig = px.histogram(
            data,
            x=config.x_column,
            color=config.color_column,
            title=config.title,
            color_discrete_sequence=config.custom_colors,
            height=config.height,
            width=config.width
        )
        return fig
    
    def _create_box_plot(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create box plot."""
        fig = px.box(
            data,
            x=config.x_column,
            y=config.y_column,
            color=config.color_column,
            title=config.title,
            color_discrete_sequence=config.custom_colors,
            height=config.height,
            width=config.width
        )
        return fig
    
    def _create_heatmap(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create heatmap."""
        # Prepare data for heatmap
        if config.x_column and config.y_column:
            pivot_data = data.pivot_table(
                values=data.select_dtypes(include=[np.number]).columns[0],
                index=config.y_column,
                columns=config.x_column,
                aggfunc='mean'
            )
        else:
            # Use correlation matrix if no specific columns specified
            numeric_data = data.select_dtypes(include=[np.number])
            pivot_data = numeric_data.corr()
        
        fig = px.imshow(
            pivot_data,
            title=config.title,
            color_continuous_scale=config.custom_colors or 'Viridis',
            height=config.height,
            width=config.width
        )
        return fig
    
    def _create_area_chart(self, data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Create area chart."""
        fig = px.area(
            data,
            x=config.x_column,
            y=config.y_column,
            color=config.color_column,
            title=config.title,
            hover_data=config.hover_data,
            color_discrete_sequence=config.custom_colors,
            height=config.height,
            width=config.width
        )
        return fig
    
    def _apply_chart_styling(self, fig: go.Figure, config: ChartConfig) -> go.Figure:
        """Apply styling to chart."""
        # Get theme colors
        theme = self.viz_settings.chart_theme
        if hasattr(theme, 'value'):
            theme_name = theme.value
        else:
            theme_name = str(theme)
        
        # Update layout
        fig.update_layout(
            title={
                'text': config.title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
            },
            showlegend=config.show_legend,
            template=theme_name,
            font={'family': 'Arial, sans-serif'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Update axes
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            title_font={'size': 14}
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            title_font={'size': 14}
        )
        
        return fig
    
    def _add_accessibility_features(self, fig: go.Figure, config: ChartConfig) -> go.Figure:
        """Add accessibility features to chart."""
        # Add ARIA labels and descriptions
        fig.update_layout(
            title_text=f"{config.title} - Interactive chart",
            annotations=[
                dict(
                    text="Use arrow keys to navigate chart elements",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0, y=-0.1,
                    xanchor='left', yanchor='top',
                    font=dict(size=10, color="gray")
                )
            ]
        )
        
        # Ensure sufficient color contrast
        if self.accessibility_settings.high_contrast:
            fig = self._apply_high_contrast_colors(fig)
        
        # Add pattern fills for colorblind accessibility
        if config.chart_type in [ChartType.BAR, ChartType.PIE]:
            fig = self._add_pattern_fills(fig)
        
        return fig
    
    def _add_interactivity(self, fig: go.Figure, config: ChartConfig) -> go.Figure:
        """Add interactive features to chart."""
        # Configure hover mode
        fig.update_layout(hovermode='closest')
        
        # Add zoom and pan
        fig.update_layout(
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False)
        )
        
        # Add selection tools
        fig.update_layout(
            selectdirection='d',
            dragmode='select'
        )
        
        return fig
    
    def _apply_accessibility_config(self, config: ChartConfig) -> ChartConfig:
        """Apply accessibility modifications to chart config."""
        # Use high contrast colors
        if self.accessibility_settings.high_contrast:
            config.custom_colors = ['#000000', '#FFFFFF', '#808080', '#404040']
        
        # Increase chart height for better visibility
        if self.accessibility_settings.large_text:
            config.height = int(config.height * 1.2)
        
        # Disable animations if reduced motion is enabled
        if self.accessibility_settings.reduced_motion:
            config.interactive = False
        
        return config
    
    def _apply_high_contrast_colors(self, fig: go.Figure) -> go.Figure:
        """Apply high contrast color scheme."""
        high_contrast_colors = ['#000000', '#FFFFFF', '#808080', '#404040', '#C0C0C0']
        
        # Update trace colors
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'marker'):
                if hasattr(trace.marker, 'color'):
                    trace.marker.color = high_contrast_colors[i % len(high_contrast_colors)]
                elif hasattr(trace.marker, 'colors'):  # For pie charts
                    trace.marker.colors = high_contrast_colors[:len(trace.marker.colors or [])]
        
        return fig
    
    def _add_pattern_fills(self, fig: go.Figure) -> go.Figure:
        """Add pattern fills for colorblind accessibility."""
        patterns = ['', '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.']
        
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'marker'):
                pattern_index = i % len(patterns)
                # Note: Pattern fills require Plotly.js 2.0+
                # This is a placeholder for pattern implementation
                pass
        
        return fig
    
    def _optimize_data_for_performance(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
        """Optimize data for better chart performance."""
        optimization_applied = False
        
        # Sample data if too large
        if len(data) > self.max_data_points:
            sampled_data = data.sample(n=self.max_data_points, random_state=42)
            optimization_applied = True
            return sampled_data, optimization_applied
        
        return data, optimization_applied
    
    def _record_performance(self, render_time: float, data_points: int, 
                          chart_type: str, optimization_applied: bool, cache_hit: bool = False) -> None:
        """Record chart performance metrics."""
        performance = ChartPerformance(
            render_time=render_time,
            data_points=data_points,
            chart_type=chart_type,
            optimization_applied=optimization_applied,
            cache_hit=cache_hit,
            timestamp=datetime.now()
        )
        
        self.performance_metrics.append(performance)
        
        # Keep only last 100 metrics
        if len(self.performance_metrics) > 100:
            self.performance_metrics = self.performance_metrics[-100:]
        
        # Performance monitoring and alerts
        if self.realtime_config.performance_monitoring:
            self._check_performance_thresholds(performance)
        
        # Warn if performance is poor
        if render_time > self.performance_threshold_ms and not cache_hit:
            alert_msg = f"Chart rendering took {render_time:.0f}ms (threshold: {self.performance_threshold_ms}ms)"
            self.performance_alerts.append(alert_msg)
            if len(self.performance_alerts) > 10:
                self.performance_alerts = self.performance_alerts[-10:]
            
            if hasattr(st, 'warning'):
                st.warning(alert_msg)
    
    def add_drill_down_capability(self, fig: go.Figure, drill_down_callback: Callable) -> go.Figure:
        """Add drill-down capability to chart."""
        # This would typically involve JavaScript callbacks
        # For Streamlit, we'll use session state to handle drill-down
        
        # Add click event handling instructions
        fig.update_layout(
            annotations=[
                dict(
                    text="Click on chart elements to drill down",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=1, y=1.02,
                    xanchor='right', yanchor='bottom',
                    font=dict(size=10, color="blue")
                )
            ]
        )
        
        return fig
    
    def render_chart_with_controls(self, data: pd.DataFrame, config: ChartConfig,
                                 show_controls: bool = True) -> go.Figure:
        """Render chart with interactive controls."""
        if show_controls:
            # Chart type selector
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                chart_types = [ct.value for ct in ChartType]
                selected_type = st.selectbox(
                    "Chart Type",
                    chart_types,
                    index=chart_types.index(config.chart_type.value)
                )
                config.chart_type = ChartType(selected_type)
            
            with col2:
                if config.x_column:
                    x_options = data.columns.tolist()
                    x_index = x_options.index(config.x_column) if config.x_column in x_options else 0
                    config.x_column = st.selectbox("X-axis", x_options, index=x_index)
            
            with col3:
                if config.y_column:
                    y_options = data.select_dtypes(include=[np.number]).columns.tolist()
                    y_index = y_options.index(config.y_column) if config.y_column in y_options else 0
                    config.y_column = st.selectbox("Y-axis", y_options, index=y_index)
            
            # Additional controls
            with st.expander("Advanced Options"):
                config.height = st.slider("Chart Height", 300, 800, config.height)
                config.show_legend = st.checkbox("Show Legend", config.show_legend)
                config.interactive = st.checkbox("Interactive", config.interactive)
        
        # Render chart
        fig = self.render_interactive_chart(data, config)
        
        return fig
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.performance_metrics:
            return {"message": "No performance data available"}
        
        render_times = [p.render_time for p in self.performance_metrics]
        data_points = [p.data_points for p in self.performance_metrics]
        cache_hits = sum(1 for p in self.performance_metrics if p.cache_hit)
        
        return {
            "total_charts": len(self.performance_metrics),
            "avg_render_time": np.mean(render_times),
            "max_render_time": np.max(render_times),
            "min_render_time": np.min(render_times),
            "avg_data_points": np.mean(data_points),
            "optimizations_applied": sum(1 for p in self.performance_metrics if p.optimization_applied),
            "performance_issues": sum(1 for p in self.performance_metrics if p.render_time > self.performance_threshold_ms),
            "cache_hit_rate": cache_hits / len(self.performance_metrics) if self.performance_metrics else 0,
            "cache_stats": self.cache_stats.copy(),
            "recent_alerts": self.performance_alerts[-5:] if self.performance_alerts else []
        }
    
    # Real-time update methods
    def _generate_data_hash(self, data: pd.DataFrame) -> str:
        """Generate hash for data to use as cache key."""
        try:
            # Create a hash based on data content and shape
            data_str = f"{data.shape}_{data.dtypes.to_dict()}_{data.head().to_string()}"
            return hashlib.md5(data_str.encode()).hexdigest()[:16]
        except Exception:
            # Fallback to timestamp-based hash
            return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    
    def _generate_config_hash(self, config: ChartConfig) -> str:
        """Generate hash for chart configuration."""
        try:
            config_dict = {
                'title': config.title,
                'chart_type': config.chart_type.value,
                'x_column': config.x_column,
                'y_column': config.y_column,
                'color_column': config.color_column,
                'height': config.height,
                'show_legend': config.show_legend,
                'interactive': config.interactive
            }
            config_str = json.dumps(config_dict, sort_keys=True)
            return hashlib.md5(config_str.encode()).hexdigest()[:16]
        except Exception:
            return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    
    def _cache_figure(self, cache_key: str, data_hash: str, config_hash: str, figure: go.Figure) -> None:
        """Cache a figure for future use."""
        # Check cache size and evict if necessary
        if len(self.chart_cache) >= self.realtime_config.max_cache_size:
            self._evict_cache_entries()
        
        # Create cache entry
        cache_entry = CacheEntry(
            data_hash=data_hash,
            config_hash=config_hash,
            figure=figure,
            timestamp=datetime.now()
        )
        
        self.chart_cache[cache_key] = cache_entry
    
    def _evict_cache_entries(self) -> None:
        """Evict least recently used cache entries."""
        if not self.chart_cache:
            return
        
        # Sort by last accessed time and remove oldest entries
        sorted_entries = sorted(
            self.chart_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest 25% of entries
        num_to_remove = max(1, len(sorted_entries) // 4)
        
        for i in range(num_to_remove):
            cache_key = sorted_entries[i][0]
            del self.chart_cache[cache_key]
            self.cache_stats['evictions'] += 1
    
    def _add_realtime_features(self, fig: go.Figure, config: ChartConfig) -> go.Figure:
        """Add real-time update features to chart."""
        # Add update timestamp annotation
        current_time = datetime.now().strftime("%H:%M:%S")
        
        fig.add_annotation(
            text=f"Last updated: {current_time}",
            showarrow=False,
            xref="paper", yref="paper",
            x=1, y=-0.1,
            xanchor='right', yanchor='top',
            font=dict(size=10, color="gray")
        )
        
        # Add auto-refresh indicator if enabled
        if self.realtime_config.auto_refresh:
            fig.add_annotation(
                text="🔄 Auto-refresh enabled",
                showarrow=False,
                xref="paper", yref="paper",
                x=0, y=-0.1,
                xanchor='left', yanchor='top',
                font=dict(size=10, color="green")
            )
        
        return fig
    
    def _check_performance_thresholds(self, performance: ChartPerformance) -> None:
        """Check performance against thresholds and generate alerts."""
        # Check render time threshold
        if performance.render_time > self.performance_threshold_ms * 2:
            alert = f"Severe performance issue: {performance.render_time:.0f}ms for {performance.chart_type}"
            self.performance_alerts.append(alert)
        
        # Check data size threshold
        if performance.data_points > self.max_data_points * 1.5:
            alert = f"Large dataset warning: {performance.data_points} points in {performance.chart_type}"
            self.performance_alerts.append(alert)
    
    def enable_auto_refresh(self, chart_id: str, update_callback: Callable, interval: float = None) -> None:
        """Enable auto-refresh for a specific chart."""
        if interval is None:
            interval = self.realtime_config.update_interval
        
        self.auto_refresh_callbacks[chart_id] = update_callback
        self.last_update_times[chart_id] = datetime.now()
    
    def disable_auto_refresh(self, chart_id: str) -> None:
        """Disable auto-refresh for a specific chart."""
        if chart_id in self.auto_refresh_callbacks:
            del self.auto_refresh_callbacks[chart_id]
        if chart_id in self.last_update_times:
            del self.last_update_times[chart_id]
    
    def should_update_chart(self, chart_id: str) -> bool:
        """Check if a chart should be updated based on auto-refresh settings."""
        if not self.realtime_config.auto_refresh:
            return False
        
        if chart_id not in self.last_update_times:
            return True
        
        last_update = self.last_update_times[chart_id]
        time_since_update = datetime.now() - last_update
        
        return time_since_update.total_seconds() >= self.realtime_config.update_interval
    
    def update_chart_data(self, chart_id: str, new_data: pd.DataFrame, config: ChartConfig) -> go.Figure:
        """Update chart with new data and return updated figure."""
        # Mark update time
        self.last_update_times[chart_id] = datetime.now()
        
        # Clear relevant cache entries
        self._invalidate_cache_for_data(new_data)
        
        # Render updated chart
        return self.render_interactive_chart(new_data, config)
    
    def _invalidate_cache_for_data(self, data: pd.DataFrame) -> None:
        """Invalidate cache entries that might be affected by data changes."""
        data_hash = self._generate_data_hash(data)
        
        # Remove cache entries with matching data hash
        keys_to_remove = []
        for cache_key, cache_entry in self.chart_cache.items():
            if cache_entry.data_hash == data_hash:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.chart_cache[key]
    
    def clear_cache(self) -> None:
        """Clear all cached figures."""
        self.chart_cache.clear()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state."""
        total_size = len(self.chart_cache)
        
        if total_size == 0:
            return {
                'size': 0,
                'max_size': self.realtime_config.max_cache_size,
                'hit_rate': 0,
                'stats': self.cache_stats.copy()
            }
        
        # Calculate cache statistics
        access_counts = [entry.access_count for entry in self.chart_cache.values()]
        timestamps = [entry.timestamp for entry in self.chart_cache.values()]
        
        hit_rate = (self.cache_stats['hits'] / max(1, self.cache_stats['total_requests'])) * 100
        
        return {
            'size': total_size,
            'max_size': self.realtime_config.max_cache_size,
            'hit_rate': hit_rate,
            'avg_access_count': np.mean(access_counts) if access_counts else 0,
            'oldest_entry': min(timestamps) if timestamps else None,
            'newest_entry': max(timestamps) if timestamps else None,
            'stats': self.cache_stats.copy()
        }
    
    def configure_realtime_updates(self, **kwargs) -> None:
        """Configure real-time update settings."""
        for key, value in kwargs.items():
            if hasattr(self.realtime_config, key):
                setattr(self.realtime_config, key, value)
    
    def render_realtime_controls(self) -> None:
        """Render controls for real-time update configuration."""
        st.markdown("### ⚡ Real-time Update Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            enabled = st.checkbox(
                "Enable Real-time Updates",
                value=self.realtime_config.enabled,
                help="Enable automatic chart updates when data changes"
            )
            self.realtime_config.enabled = enabled
        
        with col2:
            auto_refresh = st.checkbox(
                "Auto Refresh",
                value=self.realtime_config.auto_refresh,
                help="Automatically refresh charts at regular intervals"
            )
            self.realtime_config.auto_refresh = auto_refresh
        
        with col3:
            cache_enabled = st.checkbox(
                "Enable Caching",
                value=self.realtime_config.cache_enabled,
                help="Cache chart figures for better performance"
            )
            self.realtime_config.cache_enabled = cache_enabled
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                update_interval = st.slider(
                    "Update Interval (seconds)",
                    min_value=0.5,
                    max_value=10.0,
                    value=self.realtime_config.update_interval,
                    step=0.5,
                    help="How often to check for updates"
                )
                self.realtime_config.update_interval = update_interval
            
            with col2:
                max_cache_size = st.slider(
                    "Max Cache Size",
                    min_value=10,
                    max_value=500,
                    value=self.realtime_config.max_cache_size,
                    help="Maximum number of charts to cache"
                )
                self.realtime_config.max_cache_size = max_cache_size
        
        # Cache management
        st.markdown("#### 🗄️ Cache Management")
        
        cache_info = self.get_cache_info()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cache Size", f"{cache_info['size']}/{cache_info['max_size']}")
        
        with col2:
            st.metric("Hit Rate", f"{cache_info['hit_rate']:.1f}%")
        
        with col3:
            st.metric("Total Requests", cache_info['stats']['total_requests'])
        
        with col4:
            if st.button("Clear Cache"):
                self.clear_cache()
                st.success("Cache cleared!")
                st.rerun()
    
    def render_performance_dashboard(self) -> None:
        """Render performance monitoring dashboard."""
        st.markdown("### 📊 Chart Performance Metrics")
        
        summary = self.get_performance_summary()
        
        if "message" in summary:
            st.info(summary["message"])
            return
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Charts", summary["total_charts"])
        
        with col2:
            avg_time = summary['avg_render_time']
            delta_color = "normal" if avg_time < self.performance_threshold_ms else "inverse"
            st.metric("Avg Render Time", f"{avg_time:.1f}ms", delta_color=delta_color)
        
        with col3:
            st.metric("Cache Hit Rate", f"{summary['cache_hit_rate']:.1%}")
        
        with col4:
            st.metric("Performance Issues", summary["performance_issues"])
        
        # Recent alerts
        if summary["recent_alerts"]:
            st.markdown("#### ⚠️ Recent Performance Alerts")
            for alert in summary["recent_alerts"]:
                st.warning(alert)
        
        # Performance trend chart
        if len(self.performance_metrics) > 1:
            perf_df = pd.DataFrame([
                {
                    'Chart': i,
                    'Render Time (ms)': p.render_time,
                    'Data Points': p.data_points,
                    'Chart Type': p.chart_type,
                    'Cache Hit': 'Yes' if p.cache_hit else 'No',
                    'Optimized': 'Yes' if p.optimization_applied else 'No'
                }
                for i, p in enumerate(self.performance_metrics)
            ])
            
            # Performance over time
            fig = px.line(
                perf_df,
                x='Chart',
                y='Render Time (ms)',
                title='Chart Rendering Performance Over Time',
                color='Chart Type',
                hover_data=['Cache Hit', 'Optimized', 'Data Points']
            )
            
            fig.add_hline(
                y=self.performance_threshold_ms,
                line_dash="dash",
                line_color="red",
                annotation_text="Performance Threshold"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Cache performance analysis
            if summary['cache_stats']['total_requests'] > 0:
                st.markdown("#### 🗄️ Cache Performance Analysis")
                
                cache_df = pd.DataFrame([
                    {'Metric': 'Cache Hits', 'Count': summary['cache_stats']['hits']},
                    {'Metric': 'Cache Misses', 'Count': summary['cache_stats']['misses']},
                    {'Metric': 'Cache Evictions', 'Count': summary['cache_stats']['evictions']}
                ])
                
                fig_cache = px.pie(
                    cache_df,
                    values='Count',
                    names='Metric',
                    title='Cache Performance Distribution'
                )
                
                st.plotly_chart(fig_cache, use_container_width=True)
        
        # Real-time controls
        self.render_realtime_controls()


# Global visualization engine instance
visualization_engine = VisualizationEngine()