"""
Translation Orchestrator - Clean Architecture Implementation

Orchestrates translation engines using dependency injection and clean separation of concerns.
Follows SOLID principles with proper abstraction and service integration.

Author: DarkLightX / Dana Edwards
"""

import logging
import time
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import TranslationEngine, TranslationResult, TranslationDirection
from ..core.responses import TranslationError, TranslationResponse
from ..core.statistics import TranslationStatisticsService
from ..core.health_monitor import TranslationHealthMonitor, CircuitBreakerConfig
from ..core.engine_interface import ITranslationEngine, TranslationContext
from ..core.dependency_injection import ServiceContainer


logger = logging.getLogger(__name__)


class TranslationOrchestrator:
    """
    Core translation orchestration service.
    
    Follows Single Responsibility Principle - only handles routing and execution.
    Separated from statistics, health monitoring, and engine management.
    """
    
    def __init__(
        self,
        statistics_service: TranslationStatisticsService,
        health_monitor: TranslationHealthMonitor,
        service_container: ServiceContainer
    ):
        self.statistics = statistics_service
        self.health_monitor = health_monitor
        self.container = service_container
        
        # Core engine management
        self.engines: List[ITranslationEngine] = []
        self.default_engine: Optional[ITranslationEngine] = None
        self.fallback_engines: List[ITranslationEngine] = []
        
        # Configuration
        self.confidence_threshold = 0.7
        self.max_parallel_engines = 3
        self.request_timeout = 30.0
        
        self.logger = logging.getLogger(__name__)
    
    def register_engine(
        self, 
        engine: ITranslationEngine, 
        is_default: bool = False, 
        is_fallback: bool = False
    ) -> None:
        """Register a translation engine with the orchestrator."""
        if engine not in self.engines:
            self.engines.append(engine)
            
            # Register with health monitor
            self.health_monitor.register_engine(engine.metadata.name)
            
            if is_default:
                self.default_engine = engine
                self.logger.info(f"Set default engine: {engine.metadata.name}")
            
            if is_fallback:
                self.fallback_engines.append(engine)
                self.logger.info(f"Added fallback engine: {engine.metadata.name}")
            
            self.logger.info(f"Registered translation engine: {engine.metadata.name}")
    
    def get_available_engines(self, direction: Optional[TranslationDirection] = None) -> List[ITranslationEngine]:
        """Get list of available engines, optionally filtered by direction."""
        available = [
            engine for engine in self.engines 
            if engine.is_available and self._is_engine_healthy(engine)
        ]
        
        if direction:
            available = [
                engine for engine in available
                if direction in engine.get_supported_directions()
            ]
        
        return available
    
    def find_best_engine(self, text: str, direction: TranslationDirection, context: Optional[TranslationContext] = None) -> Optional[ITranslationEngine]:
        """Find the best engine for a given translation request."""
        available_engines = self.get_available_engines(direction)
        
        if not available_engines:
            return None
        
        # Filter engines that can handle this text
        capable_engines = [
            engine for engine in available_engines
            if engine.can_translate(text, direction, context)
        ]
        
        if not capable_engines:
            return None
        
        # Prefer default engine if it's capable and healthy
        if (self.default_engine and 
            self.default_engine in capable_engines and 
            self._is_engine_healthy(self.default_engine)):
            return self.default_engine
        
        # Sort by priority (healthier engines first)
        capable_engines.sort(key=lambda e: self._calculate_engine_priority(e), reverse=True)
        
        return capable_engines[0]
    
    def translate(
        self,
        text: str,
        direction: TranslationDirection,
        context: Optional[TranslationContext] = None,
        engine_name: Optional[str] = None,
        use_fallback: bool = True,
        **kwargs
    ) -> TranslationResult:
        """Translate text using the best available engine."""
        start_time = time.time()
        
        # Create context if not provided
        if context is None:
            context = TranslationContext()
        
        try:
            # Validate input
            if not text or not text.strip():
                raise TranslationError("Empty input text provided")
            
            # Find target engine
            target_engine = self._select_engine(text, direction, context, engine_name)
            if not target_engine:
                raise TranslationError(f"No available engine for direction: {direction.value}")
            
            # Attempt translation
            result = self._attempt_translation(target_engine, text, direction, context, **kwargs)
            
            # Try fallback engines if primary failed and fallback is enabled
            if not result.success and use_fallback:
                result = self._try_fallback_engines(text, direction, context, target_engine, **kwargs)
            
            # Record statistics
            self._record_translation_metrics(result, start_time)
            
            return result
            
        except Exception as e:
            # Create error result
            error_result = TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method="orchestrator_error",
                direction=direction,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
            
            # Record error statistics
            self._record_translation_metrics(error_result, start_time)
            
            self.logger.error(f"Translation orchestration failed: {e}")
            return error_result
    
    def translate_parallel(
        self,
        text: str,
        direction: TranslationDirection,
        context: Optional[TranslationContext] = None,
        max_engines: Optional[int] = None,
        **kwargs
    ) -> List[TranslationResult]:
        """Translate using multiple engines in parallel."""
        max_engines = max_engines or self.max_parallel_engines
        available_engines = self.get_available_engines(direction)
        
        capable_engines = [
            engine for engine in available_engines
            if engine.can_translate(text, direction, context)
        ][:max_engines]
        
        if not capable_engines:
            return []
        
        results = []
        with ThreadPoolExecutor(max_workers=len(capable_engines)) as executor:
            # Submit translation tasks
            future_to_engine = {
                executor.submit(
                    self._attempt_translation, 
                    engine, text, direction, context, **kwargs
                ): engine
                for engine in capable_engines
            }
            
            # Collect results
            for future in as_completed(future_to_engine, timeout=self.request_timeout):
                engine = future_to_engine[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Record statistics for each engine
                    self.statistics.record_translation(
                        engine_name=engine.metadata.name,
                        direction=direction.value,
                        success=result.success,
                        processing_time=result.processing_time,
                        confidence=result.confidence,
                        error_type=result.error_message if not result.success else None
                    )
                    
                except Exception as e:
                    self.logger.error(f"Parallel translation failed for {engine.metadata.name}: {e}")
                    error_result = TranslationResult(
                        success=False,
                        translated_text="",
                        original_text=text,
                        translation_method=engine.metadata.name,
                        direction=direction,
                        error_message=str(e)
                    )
                    results.append(error_result)
        
        # Sort by confidence score
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results
    
    def _select_engine(
        self,
        text: str,
        direction: TranslationDirection,
        context: TranslationContext,
        engine_name: Optional[str]
    ) -> Optional[ITranslationEngine]:
        """Select appropriate engine for translation."""
        if engine_name:
            # Find specific engine by name
            for engine in self.engines:
                if engine.metadata.name == engine_name and engine.is_available:
                    return engine
            return None
        
        return self.find_best_engine(text, direction, context)
    
    def _attempt_translation(
        self,
        engine: ITranslationEngine,
        text: str,
        direction: TranslationDirection,
        context: TranslationContext,
        **kwargs
    ) -> TranslationResult:
        """Attempt translation with specific engine."""
        try:
            self.logger.debug(f"Attempting translation with {engine.metadata.name}")
            
            # Check health before translation
            health_check = self.health_monitor.check_engine_health(engine.metadata.name, engine)
            if not health_check.status.value in ['healthy', 'degraded']:
                return TranslationResult(
                    success=False,
                    translated_text="",
                    original_text=text,
                    translation_method=engine.metadata.name,
                    direction=direction,
                    error_message=f"Engine unhealthy: {health_check.error_message}"
                )
            
            result = engine.translate(text, direction, context, **kwargs)
            
            if result.success:
                self.logger.info(f"Translation successful with {engine.metadata.name} (confidence: {result.confidence})")
            else:
                self.logger.warning(f"Translation failed with {engine.metadata.name}: {result.error_message}")
            
            return result
            
        except Exception as e:
            error_msg = f"Engine {engine.metadata.name} threw exception: {str(e)}"
            self.logger.error(error_msg)
            
            return TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method=engine.metadata.name,
                direction=direction,
                error_message=error_msg
            )
    
    def _try_fallback_engines(
        self,
        text: str,
        direction: TranslationDirection,
        context: TranslationContext,
        failed_engine: ITranslationEngine,
        **kwargs
    ) -> TranslationResult:
        """Try fallback engines when primary translation fails."""
        self.logger.info(f"Trying fallback engines after {failed_engine.metadata.name} failed")
        
        for fallback_engine in self.fallback_engines:
            if fallback_engine == failed_engine or not fallback_engine.is_available:
                continue
            
            if not fallback_engine.can_translate(text, direction, context):
                continue
            
            if not self._is_engine_healthy(fallback_engine):
                continue
            
            result = self._attempt_translation(fallback_engine, text, direction, context, **kwargs)
            if result.success:
                self.logger.info(f"Fallback successful with {fallback_engine.metadata.name}")
                return result
        
        # All fallbacks failed
        return TranslationResult(
            success=False,
            translated_text="",
            original_text=text,
            translation_method="all_fallbacks_failed",
            direction=direction,
            error_message="All translation engines failed"
        )
    
    def _record_translation_metrics(self, result: TranslationResult, start_time: float) -> None:
        """Record translation metrics in statistics service."""
        processing_time = result.processing_time or (time.time() - start_time)
        
        self.statistics.record_translation(
            engine_name=result.translation_method,
            direction=result.direction.value,
            success=result.success,
            processing_time=processing_time,
            confidence=result.confidence,
            error_type=result.error_message if not result.success else None
        )
    
    def _is_engine_healthy(self, engine: ITranslationEngine) -> bool:
        """Check if engine is healthy enough for use."""
        engine_health = self.health_monitor.get_engine_health(engine.metadata.name)
        if not engine_health:
            return True  # Assume healthy if no health data
        
        return engine_health.get('is_available', True)
    
    def _calculate_engine_priority(self, engine: ITranslationEngine) -> float:
        """Calculate priority score for engine selection."""
        base_priority = 1.0
        
        # Health-based scoring
        engine_health = self.health_monitor.get_engine_health(engine.metadata.name)
        if engine_health:
            success_rate = engine_health.get('success_rate', 100.0)
            avg_response_time = engine_health.get('average_response_time', 0.1)
            
            # Priority based on success rate and speed
            health_score = (success_rate / 100.0) * (1.0 / max(avg_response_time, 0.01))
            base_priority *= health_score
        
        # Default engine gets bonus
        if engine == self.default_engine:
            base_priority *= 1.5
        
        return base_priority


