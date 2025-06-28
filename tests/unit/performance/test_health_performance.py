"""
Performance tests for the health monitoring system.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import time
from unittest.mock import MagicMock

from backend.unified.domain.health_service import HealthService
from backend.unified.domain.health_types import (
    SystemMetrics, CpuPercent, MemoryPercent, DiskPercent, EngineAvailability, EngineCount
)
from backend.unified.core.result_enhanced import Success


@pytest.fixture
def mock_monitoring_infra_performance():
    """Fixture for a mocked HealthMonitoringInfrastructure for performance tests."""
    mock = MagicMock()
    mock.get_engine_availability_async.return_value = Success(EngineAvailability(
        available_count=EngineCount(3),
        total_count=EngineCount(3),
        available_engines=[]
    ))
    return mock

@pytest.fixture
def health_service_performance(mock_monitoring_infra_performance):
    """Fixture for a HealthService instance for performance tests."""
    return HealthService(infrastructure=mock_monitoring_infra_performance)


class TestHealthPerformance:
    """Performance benchmarks for health checks."""

    @pytest.mark.asyncio
    # @pytest.mark.asyncio
    async def test_basic_health_check_performance(self, health_service_performance):
        """Test the performance of the basic health check."""
        # Given: A health service
        # When: Running the health check multiple times
        start_time = time.monotonic()
        for _ in range(100):
            await health_service_performance.get_basic_health_async()
        end_time = time.monotonic()

        # Then: The execution time is within acceptable limits
        duration = end_time - start_time
        assert duration < 0.5  # Allow up to 5ms per check on average

    def test_domain_type_creation_performance(self):
        """Test the performance of creating domain types."""
        # Given: Raw data for domain types
        # When: Creating many instances of domain types
        start_time = time.monotonic()
        for i in range(1000):
            SystemMetrics(
                cpu_percent=CpuPercent(float(i % 100)),
                memory_percent=MemoryPercent(float(i % 100)),
                disk_percent=DiskPercent(float(i % 100)),
                load_average=(1.0, 1.0, 1.0)
            )
        end_time = time.monotonic()

        # Then: The creation is highly performant
        duration = end_time - start_time
        assert duration < 0.1  # Allow up to 0.1ms per creation
