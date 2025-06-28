"""
Tests for health infrastructure components.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.unified.core.result_enhanced import Success, Failure
from backend.unified.infrastructure.health_infrastructure import (
    SystemMetricsCollector, HealthMonitoringInfrastructure
)


class TestSystemMetricsCollector:
    """Test SystemMetricsCollector component."""

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.getloadavg')
    @pytest.mark.asyncio
    async def test_collect_system_metrics_success(self, mock_loadavg, mock_disk, mock_memory, mock_cpu):
        """Test successful collection of system metrics."""
        # Given: Mocks for psutil functions
        mock_cpu.return_value = 45.2
        mock_memory.return_value = MagicMock(percent=67.8)
        mock_disk.return_value = MagicMock(percent=23.4)
        mock_loadavg.return_value = (1.2, 1.5, 1.8)

        # When: Collecting system metrics
        result = await SystemMetricsCollector.collect_system_metrics_async()

        # Then: Returns successful result with correct data
        assert isinstance(result, Success)
        metrics = result.value
        assert float(metrics.cpu_percent) == 45.2
        assert float(metrics.memory_percent) == 67.8
        assert float(metrics.disk_percent) == 23.4
        assert metrics.load_average == (1.2, 1.5, 1.8)

    @patch('psutil.cpu_percent', side_effect=Exception("CPU error"))
    @pytest.mark.asyncio
    async def test_collect_system_metrics_handles_exceptions(self, mock_cpu):
        """Test that exceptions during metric collection are handled."""
        # Given: A psutil function that raises an exception
        # When: Collecting system metrics
        result = await SystemMetricsCollector.collect_system_metrics_async()

        # Then: Returns failure result
        assert isinstance(result, Failure)
        assert "Could not get system metrics" in result.message

class TestHealthInfrastructure:
    """Test HealthInfrastructure component."""

    @pytest.fixture
    def mock_infra(self):
        """Fixture for a mocked HealthInfrastructure."""
        mock = MagicMock()
        mock.resolve_health_monitor_async = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_get_monitoring_status_success(self, mock_infra):
        """Test get_monitoring_status_async returns success when monitor is available."""
        # Arrange
        mock_monitor = MagicMock()
        mock_monitor.get_monitoring_status.return_value = {"status": "active"}
        mock_infra.resolve_health_monitor_async.return_value = mock_monitor
        
        service = HealthMonitoringInfrastructure(mock_infra)

        # Act
        result = await service.get_monitoring_status_async()

        # Assert
        assert isinstance(result, Success)
        assert result.value == {"status": "active"}
        mock_infra.resolve_health_monitor_async.assert_awaited_once()
        mock_monitor.get_monitoring_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_monitoring_status_monitor_not_found(self, mock_infra):
        """Test get_monitoring_status_async handles monitor not being found."""
        # Arrange
        mock_infra.resolve_health_monitor_async.return_value = None
        service = HealthMonitoringInfrastructure(mock_infra)

        # Act
        result = await service.get_monitoring_status_async()

        # Assert
        assert isinstance(result, Success)
        assert result.value == {
            "monitoring_active": False,
            "error": "Health monitor not available"
        }
        mock_infra.resolve_health_monitor_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_monitoring_status_handles_exception(self, mock_infra):
        """Test get_monitoring_status_async returns Failure on exception."""
        # Arrange
        mock_infra.resolve_health_monitor_async.side_effect = Exception("DB error")
        service = HealthMonitoringInfrastructure(mock_infra)

        # Act
        result = await service.get_monitoring_status_async()

        # Assert
        assert isinstance(result, Failure)
        assert "Failed to get monitoring status: DB error" in result.message
        mock_infra.resolve_health_monitor_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_health_metrics_success(self, mock_infra):
        """Test get_health_metrics_async returns success when monitor is available."""
        # Arrange
        mock_monitor = MagicMock()
        mock_monitor.get_health_metrics.return_value = Success({"cpu": 50})
        mock_infra.resolve_health_monitor_async.return_value = mock_monitor
        
        service = HealthMonitoringInfrastructure(mock_infra)

        # Act
        result = await service.get_health_metrics_async(hours=1.0)

        # Assert
        assert isinstance(result, Success)
        assert result.value == {"cpu": 50}
        mock_infra.resolve_health_monitor_async.assert_awaited_once()
        mock_monitor.get_health_metrics.assert_called_once_with(hours=1.0)

    @pytest.mark.asyncio
    async def test_get_health_metrics_monitor_not_found(self, mock_infra):
        """Test get_health_metrics_async returns Failure when monitor is not found."""
        # Arrange
        mock_infra.resolve_health_monitor_async.return_value = None
        service = HealthMonitoringInfrastructure(mock_infra)

        # Act
        result = await service.get_health_metrics_async(hours=1.0)

        # Assert
        assert isinstance(result, Failure)
        assert "Health monitor not available" in result.message
        mock_infra.resolve_health_monitor_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_health_metrics_handles_exception(self, mock_infra):
        """Test get_health_metrics_async returns Failure on exception."""
        # Arrange
        mock_infra.resolve_health_monitor_async.side_effect = Exception("Infra error")
        service = HealthMonitoringInfrastructure(mock_infra)

        # Act
        result = await service.get_health_metrics_async(hours=1.0)

        # Assert
        assert isinstance(result, Failure)
        assert "Failed to get health metrics: Infra error" in result.message
        mock_infra.resolve_health_monitor_async.assert_awaited_once()
