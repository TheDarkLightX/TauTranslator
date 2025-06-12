"""
Integration Tests for Health Monitor with Translation Pipeline

Tests the complete integration of health monitoring with the translation system.
Verifies circuit breaker behavior, recovery mechanisms, and monitoring endpoints.

Author: DarkLightX / Dana Edwards
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import httpx

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.core.health_monitor import (
    TranslationHealthMonitor,
    CircuitBreakerConfig,
    HealthStatus,
    CircuitState
)
from backend.unified.translators.refactored_manager import RefactoredTranslationManager
from backend.unified.translators.base import TranslationDirection, TranslationResult
from backend.unified.core.dependency_injection import ServiceContainer
from backend.unified.api.health_refactored import router as health_router
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestHealthMonitorIntegration:
    """Integration tests for health monitor with translation system."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app with health endpoints."""
        app = FastAPI()
        app.include_router(health_router, prefix="/health")
        return app
    
    @pytest.fixture
    def container(self):
        """Create service container."""
        return ServiceContainer()
    
    @pytest.fixture
    def circuit_config(self):
        """Create test circuit breaker configuration."""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=5.0,
            success_threshold=2,
            health_check_interval=1.0,
            max_response_time=1.0
        )
    
    @pytest.fixture
    def translation_manager(self, container, circuit_config):
        """Create translation manager with health monitoring."""
        container.clear()  # Clear any existing registrations
        manager = RefactoredTranslationManager(container)
        manager.health_monitor.config = circuit_config
        return manager
    
    @pytest.fixture
    def test_client(self, app, translation_manager):
        """Create test client with app state."""
        app.state.translation_manager = translation_manager
        return TestClient(app)
    
    @pytest.fixture
    def mock_engine(self):
        """Create mock translation engine with metadata."""
        engine = Mock()
        engine.metadata = Mock()
        engine.metadata.name = "test_engine"
        engine.is_available = True
        engine.get_supported_directions = Mock(return_value=[TranslationDirection.TO_TAU, TranslationDirection.FROM_TAU])
        engine.can_translate = Mock(return_value=True)
        engine.translate = Mock(return_value=TranslationResult(
            success=True,
            translated_text="translated",
            original_text="test",
            translation_method="test_engine",
            direction=TranslationDirection.TO_TAU,
            confidence=0.9
        ))
        return engine
    
    # Test 1: Basic health monitoring integration
    def test_health_monitoring_with_translation(self, translation_manager, mock_engine):
        """Test health monitoring during translation operations."""
        # Register engine
        translation_manager.register_engine(mock_engine, is_default=True)
        
        # Perform translation
        result = translation_manager.translate("test", TranslationDirection.TO_TAU)
        assert result.success
        
        # Check health was monitored
        engine_health = translation_manager.health_monitor.get_engine_health("test_engine")
        assert engine_health["status"] == HealthStatus.HEALTHY.value
        assert engine_health["total_checks"] > 0
    
    # Test 2: Circuit breaker integration
    def test_circuit_breaker_prevents_failed_translations(self, translation_manager, circuit_config):
        """Test circuit breaker blocks requests to failing engines."""
        # Create failing engine
        failing_engine = Mock()
        failing_engine.metadata = Mock()
        failing_engine.metadata.name = "failing_engine"
        failing_engine.is_available = True
        failing_engine.get_supported_directions = Mock(return_value=[TranslationDirection.TO_TAU])
        failing_engine.can_translate = Mock(return_value=True)
        failing_engine.translate = Mock(return_value=TranslationResult(
            success=False,
            translated_text="",
            original_text="test",
            translation_method="failing_engine",
            direction=TranslationDirection.TO_TAU,
            error_message="Engine failure"
        ))
        
        translation_manager.register_engine(failing_engine, is_default=True)
        
        # Cause failures to open circuit
        for _ in range(circuit_config.failure_threshold + 1):
            result = translation_manager.translate("test", TranslationDirection.TO_TAU)
            assert not result.success
        
        # Check circuit is open
        engine_health = translation_manager.health_monitor.get_engine_health("failing_engine")
        assert engine_health["circuit_state"] == CircuitState.OPEN.value
        assert not engine_health["is_available"]
    
    # Test 3: Fallback mechanism with health monitoring
    def test_fallback_to_healthy_engine(self, translation_manager, mock_engine):
        """Test system falls back to healthy engines when primary fails."""
        # Create failing primary engine
        primary_engine = Mock()
        primary_engine.metadata = Mock()
        primary_engine.metadata.name = "primary_engine"
        primary_engine.is_available = True
        primary_engine.get_supported_directions = Mock(return_value=[TranslationDirection.TO_TAU])
        primary_engine.can_translate = Mock(return_value=True)
        primary_engine.translate = Mock(return_value=TranslationResult(
            success=False,
            translated_text="",
            original_text="test",
            translation_method="primary_engine",
            direction=TranslationDirection.TO_TAU,
            error_message="Primary failure"
        ))
        
        # Register engines
        translation_manager.register_engine(primary_engine, is_default=True)
        translation_manager.register_engine(mock_engine, is_fallback=True)
        
        # Translation should succeed via fallback
        result = translation_manager.translate("test", TranslationDirection.TO_TAU, use_fallback=True)
        assert result.success
        assert result.translation_method == "test_engine"
    
    # Test 4: Health monitoring API endpoints
    def test_health_api_endpoints(self, test_client, translation_manager, mock_engine):
        """Test health monitoring API endpoints."""
        # Register engine
        translation_manager.register_engine(mock_engine)
        
        # Test basic health check
        response = test_client.get("/health/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # Test detailed health check
        response = test_client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "overall_health" in data
        assert "engines" in data
        assert "monitoring" in data
        
        # Test metrics endpoint
        response = test_client.get("/health/metrics?hours=1")
        assert response.status_code == 200
        metrics = response.json()["data"]
        assert "total_checks" in metrics
        assert "engines_metrics" in metrics
    
    # Test 5: Continuous monitoring integration
    def test_continuous_monitoring_integration(self, test_client, translation_manager, mock_engine):
        """Test continuous monitoring via API."""
        # Register engine
        translation_manager.register_engine(mock_engine)
        
        # Start monitoring
        response = test_client.post("/health/monitoring/start")
        assert response.status_code == 200
        assert response.json()["data"]["monitoring_status"]["monitoring_active"]
        
        # Wait for some monitoring cycles
        time.sleep(2)
        
        # Check monitoring status
        response = test_client.get("/health/monitoring/status")
        assert response.status_code == 200
        status = response.json()["data"]
        assert status["monitoring_active"]
        assert status["monitoring_thread_alive"]
        
        # Stop monitoring
        response = test_client.post("/health/monitoring/stop")
        assert response.status_code == 200
        assert not response.json()["data"]["monitoring_status"]["monitoring_active"]
    
    # Test 6: Recovery mechanism integration
    def test_automatic_recovery_integration(self, translation_manager, circuit_config):
        """Test automatic recovery of failed engines."""
        # Create recovering engine
        recovering_engine = Mock()
        recovering_engine.metadata = Mock()
        recovering_engine.metadata.name = "recovering_engine"
        recovering_engine.is_available = True
        recovering_engine.get_supported_directions = Mock(return_value=[TranslationDirection.TO_TAU])
        recovering_engine.can_translate = Mock(return_value=True)
        
        # Start with failures
        recovering_engine.translate = Mock(return_value=TranslationResult(
            success=False,
            translated_text="",
            original_text="test",
            translation_method="recovering_engine",
            direction=TranslationDirection.TO_TAU,
            error_message="Initial failure"
        ))
        
        translation_manager.register_engine(recovering_engine)
        
        # Cause circuit to open
        for _ in range(circuit_config.failure_threshold):
            translation_manager.translate("test", TranslationDirection.TO_TAU, engine_name="recovering_engine")
        
        # Verify circuit is open
        engine_health = translation_manager.health_monitor.get_engine_health("recovering_engine")
        assert engine_health["circuit_state"] == CircuitState.OPEN.value
        
        # Make engine succeed
        recovering_engine.translate = Mock(return_value=TranslationResult(
            success=True,
            translated_text="recovered",
            original_text="test",
            translation_method="recovering_engine",
            direction=TranslationDirection.TO_TAU
        ))
        
        # Start monitoring for automatic recovery
        translation_manager.health_monitor.start_continuous_monitoring({"recovering_engine": recovering_engine})
        
        # Simulate recovery timeout
        health = translation_manager.health_monitor.engine_health["recovering_engine"]
        health.last_failure_time = datetime.utcnow() - timedelta(seconds=circuit_config.recovery_timeout + 1)
        
        # Wait for recovery attempt
        time.sleep(circuit_config.health_check_interval * 2)
        
        # Check recovery attempted
        updated_health = translation_manager.health_monitor.get_engine_health("recovering_engine")
        assert updated_health["circuit_state"] in [CircuitState.HALF_OPEN.value, CircuitState.CLOSED.value]
        
        # Stop monitoring
        translation_manager.health_monitor.stop_continuous_monitoring()
    
    # Test 7: Performance impact test
    def test_health_monitoring_performance_impact(self, translation_manager, mock_engine):
        """Test health monitoring doesn't significantly impact translation performance."""
        translation_manager.register_engine(mock_engine)
        
        # Measure translation time without monitoring
        start = time.time()
        for _ in range(100):
            translation_manager.translate("test", TranslationDirection.TO_TAU)
        time_without_monitoring = time.time() - start
        
        # Start monitoring
        translation_manager.health_monitor.start_continuous_monitoring({"test_engine": mock_engine})
        
        # Measure translation time with monitoring
        start = time.time()
        for _ in range(100):
            translation_manager.translate("test", TranslationDirection.TO_TAU)
        time_with_monitoring = time.time() - start
        
        translation_manager.health_monitor.stop_continuous_monitoring()
        
        # Performance impact should be minimal (less than 20% overhead)
        overhead = (time_with_monitoring - time_without_monitoring) / time_without_monitoring
        assert overhead < 0.2, f"Health monitoring overhead too high: {overhead:.2%}"
    
    # Test 8: Multi-engine health coordination
    def test_multi_engine_health_coordination(self, translation_manager):
        """Test health monitoring with multiple engines."""
        # Create multiple engines with different health states
        engines = []
        for i in range(5):
            engine = Mock()
            engine.metadata = Mock()
            engine.metadata.name = f"engine_{i}"
            engine.is_available = True
            engine.get_supported_directions = Mock(return_value=[TranslationDirection.TO_TAU])
            engine.can_translate = Mock(return_value=True)
            
            # Make some engines fail
            if i % 2 == 0:
                engine.translate = Mock(return_value=TranslationResult(
                    success=True,
                    translated_text=f"output_{i}",
                    original_text="test",
                    translation_method=f"engine_{i}",
                    direction=TranslationDirection.TO_TAU
                ))
            else:
                engine.translate = Mock(return_value=TranslationResult(
                    success=False,
                    translated_text="",
                    original_text="test",
                    translation_method=f"engine_{i}",
                    direction=TranslationDirection.TO_TAU,
                    error_message=f"Engine {i} failed"
                ))
            
            engines.append(engine)
            translation_manager.register_engine(engine)
        
        # Perform translations to generate health data
        for _ in range(3):
            for engine in engines:
                translation_manager.translate("test", TranslationDirection.TO_TAU, engine_name=engine.metadata.name)
        
        # Check overall health
        overall_health = translation_manager.health_monitor.get_overall_health()
        assert overall_health["total_engines"] == 5
        assert overall_health["healthy_engines"] == 3  # Engines 0, 2, 4
        assert overall_health["unhealthy_engines"] == 2  # Engines 1, 3
        assert overall_health["status"] != HealthStatus.HEALTHY.value  # Some engines unhealthy
    
    # Test 9: Health history and metrics
    def test_health_history_and_metrics(self, test_client, translation_manager, mock_engine):
        """Test health history tracking and metrics aggregation."""
        translation_manager.register_engine(mock_engine)
        
        # Perform multiple health checks
        for _ in range(10):
            translation_manager.translate("test", TranslationDirection.TO_TAU)
            time.sleep(0.1)
        
        # Get health history
        response = test_client.get("/health/history?hours=1")
        assert response.status_code == 200
        history = response.json()["data"]["history"]
        assert len(history) >= 10
        
        # Verify history entries
        for entry in history:
            assert "timestamp" in entry
            assert "engine_name" in entry
            assert "status" in entry
            assert "response_time" in entry
        
        # Get metrics
        response = test_client.get("/health/metrics?hours=1")
        assert response.status_code == 200
        metrics = response.json()["data"]
        assert metrics["total_checks"] >= 10
        assert metrics["success_rate"] == 100.0  # All successful with mock_engine
        assert "test_engine" in metrics["engines_metrics"]
    
    # Test 10: Alert system integration
    def test_alert_system_integration(self, translation_manager):
        """Test alert system triggers on health issues."""
        alerts_received = []
        
        def alert_handler(engine_name, status, message):
            alerts_received.append({
                "engine": engine_name,
                "status": status,
                "message": message,
                "timestamp": datetime.utcnow()
            })
        
        translation_manager.health_monitor.add_alert_callback(alert_handler)
        
        # Create critical engine
        critical_engine = Mock()
        critical_engine.metadata = Mock()
        critical_engine.metadata.name = "critical_engine"
        critical_engine.is_available = True
        critical_engine.get_supported_directions = Mock(return_value=[TranslationDirection.TO_TAU])
        critical_engine.can_translate = Mock(return_value=True)
        critical_engine.translate = Mock(side_effect=Exception("Critical system failure"))
        
        translation_manager.register_engine(critical_engine)
        
        # Trigger critical failure
        try:
            translation_manager.translate("test", TranslationDirection.TO_TAU, engine_name="critical_engine")
        except:
            pass
        
        # Verify alert was triggered
        assert len(alerts_received) > 0
        alert = alerts_received[0]
        assert alert["engine"] == "critical_engine"
        assert alert["status"] == HealthStatus.CRITICAL
        assert "Critical system failure" in alert["message"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])