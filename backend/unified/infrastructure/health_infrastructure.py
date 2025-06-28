"""
Health infrastructure layer following the Intentional Disclosure Principle.

Isolates all I/O operations, external dependencies, and impure functions
from business logic according to IDP Rule 4.

Copyright: DarkLightX / Dana Edwards
"""

import time
import psutil
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import Request
from ..core.result_enhanced import Result, Success, Failure

from ..domain.health_types import (
    SystemMetrics, CpuPercent, MemoryPercent, DiskPercent, 
    EngineName, EngineCount, EngineAvailability
)
from ..core.health_monitor import TranslationHealthMonitor
from ..core.dependency_injection import get_container

class HealthInfrastructure:
    """Handles all external dependencies and I/O operations."""
    
    def __init__(self, request: Request):
        self._request = request
    
    async def resolve_translation_manager_async(self) -> Optional[Any]:
        """Resolve translation manager from app state."""
        return getattr(self._request.app.state, 'translation_manager', None)
    
    async def resolve_health_monitor_async(self) -> Optional[TranslationHealthMonitor]:
        """Resolve health monitor with fallback mechanisms."""
        # Try app state first
        manager = await self.resolve_translation_manager_async()
        if manager and hasattr(manager, 'health_monitor'):
            return manager.health_monitor
        
        # Try dependency injection
        return self._try_dependency_injection()
    
    def _try_dependency_injection(self) -> Optional[TranslationHealthMonitor]:
        """Attempt to resolve via dependency injection."""
        try:
            container = get_container()
            return container.resolve(TranslationHealthMonitor)
        except Exception:
            return None

class SystemMetricsCollector:
    """Collects system performance metrics."""
    
    @staticmethod
    async def collect_system_metrics_async() -> Result[SystemMetrics]:
        """Collect system performance metrics with error handling."""
        try:
            cpu_percent = CpuPercent(psutil.cpu_percent(interval=1))
            memory_percent = MemoryPercent(psutil.virtual_memory().percent)
            disk_percent = DiskPercent(psutil.disk_usage('/').percent)
            
            # Handle load average safely (not available on all platforms)
            load_average = None
            if hasattr(psutil, 'getloadavg'):
                try:
                    load_average = psutil.getloadavg()
                except (OSError, AttributeError):
                    pass
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                load_average=load_average
            )
            
            return Success(metrics)
            
        except Exception as e:
            return Failure("SYSTEM_METRICS_ERROR", f"Could not get system metrics: {e}")

class EngineHealthCollector:
    """Collects engine health and availability information."""
    
    def __init__(self, infrastructure: HealthInfrastructure):
        self._infra = infrastructure
    
    async def collect_engine_availability_async(self) -> Result[EngineAvailability]:
        """Collect engine availability with enhanced monitoring support."""
        try:
            health_monitor = await self._infra.resolve_health_monitor_async()
            if health_monitor:
                return await self._collect_from_health_monitor(health_monitor)
            
            translation_manager = await self._infra.resolve_translation_manager_async()
            if translation_manager:
                return await self._collect_from_translation_manager(translation_manager)
            
            return Success(EngineAvailability(
                available_count=EngineCount(0),
                total_count=EngineCount(0),
                available_engines=[]
            ))
            
        except Exception as e:
            return Failure(f"Could not collect engine availability: {e}")
    
    async def _collect_from_health_monitor(self, health_monitor: TranslationHealthMonitor) -> Result[EngineAvailability]:
        """Collect availability from health monitor."""
        try:
            engine_health = health_monitor.get_engine_health()
            available_engines = [
                EngineName(name) for name, status in engine_health.items()
                if status.get("status") in ["healthy", "degraded"]
            ]
            
            return Success(EngineAvailability(
                available_count=EngineCount(len(available_engines)),
                total_count=EngineCount(len(engine_health)),
                available_engines=available_engines
            ))
        except Exception as e:
            return Failure(f"Health monitor error: {e}")
    
    async def _collect_from_translation_manager(self, translation_manager: Any) -> Result[EngineAvailability]:
        """Collect availability from legacy translation manager."""
        try:
            if hasattr(translation_manager, 'get_available_engines'):
                available = translation_manager.get_available_engines()
                total_engines = getattr(translation_manager, 'engines', [])
                
                return Success(EngineAvailability(
                    available_count=EngineCount(len(available)),
                    total_count=EngineCount(len(total_engines)),
                    available_engines=[EngineName(name) for name in available]
                ))
            
            return Success(EngineAvailability(
                available_count=EngineCount(0),
                total_count=EngineCount(0),
                available_engines=[]
            ))
            
        except Exception as e:
            return Failure(f"Translation manager error: {e}")

