"""
Comprehensive unit tests for the translation manager.

Author: DarkLightX / Dana Edwards
"""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, call
from concurrent.futures import Future

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.base import TranslationDirection, TranslationResult, TranslationEngine
from backend.unified.core.responses import TranslationError


class MockEngine(TranslationEngine):
    """Mock translation engine for testing."""
    
    def __init__(self, name="mock_engine", available=True, can_translate_result=True):
        super().__init__(name=name, description=f"Mock {name}")
        self.is_available = available
        self._can_translate_result = can_translate_result
        self.translate_calls = []
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        return self._can_translate_result
    
    def get_supported_directions(self) -> list:
        return [TranslationDirection.TO_TAU, TranslationDirection.TO_TCE]
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        self.translate_calls.append((text, direction, kwargs))
        return TranslationResult(
            success=True,
            translated_text=f"translated_{text}",
            original_text=text,
            translation_method=self.name,
            direction=direction,
            confidence=0.8,
            metadata={"mock": True}
        )


class TestTranslationManager:
    """Unit tests for TranslationManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a translation manager instance."""
        return TranslationManager()
    
    @pytest.fixture
    def mock_engine(self):
        """Create a mock translation engine."""
        return MockEngine()
    
    # Initialization tests
    
    def test_manager_initialization(self, manager):
        """Test manager initializes with correct defaults."""
        assert manager.engines == []
        assert manager.default_engine is None
        assert manager.fallback_engines == []
        assert manager.parallel_mode == False
        assert manager.confidence_threshold == 0.7
        assert manager.translation_count == 0
    
    # Engine registration tests
    
    def test_register_engine(self, manager, mock_engine):
        """Test engine registration."""
        manager.register_engine(mock_engine)
        
        assert mock_engine in manager.engines
        assert mock_engine.name in manager.engine_usage
        assert manager.engine_usage[mock_engine.name] == 0
    
    def test_register_default_engine(self, manager, mock_engine):
        """Test registering engine as default."""
        manager.register_engine(mock_engine, is_default=True)
        
        assert manager.default_engine == mock_engine
        assert mock_engine in manager.engines
    
    def test_register_fallback_engine(self, manager, mock_engine):
        """Test registering engine as fallback."""
        manager.register_engine(mock_engine, is_fallback=True)
        
        assert mock_engine in manager.fallback_engines
        assert mock_engine in manager.engines
    
    def test_register_multiple_engines(self, manager):
        """Test registering multiple engines."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        engine3 = MockEngine("engine3")
        
        manager.register_engine(engine1, is_default=True)
        manager.register_engine(engine2, is_fallback=True)
        manager.register_engine(engine3)
        
        assert len(manager.engines) == 3
        assert manager.default_engine == engine1
        assert engine2 in manager.fallback_engines
        assert engine3 not in manager.fallback_engines
    
    # Engine discovery tests
    
    def test_get_available_engines(self, manager):
        """Test getting available engines."""
        engine1 = MockEngine("engine1", available=True)
        engine2 = MockEngine("engine2", available=False)
        engine3 = MockEngine("engine3", available=True)
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        manager.register_engine(engine3)
        
        available = manager.get_available_engines()
        assert len(available) == 2
        assert engine1 in available
        assert engine3 in available
        assert engine2 not in available
    
    def test_get_available_engines_by_direction(self, manager):
        """Test filtering available engines by direction."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        
        # Override supported directions for engine2
        engine2.get_supported_directions = lambda: [TranslationDirection.TO_TAU]
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        # Both support TO_TAU
        tau_engines = manager.get_available_engines(TranslationDirection.TO_TAU)
        assert len(tau_engines) == 2
        
        # Only engine1 supports TO_TCE
        tce_engines = manager.get_available_engines(TranslationDirection.TO_TCE)
        assert len(tce_engines) == 1
        assert engine1 in tce_engines
    
    def test_find_best_engine(self, manager):
        """Test finding best engine for translation."""
        engine1 = MockEngine("engine1", can_translate_result=False)
        engine2 = MockEngine("engine2", can_translate_result=True)
        engine3 = MockEngine("engine3", can_translate_result=True)
        
        manager.register_engine(engine1)
        manager.register_engine(engine2, is_default=True)
        manager.register_engine(engine3)
        
        # Should prefer default engine if capable
        best = manager.find_best_engine("test", TranslationDirection.TO_TAU)
        assert best == engine2
    
    def test_find_best_engine_default_not_capable(self, manager):
        """Test finding best engine when default can't handle request."""
        engine1 = MockEngine("engine1", can_translate_result=True)
        engine2 = MockEngine("engine2", can_translate_result=False)
        
        manager.register_engine(engine1)
        manager.register_engine(engine2, is_default=True)
        
        # Should fall back to first capable engine
        best = manager.find_best_engine("test", TranslationDirection.TO_TAU)
        assert best == engine1
    
    def test_find_best_engine_none_capable(self, manager):
        """Test finding best engine when none can handle request."""
        engine1 = MockEngine("engine1", can_translate_result=False)
        engine2 = MockEngine("engine2", can_translate_result=False)
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        best = manager.find_best_engine("test", TranslationDirection.TO_TAU)
        assert best is None
    
    # Translation tests
    
    def test_translate_success(self, manager, mock_engine):
        """Test successful translation."""
        manager.register_engine(mock_engine)
        
        result = manager.translate("test", TranslationDirection.TO_TAU)
        
        assert result.success == True
        assert result.translated_text == "translated_test"
        assert result.translation_method == "mock_engine"
        assert manager.successful_translations == 1
        assert manager.engine_usage["mock_engine"] == 1
    
    def test_translate_empty_input(self, manager):
        """Test translation with empty input."""
        result = manager.translate("", TranslationDirection.TO_TAU)
        
        assert result.success == False
        assert "Empty input text" in result.error_message
        assert manager.failed_translations == 1
    
    def test_translate_no_available_engine(self, manager):
        """Test translation with no available engines."""
        result = manager.translate("test", TranslationDirection.TO_TAU)
        
        assert result.success == False
        assert "No available engine" in result.error_message
    
    def test_translate_specific_engine(self, manager):
        """Test translation with specific engine requested."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        result = manager.translate("test", TranslationDirection.TO_TAU, engine_name="engine2")
        
        assert result.success == True
        assert result.translation_method == "engine2"
        assert len(engine2.translate_calls) == 1
        assert len(engine1.translate_calls) == 0
    
    def test_translate_engine_not_found(self, manager, mock_engine):
        """Test translation with non-existent engine name."""
        manager.register_engine(mock_engine)
        
        result = manager.translate("test", TranslationDirection.TO_TAU, engine_name="nonexistent")
        
        assert result.success == False
        assert "Engine 'nonexistent' not found" in result.error_message
    
    def test_translate_engine_not_available(self, manager):
        """Test translation with unavailable engine."""
        engine = MockEngine("engine1", available=False)
        manager.register_engine(engine)
        
        result = manager.translate("test", TranslationDirection.TO_TAU, engine_name="engine1")
        
        assert result.success == False
        assert "not available" in result.error_message
    
    # Fallback tests
    
    def test_fallback_on_failure(self, manager):
        """Test fallback mechanism when primary fails."""
        # Create failing primary engine
        primary = MockEngine("primary")
        primary.translate = lambda *args, **kwargs: TranslationResult(
            success=False,
            translated_text="",
            original_text=args[0],
            translation_method="primary",
            direction=args[1],
            error_message="Primary failed"
        )
        
        # Create successful fallback engine
        fallback = MockEngine("fallback")
        
        manager.register_engine(primary, is_default=True)
        manager.register_engine(fallback, is_fallback=True)
        
        result = manager.translate("test", TranslationDirection.TO_TAU)
        
        assert result.success == True
        assert result.translation_method == "fallback"
        assert manager.engine_usage["fallback"] == 1
    
    def test_fallback_disabled(self, manager):
        """Test translation with fallback disabled."""
        # Create failing primary engine
        primary = MockEngine("primary")
        primary.translate = lambda *args, **kwargs: TranslationResult(
            success=False,
            translated_text="",
            original_text=args[0],
            translation_method="primary",
            direction=args[1],
            error_message="Primary failed"
        )
        
        fallback = MockEngine("fallback")
        
        manager.register_engine(primary, is_default=True)
        manager.register_engine(fallback, is_fallback=True)
        
        result = manager.translate("test", TranslationDirection.TO_TAU, use_fallback=False)
        
        assert result.success == False
        assert result.translation_method == "primary"
    
    def test_multiple_fallback_engines(self, manager):
        """Test multiple fallback engines tried in order."""
        primary = MockEngine("primary")
        primary.translate = lambda *args, **kwargs: TranslationResult(
            success=False, translated_text="", original_text=args[0],
            translation_method="primary", direction=args[1]
        )
        
        fallback1 = MockEngine("fallback1")
        fallback1.translate = lambda *args, **kwargs: TranslationResult(
            success=False, translated_text="", original_text=args[0],
            translation_method="fallback1", direction=args[1]
        )
        
        fallback2 = MockEngine("fallback2")  # This one succeeds
        
        manager.register_engine(primary, is_default=True)
        manager.register_engine(fallback1, is_fallback=True)
        manager.register_engine(fallback2, is_fallback=True)
        
        result = manager.translate("test", TranslationDirection.TO_TAU)
        
        assert result.success == True
        assert result.translation_method == "fallback2"
    
    # Parallel translation tests
    
    def test_translate_parallel(self, manager):
        """Test parallel translation with multiple engines."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        engine3 = MockEngine("engine3")
        
        # Set different confidence scores
        engine1.translate = lambda *args, **kwargs: TranslationResult(
            success=True, translated_text="result1", original_text=args[0],
            translation_method="engine1", direction=args[1], confidence=0.7
        )
        engine2.translate = lambda *args, **kwargs: TranslationResult(
            success=True, translated_text="result2", original_text=args[0],
            translation_method="engine2", direction=args[1], confidence=0.9
        )
        engine3.translate = lambda *args, **kwargs: TranslationResult(
            success=True, translated_text="result3", original_text=args[0],
            translation_method="engine3", direction=args[1], confidence=0.8
        )
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        manager.register_engine(engine3)
        
        results = manager.translate_parallel("test", TranslationDirection.TO_TAU)
        
        assert len(results) == 3
        # Should be sorted by confidence (highest first)
        assert results[0].translation_method == "engine2"  # 0.9
        assert results[1].translation_method == "engine3"  # 0.8
        assert results[2].translation_method == "engine1"  # 0.7
    
    def test_translate_parallel_with_failures(self, manager):
        """Test parallel translation handles engine failures."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        
        # Make engine2 fail
        engine2.translate = lambda *args, **kwargs: raise_exception()
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        results = manager.translate_parallel("test", TranslationDirection.TO_TAU)
        
        assert len(results) == 2
        # engine1 should succeed
        assert any(r.success and r.translation_method == "engine1" for r in results)
        # engine2 should have error result
        assert any(not r.success and r.translation_method == "engine2" for r in results)
    
    def test_translate_parallel_max_engines(self, manager):
        """Test parallel translation respects max_engines limit."""
        engines = [MockEngine(f"engine{i}") for i in range(5)]
        for engine in engines:
            manager.register_engine(engine)
        
        results = manager.translate_parallel("test", TranslationDirection.TO_TAU, max_engines=3)
        
        assert len(results) == 3
    
    # Statistics tests
    
    def test_statistics_tracking(self, manager):
        """Test translation statistics are tracked correctly."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        # Do some translations
        manager.translate("test1", TranslationDirection.TO_TAU, engine_name="engine1")
        manager.translate("test2", TranslationDirection.TO_TAU, engine_name="engine1")
        manager.translate("test3", TranslationDirection.TO_TAU, engine_name="engine2")
        
        stats = manager.get_statistics()
        
        assert stats['total_translations'] == 3
        assert stats['successful_translations'] == 3
        assert stats['failed_translations'] == 0
        assert stats['success_rate'] == 100.0
        assert stats['engine_usage']['engine1'] == 2
        assert stats['engine_usage']['engine2'] == 1
    
    def test_reset_statistics(self, manager, mock_engine):
        """Test resetting statistics."""
        manager.register_engine(mock_engine)
        
        # Do some translations
        manager.translate("test", TranslationDirection.TO_TAU)
        manager.translate("test", TranslationDirection.TO_TAU)
        
        # Reset
        manager.reset_statistics()
        
        stats = manager.get_statistics()
        assert stats['total_translations'] == 0
        assert stats['successful_translations'] == 0
        assert stats['failed_translations'] == 0
        assert stats['engine_usage']['mock_engine'] == 0
    
    # Confidence threshold tests
    
    def test_set_confidence_threshold(self, manager):
        """Test setting confidence threshold."""
        manager.set_confidence_threshold(0.85)
        assert manager.confidence_threshold == 0.85
        
        # Test clamping
        manager.set_confidence_threshold(1.5)
        assert manager.confidence_threshold == 1.0
        
        manager.set_confidence_threshold(-0.5)
        assert manager.confidence_threshold == 0.0
    
    # Health check tests
    
    def test_health_check_all_healthy(self, manager):
        """Test health check with all engines healthy."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        health = manager.health_check()
        
        assert health['overall_status'] == 'healthy'
        assert health['engines']['engine1']['status'] == 'healthy'
        assert health['engines']['engine2']['status'] == 'healthy'
    
    def test_health_check_degraded(self, manager):
        """Test health check with some engines unhealthy."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        
        # Make engine2 fail health check
        engine2.translate = lambda *args, **kwargs: raise_exception()
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        health = manager.health_check()
        
        assert health['overall_status'] == 'degraded'
        assert health['engines']['engine1']['status'] == 'healthy'
        assert health['engines']['engine2']['status'] == 'unhealthy'
    
    def test_health_check_critical(self, manager):
        """Test health check with all engines unhealthy."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        
        # Make both fail health check
        engine1.translate = lambda *args, **kwargs: raise_exception()
        engine2.translate = lambda *args, **kwargs: raise_exception()
        
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        health = manager.health_check()
        
        assert health['overall_status'] == 'critical'
        assert health['engines']['engine1']['status'] == 'unhealthy'
        assert health['engines']['engine2']['status'] == 'unhealthy'
    
    # Engine status tests
    
    def test_get_engine_status(self, manager):
        """Test getting engine status."""
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2", available=False)
        
        manager.register_engine(engine1, is_default=True)
        manager.register_engine(engine2, is_fallback=True)
        
        status = manager.get_engine_status()
        
        assert len(status['engines']) == 2
        assert status['default_engine'] == 'engine1'
        assert 'engine2' in status['fallback_engines']
        assert status['total_engines'] == 2
        assert status['available_engines'] == 1
    
    # Error handling tests
    
    def test_engine_exception_handling(self, manager):
        """Test handling of engine exceptions."""
        engine = MockEngine("engine1")
        engine.translate = lambda *args, **kwargs: raise_exception()
        
        manager.register_engine(engine)
        
        result = manager.translate("test", TranslationDirection.TO_TAU, use_fallback=False)
        
        assert result.success == False
        assert "threw exception" in result.error_message
        assert engine.last_error is not None
    
    def test_processing_time_tracking(self, manager, mock_engine):
        """Test that processing time is tracked."""
        manager.register_engine(mock_engine)
        
        result = manager.translate("test", TranslationDirection.TO_TAU)
        
        assert result.processing_time > 0
        assert result.processing_time < 1.0  # Should be fast


def raise_exception():
    """Helper function to raise an exception."""
    raise Exception("Test exception")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])