"""
Translation Manager - Refactored with Orchestrator Pattern.

Orchestrates multiple translation engines with clear separation of concerns.
Follows Rule 2: Structure for Scannability via Orchestrator Methods.

Copyright: DarkLightX/Dana Edwards
"""

import logging
import time
from typing import List, Optional, Dict, Any, Set
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass
from enum import Enum

from ..core.domain_types import (
    SourceText, TargetText, Result, Success, Failure,
    TranslationId, EngineType
)
from .base import TranslationEngine, TranslationResult, TranslationDirection
from ..core.interfaces import IEventBus, ICacheRepository


@dataclass
class EngineSelectionCriteria:
    """Criteria for selecting translation engines."""
    direction: TranslationDirection
    text_length: int
    required_confidence: float
    preferred_engine: Optional[str] = None
    exclude_engines: Set[str] = None


@dataclass
class TranslationStatistics:
    """Statistics for translation operations."""
    total_count: int = 0
    successful_count: int = 0
    failed_count: int = 0
    engine_usage: Dict[str, int] = None
    average_time: float = 0.0
    
    def __post_init__(self):
        if self.engine_usage is None:
            self.engine_usage = {}


class TranslationManager:
    """
    Manages multiple translation engines with clear orchestration.
    Rule 2: Public methods are high-level orchestrators.
    """
    
    def __init__(
        self,
        event_bus: IEventBus,
        cache_repository: ICacheRepository,
        confidence_threshold: float = 0.7
    ):
        """Initialize with injected dependencies."""
        self._engines: List[TranslationEngine] = []
        self._default_engine: Optional[TranslationEngine] = None
        self._fallback_engines: List[TranslationEngine] = []
        self._event_bus = event_bus
        self._cache = cache_repository
        self._confidence_threshold = confidence_threshold
        self._statistics = TranslationStatistics()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self.logger = logging.getLogger(__name__)
    
    def register_translation_engine(
        self,
        engine: TranslationEngine,
        is_default: bool = False,
        is_fallback: bool = False
    ) -> Result[None]:
        """
        Register a translation engine with the manager.
        Rule 2: High-level orchestration of registration process.
        """
        # Validate engine
        validation_result = self._validate_engine_registration(engine)
        if isinstance(validation_result, Failure):
            return validation_result
        
        # Add to appropriate collections
        self._add_engine_to_collections(engine, is_default, is_fallback)
        
        # Initialize engine statistics
        self._initialize_engine_statistics(engine)
        
        # Publish registration event
        self._publish_engine_event("engine_registered", engine)
        
        return Success(None)
    
    async def translate_text_with_best_engine_async(
        self,
        text: SourceText,
        direction: TranslationDirection,
        engine_name: Optional[str] = None,
        use_fallback: bool = True
    ) -> Result[TranslationResult]:
        """
        Translate text using the best available engine.
        Rule 1: Name explicitly indicates async translation with best engine.
        Rule 2: Clear orchestration of translation process.
        """
        start_time = time.time()
        
        # Validate input
        validation_result = self._validate_translation_input(text, direction)
        if isinstance(validation_result, Failure):
            return validation_result
        
        # Check cache first
        cache_result = await self._check_translation_cache_async(text, direction)
        if cache_result and cache_result.success:
            return Success(cache_result.value)
        
        # Select appropriate engine
        criteria = self._create_selection_criteria(text, direction, engine_name)
        engine_result = self._select_translation_engine(criteria)
        
        if isinstance(engine_result, Failure):
            return engine_result
        
        selected_engine = engine_result.value
        
        # Attempt translation with selected engine
        translation_result = await self._execute_translation_async(
            selected_engine, text, direction
        )
        
        # Try fallback engines if needed
        if not translation_result.success and use_fallback:
            translation_result = await self._attempt_fallback_translation_async(
                text, direction, selected_engine
            )
        
        # Update statistics and cache
        self._update_translation_statistics(translation_result, time.time() - start_time)
        
        if translation_result.success:
            await self._cache_translation_result_async(text, direction, translation_result)
        
        # Publish translation event
        await self._publish_translation_event_async(translation_result)
        
        return Success(translation_result)
    
    async def translate_with_multiple_engines_async(
        self,
        text: SourceText,
        direction: TranslationDirection,
        min_engines: int = 2
    ) -> Result[List[TranslationResult]]:
        """
        Translate using multiple engines in parallel.
        Rule 1: Name indicates parallel translation with multiple engines.
        Rule 2: Orchestrates parallel execution.
        """
        # Get available engines
        available_engines = self._get_engines_for_direction(direction)
        
        if len(available_engines) < min_engines:
            return Failure(
                "INSUFFICIENT_ENGINES",
                f"Need at least {min_engines} engines, found {len(available_engines)}"
            )
        
        # Create translation tasks
        tasks = self._create_parallel_translation_tasks(
            available_engines, text, direction
        )
        
        # Execute in parallel and collect results
        results = await self._execute_parallel_translations_async(tasks)
        
        # Sort by confidence
        sorted_results = self._sort_results_by_confidence(results)
        
        # Publish comparison event
        await self._publish_comparison_event_async(sorted_results)
        
        return Success(sorted_results)
    
    def get_engine_statistics_for_reporting(self) -> Dict[str, Any]:
        """
        Get comprehensive engine statistics for reporting.
        Rule 1: Name indicates statistics retrieval for reporting purpose.
        """
        return {
            "total_translations": self._statistics.total_count,
            "successful_translations": self._statistics.successful_count,
            "failed_translations": self._statistics.failed_count,
            "success_rate": self._calculate_success_rate(),
            "engine_usage": self._format_engine_usage_stats(),
            "average_translation_time": self._statistics.average_time,
            "available_engines": self._get_engine_availability_status()
        }
    
    # --- Private Implementation Methods (Rule 2) ---
    
    def _validate_engine_registration(self, engine: TranslationEngine) -> Result[None]:
        """Validate engine before registration."""
        if not engine.name:
            return Failure("INVALID_ENGINE", "Engine must have a name")
        
        if any(e.name == engine.name for e in self._engines):
            return Failure("DUPLICATE_ENGINE", f"Engine '{engine.name}' already registered")
        
        return Success(None)
    
    def _add_engine_to_collections(
        self,
        engine: TranslationEngine,
        is_default: bool,
        is_fallback: bool
    ) -> None:
        """Add engine to appropriate collections."""
        self._engines.append(engine)
        
        if is_default:
            self._default_engine = engine
            
        if is_fallback:
            self._fallback_engines.append(engine)
    
    def _initialize_engine_statistics(self, engine: TranslationEngine) -> None:
        """Initialize statistics tracking for engine."""
        self._statistics.engine_usage[engine.name] = 0
    
    def _publish_engine_event(self, event_type: str, engine: TranslationEngine) -> None:
        """Publish engine-related event."""
        # Sync method, so we schedule async publish
        import asyncio
        asyncio.create_task(
            self._event_bus.publish_event_async(
                f"translation.{event_type}",
                {"engine_name": engine.name, "engine_type": engine.description}
            )
        )
    
    def _validate_translation_input(
        self,
        text: SourceText,
        direction: TranslationDirection
    ) -> Result[None]:
        """Validate translation input parameters."""
        if not text or not text.strip():
            return Failure("EMPTY_INPUT", "Input text cannot be empty")
        
        if len(text) > 100000:  # 100KB limit
            return Failure("TEXT_TOO_LONG", "Input text exceeds maximum length")
        
        return Success(None)
    
    async def _check_translation_cache_async(
        self,
        text: SourceText,
        direction: TranslationDirection
    ) -> Optional[TranslationResult]:
        """Check cache for existing translation."""
        cache_key = self._generate_cache_key(text, direction)
        cache_result = await self._cache.get_cached_value_async(cache_key)
        
        if cache_result.success and cache_result.value:
            self.logger.debug(f"Cache hit for translation: {cache_key}")
            return cache_result.value
            
        return None
    
    def _create_selection_criteria(
        self,
        text: SourceText,
        direction: TranslationDirection,
        engine_name: Optional[str]
    ) -> EngineSelectionCriteria:
        """Create criteria for engine selection."""
        return EngineSelectionCriteria(
            direction=direction,
            text_length=len(text),
            required_confidence=self._confidence_threshold,
            preferred_engine=engine_name
        )
    
    def _select_translation_engine(
        self,
        criteria: EngineSelectionCriteria
    ) -> Result[TranslationEngine]:
        """Select best engine based on criteria."""
        # If specific engine requested
        if criteria.preferred_engine:
            engine = self._get_engine_by_name(criteria.preferred_engine)
            if not engine:
                return Failure(
                    "ENGINE_NOT_FOUND",
                    f"Engine '{criteria.preferred_engine}' not found"
                )
            if not engine.is_available:
                return Failure(
                    "ENGINE_UNAVAILABLE",
                    f"Engine '{criteria.preferred_engine}' is not available"
                )
            return Success(engine)
        
        # Find best available engine
        available_engines = self._get_engines_for_direction(criteria.direction)
        
        if not available_engines:
            return Failure(
                "NO_ENGINES_AVAILABLE",
                f"No engines available for direction: {criteria.direction.value}"
            )
        
        # Prefer default engine if available
        if self._default_engine and self._default_engine in available_engines:
            return Success(self._default_engine)
        
        # Return first available
        return Success(available_engines[0])
    
    async def _execute_translation_async(
        self,
        engine: TranslationEngine,
        text: SourceText,
        direction: TranslationDirection
    ) -> TranslationResult:
        """Execute translation with specific engine."""
        try:
            # If engine has async method, use it
            if hasattr(engine, 'translate_async'):
                return await engine.translate_async(text, direction)
            else:
                # Run sync method in thread pool
                import asyncio
                return await asyncio.to_thread(
                    engine.translate, text, direction
                )
        except Exception as e:
            self.logger.error(f"Translation error with {engine.name}: {e}")
            return TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method=engine.name,
                direction=direction,
                error_message=str(e),
                confidence=0.0
            )
    
    async def _attempt_fallback_translation_async(
        self,
        text: SourceText,
        direction: TranslationDirection,
        failed_engine: TranslationEngine
    ) -> TranslationResult:
        """Attempt translation with fallback engines."""
        for fallback_engine in self._fallback_engines:
            if fallback_engine != failed_engine:
                self.logger.info(f"Trying fallback engine: {fallback_engine.name}")
                
                result = await self._execute_translation_async(
                    fallback_engine, text, direction
                )
                
                if result.success:
                    result.metadata["used_fallback"] = True
                    result.metadata["original_engine"] = failed_engine.name
                    return result
        
        # All fallbacks failed
        return TranslationResult(
            success=False,
            translated_text="",
            original_text=text,
            translation_method="none",
            direction=direction,
            error_message="All engines failed",
            confidence=0.0
        )
    
    def _update_translation_statistics(
        self,
        result: TranslationResult,
        elapsed_time: float
    ) -> None:
        """Update translation statistics."""
        self._statistics.total_count += 1
        
        if result.success:
            self._statistics.successful_count += 1
            self._statistics.engine_usage[result.translation_method] = \
                self._statistics.engine_usage.get(result.translation_method, 0) + 1
        else:
            self._statistics.failed_count += 1
        
        # Update average time
        current_avg = self._statistics.average_time
        self._statistics.average_time = (
            (current_avg * (self._statistics.total_count - 1) + elapsed_time) /
            self._statistics.total_count
        )
    
    async def _cache_translation_result_async(
        self,
        text: SourceText,
        direction: TranslationDirection,
        result: TranslationResult
    ) -> None:
        """Cache successful translation result."""
        cache_key = self._generate_cache_key(text, direction)
        await self._cache.set_cached_value_async(
            cache_key,
            result,
            ttl_seconds=3600  # 1 hour
        )
    
    async def _publish_translation_event_async(
        self,
        result: TranslationResult
    ) -> None:
        """Publish translation completion event."""
        await self._event_bus.publish_event_async(
            "translation.completed",
            {
                "success": result.success,
                "engine": result.translation_method,
                "direction": result.direction.value,
                "confidence": result.confidence,
                "processing_time": result.processing_time
            }
        )
    
    def _get_engine_by_name(self, name: str) -> Optional[TranslationEngine]:
        """Get engine by name."""
        return next((e for e in self._engines if e.name == name), None)
    
    def _get_engines_for_direction(
        self,
        direction: TranslationDirection
    ) -> List[TranslationEngine]:
        """Get engines that support given direction."""
        return [
            engine for engine in self._engines
            if engine.is_available and direction in engine.get_supported_directions()
        ]
    
    def _generate_cache_key(
        self,
        text: SourceText,
        direction: TranslationDirection
    ) -> str:
        """Generate cache key for translation."""
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"translation:{direction.value}:{text_hash}"
    
    def _calculate_success_rate(self) -> float:
        """Calculate translation success rate."""
        if self._statistics.total_count == 0:
            return 0.0
        return self._statistics.successful_count / self._statistics.total_count
    
    def _format_engine_usage_stats(self) -> Dict[str, Any]:
        """Format engine usage statistics."""
        return {
            name: {
                "count": count,
                "percentage": count / max(self._statistics.total_count, 1) * 100
            }
            for name, count in self._statistics.engine_usage.items()
        }
    
    def _get_engine_availability_status(self) -> List[Dict[str, Any]]:
        """Get availability status of all engines."""
        return [
            {
                "name": engine.name,
                "available": engine.is_available,
                "supported_directions": [d.value for d in engine.get_supported_directions()]
            }
            for engine in self._engines
        ]
    
    def _create_parallel_translation_tasks(
        self,
        engines: List[TranslationEngine],
        text: SourceText,
        direction: TranslationDirection
    ) -> List[Future[TranslationResult]]:
        """Create parallel translation tasks."""
        return [
            self._executor.submit(engine.translate, text, direction)
            for engine in engines
        ]
    
    async def _execute_parallel_translations_async(
        self,
        tasks: List[Future[TranslationResult]]
    ) -> List[TranslationResult]:
        """Execute translations in parallel and collect results."""
        results = []
        
        for future in as_completed(tasks):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Parallel translation error: {e}")
        
        return results
    
    def _sort_results_by_confidence(
        self,
        results: List[TranslationResult]
    ) -> List[TranslationResult]:
        """Sort translation results by confidence score."""
        return sorted(
            results,
            key=lambda r: r.confidence if r.success else 0.0,
            reverse=True
        )
    
    async def _publish_comparison_event_async(
        self,
        results: List[TranslationResult]
    ) -> None:
        """Publish event with translation comparison results."""
        await self._event_bus.publish_event_async(
            "translation.comparison_completed",
            {
                "engine_count": len(results),
                "results": [
                    {
                        "engine": r.translation_method,
                        "success": r.success,
                        "confidence": r.confidence
                    }
                    for r in results
                ]
            }
        )