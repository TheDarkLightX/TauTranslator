"""
Translation Health Monitoring Service

Implements health monitoring for translation engines with circuit breaker pattern.
Follows Single Responsibility Principle by separating health concerns.

Author: DarkLightX / Dana Edwards
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class HealthCheck:
    """Individual health check result."""
    timestamp: datetime
    engine_name: str
    status: HealthStatus
    response_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: float = 60.0      # Seconds before attempting recovery
    success_threshold: int = 3          # Successes needed to close
    health_check_interval: float = 30.0 # Seconds between health checks
    max_response_time: float = 5.0      # Maximum acceptable response time


@dataclass
class EngineHealth:
    """Health information for a translation engine."""
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    circuit_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_check_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    total_checks: int = 0
    total_failures: int = 0
    average_response_time: float = 0.0
    error_message: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_checks == 0:
            return 0.0
        return ((self.total_checks - self.total_failures) / self.total_checks) * 100
    
    @property
    def is_available(self) -> bool:
        """Check if engine is available for requests."""
        return self.circuit_state != CircuitState.OPEN


class TranslationHealthMonitor:
    """
    Health monitoring service for translation engines.
    
    Features:
    - Continuous health checking
    - Circuit breaker pattern for failing engines
    - Health history tracking
    - Alerting threshold monitoring
    - Thread-safe operations
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.engine_health: Dict[str, EngineHealth] = {}
        self.health_history: deque = deque(maxlen=1000)
        self.alert_callbacks: List[Callable[[str, HealthStatus, str], None]] = []
        self._lock = threading.RLock()
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        # Health check thresholds
        self.status_thresholds = {
            HealthStatus.HEALTHY: 95.0,     # >= 95% success rate
            HealthStatus.DEGRADED: 80.0,    # >= 80% success rate
            HealthStatus.UNHEALTHY: 50.0,   # >= 50% success rate
            # < 50% = CRITICAL
        }
        
        self.logger = logging.getLogger(__name__)
    
    def register_engine(self, engine_name: str, health_check_func: Optional[Callable[[], bool]] = None) -> None:
        """Register an engine for health monitoring."""
        with self._lock:
            if engine_name not in self.engine_health:
                self.engine_health[engine_name] = EngineHealth(name=engine_name)
                self.logger.info(f"Registered engine for health monitoring: {engine_name}")
            
            # Store health check function (in real implementation)
            # For now, we'll use a simple test translation approach
    
    def check_engine_health(self, engine_name: str, engine_instance=None) -> HealthCheck:
        """Perform health check on specific engine."""
        start_time = time.time()
        
        try:
            # Perform basic health check (simple translation test)
            if engine_instance and hasattr(engine_instance, 'translate'):
                from ..translators.base import TranslationDirection
                test_result = engine_instance.translate("test", TranslationDirection.TO_TAU)
                
                response_time = time.time() - start_time
                
                # Determine health status based on result and response time
                if test_result.success and response_time <= self.config.max_response_time:
                    status = HealthStatus.HEALTHY
                    error_msg = None
                elif test_result.success:
                    status = HealthStatus.DEGRADED
                    error_msg = f"Slow response: {response_time:.2f}s"
                else:
                    status = HealthStatus.UNHEALTHY
                    error_msg = test_result.error_message or "Translation failed"
            else:
                # No engine instance provided - basic availability check
                status = HealthStatus.UNKNOWN
                error_msg = "Engine instance not available for testing"
                response_time = time.time() - start_time
        
        except Exception as e:
            status = HealthStatus.CRITICAL
            error_msg = f"Health check failed: {str(e)}"
            response_time = time.time() - start_time
        
        # Create health check record
        health_check = HealthCheck(
            timestamp=datetime.utcnow(),
            engine_name=engine_name,
            status=status,
            response_time=response_time,
            error_message=error_msg
        )
        
        # Update engine health
        self._update_engine_health(health_check)
        
        # Add to history
        self.health_history.append(health_check)
        
        return health_check
    
    def _update_engine_health(self, health_check: HealthCheck) -> None:
        """Update engine health based on check result."""
        with self._lock:
            engine_name = health_check.engine_name
            
            if engine_name not in self.engine_health:
                self.engine_health[engine_name] = EngineHealth(name=engine_name)
            
            engine = self.engine_health[engine_name]
            
            # Update basic info
            engine.status = health_check.status
            engine.last_check_time = health_check.timestamp
            engine.total_checks += 1
            engine.error_message = health_check.error_message
            
            # Update response time (rolling average)
            if engine.total_checks == 1:
                engine.average_response_time = health_check.response_time
            else:
                # Weighted average with 10% weight to new value
                weight = 0.1
                engine.average_response_time = (
                    engine.average_response_time * (1 - weight) + 
                    health_check.response_time * weight
                )
            
            # Update success/failure tracking
            is_success = health_check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            
            if is_success:
                engine.consecutive_successes += 1
                engine.consecutive_failures = 0
                engine.last_success_time = health_check.timestamp
            else:
                engine.consecutive_failures += 1
                engine.consecutive_successes = 0
                engine.total_failures += 1
                engine.last_failure_time = health_check.timestamp
            
            # Update circuit breaker state
            self._update_circuit_breaker(engine)
            
            # Check for alerts
            self._check_alert_conditions(engine)
    
    def _update_circuit_breaker(self, engine: EngineHealth) -> None:
        """Update circuit breaker state based on health metrics."""
        current_state = engine.circuit_state
        
        if current_state == CircuitState.CLOSED:
            # Check if we should open the circuit
            if engine.consecutive_failures >= self.config.failure_threshold:
                engine.circuit_state = CircuitState.OPEN
                self.logger.warning(f"Circuit breaker OPENED for engine {engine.name}")
                self._trigger_alert(
                    engine.name, 
                    HealthStatus.CRITICAL,
                    f"Circuit breaker opened due to {engine.consecutive_failures} consecutive failures"
                )
        
        elif current_state == CircuitState.OPEN:
            # Check if we should attempt recovery
            if (engine.last_failure_time and 
                datetime.utcnow() - engine.last_failure_time > timedelta(seconds=self.config.recovery_timeout)):
                engine.circuit_state = CircuitState.HALF_OPEN
                self.logger.info(f"Circuit breaker HALF-OPEN for engine {engine.name} - attempting recovery")
        
        elif current_state == CircuitState.HALF_OPEN:
            # Check if we should close or re-open
            if engine.consecutive_successes >= self.config.success_threshold:
                engine.circuit_state = CircuitState.CLOSED
                self.logger.info(f"Circuit breaker CLOSED for engine {engine.name} - recovery successful")
            elif engine.consecutive_failures > 0:
                engine.circuit_state = CircuitState.OPEN
                self.logger.warning(f"Circuit breaker RE-OPENED for engine {engine.name} - recovery failed")
    
    def _check_alert_conditions(self, engine: EngineHealth) -> None:
        """Check if alert conditions are met."""
        # Alert on status degradation
        if engine.status == HealthStatus.CRITICAL:
            self._trigger_alert(
                engine.name,
                HealthStatus.CRITICAL,
                f"Engine critically unhealthy: {engine.error_message}"
            )
        elif engine.status == HealthStatus.UNHEALTHY and engine.consecutive_failures >= 3:
            self._trigger_alert(
                engine.name,
                HealthStatus.UNHEALTHY,
                f"Engine unhealthy for {engine.consecutive_failures} consecutive checks"
            )
    
    def _trigger_alert(self, engine_name: str, status: HealthStatus, message: str) -> None:
        """Trigger alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                callback(engine_name, status, message)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable[[str, HealthStatus, str], None]) -> None:
        """Add alert callback function."""
        self.alert_callbacks.append(callback)
    
    def get_engine_health(self, engine_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health information for engines."""
        with self._lock:
            if engine_name:
                if engine_name not in self.engine_health:
                    return {}
                return self._engine_health_to_dict(self.engine_health[engine_name])
            
            return {
                name: self._engine_health_to_dict(health)
                for name, health in self.engine_health.items()
            }
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        with self._lock:
            if not self.engine_health:
                return {
                    'status': HealthStatus.UNKNOWN.value,
                    'total_engines': 0,
                    'healthy_engines': 0,
                    'degraded_engines': 0,
                    'unhealthy_engines': 0,
                    'critical_engines': 0
                }
            
            # Count engines by status
            status_counts = defaultdict(int)
            available_engines = 0
            
            for engine in self.engine_health.values():
                status_counts[engine.status] += 1
                if engine.is_available:
                    available_engines += 1
            
            # Determine overall status
            total_engines = len(self.engine_health)
            if status_counts[HealthStatus.CRITICAL] > 0:
                overall_status = HealthStatus.CRITICAL
            elif status_counts[HealthStatus.UNHEALTHY] > total_engines // 2:
                overall_status = HealthStatus.UNHEALTHY
            elif status_counts[HealthStatus.DEGRADED] > 0:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY
            
            return {
                'status': overall_status.value,
                'total_engines': total_engines,
                'available_engines': available_engines,
                'healthy_engines': status_counts[HealthStatus.HEALTHY],
                'degraded_engines': status_counts[HealthStatus.DEGRADED],
                'unhealthy_engines': status_counts[HealthStatus.UNHEALTHY],
                'critical_engines': status_counts[HealthStatus.CRITICAL],
                'last_check': max(
                    (engine.last_check_time for engine in self.engine_health.values() 
                     if engine.last_check_time),
                    default=None
                )
            }
    
    def get_health_history(self, engine_name: Optional[str] = None, hours: float = 24.0) -> List[Dict[str, Any]]:
        """Get health check history."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        filtered_history = [
            check for check in self.health_history
            if check.timestamp >= cutoff_time and 
            (engine_name is None or check.engine_name == engine_name)
        ]
        
        return [
            {
                'timestamp': check.timestamp.isoformat(),
                'engine_name': check.engine_name,
                'status': check.status.value,
                'response_time': check.response_time,
                'error_message': check.error_message
            }
            for check in filtered_history
        ]
    
    def force_circuit_state(self, engine_name: str, state: CircuitState) -> bool:
        """Force circuit breaker to specific state (for testing/admin)."""
        with self._lock:
            if engine_name not in self.engine_health:
                return False
            
            self.engine_health[engine_name].circuit_state = state
            self.logger.info(f"Forced circuit breaker state to {state.value} for engine {engine_name}")
            return True
    
    def reset_engine_health(self, engine_name: str) -> bool:
        """Reset health metrics for specific engine."""
        with self._lock:
            if engine_name not in self.engine_health:
                return False
            
            engine = self.engine_health[engine_name]
            engine.consecutive_failures = 0
            engine.consecutive_successes = 0
            engine.total_checks = 0
            engine.total_failures = 0
            engine.circuit_state = CircuitState.CLOSED
            engine.status = HealthStatus.UNKNOWN
            
            self.logger.info(f"Reset health metrics for engine {engine_name}")
            return True
    
    def _engine_health_to_dict(self, health: EngineHealth) -> Dict[str, Any]:
        """Convert EngineHealth to dictionary."""
        return {
            'name': health.name,
            'status': health.status.value,
            'circuit_state': health.circuit_state.value,
            'is_available': health.is_available,
            'consecutive_failures': health.consecutive_failures,
            'consecutive_successes': health.consecutive_successes,
            'success_rate': health.success_rate,
            'total_checks': health.total_checks,
            'total_failures': health.total_failures,
            'average_response_time': health.average_response_time,
            'last_check_time': health.last_check_time.isoformat() if health.last_check_time else None,
            'last_success_time': health.last_success_time.isoformat() if health.last_success_time else None,
            'last_failure_time': health.last_failure_time.isoformat() if health.last_failure_time else None,
            'error_message': health.error_message
        }
    
    def start_continuous_monitoring(self, engines_with_instances: Dict[str, Any]) -> None:
        """Start continuous health monitoring thread."""
        if self._monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self._monitoring_active = True
        self._engines_with_instances = engines_with_instances
        
        def monitor_loop():
            """Main monitoring loop."""
            self.logger.info("Starting continuous health monitoring")
            
            while self._monitoring_active:
                try:
                    # Check all registered engines
                    for engine_name, engine_instance in self._engines_with_instances.items():
                        if engine_name in self.engine_health:
                            # Perform health check
                            self.check_engine_health(engine_name, engine_instance)
                            
                            # Check for automatic recovery
                            engine_health = self.engine_health[engine_name]
                            if (engine_health.circuit_state == CircuitState.OPEN and
                                engine_health.last_failure_time and
                                datetime.utcnow() - engine_health.last_failure_time > timedelta(seconds=self.config.recovery_timeout)):
                                self.logger.info(f"Attempting automatic recovery for {engine_name}")
                                self._attempt_recovery(engine_name, engine_instance)
                    
                    # Sleep before next check
                    time.sleep(self.config.health_check_interval)
                    
                except Exception as e:
                    self.logger.error(f"Error in health monitoring loop: {e}")
                    time.sleep(self.config.health_check_interval)
        
        self._monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitoring_thread.start()
    
    def stop_continuous_monitoring(self) -> None:
        """Stop continuous health monitoring."""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5.0)
            self._monitoring_thread = None
        self.logger.info("Stopped continuous health monitoring")
    
    def _attempt_recovery(self, engine_name: str, engine_instance: Any) -> None:
        """Attempt automatic recovery for failed engine."""
        with self._lock:
            engine_health = self.engine_health[engine_name]
            
            # Move to half-open state
            engine_health.circuit_state = CircuitState.HALF_OPEN
            engine_health.consecutive_successes = 0
            engine_health.consecutive_failures = 0
            
            self.logger.info(f"Moving {engine_name} to HALF-OPEN state for recovery test")
            
            # Perform test health check
            health_check = self.check_engine_health(engine_name, engine_instance)
            
            if health_check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                self.logger.info(f"Recovery test successful for {engine_name}")
                # Circuit state will be updated by normal health check flow
            else:
                self.logger.warning(f"Recovery test failed for {engine_name}")
                # Circuit will reopen automatically
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            'monitoring_active': self._monitoring_active,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'success_threshold': self.config.success_threshold,
                'health_check_interval': self.config.health_check_interval,
                'max_response_time': self.config.max_response_time
            },
            'registered_engines': len(self.engine_health),
            'monitoring_thread_alive': self._monitoring_thread.is_alive() if self._monitoring_thread else False
        }
    
    def get_health_metrics(self, hours: float = 1.0) -> Dict[str, Any]:
        """Get aggregated health metrics for performance monitoring."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter recent health checks
        recent_checks = [
            check for check in self.health_history
            if check.timestamp >= cutoff_time
        ]
        
        if not recent_checks:
            return {
                'time_window_hours': hours,
                'total_checks': 0,
                'average_response_time': 0.0,
                'success_rate': 0.0,
                'engines_metrics': {}
            }
        
        # Aggregate metrics
        total_checks = len(recent_checks)
        successful_checks = sum(1 for check in recent_checks if check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED])
        total_response_time = sum(check.response_time for check in recent_checks)
        
        # Per-engine metrics
        engine_metrics = defaultdict(lambda: {'checks': 0, 'successes': 0, 'total_response_time': 0.0})
        
        for check in recent_checks:
            metrics = engine_metrics[check.engine_name]
            metrics['checks'] += 1
            if check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                metrics['successes'] += 1
            metrics['total_response_time'] += check.response_time
        
        # Calculate averages
        formatted_engine_metrics = {}
        for engine_name, metrics in engine_metrics.items():
            formatted_engine_metrics[engine_name] = {
                'total_checks': metrics['checks'],
                'success_rate': (metrics['successes'] / metrics['checks'] * 100) if metrics['checks'] > 0 else 0.0,
                'average_response_time': metrics['total_response_time'] / metrics['checks'] if metrics['checks'] > 0 else 0.0
            }
        
        return {
            'time_window_hours': hours,
            'total_checks': total_checks,
            'average_response_time': total_response_time / total_checks if total_checks > 0 else 0.0,
            'success_rate': (successful_checks / total_checks * 100) if total_checks > 0 else 0.0,
            'engines_metrics': formatted_engine_metrics
        }