"""
Translation Manager - Refactored for minimal complexity.
Orchestrates multiple translation engines with clean architecture.
"""

import logging
import time
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from ..core.domain_types import (
    SourceText, TargetText, Result, Success, Failure, AppError
)
from ..core.functional_utils import guard, guard_not_none
from .base import TranslationEngine, TranslationResult, TranslationDirection
from ..core.interfaces import IEventBus, ICacheRepository


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
        
        for reg in engines:
            if reg.engine.name == request.preferred_engine:
                if reg.engine.can_translate(request.text, request.direction):
                    return Success(reg.engine)
                return Failure(AppError(
                    error_code="ENGINE_CANNOT_TRANSLATE",
                    message=f"Engine {request.preferred_engine} cannot handle request"
                ))
        
        return Failure(AppError(
            error_code="ENGINE_NOT_FOUND",
            message=f"Engine {request.preferred_engine} not found"
        ))


class DefaultEngineStrategy(EngineSelectionStrategy):
    """Select default engine."""
    
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Select default engine."""
        for reg in engines:
            if reg.is_default and reg.engine.can_translate(request.text, request.direction):
                return Success(reg.engine)
        
        return Failure(AppError(error_code="NO_DEFAULT_ENGINE", message="No default engine available"))


class BestAvailableStrategy(EngineSelectionStrategy):
    """Select best available engine by priority."""
    
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine, AppError]:
        """Select highest priority engine that can handle request."""
        sorted_engines = sorted(engines, key=lambda r: r.priority, reverse=True)
        
        for reg in sorted_engines:
            if reg.engine.can_translate(request.text, request.direction):
                return Success(reg.engine)
        
        return Failure(AppError(error_code="NO_SUITABLE_ENGINE", message="No engine can handle this request"))


# Cache Key Generator
class CacheKeyGenerator:
    """Generates cache keys for translations."""
    
    @staticmethod
    def generate(request: TranslationRequest) -> str:
        """Generate cache key for request."""
        import hashlib
        
        key_parts = [
            str(request.text),
            request.direction.value,
            request.preferred_engine or "any"
        ]
        
        key_string = "|".join(key_parts)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        
        return f"{ManagerConstants.CACHE_KEY_PREFIX}_{request.direction.value}_{key_hash}"


# Event Publisher
class TranslationEventPublisher:
    """Publishes translation events."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus

    async def publish_started(self, engine_name: str, request: TranslationRequest):
        """Publish translation started event."""
        await self._event_bus.publish_event_async(
            event_type="translation.started",
            data={
                "engine": engine_name,
                "direction": request.direction.value,
                "text_length": len(request.text)
            }
        )

    async def publish_completed(self, metrics: TranslationMetrics):
        """Publish translation completed event."""
        await self._event_bus.publish_event_async(
            event_type="translation.completed",
            data={
                "engine": metrics.engine_name,
                "success": metrics.success,
                "duration_ms": metrics.duration_ms,
                "confidence": metrics.confidence,
                "cache_hit": metrics.cache_hit
            }
        )

    async def publish_failed(self, engine_name: str, error: str):
        """Publish translation failed event."""
        await self._event_bus.publish_event_async(
            event_type="translation.failed",
            data={
                "engine": engine_name,
                "error": error
            }
        )


# Engine Registry
class EngineRegistry:
    """Manages registered engines."""
    
    def __init__(self):
        self._registrations: List[EngineRegistration] = []
        self._engines_by_name: Dict[str, TranslationEngine] = {}
    
    def register(self, registration: EngineRegistration) -> Result[None, AppError]:
        """Register an engine."""
        engine = registration.engine
        
        # Validate
        if engine.name in self._engines_by_name:
            return Failure(AppError(error_code="DUPLICATE_ENGINE", message=f"Engine {engine.name} already registered"))
        
        # Add to registry
        self._registrations.append(registration)
        self._engines_by_name[engine.name] = engine
        
        return Success(None)
    
    def get_all(self) -> List[EngineRegistration]:
        """Get all registrations."""
        return self._registrations.copy()
    
    def get_by_name(self, name: str) -> Optional[TranslationEngine]:
        """Get engine by name."""
        return self._engines_by_name.get(name)
    
    def get_fallback_engines(self) -> List[TranslationEngine]:
        """Get fallback engines."""
        return [r.engine for r in self._registrations if r.is_fallback]


