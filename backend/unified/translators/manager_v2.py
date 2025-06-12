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
    SourceText, TargetText, Result, Success, Failure,
    success, failure
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
    ) -> Result[TranslationEngine]:
        """Select an engine for the request."""
        pass


class PreferredEngineStrategy(EngineSelectionStrategy):
    """Select preferred engine if available."""
    
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine]:
        """Select preferred engine."""
        if not request.preferred_engine:
            return failure("NO_PREFERENCE", "No preferred engine specified")
        
        for reg in engines:
            if reg.engine.name == request.preferred_engine:
                if reg.engine.can_translate(request.text, request.direction):
                    return success(reg.engine)
                return failure("ENGINE_CANNOT_TRANSLATE", 
                             f"Engine {request.preferred_engine} cannot handle request")
        
        return failure("ENGINE_NOT_FOUND", f"Engine {request.preferred_engine} not found")


class DefaultEngineStrategy(EngineSelectionStrategy):
    """Select default engine."""
    
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine]:
        """Select default engine."""
        for reg in engines:
            if reg.is_default and reg.engine.can_translate(request.text, request.direction):
                return success(reg.engine)
        
        return failure("NO_DEFAULT_ENGINE", "No default engine available")


class BestAvailableStrategy(EngineSelectionStrategy):
    """Select best available engine by priority."""
    
    def select(
        self,
        engines: List[EngineRegistration],
        request: TranslationRequest
    ) -> Result[TranslationEngine]:
        """Select highest priority engine that can handle request."""
        sorted_engines = sorted(engines, key=lambda r: r.priority, reverse=True)
        
        for reg in sorted_engines:
            if reg.engine.can_translate(request.text, request.direction):
                return success(reg.engine)
        
        return failure("NO_SUITABLE_ENGINE", "No engine can handle this request")


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
    
    def publish_started(self, engine_name: str, request: TranslationRequest):
        """Publish translation started event."""
        self._event_bus.publish({
            "type": "translation.started",
            "engine": engine_name,
            "direction": request.direction.value,
            "text_length": len(request.text)
        })
    
    def publish_completed(self, metrics: TranslationMetrics):
        """Publish translation completed event."""
        self._event_bus.publish({
            "type": "translation.completed",
            "engine": metrics.engine_name,
            "success": metrics.success,
            "duration_ms": metrics.duration_ms,
            "confidence": metrics.confidence,
            "cache_hit": metrics.cache_hit
        })
    
    def publish_failed(self, engine_name: str, error: str):
        """Publish translation failed event."""
        self._event_bus.publish({
            "type": "translation.failed",
            "engine": engine_name,
            "error": error
        })


# Engine Registry
class EngineRegistry:
    """Manages registered engines."""
    
    def __init__(self):
        self._registrations: List[EngineRegistration] = []
        self._engines_by_name: Dict[str, TranslationEngine] = {}
    
    def register(self, registration: EngineRegistration) -> Result[None]:
        """Register an engine."""
        engine = registration.engine
        
        # Validate
        if engine.name in self._engines_by_name:
            return failure("DUPLICATE_ENGINE", f"Engine {engine.name} already registered")
        
        # Add to registry
        self._registrations.append(registration)
        self._engines_by_name[engine.name] = engine
        
        return success(None)
    
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
        event_bus: IEventBus,
        cache_repository: ICacheRepository,
        confidence_threshold: float = ManagerConstants.DEFAULT_CONFIDENCE_THRESHOLD
    ):
        """Initialize manager."""
        self._registry = EngineRegistry()
        self._cache = cache_repository
        self._event_publisher = TranslationEventPublisher(event_bus)
        self._confidence_threshold = confidence_threshold
        self._cache_key_generator = CacheKeyGenerator()
        self._selection_strategies = self._init_strategies()
        self.logger = logging.getLogger(__name__)
    
    def register_engine(
        self,
        engine: TranslationEngine,
        is_default: bool = False,
        is_fallback: bool = False,
        priority: int = 0
    ) -> Result[None]:
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
    ) -> Result[TranslationResult]:
        """Translate text with best engine."""
        request = self._create_request(text, direction, preferred_engine)
        
        # Pipeline: cache -> translate -> fallback -> cache result
        result = await self._try_cached_translation(request, use_cache)
        if isinstance(result, Success):
            return result
            
        result = await self._perform_translation(request, use_fallback)
        
        if isinstance(result, Success) and use_cache:
            await self._cache_result_async(request, result.value)
        
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
    ) -> Result[TranslationResult]:
        """Try to get cached translation."""
        if use_cache:
            return await self._try_cache_async(request)
        return failure("CACHE_DISABLED", "Cache not used")
    
    async def _perform_translation(
        self,
        request: TranslationRequest,
        use_fallback: bool
    ) -> Result[TranslationResult]:
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
    
    async def _try_cache_async(self, request: TranslationRequest) -> Result[TranslationResult]:
        """Try to get result from cache."""
        cache_key = self._cache_key_generator.generate(request)
        
        cached = await self._cache.get_async(cache_key)
        if cached:
            metrics = TranslationMetrics(
                engine_name="cache",
                duration_ms=0.0,
                success=True,
                cache_hit=True
            )
            self._event_publisher.publish_completed(metrics)
            return success(cached)
        
        return failure("CACHE_MISS", "No cached result")
    
    async def _select_and_translate_async(
        self,
        request: TranslationRequest
    ) -> Result[TranslationResult]:
        """Select engine and translate."""
        # Try each strategy
        for strategy in self._selection_strategies:
            engine_result = strategy.select(self._registry.get_all(), request)
            if isinstance(engine_result, Success):
                return await self._execute_translation_async(
                    engine_result.value, request
                )
        
        return failure("NO_ENGINE_AVAILABLE", "No engine could handle the request")
    
    async def _execute_translation_async(
        self,
        engine: TranslationEngine,
        request: TranslationRequest
    ) -> Result[TranslationResult]:
        """Execute translation with engine."""
        start_time = time.time()
        self._event_publisher.publish_started(engine.name, request)
        
        try:
            result = await self._run_engine_translation(engine, request)
            metrics = self._create_metrics(engine.name, start_time, result)
            self._event_publisher.publish_completed(metrics)
            return self._process_translation_result(result)
        except Exception as e:
            self._event_publisher.publish_failed(engine.name, str(e))
            return failure("TRANSLATION_ERROR", f"Engine error: {str(e)}")
    
    async def _run_engine_translation(
        self,
        engine: TranslationEngine,
        request: TranslationRequest
    ) -> TranslationResult:
        """Run the actual translation."""
        # Note: engine.translate is synchronous
        return engine.translate(request.text, request.direction)
    
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
    
    def _process_translation_result(self, result: TranslationResult) -> Result[TranslationResult]:
        """Process translation result."""
        if result.success:
            return success(result)
        return failure("TRANSLATION_FAILED", result.error_message or "Unknown error")
    
    async def _try_fallback_async(self, request: TranslationRequest) -> Result[TranslationResult]:
        """Try fallback engines."""
        fallback_engines = self._registry.get_fallback_engines()
        
        for engine in fallback_engines:
            if engine.can_translate(request.text, request.direction):
                result = await self._execute_translation_async(engine, request)
                if isinstance(result, Success):
                    return result
        
        return failure("ALL_ENGINES_FAILED", "All fallback engines failed")
    
    async def _cache_result_async(self, request: TranslationRequest, result: TranslationResult):
        """Cache successful result."""
        cache_key = self._cache_key_generator.generate(request)
        await self._cache.set_async(cache_key, result, ttl_seconds=3600)