"""
Comprehensive unit tests for refactored health module.

Tests all components in isolation following TDD principles.
Each test follows Given-When-Then structure with clear naming.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Import components to test
from backend.unified.domain.health_types import (
    SystemMetrics, ServiceHealth, EngineAvailability, ReadinessStatus,
    LivenessStatus, HealthSummary, HealthQuery, MonitoringCommand,
    HealthStatus, CpuPercent, MemoryPercent, DiskPercent, 
    UpTimeSeconds, VersionString, EngineCount, EngineName, MetricHours
)

from backend.unified.domain.health_service import HealthService, PingService
from backend.unified.infrastructure.health_infrastructure import (
    HealthInfrastructure, SystemMetricsCollector, EngineHealthCollector,
    HealthMonitoringInfrastructure, StartupTimeTracker
)

from returns.result import Success, Failure


# ===== Test Fixtures =====

@pytest.fixture
def mock_request():
    """Mock FastAPI request."""
    request = Mock()
    request.app.state.translation_manager = None
    return request

@pytest.fixture
def health_infrastructure(mock_request):
    """Health infrastructure with mocked request."""
    return HealthInfrastructure(mock_request)

@pytest.fixture
def health_service(health_infrastructure):
    """Health service with mocked infrastructure."""
    return HealthService(health_infrastructure)

@pytest.fixture
def sample_system_metrics():
    """Sample system metrics for testing."""
    return SystemMetrics(
        cpu_percent=CpuPercent(45.2),
        memory_percent=MemoryPercent(67.8),
        disk_percent=DiskPercent(23.4),
        load_average=(1.2, 1.5, 1.8)
    )

@pytest.fixture
def sample_engine_availability():
    """Sample engine availability for testing."""
    return EngineAvailability(
        available_count=EngineCount(3),
        total_count=EngineCount(5),
        available_engines=[EngineName("engine1"), EngineName("engine2"), EngineName("engine3")]
    )


# ===== Domain Types Tests =====

class TestSystemMetrics:
    """Test SystemMetrics domain type."""
    
    def test_system_metrics_creation_with_valid_data(self, sample_system_metrics):
        """Test SystemMetrics creation with valid data."""
        # Given: Valid system metrics data
        metrics = sample_system_metrics
        
        # When: Accessing properties
        cpu = metrics.cpu_percent
        memory = metrics.memory_percent
        
        # Then: All values are preserved correctly
        assert float(cpu) == 45.2
        assert float(memory) == 67.8
        assert metrics.load_average == (1.2, 1.5, 1.8)
    
    def test_system_metrics_to_dict_conversion(self, sample_system_metrics):
        """Test SystemMetrics conversion to dictionary."""
        # Given: SystemMetrics instance
        metrics = sample_system_metrics
        
        # When: Converting to dictionary
        result = metrics.to_dict()
        
        # Then: All fields are present and correctly formatted
        assert result["cpu_percent"] == 45.2
        assert result["memory_percent"] == 67.8
        assert result["disk_percent"] == 23.4
        assert result["load_average"] == (1.2, 1.5, 1.8)
        assert "timestamp" in result
    
    def test_system_metrics_immutability(self, sample_system_metrics):
        """Test SystemMetrics is immutable."""
        # Given: SystemMetrics instance
        metrics = sample_system_metrics
        
        # When: Attempting to modify (should raise AttributeError)
        # Then: Object is immutable
        with pytest.raises(AttributeError):
            metrics.cpu_percent = CpuPercent(99.9)

class TestEngineAvailability:
    """Test EngineAvailability domain type."""
    
    def test_engine_availability_is_available_when_engines_exist(self, sample_engine_availability):
        """Test is_available property when engines are available."""
        # Given: Engine availability with available engines
        availability = sample_engine_availability
        
        # When: Checking availability
        is_available = availability.is_available
        
        # Then: Returns True
        assert is_available is True
    
    def test_engine_availability_is_not_available_when_no_engines(self):
        """Test is_available property when no engines are available."""
        # Given: Engine availability with no available engines
        availability = EngineAvailability(
            available_count=EngineCount(0),
            total_count=EngineCount(5),
            available_engines=[]
        )
        
        # When: Checking availability
        is_available = availability.is_available
        
        # Then: Returns False
        assert is_available is False
    
    def test_engine_availability_ratio_calculation(self, sample_engine_availability):
        """Test availability ratio calculation."""
        # Given: Engine availability with 3/5 engines available
        availability = sample_engine_availability
        
        # When: Calculating ratio
        ratio = availability.availability_ratio
        
        # Then: Ratio is correct
        assert ratio == 0.6
    
    def test_engine_availability_ratio_zero_when_no_total(self):
        """Test availability ratio is zero when total is zero."""
        # Given: Engine availability with zero total engines
        availability = EngineAvailability(
            available_count=EngineCount(0),
            total_count=EngineCount(0),
            available_engines=[]
        )
        
        # When: Calculating ratio
        ratio = availability.availability_ratio
        
        # Then: Ratio is zero
        assert ratio == 0.0

class TestHealthQuery:
    """Test HealthQuery domain type."""
    
    def test_health_query_validation_with_valid_hours(self):
        """Test HealthQuery validation with valid time window."""
        # Given: HealthQuery with valid hours
        query = HealthQuery(time_window_hours=MetricHours(12.0))
        
        # When: Validating query
        is_valid = query.validate()
        
        # Then: Validation passes
        assert is_valid is True
    
    def test_health_query_validation_fails_with_too_small_hours(self):
        """Test HealthQuery validation fails with too small time window."""
        # Given: HealthQuery with too small hours
        query = HealthQuery(time_window_hours=MetricHours(0.05))
        
        # When: Validating query
        is_valid = query.validate()
        
        # Then: Validation fails
        assert is_valid is False
    
    def test_health_query_validation_fails_with_too_large_hours(self):
        """Test HealthQuery validation fails with too large time window."""
        # Given: HealthQuery with too large hours
        query = HealthQuery(time_window_hours=MetricHours(200.0))
        
        # When: Validating query
        is_valid = query.validate()
        
        # Then: Validation fails
        assert is_valid is False


# ===== Infrastructure Tests =====

class TestSystemMetricsCollector:
    """Test SystemMetricsCollector infrastructure component."""
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.getloadavg')
    @pytest.mark.asyncio
    async def test_collect_system_metrics_success(self, mock_loadavg, mock_disk, mock_memory, mock_cpu):
        """Test successful system metrics collection."""
        # Given: Mocked psutil functions
        mock_cpu.return_value = 45.2
        mock_memory.return_value = Mock(percent=67.8)
        mock_disk.return_value = Mock(percent=23.4)
        mock_loadavg.return_value = (1.2, 1.5, 1.8)
        
        # When: Collecting system metrics
        result = await SystemMetricsCollector.collect_system_metrics_async()
        
        # Then: Returns successful result with correct data
        assert isinstance(result, Success)
        metrics = result.unwrap()
        assert float(metrics.cpu_percent) == 45.2
        assert float(metrics.memory_percent) == 67.8
        assert float(metrics.disk_percent) == 23.4
        assert metrics.load_average == (1.2, 1.5, 1.8)
    
    @patch('psutil.cpu_percent')
    @pytest.mark.asyncio
    async def test_collect_system_metrics_handles_exceptions(self, mock_cpu):
        """Test system metrics collection handles exceptions gracefully."""
        # Given: psutil function that raises exception
        mock_cpu.side_effect = Exception("System error")
        
        # When: Collecting system metrics
        result = await SystemMetricsCollector.collect_system_metrics_async()
        
        # Then: Returns failure result
        assert isinstance(result, Failure)
        assert "Could not get system metrics" in result.failure()

class TestHealthInfrastructure:
    """Test HealthInfrastructure component."""
    
    @pytest.mark.asyncio
    async def test_resolve_translation_manager_from_app_state(self, health_infrastructure, mock_request):
        """Test resolving translation manager from app state."""
        # Given: Request with translation manager in app state
        mock_manager = Mock()
        mock_request.app.state.translation_manager = mock_manager
        
        # When: Resolving translation manager
        result = await health_infrastructure.resolve_translation_manager_async()
        
        # Then: Returns the manager from app state
        assert result is mock_manager
    
    @pytest.mark.asyncio
    async def test_resolve_translation_manager_returns_none_when_not_found(self, health_infrastructure):
        """Test resolving translation manager returns None when not found."""
        # Given: Request with no translation manager
        # (mock_request fixture already has None)
        
        # When: Resolving translation manager
        result = await health_infrastructure.resolve_translation_manager_async()
        
        # Then: Returns None
        assert result is None
    
    @pytest.mark.asyncio
    async def test_resolve_health_monitor_from_manager(self, health_infrastructure, mock_request):
        """Test resolving health monitor from translation manager."""
        # Given: Request with translation manager that has health monitor
        mock_health_monitor = Mock()
        mock_manager = Mock()
        mock_manager.health_monitor = mock_health_monitor
        mock_request.app.state.translation_manager = mock_manager
        
        # When: Resolving health monitor
        result = await health_infrastructure.resolve_health_monitor_async()
        
        # Then: Returns the health monitor
        assert result is mock_health_monitor


# ===== Service Tests =====

class TestHealthService:
    """Test HealthService business logic."""
    
    @pytest.mark.asyncio
    async def test_get_basic_health_returns_healthy_status(self, health_service):
        """Test getting basic health returns healthy status."""
        # Given: Health service
        # When: Getting basic health
        result = await health_service.get_basic_health_async()
        
        # Then: Returns healthy service health
        assert isinstance(result, ServiceHealth)
        assert result.status == HealthStatus.HEALTHY
        assert result.version == VersionString("2.0.0")
        assert isinstance(result.uptime_seconds, float)
    
    @pytest.mark.asyncio
    async def test_get_liveness_status_returns_alive(self, health_service):
        """Test getting liveness status returns alive."""
        # Given: Health service
        # When: Getting liveness status
        result = await health_service.get_liveness_status_async()
        
        # Then: Returns alive status
        assert isinstance(result, LivenessStatus)
        assert result.alive is True
        assert isinstance(result.timestamp, datetime)
    
    @patch.object(HealthService, '_collect_engine_availability_safely')
    @pytest.mark.asyncio
    async def test_get_readiness_status_ready_when_engines_available(self, mock_collect, health_service):
        """Test readiness status is ready when engines are available."""
        # Given: Health service with available engines
        mock_collect.return_value = EngineAvailability(
            available_count=EngineCount(2),
            total_count=EngineCount(3),
            available_engines=[EngineName("engine1"), EngineName("engine2")]
        )
        
        # Mock translation manager
        with patch.object(health_service._infra, 'resolve_translation_manager_async', return_value=Mock()):
            # When: Getting readiness status
            result = await health_service.get_readiness_status_async()
            
            # Then: Returns ready status
            assert isinstance(result, ReadinessStatus)
            assert result.ready is True
            assert result.available_engines == EngineCount(2)
    
    @pytest.mark.asyncio
    async def test_get_readiness_status_not_ready_when_no_manager(self, health_service):
        """Test readiness status is not ready when no translation manager."""
        # Given: Health service with no translation manager
        # (health_infrastructure mock already returns None)
        
        # When: Getting readiness status
        result = await health_service.get_readiness_status_async()
        
        # Then: Returns not ready status
        assert isinstance(result, ReadinessStatus)
        assert result.ready is False
        assert result.reason == "Translation manager not initialized"

class TestPingService:
    """Test PingService functionality."""
    
    @pytest.mark.asyncio
    async def test_ping_returns_pong_with_timestamp(self):
        """Test ping service returns pong with timestamp."""
        # Given: PingService
        # When: Calling ping
        result = await PingService.ping_async()
        
        # Then: Returns pong with timestamp
        assert result["ping"] == "pong"
        assert "timestamp" in result
        # Verify timestamp is in ISO format
        datetime.fromisoformat(result["timestamp"].replace('Z', '+00:00'))

class TestStartupTimeTracker:
    """Test StartupTimeTracker utility."""
    
    def test_startup_time_tracker_initialization(self):
        """Test StartupTimeTracker initializes with current time."""
        # Given: Current time before creation
        before_time = time.time()
        
        # When: Creating tracker
        tracker = StartupTimeTracker()
        
        # Then: Startup time is approximately current time
        after_time = time.time()
        uptime = tracker.get_uptime_seconds()
        assert 0 <= uptime <= (after_time - before_time + 0.1)  # Allow small margin
    
    def test_startup_time_tracker_uptime_increases(self):
        """Test StartupTimeTracker uptime increases over time."""
        # Given: Startup time tracker
        tracker = StartupTimeTracker()
        
        # When: Getting initial uptime then waiting and getting again
        initial_uptime = tracker.get_uptime_seconds()
        time.sleep(0.01)  # Wait 10ms
        later_uptime = tracker.get_uptime_seconds()
        
        # Then: Later uptime is greater than initial
        assert later_uptime > initial_uptime


# ===== Integration Tests =====

class TestHealthServiceIntegration:
    """Integration tests for HealthService with mocked infrastructure."""
    
    @patch.object(EngineHealthCollector, 'collect_engine_availability_async')
    @patch.object(SystemMetricsCollector, 'collect_system_metrics_async')
    @pytest.mark.asyncio
    async def test_comprehensive_health_aggregates_all_data(self, mock_system, mock_engines, health_service):
        """Test comprehensive health aggregates data from all sources."""
        # Given: Mocked successful data collection
        mock_system.return_value = Success(SystemMetrics(
            cpu_percent=CpuPercent(50.0),
            memory_percent=MemoryPercent(60.0),
            disk_percent=DiskPercent(30.0)
        ))
        
        mock_engines.return_value = Success(EngineAvailability(
            available_count=EngineCount(3),
            total_count=EngineCount(3),
            available_engines=[EngineName("engine1"), EngineName("engine2"), EngineName("engine3")]
        ))
        
        # When: Getting comprehensive health
        result = await health_service.get_comprehensive_health_async()
        
        # Then: Returns complete health summary
        assert isinstance(result, HealthSummary)
        assert result.service.status == HealthStatus.HEALTHY
        assert result.system is not None
        assert result.engines is not None
        assert result.engines.available_count == EngineCount(3)
    
    def test_determine_overall_status_degraded_when_low_availability(self, health_service):
        """Test overall status becomes degraded when engine availability is low."""
        # Given: Low engine availability
        engines = EngineAvailability(
            available_count=EngineCount(1),
            total_count=EngineCount(5),  # 20% availability
            available_engines=[EngineName("engine1")]
        )
        
        # When: Determining overall status
        result = health_service._determine_overall_status(HealthStatus.HEALTHY, engines)
        
        # Then: Status is degraded
        assert result == HealthStatus.DEGRADED
    
    def test_determine_overall_status_unhealthy_when_no_engines(self, health_service):
        """Test overall status becomes unhealthy when no engines available."""
        # Given: No available engines
        engines = EngineAvailability(
            available_count=EngineCount(0),
            total_count=EngineCount(5),
            available_engines=[]
        )
        
        # When: Determining overall status
        result = health_service._determine_overall_status(HealthStatus.HEALTHY, engines)
        
        # Then: Status is unhealthy
        assert result == HealthStatus.UNHEALTHY


# ===== Performance Tests =====

class TestHealthPerformance:
    """Performance tests for health components."""
    
    @pytest.mark.asyncio
    async def test_basic_health_check_performance(self, health_service):
        """Test basic health check completes quickly."""
        # Given: Health service
        start_time = time.time()
        
        # When: Getting basic health 100 times
        for _ in range(100):
            await health_service.get_basic_health_async()
        
        # Then: Completes within reasonable time
        elapsed = time.time() - start_time
        assert elapsed < 0.1  # Should complete 100 calls in under 100ms
    
    def test_domain_type_creation_performance(self, sample_system_metrics):
        """Test domain type creation is efficient."""
        # Given: Sample metrics data
        start_time = time.time()
        
        # When: Creating 1000 SystemMetrics instances
        for i in range(1000):
            SystemMetrics(
                cpu_percent=CpuPercent(float(i % 100)),
                memory_percent=MemoryPercent(float((i + 10) % 100)),
                disk_percent=DiskPercent(float((i + 20) % 100))
            )
        
        # Then: Completes quickly
        elapsed = time.time() - start_time
        assert elapsed < 0.1  # Should complete 1000 creations in under 100ms