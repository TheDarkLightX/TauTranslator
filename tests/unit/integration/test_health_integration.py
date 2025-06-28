"""
Integration tests for the health monitoring system.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from backend.unified.domain.health_service import HealthService
from backend.unified.domain.health_types import (
    HealthStatus, EngineAvailability, EngineCount, SystemMetrics, 
    CpuPercent, MemoryPercent, DiskPercent
)
from backend.unified.core.result_enhanced import Success
from backend.unified.infrastructure.health_infrastructure import HealthInfrastructure


@pytest.fixture
def health_service():
    """Fixture for a HealthService instance with mocked internal components."""
    # Arrange: Create a mock for the infrastructure dependency
    mock_infra = MagicMock(spec=HealthInfrastructure)
    
    # Arrange: Instantiate the service
    service = HealthService(infrastructure=mock_infra)
    
    # Arrange: Mock the internal components and their async methods
    service._engine_collector = MagicMock()
    service._engine_collector.collect_engine_availability_async = AsyncMock()
    
    service._system_collector = MagicMock()
    service._system_collector.collect_system_metrics_async = AsyncMock()

    service._monitoring_infra = MagicMock()
    service._monitoring_infra.get_health_history_async = AsyncMock()
    service._monitoring_infra.get_monitoring_status_async = AsyncMock()
    
    return service


class TestHealthServiceIntegration:
    """Test comprehensive health checks and status determination logic."""

    @pytest.mark.asyncio
    async def test_comprehensive_health_aggregates_all_data(self, health_service):
        """Test that comprehensive health check aggregates data from all sources."""
        # Arrange
        health_service._engine_collector.collect_engine_availability_async.return_value = Success(EngineAvailability(
            available_count=EngineCount(3),
            total_count=EngineCount(5),
            available_engines=[]
        ))
        health_service._system_collector.collect_system_metrics_async.return_value = Success(SystemMetrics(
            cpu_percent=CpuPercent(45.0),
            memory_percent=MemoryPercent(65.0),
            disk_percent=DiskPercent(30.0),
            load_average=(1.0, 1.0, 1.0)
        ))
        health_service._monitoring_infra.get_health_history_async.return_value = Success([
            {"status": "HEALTHY", "timestamp": "2023-01-01T12:00:00"}
        ])

        # Act
        report = await health_service.get_comprehensive_health_async()

        # Assert
        assert report.service.status == HealthStatus.HEALTHY
        assert report.system.cpu_percent == CpuPercent(45.0)
        assert report.engines.availability_ratio == 0.6

    @pytest.mark.asyncio
    async def test_determine_overall_status_degraded_when_low_availability(self, health_service):
        """Test that overall status is DEGRADED with low engine availability."""
        # Arrange
        health_service._engine_collector.collect_engine_availability_async.return_value = Success(EngineAvailability(
            available_count=EngineCount(1),
            total_count=EngineCount(5),
            available_engines=[]
        ))
        # Mock other dependencies to return valid data
        health_service._system_collector.collect_system_metrics_async.return_value = Success(SystemMetrics(
            cpu_percent=CpuPercent(10.0), memory_percent=MemoryPercent(10.0), disk_percent=DiskPercent(10.0), load_average=(0,0,0)
        ))
        health_service._monitoring_infra.get_health_history_async.return_value = Success([])

        # Act
        report = await health_service.get_comprehensive_health_async()

        # Assert
        assert report.service.status == HealthStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_determine_overall_status_unhealthy_when_no_engines(self, health_service):
        """Test that overall status is UNHEALTHY when no engines are available."""
        # Arrange
        health_service._engine_collector.collect_engine_availability_async.return_value = Success(EngineAvailability(
            available_count=EngineCount(0),
            total_count=EngineCount(5),
            available_engines=[]
        ))
        # Mock other dependencies to return valid data
        health_service._system_collector.collect_system_metrics_async.return_value = Success(SystemMetrics(
            cpu_percent=CpuPercent(10.0), memory_percent=MemoryPercent(10.0), disk_percent=DiskPercent(10.0), load_average=(0,0,0)
        ))
        health_service._monitoring_infra.get_health_history_async.return_value = Success([])

        # Act
        report = await health_service.get_comprehensive_health_async()

        # Assert
        assert report.service.status == HealthStatus.UNHEALTHY
