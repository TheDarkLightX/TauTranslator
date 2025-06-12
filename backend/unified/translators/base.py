"""
Base classes for translation engines.

Defines the interface that all translation engines must implement.

Author: DarkLightX / Dana Edwards
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import time


class TranslationDirection(Enum):
    """Direction of translation."""
    TO_TAU = "to_tau"
    TO_TCE = "to_tce" 
    TO_ENGLISH = "to_english"
    BIDIRECTIONAL = "bidirectional"
    NL_TO_TAU = "nl_to_tau"  # Natural Language to Tau
    NL_TO_TCE = "nl_to_tce"  # Natural Language to TCE
    TCE_TO_TAU = "tce_to_tau"  # TCE to Tau
    TCE_TO_NL = "tce_to_nl"  # TCE to Natural Language


@dataclass
class TranslationResult:
    """Result of a translation operation."""
    success: bool
    translated_text: str
    original_text: str
    translation_method: str
    direction: TranslationDirection
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'translated_text': self.translated_text,
            'original_text': self.original_text,
            'translation_method': self.translation_method,
            'direction': self.direction.value,
            'confidence': self.confidence,
            'metadata': self.metadata or {},
            'error_message': self.error_message,
            'processing_time': self.processing_time
        }


class TranslationEngine(ABC):
    """Abstract base class for all translation engines."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.is_available = True
        self.last_error: Optional[str] = None
    
    @abstractmethod
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the given translation."""
        pass
    
    @abstractmethod
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform the translation."""
        pass
    
    @abstractmethod
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get list of supported translation directions."""
        pass
    
    def validate_input(self, text: str) -> bool:
        """Validate input text. Override for custom validation."""
        if not text or not text.strip():
            return False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status information."""
        return {
            'name': self.name,
            'description': self.description,
            'is_available': self.is_available,
            'supported_directions': [d.value for d in self.get_supported_directions()],
            'last_error': self.last_error
        }
    
    def _create_result(
        self,
        success: bool,
        translated_text: str,
        original_text: str,
        direction: TranslationDirection,
        confidence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        start_time: float = None
    ) -> TranslationResult:
        """Helper to create a TranslationResult."""
        processing_time = time.time() - start_time if start_time else 0.0
        
        return TranslationResult(
            success=success,
            translated_text=translated_text,
            original_text=original_text,
            translation_method=self.name,
            direction=direction,
            confidence=confidence,
            metadata=metadata,
            error_message=error_message,
            processing_time=processing_time
        )


class ConfigurableEngine(TranslationEngine):
    """Base class for engines that can be configured."""
    
    def __init__(self, name: str, description: str = "", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, description)
        self.config = config or {}
    
    def update_config(self, config: Dict[str, Any]):
        """Update engine configuration."""
        self.config.update(config)
        self._apply_config()
    
    def _apply_config(self):
        """Apply configuration changes. Override in subclasses."""
        pass


class CachingEngine(TranslationEngine):
    """Base class for engines with caching capabilities."""
    
    def __init__(self, name: str, description: str = "", cache_size: int = 100):
        super().__init__(name, description)
        self.cache: Dict[str, TranslationResult] = {}
        self.cache_size = cache_size
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _get_cache_key(self, text: str, direction: TranslationDirection, **kwargs) -> str:
        """Generate cache key for translation."""
        # Simple cache key - can be overridden for more complex scenarios
        return f"{self.name}:{direction.value}:{hash(text)}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[TranslationResult]:
        """Get result from cache."""
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        self.cache_misses += 1
        return None
    
    def _store_in_cache(self, cache_key: str, result: TranslationResult):
        """Store result in cache with LRU eviction."""
        if len(self.cache) >= self.cache_size:
            # Simple LRU: remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = result
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.cache_size,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate
        }
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0