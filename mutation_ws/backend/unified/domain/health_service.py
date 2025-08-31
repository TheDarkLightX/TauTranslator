"""
Health service with pure business logic following the Intentional Disclosure Principle.

Contains all health-related business logic separated from infrastructure concerns.
All methods follow IDP Rule 2 (≤10 lines) and Rule 3 (type disclosure).

Copyright: DarkLightX / Dana Edwards
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from ..core.result_enhanced import Result, Success, Failure

from .health_types import (
    ServiceHealth, HealthSummary, SystemMetrics, EngineAvailability,
    ReadinessStatus, LivenessStatus, HealthStatus, UpTimeSeconds, 
    VersionString, EngineCount, EngineName, HealthQuery, MetricHours
)
from ..infrastructure.health_infrastructure import (
    HealthInfrastructure, SystemMetricsCollector, EngineHealthCollector,
    HealthMonitoringInfrastructure, startup_tracker
)

class HealthService:
    """Pure business logic for health operations."""
    
    def __init__(self, infrastructure: HealthInfrastructure):
        self._infra = infrastructure
        self._system_collector = SystemMetricsCollector()
        self._engine_collector = EngineHealthCollector(infrastructure)
        self._monitoring_infra = HealthMonitoringInfrastructure(infrastructure)
    
    async def get_basic_health_async(self) -> ServiceHealth:
        """Get basic service health information."""
        uptime = UpTimeSeconds(startup_tracker.get_uptime_seconds())
        
        return ServiceHealth(
            status=HealthStatus.HEALTHY,
            uptime_seconds=uptime,
            timestamp=datetime.now(timezone.utc),
            version=VersionString("2.0.0")
        )
    
    async def get_comprehensive_health_async(self, user: Optional[Dict[str, Any]] = None) -> HealthSummary:
        """Aggregate comprehensive health from all sources."""
        service_health = await self.get_basic_health_async()
        system_metrics = await self._collect_system_metrics_safely()
        engine_availability = await self._collect_engine_availability_safely()
        monitoring_status = await self._get_monitoring_status_safely()
        
        # Determine overall status based on engine availability
        final_status = self._determine_overall_status(service_health.status, engine_availability)
        
        updated_service = ServiceHealth(
            status=final_status,
            uptime_seconds=service_health.uptime_seconds,
            timestamp=service_health.timestamp,
            version=service_health.version
        )
        
        return HealthSummary(
            service=updated_service,
            system=system_metrics,
            engines=engine_availability,
            monitoring_active=monitoring_status
        )
    
    async def get_readiness_status_async(self) -> ReadinessStatus:
        """Determine Kubernetes-style readiness status."""
        translation_manager = await self._infra.resolve_translation_manager_async()
        
        if not translation_manager:
            return ReadinessStatus(
                ready=False,
                reason="Translation manager not initialized"
            )
        
        engine_availability = await self._collect_engine_availability_safely()
        if not engine_availability or not engine_availability.is_available:
            return ReadinessStatus(
                ready=False,
                reason="No translation engines available"
            )
        
        return ReadinessStatus(
            ready=True,
            available_engines=engine_availability.available_count
        )
    
    async def get_liveness_status_async(self) -> LivenessStatus:
        """Get Kubernetes-style liveness status."""
        return LivenessStatus(alive=True)
    
    async def get_engine_status_async(self) -> Dict[str, Any]:
        """Get detailed engine status information."""
        translation_manager = await self._infra.resolve_translation_manager_async()
        
        if not translation_manager:
            return {
                "engines": [],
                "message": "Translation manager not initialized"
            }
        
        if hasattr(translation_manager, 'get_engine_status'):
            return translation_manager.get_engine_status()
        
        return {"engines": [], "message": "Engine status not available"}
    
    async def get_translation_statistics_async(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Get translation statistics for authenticated users."""
        translation_manager = await self._infra.resolve_translation_manager_async()
        
        if not translation_manager:
            return {
                "statistics": {},
                "message": "Translation manager not initialized"
            }
        
        if hasattr(translation_manager, 'get_statistics'):
            return translation_manager.get_statistics()
        
        return {"statistics": {}, "message": "Statistics not available"}
    
    async def get_health_metrics_async(self, query: HealthQuery) -> Result[Dict[str, Any]]:
        """Get aggregated health metrics for time window."""
        if not query.validate():
            return Failure("Invalid query parameters")
        
        return await self._monitoring_infra.get_health_metrics_async(float(query.time_window_hours))
    
    async def get_health_history_async(self, query: HealthQuery) -> Result[List[Dict[str, Any]]]:
        """Get health check history for time window."""
        if not query.validate():
            return Failure("Invalid query parameters")
        
        engine_name = str(query.engine_filter) if query.engine_filter else None
        return await self._monitoring_infra.get_health_history_async(engine_name, float(query.time_window_hours))
    
    async def reset_engine_health_async(self, engine_name: EngineName) -> Result[bool]:
        """Reset health metrics for specific engine."""
        return await self._monitoring_infra.reset_engine_health_async(str(engine_name))
    
    async def start_monitoring_async(self) -> Result[Dict[str, Any]]:
        """Start continuous health monitoring."""
        return await self._monitoring_infra.start_monitoring_async()
    
    async def stop_monitoring_async(self) -> Result[Dict[str, Any]]:
        """Stop continuous health monitoring."""
        return await self._monitoring_infra.stop_monitoring_async()
    
    async def get_monitoring_status_async(self) -> Result[Dict[str, Any]]:
        """Get current monitoring status."""
        return await self._monitoring_infra.get_monitoring_status_async()
    
    # Private helper methods (all ≤10 lines following IDP Rule 2)
    
    async def _collect_system_metrics_safely(self) -> Optional[SystemMetrics]:
        """Safely collect system metrics with error handling."""
        result = await self._system_collector.collect_system_metrics_async()
        return result.value if isinstance(result, Success) else None
    
    async def _collect_engine_availability_safely(self) -> Optional[EngineAvailability]:
        """Safely collect engine availability with error handling."""
        result = await self._engine_collector.collect_engine_availability_async()
        return result.value if isinstance(result, Success) else None
    
    async def _get_monitoring_status_safely(self) -> bool:
        """Safely get monitoring status."""
        result = await self._monitoring_infra.get_monitoring_status_async()
        if isinstance(result, Success):
            status = result.value
            return status.get("monitoring_active", False)
        return False
    
    def _determine_overall_status(self, base_status: HealthStatus, engines: Optional[EngineAvailability]) -> HealthStatus:
        """Determine overall health status based on engine availability."""
        if not engines or not engines.is_available:
            return HealthStatus.UNHEALTHY
        
        if engines.availability_ratio < 0.5:
            return HealthStatus.DEGRADED
        
        return base_status

class PingService:
    """Simple ping service for load balancers."""
    
    @staticmethod
    async def ping_async() -> Dict[str, str]:
        """Simple ping response."""
        return {
            "ping": "pong",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }