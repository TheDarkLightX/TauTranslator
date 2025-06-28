"""
Translation Manager - Refactored for minimal complexity.
Orchestrates multiple translation engines with clean architecture.
"""

import logging
import time
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from backend.unified.core.domain_types import (SourceText, TargetText, AppError)
from returns.result import Result, Success, Failure
from returns.pipeline import is_successful
from backend.unified.core.functional_utils import guard, guard_not_none
from .base import TranslationEngine, TranslationResult, TranslationDirection
from backend.unified.core.interfaces import IEventBus, ICacheRepository


# Constants
class ManagerConstants:
    DEFAULT_CONFIDENCE_THRESHOLD = 0.7
    MAX_WORKERS = 4
    CACHE_KEY_PREFIX = "trans"
    DEFAULT_TIMEOUT = 30.0


# Domain Models
@dataclass
class EngineRegistration:
    """Registration info for an engine."""
    engine: TranslationEngine
    is_default: bool = False
    is_fallback: bool = False
    priority: int = 0


@dataclass
class TranslationRequest:
    """Encapsulates a translation request."""
    text: SourceText
    direction: TranslationDirection
    preferred_engine: Optional[str] = None
    timeout: float = ManagerConstants.DEFAULT_TIMEOUT
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranslationMetrics:
    """Metrics for a translation operation."""
    engine_name: str
    duration_ms: float
    success: bool
    confidence: float = 0.0
    cache_hit: bool = False


