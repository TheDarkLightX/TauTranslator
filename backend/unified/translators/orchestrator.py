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

from returns.result import Result, Success, Failure
from ..core.domain_types import AppError

from .base import TranslationEngine, TranslationResult, TranslationDirection
from ..core.responses import TranslationError, TranslationResponse
from ..core.statistics import TranslationStatisticsService
from ..core.health_monitor import TranslationHealthMonitor, CircuitBreakerConfig
from ..core.engine_interface import ITranslationEngine, TranslationContext
from ..core.dependency_injection import ServiceContainer
from .grammar_translator import GrammarTranslationEngine # Added for facade


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
    ) -> Result[TranslationResult, AppError]:
        """Translate text using the best available engine."""
        start_time = time.time()

        if context is None:
            context = TranslationContext()

        try:
            if not text or not text.strip():
                return Failure(AppError(detail="Empty input text provided"))

            target_engine = self._select_engine(text, direction, context, engine_name)
            if not target_engine:
                return Failure(AppError(detail=f"No available engine for direction: {direction.value}"))

            # _attempt_translation now returns a Result
            result_monad = self._attempt_translation(target_engine, text, direction, context, **kwargs)

            # If the first attempt fails, try fallbacks
            if isinstance(result_monad, Failure) and use_fallback:
                result_monad = self._try_fallback_engines(text, direction, context, target_engine, **kwargs)

            # Record metrics regardless of outcome
            if isinstance(result_monad, Success):
                self._record_translation_metrics(result_monad.unwrap(), start_time)
            elif isinstance(result_monad, Failure):
                # Create a temporary TranslationResult for metrics
                error_result = TranslationResult(
                    success=False,
                    translated_text="",
                    original_text=text,
                    translation_method="orchestrator_error",
                    direction=direction,
                    error_message=result_monad.failure().detail,
                    processing_time=time.time() - start_time
                )
                self._record_translation_metrics(error_result, start_time)

            return result_monad

        except Exception as e:
            self.logger.error(f"Unhandled exception in translation orchestration: {e}", exc_info=True)
            # Create a temporary TranslationResult for metrics
            error_result = TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method="orchestrator_error",
                direction=direction,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
            self._record_translation_metrics(error_result, start_time)
            return Failure(AppError(detail=str(e), context={"error_type": "unhandled_exception"}))
    
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
    ) -> Result[TranslationResult, AppError]:
        """Attempt translation with a single engine."""
        try:
            if not self._is_engine_healthy(engine):
                return Failure(AppError(detail=f"Engine {engine.metadata.name} is not healthy"))

            # engine.translate now returns a Result
            translation_result = engine.translate(text, direction, context, **kwargs)

            # Handle the Result monad
            if isinstance(translation_result, Failure):
                return translation_result # Propagate the failure

            # On success, unwrap and perform post-processing
            result = translation_result.unwrap()
            if result.confidence < self.confidence_threshold:
                result.success = False
                result.error_message = f"Confidence ({result.confidence}) below threshold ({self.confidence_threshold})"
            
            return Success(result)

        except Exception as e:
            self.logger.error(f"Translation attempt failed for engine {engine.metadata.name}: {e}", exc_info=True)
            # Create a consistent AppError on unexpected exceptions
            error_context = {"engine": engine.metadata.name, "direction": direction.value}
            return Failure(AppError(detail=str(e), context=error_context))
    
    def _try_fallback_engines(
        self,
        text: str,
        direction: TranslationDirection,
        context: TranslationContext,
        primary_engine: ITranslationEngine,
        **kwargs
    ) -> Result[TranslationResult, AppError]:
        """Try fallback engines if primary fails."""
        self.logger.warning(f"Primary engine {primary_engine.metadata.name} failed. Trying fallbacks.")
        
        last_error: Optional[AppError] = None

        for fallback_engine in self.fallback_engines:
            if fallback_engine != primary_engine and self._is_engine_healthy(fallback_engine):
                self.logger.info(f"Trying fallback engine: {fallback_engine.metadata.name}")
                
                fallback_result = self._attempt_translation(
                    fallback_engine, text, direction, context, **kwargs
                )

                if isinstance(fallback_result, Success):
                    return fallback_result  # Propagate success immediately
                
                if isinstance(fallback_result, Failure):
                    last_error = fallback_result.failure()

        # If all fallbacks fail, return a Failure
        error_detail = "All fallback engines failed."
        if last_error:
            error_detail += f" Last error from '{last_error.context.get('engine', 'unknown')}': {last_error.detail}"
        
        return Failure(AppError(detail=error_detail))

    
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