class RefactoredTranslationManager:
    """
    Refactored Translation Manager using clean architecture principles.
    
    Acts as a facade over the orchestrator and provides backward compatibility
    while leveraging the new service-oriented architecture.
    """
    
    def __init__(self, service_container: Optional[ServiceContainer] = None):
        # Initialize or get service container
        if service_container is None:
            from ..core.dependency_injection import get_container
            service_container = get_container()
        
        self.container = service_container
        
        # Initialize services
        self.statistics = TranslationStatisticsService()
        self.health_monitor = TranslationHealthMonitor(CircuitBreakerConfig())
        self.orchestrator = TranslationOrchestrator(
            self.statistics,
            self.health_monitor,
            self.container
        )
        
        # Register services in container
        self.container.register_instance(TranslationStatisticsService, self.statistics)
        self.container.register_instance(TranslationHealthMonitor, self.health_monitor)
        self.container.register_instance(TranslationOrchestrator, self.orchestrator)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialized RefactoredTranslationManager with clean architecture")
    
    # Facade methods for backward compatibility
    
    def register_engine(self, engine: TranslationEngine, is_default: bool = False, is_fallback: bool = False):
        """Register a translation engine (backward compatibility)."""
        # Convert legacy engine to new interface if needed
        if hasattr(engine, 'metadata'):
            new_engine = engine
        else:
            # Wrap legacy engine with adapter (would implement adapter pattern)
            new_engine = self._create_engine_adapter(engine)
        
        self.orchestrator.register_engine(new_engine, is_default, is_fallback)
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Translate text (backward compatibility)."""
        return self.orchestrator.translate(text, direction, **kwargs)
    
    def translate_parallel(self, text: str, direction: TranslationDirection, **kwargs) -> List[TranslationResult]:
        """Parallel translation (backward compatibility)."""
        return self.orchestrator.translate_parallel(text, direction, **kwargs)
    
    def get_available_engines(self, direction: TranslationDirection = None) -> List[TranslationEngine]:
        """Get available engines (backward compatibility)."""
        new_engines = self.orchestrator.get_available_engines(direction)
        # Convert back to legacy format if needed
        return [self._convert_to_legacy_engine(e) for e in new_engines]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get translation statistics."""
        return self.statistics.get_overall_statistics()
    
    def get_engine_statistics(self, engine_name: Optional[str] = None) -> Dict[str, Any]:
        """Get engine-specific statistics."""
        return self.statistics.get_engine_statistics(engine_name)
    
    def get_performance_metrics(self, time_window_hours: float = 24.0) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.statistics.get_performance_metrics(time_window_hours)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        return self.health_monitor.get_overall_health()
    
    def get_engine_health(self, engine_name: Optional[str] = None) -> Dict[str, Any]:
        """Get engine health information."""
        return self.health_monitor.get_engine_health(engine_name)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        overall_health = self.health_monitor.get_overall_health()
        statistics = self.statistics.get_overall_statistics()
        
        return {
            'overall_status': overall_health['status'],
            'engines': overall_health,
            'statistics': statistics,
            'uptime_seconds': time.time() - self.statistics.session_start_time.timestamp()
        }
    
    def reset_statistics(self):
        """Reset all statistics."""
        self.statistics.reset_statistics()
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold."""
        self.orchestrator.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def _create_engine_adapter(self, legacy_engine: TranslationEngine) -> ITranslationEngine:
        """Create adapter for legacy engine (placeholder for adapter pattern)."""
        # Would implement proper adapter pattern here
        return legacy_engine
    
    def _convert_to_legacy_engine(self, new_engine: ITranslationEngine) -> TranslationEngine:
        """Convert new engine back to legacy format if needed."""
        # Would implement reverse adapter here
        return new_engine