# Strategy Pattern for Engine Selection
class EngineSelectionStrategy(ABC):
    """Base strategy for engine selection."""
    
    @abstractmethod
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Select an engine for the request."""
        pass


class PreferredEngineStrategy(EngineSelectionStrategy):
    """Select preferred engine if available."""
    
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Select preferred engine."""
        if not request.preferred_engine:
            return Failure(AppError(error_code="NO_PREFERENCE", message="No preferred engine specified"))
        
        return self._find_preferred_engine(engines, request)
    
    def _find_preferred_engine(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Find the preferred engine."""
        engine = self._get_engine_by_name(engines, request.preferred_engine)
        if engine:
            return self._validate_engine_capability(engine, request)
        return Failure(AppError(error_code="ENGINE_NOT_FOUND", message=f"Engine {request.preferred_engine} not found"))
    
    def _get_engine_by_name(
        self,
        engines: List[EngineRegistration],
        name: str
    ) -> Optional[TranslationEngine]:
        """Get engine by name from registrations."""
        for reg in engines:
            if reg.engine.name == name:
                return reg.engine
        return None
    
    def _validate_engine_capability(
        self,
        engine: TranslationEngine,
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Validate engine can handle request."""
        if engine.can_translate(request.text, request.direction):
            return Success(engine)
        return Failure(AppError(error_code="ENGINE_CANNOT_TRANSLATE", 
                      message=f"Engine {engine.name} cannot handle request"))


class DefaultEngineStrategy(EngineSelectionStrategy):
    """Select default engine."""
    
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Select default engine."""
        engine = self._find_default_engine(engines, request)
        if engine:
            return Success(engine)
        return Failure(AppError(error_code="DEFAULT_ENGINE_NOT_FOUND", message="No default engine found"))
    
    def _find_default_engine(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Optional[TranslationEngine]:
        """Find capable default engine."""
        for reg in engines:
            if reg.is_default and reg.engine.can_translate(request.text, request.direction):
                return reg.engine
        return None


class BestAvailableStrategy(EngineSelectionStrategy):
    """Select best available engine by priority."""
    
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Select highest priority engine that can handle request."""
        sorted_engines = self._sort_by_priority(engines)
        return self._find_capable_engine(sorted_engines, request)
    
    def _sort_by_priority(self, engines: List[EngineRegistration]) -> List[EngineRegistration]:
        """
        Note: This is a pure function (no side effects).
        Sort engines by priority."""
        return sorted(engines, key=lambda r: r.priority, reverse=True)
    
    def _find_capable_engine(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Find first capable engine."""
        engine = self._get_first_capable(engines, request)
        if engine:
            return Success(engine)
        return Failure(AppError(error_code="NO_SUITABLE_ENGINE", message="No suitable engine found"))
    
    def _get_first_capable(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Optional[TranslationEngine]:
        """Get first engine capable of handling request."""
        for reg in engines:
            if reg.engine.can_translate(request.text, request.direction):
                return reg.engine
        return None


# Cache Key Generator
class CacheKeyGenerator:
    """Generates cache keys for translations."""
    
    @staticmethod
    def generate(request: TranslationRequest) -> str:
        """
        Note: This is a pure function (no side effects).
        Generate cache key for request."""
        key_hash = CacheKeyGenerator._hash_request(request)
        return f"{ManagerConstants.CACHE_KEY_PREFIX}_{request.direction.value}_{key_hash}"
    
    @staticmethod
    def _hash_request(request: TranslationRequest) -> str:
        """
        Note: This is a pure function (no side effects).
        Hash request data."""
        import hashlib
        key_string = CacheKeyGenerator._build_key_string(request)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    @staticmethod
    def _build_key_string(request: TranslationRequest) -> str:
        """
        Note: This is a pure function (no side effects).
        Build key string from request."""
        parts = [str(request.text), request.direction.value, request.preferred_engine or "any"]
        return "|".join(parts)


# Event Publisher
class TranslationEventPublisher:
    """Publishes translation events."""
    
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
    
    def publish_started(self, engine_name: str, request: TranslationRequest):
        """
        Note: This is a pure function (no side effects).
        Publish translation started event."""
        event = self._create_started_event(engine_name, request)
        self._event_bus.publish(event)
    
    def publish_completed(self, metrics: TranslationMetrics):
        """
        Note: This is a pure function (no side effects).
        Publish translation completed event."""
        event = self._create_completed_event(metrics)
        self._event_bus.publish(event)
    
    def publish_failed(self, engine_name: str, error: str):
        """
        Note: This is a pure function (no side effects).
        Publish translation failed event."""
        event = self._create_failed_event(engine_name, error)
        self._event_bus.publish(event)
    
    def _create_started_event(self, engine_name: str, request: TranslationRequest) -> Dict[str, Any]:
        """
        Note: This is a pure function (no side effects).
        Create started event data."""
        return {
            "type": "translation.started",
            "engine": engine_name,
            "direction": request.direction.value,
            "text_length": len(request.text)
        }
    
    def _create_completed_event(self, metrics: TranslationMetrics) -> Dict[str, Any]:
        """
        Note: This is a pure function (no side effects).
        Create completed event data."""
        return {
            "type": "translation.completed",
            "engine": metrics.engine_name,
            "success": metrics.success,
            "duration_ms": metrics.duration_ms,
            "confidence": metrics.confidence,
            "cache_hit": metrics.cache_hit
        }
    
    def _create_failed_event(self, engine_name: str, error: str) -> Dict[str, Any]:
        """
        Note: This is a pure function (no side effects).
        Create failed event data."""
        return {
            "type": "translation.failed",
            "engine": engine_name,
            "error": error
        }


# Engine Registry
class EngineRegistry:
    """Manages registered engines."""
    
    def __init__(self):
        self._registrations: List[EngineRegistration] = []
        self._engines_by_name: Dict[str, TranslationEngine] = {}
    
    def register(self, registration: EngineRegistration) -> Result[None, AppError]:
        """
        Note: This is a pure function (no side effects).
        Register an engine."""
        validation = self._validate_registration(registration)
        if isinstance(validation, Failure):
            return validation
        
        self._add_registration(registration)
        return Success(None)
    
    def _validate_registration(self, registration: EngineRegistration) -> Result[None, AppError]:
        """
        Note: This is a pure function (no side effects).
        Validate engine registration."""
        if registration.engine.name in self._engines_by_name:
            return Failure(AppError(error_code="DUPLICATE_ENGINE", message=f"Engine {registration.engine.name} already registered"))
        return Success(None)
    
    def _add_registration(self, registration: EngineRegistration):
        """
        Note: This is a pure function (no side effects).
        Add registration to registry."""
        self._registrations.append(registration)
        self._engines_by_name[registration.engine.name] = registration.engine
    
    def get_all(self) -> List[EngineRegistration]:
        """
        Note: This is a pure function (no side effects).
        Get all registrations."""
        return self._registrations.copy()
    
    def get_by_name(self, name: str) -> Optional[TranslationEngine]:
        """
        Note: This is a pure function (no side effects).
        Get engine by name."""
        return self._engines_by_name.get(name)
    
    def get_fallback_engines(self) -> List[TranslationEngine]:
        """
        Note: This is a pure function (no side effects).
        Get fallback engines."""
        return [r.engine for r in self._registrations if r.is_fallback]


# Main Translation Manager
class TranslationManager:
    """Orchestrates translation operations with minimal complexity."""
    
    def __init__(
        self,
        event_bus: IEventBus,
        cache_repository: ICacheRepository,
        confidence_threshold: float = ManagerConstants.DEFAULT_CONFIDENCE_THRESHOLD
    ):
        """Initialize manager."""
        self._init_core_components(event_bus, cache_repository, confidence_threshold)
        self._init_auxiliary_components()
    
    def _init_core_components(self, event_bus, cache_repository, confidence_threshold):
        """
        Note: This is a pure function (no side effects).
        Initialize core components."""
        self._registry = EngineRegistry()
        self._cache = cache_repository
        self._event_bus = event_bus
        self._event_publisher = TranslationEventPublisher(event_bus)
        self._confidence_threshold = confidence_threshold
    
    def _init_auxiliary_components(self):
        """Initialize auxiliary components."""
        self._cache_key_generator = CacheKeyGenerator()
        self._selection_strategies = self._init_strategies()
        self.logger = logging.getLogger(__name__)
    
    def register_engine(
        self,
        engine: TranslationEngine,
        is_default: bool = False,
        is_fallback: bool = False,
        priority: int = 0
    ) -> Result[bool, AppError]:
        """Register a translation engine."""
        try:
            registration = self._create_registration(engine, is_default, is_fallback, priority)
            self._registry.register(registration)
            self._event_bus.publish(
                "engine_registered", {"engine_name": engine.name}
            )
            return Success(True)
        except ValueError as e:
            return Failure(AppError(error_code="REGISTRATION_FAILED", message=str(e)))

    def _create_registration(
        self, engine: TranslationEngine, is_default: bool, 
        is_fallback: bool, priority: int
    ) -> EngineRegistration:
        """Create engine registration."""
        return EngineRegistration(
            engine=engine, is_default=is_default,
            is_fallback=is_fallback, priority=priority
        )
    
    async def translate_async(
            self, text: SourceText, direction: TranslationDirection,
            preferred_engine: Optional[str] = None, use_cache: bool = True,
            use_fallback: bool = True
        ) -> Result[TranslationResult, AppError]:
            """Translate text with best engine."""
            if not str(text).strip():
                return Failure(AppError(error_code="EMPTY_TEXT", message="Input text cannot be empty."))
            request = self._create_request(text, direction, preferred_engine)
            return await self._translate_with_pipeline(request, use_cache, use_fallback)

    
    async def _translate_with_pipeline(
        self,
        request: TranslationRequest,
        use_cache: bool,
        use_fallback: bool
    ) -> Result[TranslationResult, AppError]:
        """Execute translation pipeline."""
        result = await self._check_cache_or_translate(request, use_cache, use_fallback)
        await self._cache_if_needed(request, result, use_cache)
        return result
    
    async def _check_cache_or_translate(
        self, request: TranslationRequest, use_cache: bool, use_fallback: bool
    ) -> Result[TranslationResult, AppError]:
        """Check cache or perform translation."""
        result = await self._try_cached_translation(request, use_cache)
        if is_successful(result):
            return result
        return await self._perform_translation(request, use_fallback)
    
    async def _cache_if_needed(
        self,
        request: TranslationRequest,
        result: Result[TranslationResult, AppError],
        use_cache: bool
    ):
        """Cache result if successful and caching enabled."""
        if is_successful(result) and use_cache:
            await self._cache_result_async(request, result.unwrap())
    
    def _create_request(
        self,
        text: SourceText,
        direction: TranslationDirection,
        preferred_engine: Optional[str]
    ) -> TranslationRequest:
        """Create translation request."""
        return TranslationRequest(
            text=text, direction=direction, preferred_engine=preferred_engine
        )
    
    async def _try_cached_translation(
        self,
        request: TranslationRequest,
        use_cache: bool
    ) -> Result[TranslationResult, AppError]:
        """Try to get cached translation."""
        if use_cache:
            return await self._try_cache_async(request)
        return Failure(AppError(error_code="CACHE_DISABLED", message="Cache not used"))
    
    async def _perform_translation(
            self, request: TranslationRequest, use_fallback: bool
        ) -> Result[TranslationResult, AppError]:
            """Perform translation with optional fallback."""
            result = await self._select_and_translate_async(request)

            if isinstance(result, Failure) and use_fallback:
                error = result.failure()
                if error.error_code in ["LOW_CONFIDENCE", "TRANSLATION_ERROR"]:
                    self.logger.info(f"Primary translation failed ({error.error_code}), attempting fallback.")
                    return await self._try_fallback_async(request)

            return result

    
    def _should_try_fallback(self, result: Result[TranslationResult, AppError], use_fallback: bool) -> bool:
        """
        Note: This is a pure function (no side effects).
        Check if fallback should be attempted."""
        return isinstance(result, Failure) and use_fallback
    
    def _init_strategies(self) -> List[EngineSelectionStrategy]:
        """
        Note: This is a pure function (no side effects).
        Initialize selection strategies in priority order."""
        return [
            PreferredEngineStrategy(),
            DefaultEngineStrategy(),
            BestAvailableStrategy()
        ]
    
    async def _try_cache_async(self, request: TranslationRequest) -> Result[TranslationResult, AppError]:
        """
        Note: This is a pure function (no side effects).
        Try to get result from cache."""
        cache_key = self._cache_key_generator.generate(request)
        cached = await self._cache.get_async(cache_key)
        
        if cached:
            self._publish_cache_hit()
            return Success(cached)
        
        return Failure(AppError(error_code="CACHE_MISS", message="No cached result"))
    
    def _publish_cache_hit(self):
        """
        Note: This is a pure function (no side effects).
        Publish cache hit metrics."""
        metrics = TranslationMetrics(
            engine_name="cache",
            duration_ms=0.0,
            success=True,
            cache_hit=True
        )
        self._event_publisher.publish_completed(metrics)
    
    async def _select_and_translate_async(
        self,
        request: TranslationRequest
    ) -> Result[TranslationResult, AppError]:
        """Select engine and translate."""
        engine_result = self._select_engine(request)

        if isinstance(engine_result, Failure):
            return engine_result

        engine = engine_result.unwrap()
        return await self._execute_translation_async(engine, request)

    def _select_engine(self, request: TranslationRequest) -> Result[TranslationEngine, AppError]:
        """
        Note: This is a pure function (no side effects).
        Select engine using strategies."""
        for strategy in self._selection_strategies:
            result = strategy.select(self._registry.get_all(), request)
            if is_successful(result):
                return result
        
        return Failure(AppError(error_code="NO_ENGINE_AVAILABLE", message="No engine could handle the request"))
    
    async def _execute_translation_async(
        self,
        engine: TranslationEngine,
        request: TranslationRequest
    ) -> Result[TranslationResult, AppError]:
        """Execute translation with engine."""
        start_time = self._start_translation(engine, request)
        result = await self._safe_translate(engine, request)
        self._publish_result(engine.name, start_time, result)
        return result
    
    def _start_translation(self, engine: TranslationEngine, request: TranslationRequest) -> float:
        """
        Note: This is a pure function (no side effects).
        Start translation and return start time."""
        self._event_publisher.publish_started(engine.name, request)
        return time.time()
    
    async def _safe_translate(
        self, engine: TranslationEngine, request: TranslationRequest
    ) -> Result[TranslationResult, AppError]:
        """Safely execute translation."""
        try:
            return await self._run_engine_translation(engine, request)
        except Exception as e:
            return self._handle_translation_error(engine.name, e)
    
    def _handle_translation_error(self, engine_name: str, error: Exception) -> Result[TranslationResult, AppError]:
        """
        Note: This is a pure function (no side effects).
        Handle translation error."""
        self._event_publisher.publish_failed(engine_name, str(error))
        return Failure(AppError(error_code="TRANSLATION_ERROR", message=f"Engine error: {str(error)}"))
    
    def _publish_result(
        self,
        engine_name: str,
        start_time: float,
        result: Result[TranslationResult, AppError]
    ):
        """Publish translation result metrics."""
        if is_successful(result):
            metrics = self._create_metrics(engine_name, start_time, result.unwrap())
            self._event_publisher.publish_completed(metrics)
    
    async def _run_engine_translation(
        self,
        engine: TranslationEngine,
        request: TranslationRequest
    ) -> Result[TranslationResult, AppError]:
        """Run the actual translation."""
        # Note: We now correctly call the async version of the engine's translate method.
        return await engine.translate_async(request.text, request.direction)
    
    def _create_metrics(
        self, engine_name: str, start_time: float, result: TranslationResult
    ) -> TranslationMetrics:
        """Create metrics from translation result."""
        return TranslationMetrics(
            engine_name=engine_name,
            duration_ms=self._calculate_duration_ms(start_time),
            success=result.success,
            confidence=self._get_confidence(result)
        )
    
    def _calculate_duration_ms(self, start_time: float) -> float:
        """
        Note: This is a pure function (no side effects).
        Calculate duration in milliseconds."""
        return (time.time() - start_time) * 1000
    
    def _get_confidence(self, result: TranslationResult) -> float:
        """
        Note: This is a pure function (no side effects).
        Get confidence from result."""
        return result.confidence if result.success else 0.0
    

    
    async def _try_fallback_async(self, request: TranslationRequest) -> Result[TranslationResult, AppError]:
        """
        Note: This is a pure function (no side effects).
        Try fallback engines."""
        engines = self._get_capable_fallback_engines(request)
        
        for engine in engines:
            result = await self._execute_translation_async(engine, request)
            if is_successful(result):
                return result
        
        return Failure(AppError(error_code="ALL_ENGINES_FAILED", message="All fallback engines failed"))
    
    def _get_capable_fallback_engines(
        self,
        request: TranslationRequest
    ) -> List[TranslationEngine]:
        """Get fallback engines capable of handling request."""
        return [
            engine for engine in self._registry.get_fallback_engines()
            if engine.can_translate(request.text, request.direction)
        ]
    
    async def _cache_result_async(self, request: TranslationRequest, result: TranslationResult):
        """
        Note: This is a pure function (no side effects).
        Cache successful result."""
        cache_key = self._cache_key_generator.generate(request)
        await self._cache.set_async(cache_key, result, ttl_seconds=3600)