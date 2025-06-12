"""
Health domain types following the Intentional Disclosure Principle.

These immutable domain types replace primitive obsession and provide clear
type boundaries for health monitoring operations.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Literal, NewType
from enum import Enum

# Domain Type Aliases
UpTimeSeconds = NewType("UpTimeSeconds", float)
EngineCount = NewType("EngineCount", int)
CpuPercent = NewType("CpuPercent", float)
MemoryPercent = NewType("MemoryPercent", float)
DiskPercent = NewType("DiskPercent", float)
EngineName = NewType("EngineName", str)
VersionString = NewType("VersionString", str)
MetricHours = NewType("MetricHours", float)

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class MonitoringAction(Enum):
    """Monitoring action enumeration."""
    START = "start"
    STOP = "stop"
    RESET = "reset"

@dataclass(frozen=True)
class SystemMetrics:
    """Immutable system performance metrics."""
    cpu_percent: CpuPercent
    memory_percent: MemoryPercent
    disk_percent: DiskPercent
    load_average: Optional[Tuple[float, float, float]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "cpu_percent": float(self.cpu_percent),
            "memory_percent": float(self.memory_percent),
            "disk_percent": float(self.disk_percent),
            "load_average": self.load_average,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass(frozen=True)
class ServiceHealth:
    """Core service health information."""
    status: HealthStatus
    uptime_seconds: UpTimeSeconds
    timestamp: datetime
    version: VersionString

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "uptime_seconds": float(self.uptime_seconds),
            "timestamp": self.timestamp.isoformat(),
            "version": str(self.version)
        }

@dataclass(frozen=True)
class EngineAvailability:
    """Engine availability metrics."""
    available_count: EngineCount
    total_count: EngineCount
    available_engines: List[EngineName] = field(default_factory=list)

    @property
    def is_available(self) -> bool:
        """Check if any engines are available."""
        return self.available_count > 0

    @property
    def availability_ratio(self) -> float:
        """Calculate availability ratio."""
        if self.total_count == 0:
            return 0.0
        return float(self.available_count) / float(self.total_count)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "available_count": int(self.available_count),
            "total_count": int(self.total_count),
            "available_engines": [str(name) for name in self.available_engines],
            "availability_ratio": self.availability_ratio
        }

@dataclass(frozen=True)
class MonitoringCommand:
    """Command for monitoring operations."""
    action: MonitoringAction
    engine_name: Optional[EngineName] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class HealthQuery:
    """Query parameters for health data retrieval."""
    time_window_hours: MetricHours
    engine_filter: Optional[EngineName] = None
    include_system_metrics: bool = True

    def validate(self) -> bool:
        """Validate query parameters."""
        return 0.1 <= float(self.time_window_hours) <= 168.0

@dataclass(frozen=True)
class HealthSummary:
    """Comprehensive health summary."""
    service: ServiceHealth
    system: Optional[SystemMetrics]
    engines: Optional[EngineAvailability]
    monitoring_active: bool = False
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            **self.service.to_dict(),
            "monitoring_active": self.monitoring_active
        }
        
        if self.system:
            result["system"] = self.system.to_dict()
        
        if self.engines:
            result["engines"] = self.engines.to_dict()
        
        if self.errors:
            result["errors"] = self.errors
            
        return result

@dataclass(frozen=True)
class ReadinessStatus:
    """Kubernetes-style readiness status."""
    ready: bool
    reason: Optional[str] = None
    available_engines: EngineCount = EngineCount(0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "ready": self.ready,
            "available_engines": int(self.available_engines)
        }
        if self.reason:
            result["reason"] = self.reason
        return result

@dataclass(frozen=True)
class LivenessStatus:
    """Kubernetes-style liveness status."""
    alive: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "alive": self.alive,
            "timestamp": self.timestamp.isoformat()
        }