# Main Translation Manager
class TranslationManager:
    """Orchestrates translation operations with minimal complexity."""
    
    def __init__(
        self,
        cache_repository: ICacheRepository,
        event_bus: IEventBus,
        selection_strategies: Optional[List[EngineSelectionStrategy]] = None,
        fallback_enabled: bool = True,
        confidence_threshold: float = ManagerConstants.DEFAULT_CONFIDENCE_THRESHOLD
    ):
        """Initialize manager."""
        self._registry = EngineRegistry()
        self._cache = cache_repository
        self._event_publisher = TranslationEventPublisher(event_bus)
        self._confidence_threshold = confidence_threshold
        self._cache_key_generator = CacheKeyGenerator()
        self._selection_strategies = selection_strategies if selection_strategies else self._init_strategies()
        self._fallback_enabled = fallback_enabled
        self.logger = logging.getLogger(__name__)
    
    def register_engine(
        self,
        engine: TranslationEngine,
        is_default: bool = False,
        is_fallback: bool = False,
        priority: int = 0
    ) -> Result[None, AppError]:
        """Register a translation engine."""
        registration = EngineRegistration(
            engine=engine,
            is_default=is_default,
            is_fallback=is_fallback,
            priority=priority
        )
        
        return self._registry.register(registration)
    
    async def translate_async(
        self,
        text: SourceText,
        direction: TranslationDirection,
        preferred_engine: Optional[str] = None,
        use_cache: bool = True,
        use_fallback: bool = True
    ) -> Result[TranslationResult, AppError]:
        """Translate text with best engine."""
        # Guard clause: If no engines are registered, fail fast.
        if not self._registry.get_all():
            return Failure(AppError(error_code="NO_ENGINE_AVAILABLE", message="No translation engines are registered."))

        request = self._create_request(text, direction, preferred_engine)

        # Pipeline: cache -> translate -> fallback -> cache result
        result = await self._try_cached_translation(request, use_cache)
        if isinstance(result, Success):
            return result

        result = await self._perform_translation(request, use_fallback)

        if isinstance(result, Success) and use_cache:
            await self._cache_result_async(request, result.unwrap())

        return result
    
    def _create_request(
        self,
        text: SourceText,
        direction: TranslationDirection,
        preferred_engine: Optional[str]
    ) -> TranslationRequest:
        """Create translation request."""
        return TranslationRequest(
            text=text,
            direction=direction,
            preferred_engine=preferred_engine
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
        self,
        request: TranslationRequest,
        use_fallback: bool
    ) -> Result[TranslationResult, AppError]:
        """Perform translation with optional fallback."""
        result = await self._select_and_translate_async(request)
        
        if isinstance(result, Failure) and use_fallback:
            result = await self._try_fallback_async(request)
        
        return result
    
    def _init_strategies(self) -> List[EngineSelectionStrategy]:
        """Initialize selection strategies in priority order."""
        return [
            PreferredEngineStrategy(),
            DefaultEngineStrategy(),
            BestAvailableStrategy()
        ]
    
    async def _try_cache_async(self, request: TranslationRequest) -> Result[TranslationResult, AppError]:
        """Try to get result from cache."""
        cache_key = self._cache_key_generator.generate(request)
        
        cached_result_container = await self._cache.get_cached_value_async(cache_key)

        if isinstance(cached_result_container, Failure):
            return cached_result_container  # Propagate cache error

        # Now we know it's a Success object
        cached_value = cached_result_container.unwrap()

        if cached_value is not None:
            # Cache HIT
            metrics = TranslationMetrics(
                engine_name="cache",
                duration_ms=0.0,
                success=True,
                cache_hit=True
            )
            await self._event_publisher.publish_completed(metrics)
            # The cached value is the TranslationResult. The function needs to return
            # a Result object, so we wrap it in Success.
            return Success(cached_value)
        else:
            # Cache MISS
            return Failure(AppError(error_code="CACHE_MISS", message="No cached result"))
    
    async def _select_and_translate_async(
        self,
        request: TranslationRequest
    ) -> Result[TranslationResult, AppError]:
        """Select engine and translate."""
        # Try each strategy
        for strategy in self._selection_strategies:
            engine_result = strategy.select(self._registry.get_all(), request)
            if isinstance(engine_result, Success):
                return await self._execute_translation_async(
                    engine_result.unwrap(), request
                )
        
        return Failure(AppError(error_code="NO_ENGINE_AVAILABLE", message="No engine could handle the request"))
    
    async def _execute_translation_async(
        self,
        engine: TranslationEngine,
        request: TranslationRequest
    ) -> Result[TranslationResult, AppError]:
        """Execute translation with engine."""
        start_time = time.time()
        await self._event_publisher.publish_started(engine.name, request)
        
        try:
            result = await self._run_engine_translation(engine, request)
            metrics = self._create_metrics(engine.name, start_time, result)
            await self._event_publisher.publish_completed(metrics)
            return self._process_translation_result(result)
        except Exception as e:
            await self._event_publisher.publish_failed(engine.name, str(e))
            return Failure(AppError(error_code="TRANSLATION_ERROR", message=f"Engine error: {str(e)}"))
    
    async def _run_engine_translation(
        self,
        engine: TranslationEngine,
        request: TranslationRequest
    ) -> TranslationResult:
        """Run the actual translation, calling the async method on the engine."""
        engine_result = await engine.translate_async(request.text, request.direction)
        if isinstance(engine_result, Success):
            return engine_result.unwrap()
        else:
            # Raise an exception to be caught by the caller, which expects exceptions for failures
            raise RuntimeError(f"Engine translation failed: {engine_result.failure()}")
    
    def _create_metrics(
        self,
        engine_name: str,
        start_time: float,
        result: TranslationResult
    ) -> TranslationMetrics:
        """Create metrics from translation result."""
        return TranslationMetrics(
            engine_name=engine_name,
            duration_ms=(time.time() - start_time) * 1000,
            success=result.success,
            confidence=result.confidence if result.success else 0.0
        )
    
    def _process_translation_result(self, result: TranslationResult) -> Result[TranslationResult, AppError]:
        """Process translation result."""
        if result.success:
            return Success(result)
        return Failure(AppError(error_code="TRANSLATION_FAILED", message=result.error_message or "Unknown error"))
    
    async def _try_fallback_async(self, request: TranslationRequest) -> Result[TranslationResult, AppError]:
        """Try fallback engines."""
        fallback_engines = self._registry.get_fallback_engines()
        
        for engine in fallback_engines:
            if engine.can_translate(request.text, request.direction):
                result = await self._execute_translation_async(engine, request)
                if isinstance(result, Success):
                    return result
        
        return Failure(AppError(error_code="ALL_ENGINES_FAILED", message="All fallback engines failed"))
    
    async def _cache_result_async(self, request: TranslationRequest, result: TranslationResult):
        """Cache successful result."""
        cache_key = self._cache_key_generator.generate(request)
        await self._cache.set_cached_value_async(cache_key, result, ttl_seconds=3600)