"""
Translation Statistics Service

Handles collection, calculation, and reporting of translation metrics.
Follows Single Responsibility Principle by separating statistics concerns.

Author: DarkLightX / Dana Edwards
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import time


@dataclass
class TranslationMetric:
    """Individual translation metric data."""
    timestamp: datetime
    engine_name: str
    direction: str
    success: bool
    processing_time: float
    confidence: float = 0.0
    error_type: Optional[str] = None


@dataclass
class EngineStatistics:
    """Statistics for a specific translation engine."""
    name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_processing_time: float = 0.0
    average_confidence: float = 0.0
    last_used: Optional[datetime] = None
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average processing time."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_processing_time / self.successful_requests


class TranslationStatisticsService:
    """
    Service for collecting and analyzing translation statistics.
    
    Implements Single Responsibility Principle by focusing solely on metrics.
    Thread-safe for concurrent access.
    """
    
    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history
        self.metrics_history: deque = deque(maxlen=max_metrics_history)
        self.engine_stats: Dict[str, EngineStatistics] = {}
        self.session_start_time = datetime.utcnow()
        self._lock = threading.RLock()
        
        # Real-time tracking
        self.total_translations = 0
        self.successful_translations = 0
        self.failed_translations = 0
    
    def record_translation(
        self,
        engine_name: str,
        direction: str,
        success: bool,
        processing_time: float,
        confidence: float = 0.0,
        error_type: Optional[str] = None
    ) -> None:
        """Record a translation event."""
        with self._lock:
            # Create metric record
            metric = TranslationMetric(
                timestamp=datetime.utcnow(),
                engine_name=engine_name,
                direction=direction,
                success=success,
                processing_time=processing_time,
                confidence=confidence,
                error_type=error_type
            )
            
            # Add to history
            self.metrics_history.append(metric)
            
            # Update engine statistics
            if engine_name not in self.engine_stats:
                self.engine_stats[engine_name] = EngineStatistics(name=engine_name)
            
            engine_stat = self.engine_stats[engine_name]
            engine_stat.total_requests += 1
            engine_stat.last_used = metric.timestamp
            
            if success:
                engine_stat.successful_requests += 1
                engine_stat.total_processing_time += processing_time
                # Update rolling average confidence
                if engine_stat.successful_requests == 1:
                    engine_stat.average_confidence = confidence
                else:
                    # Weighted average with more recent values having higher weight
                    weight = 0.1  # 10% weight to new value
                    engine_stat.average_confidence = (
                        engine_stat.average_confidence * (1 - weight) + confidence * weight
                    )
                self.successful_translations += 1
            else:
                engine_stat.failed_requests += 1
                if error_type:
                    engine_stat.error_counts[error_type] = engine_stat.error_counts.get(error_type, 0) + 1
                self.failed_translations += 1
            
            self.total_translations += 1
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall translation statistics."""
        with self._lock:
            uptime = datetime.utcnow() - self.session_start_time
            
            return {
                'total_translations': self.total_translations,
                'successful_translations': self.successful_translations,
                'failed_translations': self.failed_translations,
                'overall_success_rate': self._calculate_success_rate(),
                'uptime_seconds': uptime.total_seconds(),
                'metrics_history_size': len(self.metrics_history),
                'active_engines': len(self.engine_stats),
                'session_start_time': self.session_start_time.isoformat()
            }
    
    def get_engine_statistics(self, engine_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for specific engine or all engines."""
        with self._lock:
            if engine_name:
                if engine_name not in self.engine_stats:
                    return {}
                return self._engine_stats_to_dict(self.engine_stats[engine_name])
            
            return {
                name: self._engine_stats_to_dict(stats)
                for name, stats in self.engine_stats.items()
            }
    
    def get_performance_metrics(self, time_window_hours: float = 24.0) -> Dict[str, Any]:
        """Get performance metrics for a specific time window."""
        with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            recent_metrics = [
                metric for metric in self.metrics_history
                if metric.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {
                    'time_window_hours': time_window_hours,
                    'total_requests': 0,
                    'average_response_time': 0.0,
                    'p95_response_time': 0.0,
                    'requests_per_hour': 0.0
                }
            
            # Calculate metrics
            successful_metrics = [m for m in recent_metrics if m.success]
            processing_times = [m.processing_time for m in successful_metrics]
            
            # Sort for percentile calculation
            processing_times.sort()
            
            return {
                'time_window_hours': time_window_hours,
                'total_requests': len(recent_metrics),
                'successful_requests': len(successful_metrics),
                'average_response_time': sum(processing_times) / len(processing_times) if processing_times else 0.0,
                'p95_response_time': self._calculate_percentile(processing_times, 95),
                'requests_per_hour': len(recent_metrics) / time_window_hours,
                'success_rate': (len(successful_metrics) / len(recent_metrics)) * 100
            }
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """Get detailed error analysis."""
        with self._lock:
            error_summary = defaultdict(int)
            engine_errors = defaultdict(lambda: defaultdict(int))
            
            for engine_name, stats in self.engine_stats.items():
                for error_type, count in stats.error_counts.items():
                    error_summary[error_type] += count
                    engine_errors[engine_name][error_type] = count
            
            return {
                'total_error_types': len(error_summary),
                'error_summary': dict(error_summary),
                'errors_by_engine': dict(engine_errors),
                'most_common_error': max(error_summary.items(), key=lambda x: x[1])[0] if error_summary else None
            }
    
    def reset_statistics(self) -> None:
        """Reset all statistics and metrics history."""
        with self._lock:
            self.metrics_history.clear()
            self.engine_stats.clear()
            self.total_translations = 0
            self.successful_translations = 0
            self.failed_translations = 0
            self.session_start_time = datetime.utcnow()
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_translations == 0:
            return 0.0
        return (self.successful_translations / self.total_translations) * 100
    
    def _engine_stats_to_dict(self, stats: EngineStatistics) -> Dict[str, Any]:
        """Convert EngineStatistics to dictionary."""
        return {
            'name': stats.name,
            'total_requests': stats.total_requests,
            'successful_requests': stats.successful_requests,
            'failed_requests': stats.failed_requests,
            'success_rate': stats.success_rate,
            'average_processing_time': stats.average_processing_time,
            'average_confidence': stats.average_confidence,
            'last_used': stats.last_used.isoformat() if stats.last_used else None,
            'error_counts': dict(stats.error_counts)
        }
    
    def _calculate_percentile(self, sorted_values: list, percentile: float) -> float:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0.0
        
        index = (percentile / 100) * (len(sorted_values) - 1)
        if index.is_integer():
            return sorted_values[int(index)]
        
        # Linear interpolation
        lower_index = int(index)
        upper_index = lower_index + 1
        weight = index - lower_index
        
        if upper_index >= len(sorted_values):
            return sorted_values[lower_index]
        
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight