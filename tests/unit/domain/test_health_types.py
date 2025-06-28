"""
Tests for health domain types.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from backend.unified.domain.health_types import (
    SystemMetrics, EngineAvailability, HealthQuery,
    CpuPercent, MemoryPercent, DiskPercent, EngineCount, EngineName
)


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
        # Given: EngineAvailability instance with available engines
        availability = sample_engine_availability

        # When: Checking is_available property
        is_available = availability.is_available

        # Then: is_available is True
        assert is_available is True
        assert availability.available_count == EngineCount(3)

    def test_engine_availability_is_not_available_when_no_engines(self):
        """Test is_available property when no engines are available."""
        # Given: EngineAvailability instance with no available engines
        availability = EngineAvailability(
            available_count=EngineCount(0),
            total_count=EngineCount(5),
            available_engines=[]
        )

        # When: Checking is_available property
        is_available = availability.is_available

        # Then: is_available is False
        assert is_available is False

    def test_engine_availability_ratio_calculation(self, sample_engine_availability):
        """Test availability ratio calculation."""
        # Given: EngineAvailability instance
        availability = sample_engine_availability

        # When: Calculating availability ratio
        ratio = availability.availability_ratio

        # Then: Ratio is calculated correctly (3/5 = 0.6)
        assert ratio == 0.6

    def test_engine_availability_ratio_zero_when_no_total(self):
        """Test availability ratio is zero when total is zero."""
        # Given: EngineAvailability instance with zero total engines
        availability = EngineAvailability(
            available_count=EngineCount(0),
            total_count=EngineCount(0),
            available_engines=[]
        )

        # When: Calculating availability ratio
        ratio = availability.availability_ratio

        # Then: Ratio is 0.0 to avoid division by zero
        assert ratio == 0.0

class TestHealthQuery:
    """Test HealthQuery domain type."""

    def test_health_query_validation_with_valid_hours(self):
        """Test HealthQuery validation with valid time window."""
        # Given: A valid time window
        query = HealthQuery(time_window_hours=24)

        # When: Validating the query
        is_valid = query.validate()

        # Then: The query is valid
        assert is_valid is True

    def test_health_query_validation_fails_with_too_small_hours(self):
        """Test HealthQuery validation fails with too small time window."""
        # Given: A time window that is too small
        query = HealthQuery(time_window_hours=0)

        # When: Validating the query
        is_valid = query.validate()

        # Then: The query is invalid
        assert is_valid is False

    def test_health_query_validation_fails_with_too_large_hours(self):
        """Test HealthQuery validation fails with too large time window."""
        # Given: A time window that is too large
        query = HealthQuery(time_window_hours=1000)

        # When: Validating the query
        is_valid = query.validate()

        # Then: The query is invalid
        assert is_valid is False