class BackwardCompatibleFacade:
    """
    Refactored Translation Manager using clean architecture principles.
    
    Acts as a facade over the orchestrator and provides backward compatibility
    while leveraging the new service-oriented architecture.
    This version is adapted for simpler instantiation with grammar_content for testing.
    """
    
    def __init__(self, grammar_content: str, service_container: Optional[ServiceContainer] = None):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing BackwardCompatibleFacade with grammar_content (first 50 chars): {grammar_content[:50]}...")

        # 1. Setup dummy/default services for the core orchestrator
        # For real use, these would be properly injected or configured.
        if service_container is None:
            self.container = ServiceContainer()
            # Register dummy services if not already in a provided container
            if not self.container.has_provider(TranslationStatisticsService):
                self.container.register_singleton(TranslationStatisticsService, lambda: TranslationStatisticsService()) # Assuming default constructor
            if not self.container.has_provider(TranslationHealthMonitor):
                # Assuming CircuitBreakerConfig might be needed or has defaults
                dummy_circuit_breaker_config = CircuitBreakerConfig(failure_threshold=5, recovery_timeout_seconds=60)
                self.container.register_singleton(TranslationHealthMonitor, lambda: TranslationHealthMonitor(config=dummy_circuit_breaker_config)) # Assuming default constructor or simple config
        else:
            self.container = service_container

        try:
            stats_service = self.container.resolve(TranslationStatisticsService)
            health_monitor = self.container.resolve(TranslationHealthMonitor)
        except Exception as e:
            self.logger.error(f"Error resolving core services for BackwardCompatibleFacade: {e}")
            # Fallback to basic instantiation if resolution fails, this might not be fully functional
            stats_service = TranslationStatisticsService()
            health_monitor = TranslationHealthMonitor(config=CircuitBreakerConfig(failure_threshold=5, recovery_timeout_seconds=60))
            if not self.container.has_provider(TranslationStatisticsService):
                 self.container.register_instance(TranslationStatisticsService, stats_service)
            if not self.container.has_provider(TranslationHealthMonitor):
                 self.container.register_instance(TranslationHealthMonitor, health_monitor)

        # 2. Instantiate the main TranslationOrchestrator
        # The main TranslationOrchestrator (first class in this file) is now the one being instantiated here.
        self.orchestrator = TranslationOrchestrator(
            statistics_service=stats_service,
            health_monitor=health_monitor,
            service_container=self.container
        )
        self.container.register_instance(TranslationOrchestrator, self.orchestrator) # Register the main orchestrator instance
        
        # 3. Instantiate GrammarTranslationEngine
        try:
            grammar_engine = GrammarTranslationEngine(grammar_string=grammar_content, engine_name="FacadeGrammarEngine")
            self.logger.info(f"Successfully instantiated GrammarTranslationEngine: {grammar_engine.name}")
        except Exception as e:
            self.logger.error(f"Failed to instantiate GrammarTranslationEngine in BackwardCompatibleFacade: {e}", exc_info=True)
            raise # Re-raise the exception as this is critical for the facade's purpose

        # 4. Register the grammar engine with the orchestrator
        self.orchestrator.register_engine(grammar_engine, is_default=True)
        self.logger.info(f"Registered GrammarTranslationEngine '{grammar_engine.name}' as default.")

        # Existing facade logic for service container setup (if any was intended beyond orchestrator)
        # self.statistics = self.container.resolve(TranslationStatisticsService)
        # self.health_monitor = self.container.resolve(TranslationHealthMonitor)
        # No, these are part of the main orchestrator, the facade just uses it.

        self.logger.info("Initialized BackwardCompatibleFacade with grammar support.")
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
        self.logger.info("Initialized TranslationOrchestrator with clean architecture")
    
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
    
    def translate_english_to_formal(self, english_text: str) -> str:
        """Translates English text to its formal representation using the configured grammar engine."""
        self.logger.debug(f"BackwardCompatibleFacade: translating English to Formal: '{english_text}'")
        # Default context or allow passing one?
        # For now, assume no special context or use orchestrator's default handling.
        result = self.orchestrator.translate(text=english_text, direction=TranslationDirection.EN_TO_FORMAL)
        if result.success:
            self.logger.info(f"BackwardCompatibleFacade: EN_TO_FORMAL success for '{english_text[:30]}...' -> '{result.translated_text[:30]}...'")
            return result.translated_text
        else:
            self.logger.error(f"BackwardCompatibleFacade: EN_TO_FORMAL failed for '{english_text}': {result.error_message}")
            # Consider how to propagate errors; for now, returning error message or raising an exception.
            # For BDD tests, returning a string indicating error might be useful.
            return f"ERROR_TRANSLATING_TO_FORMAL: {result.error_message}"

    def translate_formal_to_english(self, formal_text: str) -> str:
        """Translates formal specification text to English using the configured grammar engine."""
        self.logger.debug(f"BackwardCompatibleFacade: translating Formal to English: '{formal_text}'")
        result = self.orchestrator.translate(text=formal_text, direction=TranslationDirection.FORMAL_TO_EN)
        if result.success:
            self.logger.info(f"BackwardCompatibleFacade: FORMAL_TO_EN success for '{formal_text[:30]}...' -> '{result.translated_text[:30]}...'")
            return result.translated_text
        else:
            self.logger.error(f"BackwardCompatibleFacade: FORMAL_TO_EN failed for '{formal_text}': {result.error_message}")
            return f"ERROR_TRANSLATING_TO_ENGLISH: {result.error_message}"

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