class HealthMonitoringInfrastructure:
    """Handles health monitoring operations."""
    
    def __init__(self, infrastructure: HealthInfrastructure):
        self._infra = infrastructure
    
    async def get_health_metrics_async(self, hours: float) -> Result[Dict[str, Any]]:
        """Get health metrics from monitoring system."""
        try:
            health_monitor = await self._infra.resolve_health_monitor_async()
            if not health_monitor:
                return Failure(error_code="HEALTH_MONITOR_UNAVAILABLE", message="Health monitor not available")
            
            return health_monitor.get_health_metrics(hours=hours)
            
        except Exception as e:
            return Failure(error_code="HEALTH_METRICS_ERROR", message=f"Failed to get health metrics: {e}")
    
    async def get_health_history_async(self, engine_name: Optional[str], hours: float) -> Result[List[Dict[str, Any]]]:
        """Get health history from monitoring system."""
        try:
            health_monitor = await self._infra.resolve_health_monitor_async()
            if not health_monitor:
                return Failure("Health monitor not available")
            
            history = health_monitor.get_health_history(engine_name=engine_name, hours=hours)
            return Success(history)
            
        except Exception as e:
            return Failure(f"Failed to get health history: {e}")
    
    async def reset_engine_health_async(self, engine_name: str) -> Result[bool]:
        """Reset health metrics for specific engine."""
        try:
            health_monitor = await self._infra.resolve_health_monitor_async()
            if not health_monitor:
                return Failure("Health monitor not available")
            
            success = health_monitor.reset_engine_health(engine_name)
            return Success(success)
            
        except Exception as e:
            return Failure(f"Failed to reset engine health: {e}")
    
    async def start_monitoring_async(self) -> Result[Dict[str, Any]]:
        """Start continuous health monitoring."""
        try:
            health_monitor = await self._infra.resolve_health_monitor_async()
            if not health_monitor:
                return Failure("Health monitor not available")
            
            translation_manager = await self._infra.resolve_translation_manager_async()
            if not translation_manager:
                return Failure("Translation manager not available")
            
            engines_map = await self._build_engines_map(translation_manager)
            health_monitor.start_continuous_monitoring(engines_map)
            
            monitoring_status = health_monitor.get_monitoring_status()
            return Success(monitoring_status)
            
        except Exception as e:
            return Failure(f"Failed to start monitoring: {e}")
    
    async def _build_engines_map(self, translation_manager: Any) -> Dict[str, Any]:
        """Build engines map from translation manager."""
        engines_map = {}
        
        if hasattr(translation_manager, 'orchestrator'):
            for engine in translation_manager.orchestrator.engines:
                engines_map[engine.metadata.name] = engine
        else:
            # Legacy support
            for engine in translation_manager.engines:
                engines_map[engine.name] = engine
        
        return engines_map
    
    async def stop_monitoring_async(self) -> Result[Dict[str, Any]]:
        """Stop continuous health monitoring."""
        try:
            health_monitor = await self._infra.resolve_health_monitor_async()
            if not health_monitor:
                return Failure("Health monitor not available")
            
            health_monitor.stop_continuous_monitoring()
            monitoring_status = health_monitor.get_monitoring_status()
            return Success(monitoring_status)
            
        except Exception as e:
            return Failure(f"Failed to stop monitoring: {e}")
    
    async def get_monitoring_status_async(self) -> Result[Dict[str, Any]]:
        """Get current monitoring status."""
        try:
            health_monitor = await self._infra.resolve_health_monitor_async()
            if not health_monitor:
                return Success({
                    "monitoring_active": False,
                    "error": "Health monitor not available"
                })
            
            status = health_monitor.get_monitoring_status()
            return Success(status)
            
        except Exception as e:
            return Failure(error_code="MONITORING_STATUS_ERROR", message=f"Failed to get monitoring status: {e}")

class StartupTimeTracker:
    """Tracks application startup time."""
    
    def __init__(self):
        self._startup_time = time.time()
    
    def get_uptime_seconds(self) -> float:
        """Get current uptime in seconds."""
        return time.time() - self._startup_time

# Global startup time tracker
startup_tracker = StartupTimeTracker()