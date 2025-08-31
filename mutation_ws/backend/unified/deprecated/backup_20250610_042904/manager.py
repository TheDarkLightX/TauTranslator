"""
Translation Manager - orchestrates multiple translation engines.

Combines all translation engines and provides intelligent routing.

Author: DarkLightX / Dana Edwards
"""

import logging
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .base import TranslationEngine, TranslationResult, TranslationDirection
from ..core.responses import TranslationError
from ..core.config import settings

logger = logging.getLogger(__name__)


class TranslationManager:
    """Manages multiple translation engines and routes requests intelligently."""
    
    def __init__(self):
        self.engines: List[TranslationEngine] = []
        self.default_engine: Optional[TranslationEngine] = None
        self.fallback_engines: List[TranslationEngine] = []
        self.parallel_mode = False
        self.confidence_threshold = 0.7
        
        # Statistics
        self.translation_count = 0
        self.successful_translations = 0
        self.failed_translations = 0
        self.engine_usage: Dict[str, int] = {}
    
    def register_engine(self, engine: TranslationEngine, is_default: bool = False, is_fallback: bool = False):
        """Register a translation engine."""
        self.engines.append(engine)
        
        if is_default:
            self.default_engine = engine
        
        if is_fallback:
            self.fallback_engines.append(engine)
        
        self.engine_usage[engine.name] = 0
        logger.info(f"Registered translation engine: {engine.name}")
    
    def get_available_engines(self, direction: TranslationDirection = None) -> List[TranslationEngine]:
        """Get list of available engines, optionally filtered by direction."""
        available = [engine for engine in self.engines if engine.is_available]
        
        if direction:
            available = [
                engine for engine in available 
                if direction in engine.get_supported_directions()
            ]
        
        return available
    
    def find_best_engine(self, text: str, direction: TranslationDirection) -> Optional[TranslationEngine]:
        """Find the best engine for a given translation request."""
        available_engines = self.get_available_engines(direction)
        
        if not available_engines:
            return None
        
        # Filter engines that can handle this text
        capable_engines = [
            engine for engine in available_engines
            if engine.can_translate(text, direction)
        ]
        
        if not capable_engines:
            return None
        
        # Prefer default engine if it's capable
        if self.default_engine and self.default_engine in capable_engines:
            return self.default_engine
        
        # Otherwise return the first capable engine
        return capable_engines[0]
    
    def translate(
        self, 
        text: str, 
        direction: TranslationDirection,
        engine_name: Optional[str] = None,
        use_fallback: bool = True,
        **kwargs
    ) -> TranslationResult:
        """Translate text using the best available engine."""
        start_time = time.time()
        self.translation_count += 1
        
        try:
            # Validate input
            if not text or not text.strip():
                raise TranslationError("Empty input text provided")
            
            # Find target engine
            target_engine = None
            if engine_name:
                target_engine = self._get_engine_by_name(engine_name)
                if not target_engine:
                    raise TranslationError(f"Engine '{engine_name}' not found")
                if not target_engine.is_available:
                    raise TranslationError(f"Engine '{engine_name}' is not available")
            else:
                target_engine = self.find_best_engine(text, direction)
                if not target_engine:
                    raise TranslationError(f"No available engine for direction: {direction.value}")
            
            # Attempt translation
            result = self._attempt_translation(target_engine, text, direction, **kwargs)
            
            # If translation failed and fallback is enabled, try fallback engines
            if not result.success and use_fallback:
                result = self._try_fallback_engines(text, direction, target_engine, **kwargs)
            
            # Update statistics
            if result.success:
                self.successful_translations += 1
                self.engine_usage[result.translation_method] += 1
            else:
                self.failed_translations += 1
            
            # Add processing time to result
            result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            self.failed_translations += 1
            logger.error(f"Translation failed: {e}")
            
            return TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method="manager",
                direction=direction,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def translate_parallel(
        self, 
        text: str, 
        direction: TranslationDirection,
        max_engines: int = 3,
        **kwargs
    ) -> List[TranslationResult]:
        """Translate using multiple engines in parallel and return all results."""
        available_engines = self.get_available_engines(direction)
        capable_engines = [
            engine for engine in available_engines
            if engine.can_translate(text, direction)
        ]
        
        if not capable_engines:
            return []
        
        # Limit number of engines
        engines_to_use = capable_engines[:max_engines]
        
        results = []
        with ThreadPoolExecutor(max_workers=len(engines_to_use)) as executor:
            # Submit translation tasks
            future_to_engine = {
                executor.submit(self._attempt_translation, engine, text, direction, **kwargs): engine
                for engine in engines_to_use
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_engine):
                engine = future_to_engine[future]
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    results.append(result)
                except Exception as e:
                    logger.error(f"Parallel translation failed for {engine.name}: {e}")
                    results.append(TranslationResult(
                        success=False,
                        translated_text="",
                        original_text=text,
                        translation_method=engine.name,
                        direction=direction,
                        error_message=str(e)
                    ))
        
        # Sort by confidence score
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results
    
    def _get_engine_by_name(self, name: str) -> Optional[TranslationEngine]:
        """Get engine by name."""
        for engine in self.engines:
            if engine.name == name:
                return engine
        return None
    
    def _attempt_translation(
        self, 
        engine: TranslationEngine, 
        text: str, 
        direction: TranslationDirection,
        **kwargs
    ) -> TranslationResult:
        """Attempt translation with a specific engine."""
        try:
            logger.debug(f"Attempting translation with {engine.name}")
            result = engine.translate(text, direction, **kwargs)
            
            if result.success:
                logger.info(f"Translation successful with {engine.name} (confidence: {result.confidence})")
            else:
                logger.warning(f"Translation failed with {engine.name}: {result.error_message}")
                engine.last_error = result.error_message
            
            return result
            
        except Exception as e:
            error_msg = f"Engine {engine.name} threw exception: {str(e)}"
            logger.error(error_msg)
            engine.last_error = error_msg
            
            return TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method=engine.name,
                direction=direction,
                error_message=error_msg
            )
    
    def _try_fallback_engines(
        self, 
        text: str, 
        direction: TranslationDirection, 
        failed_engine: TranslationEngine,
        **kwargs
    ) -> TranslationResult:
        """Try fallback engines when primary translation fails."""
        logger.info(f"Trying fallback engines after {failed_engine.name} failed")
        
        for fallback_engine in self.fallback_engines:
            if fallback_engine == failed_engine:
                continue
            
            if not fallback_engine.is_available:
                continue
            
            if not fallback_engine.can_translate(text, direction):
                continue
            
            result = self._attempt_translation(fallback_engine, text, direction, **kwargs)
            if result.success:
                logger.info(f"Fallback successful with {fallback_engine.name}")
                return result
        
        # If all fallbacks failed, return the original failure
        return TranslationResult(
            success=False,
            translated_text="",
            original_text=text,
            translation_method="fallback_failed",
            direction=direction,
            error_message="All translation engines failed"
        )
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get status of all engines."""
        return {
            'engines': [engine.get_status() for engine in self.engines],
            'default_engine': self.default_engine.name if self.default_engine else None,
            'fallback_engines': [engine.name for engine in self.fallback_engines],
            'total_engines': len(self.engines),
            'available_engines': len(self.get_available_engines())
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get translation statistics."""
        success_rate = 0
        if self.translation_count > 0:
            success_rate = (self.successful_translations / self.translation_count) * 100
        
        return {
            'total_translations': self.translation_count,
            'successful_translations': self.successful_translations,
            'failed_translations': self.failed_translations,
            'success_rate': success_rate,
            'engine_usage': self.engine_usage.copy()
        }
    
    def reset_statistics(self):
        """Reset translation statistics."""
        self.translation_count = 0
        self.successful_translations = 0
        self.failed_translations = 0
        self.engine_usage = {engine.name: 0 for engine in self.engines}
    
    def set_confidence_threshold(self, threshold: float):
        """Set minimum confidence threshold for accepting translations."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all engines."""
        health_status = {
            'overall_status': 'healthy',
            'engines': {}
        }
        
        unhealthy_engines = 0
        for engine in self.engines:
            try:
                # Simple health check - try to translate a basic text
                test_result = engine.translate("test", TranslationDirection.TO_TAU)
                engine_healthy = True
            except Exception as e:
                engine_healthy = False
                engine.last_error = str(e)
                unhealthy_engines += 1
            
            health_status['engines'][engine.name] = {
                'status': 'healthy' if engine_healthy else 'unhealthy',
                'is_available': engine.is_available,
                'last_error': engine.last_error
            }
        
        if unhealthy_engines > 0:
            if unhealthy_engines == len(self.engines):
                health_status['overall_status'] = 'critical'
            else:
                health_status['overall_status'] = 'degraded'
        
        return health_status