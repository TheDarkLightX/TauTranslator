"""
Tests for health domain service.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from backend.unified.domain.health_service import HealthService, PingService
from backend.unified.domain.health_types import (
    HealthStatus, LivenessStatus, ReadinessStatus, EngineAvailability, EngineCount, ServiceHealth
)
from backend.unified.core.result_enhanced import Success


@pytest.fixture
def mock_infra():
    """Fixture for a mocked HealthInfrastructure."""
    mock = MagicMock()
    # Mock the collectors and other components that HealthService depends on
    mock.resolve_translation_manager_async = AsyncMock(return_value=MagicMock())
    return mock

@pytest.fixture
def health_service(mock_infra):
    """Fixture for a HealthService instance with mocked infrastructure."""
    with patch('backend.unified.domain.health_service.SystemMetricsCollector') as MockSystemCollector:
        with patch('backend.unified.domain.health_service.EngineHealthCollector') as MockEngineCollector:
            with patch('backend.unified.domain.health_service.startup_tracker') as mock_startup_tracker:
                # Configure mocks
                mock_startup_tracker.get_uptime_seconds.return_value = 12345.0
                MockSystemCollector.return_value.collect_system_metrics_async.return_value = Success(MagicMock())
                MockEngineCollector.return_value.collect_engine_availability_async = AsyncMock(return_value=Success(EngineAvailability(
                    available_count=EngineCount(3),
                    total_count=EngineCount(3),
                    available_engines=[]
                )))

                # Instantiate the service with the base infrastructure mock
                service = HealthService(infrastructure=mock_infra)
                yield service


class TestHealthService:
    """Test HealthService business logic."""

    @pytest.mark.asyncio
    async def test_get_basic_health_async(self, health_service):
        """Test that basic health check returns a ServiceHealth object."""
        result = await health_service.get_basic_health_async()
        assert isinstance(result, ServiceHealth)
        assert result.status == HealthStatus.HEALTHY
        assert result.uptime_seconds > 0

    @pytest.mark.asyncio
    async def test_get_liveness_status_returns_alive(self, health_service):
        """Test that liveness check returns ALIVE status."""
        liveness = await health_service.get_liveness_status_async()
        assert isinstance(liveness, LivenessStatus)
        assert liveness.alive is True

    @pytest.mark.asyncio
    async def test_get_readiness_status_ready_when_engines_available(self, health_service):
        """Test readiness check returns READY when engines are available."""
        readiness = await health_service.get_readiness_status_async()
        assert isinstance(readiness, ReadinessStatus)
        assert readiness.ready is True

    @pytest.mark.asyncio
    async def test_get_readiness_status_not_ready_on_failure(self, health_service):
        """Test readiness check returns NOT_READY when infrastructure fails."""
        # GIVEN: The engine collector will fail (return 0 engines)
        with patch.object(health_service._engine_collector, 'collect_engine_availability_async') as mock_collect:
            mock_collect.return_value = Success(EngineAvailability(
                available_count=EngineCount(0),
                total_count=EngineCount(3),
                available_engines=[]
            ))

            # WHEN: Getting readiness status
            readiness = await health_service.get_readiness_status_async()

            # THEN: The status is NOT_READY
            assert readiness.ready is False
            assert "No translation engines available" in readiness.reason


class TestPingService:
    """Test PingService functionality."""

    @pytest.mark.asyncio
    async def test_ping_returns_pong_with_timestamp(self):
        """Test that ping returns a pong with the current timestamp."""
        # GIVEN: A PingService instance
        service = PingService()

        # WHEN: Pinging the service
        response = await service.ping_async()

        # THEN: The response is a pong with a timestamp
        assert response["ping"] == "pong"
        assert "timestamp" in response
