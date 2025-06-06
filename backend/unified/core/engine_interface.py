"""
Enhanced Translation Engine Interface

Defines comprehensive interfaces for translation engines with proper abstractions.
Implements Interface Segregation Principle with focused interfaces.

Author: DarkLightX / Dana Edwards
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass
from enum import Enum
import time


class EngineCapability(Enum):
    """Engine capability flags."""
    BIDIRECTIONAL = "bidirectional"
    CACHING = "caching"
    CONFIDENCE_SCORING = "confidence_scoring"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME = "real_time"
    OFFLINE = "offline"
    GRAMMAR_AWARE = "grammar_aware"
    PATTERN_BASED = "pattern_based"
    AI_POWERED = "ai_powered"
    CONFIGURABLE = "configurable"


class EngineState(Enum):
    """Engine operational states."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"


@dataclass
class EngineMetadata:
    """Comprehensive engine metadata."""
    name: str
    version: str
    description: str
    author: str
    capabilities: Set[EngineCapability]
    supported_directions: List['TranslationDirection']
    max_text_length: Optional[int] = None
    estimated_speed: Optional[str] = None  # "fast", "medium", "slow"
    memory_usage: Optional[str] = None     # "low", "medium", "high"
    requires_internet: bool = False
    configuration_schema: Optional[Dict[str, Any]] = None


@dataclass
class TranslationContext:
    """Context information for translation requests."""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    priority: int = 0  # 0 = normal, higher = more priority
    timeout: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EnginePerformanceMetrics:
    """Performance metrics for an engine."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    cache_hit_rate: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


# Import these from base.py to maintain compatibility
from ..translators.base import TranslationDirection, TranslationResult


class ITranslationEngine(ABC):
    """
    Core translation engine interface.
    
    Defines the fundamental contract that all translation engines must implement.
    Follows Interface Segregation Principle.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> EngineMetadata:
        """Get engine metadata information."""
        pass
    
    @property
    @abstractmethod
    def state(self) -> EngineState:
        """Get current engine state."""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if engine is available for translation requests."""
        pass
    
    @abstractmethod
    def can_translate(self, text: str, direction: TranslationDirection, context: Optional[TranslationContext] = None) -> bool:
        """
        Check if this engine can handle the given translation.
        
        Args:
            text: Source text to translate
            direction: Translation direction
            context: Optional context information
            
        Returns:
            True if engine can handle this translation
        """
        pass
    
    @abstractmethod
    def translate(
        self, 
        text: str, 
        direction: TranslationDirection, 
        context: Optional[TranslationContext] = None,
        **kwargs
    ) -> TranslationResult:
        """
        Perform translation.
        
        Args:
            text: Source text to translate
            direction: Translation direction
            context: Optional context information
            **kwargs: Additional engine-specific parameters
            
        Returns:
            TranslationResult with success status and translated text
        """
        pass
    
    @abstractmethod
    def validate_input(self, text: str, direction: TranslationDirection) -> tuple[bool, Optional[str]]:
        """
        Validate input text for translation.
        
        Args:
            text: Text to validate
            direction: Translation direction
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get list of supported translation directions."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status information."""
        pass


class IConfigurableEngine(ABC):
    """Interface for engines that support configuration."""
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """Get current engine configuration."""
        pass
    
    @abstractmethod
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update engine configuration.
        
        Args:
            config: New configuration parameters
            
        Returns:
            True if configuration was successfully updated
        """
        pass
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate configuration parameters.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass
    
    @abstractmethod
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get JSON schema for configuration validation."""
        pass


class ICacheableEngine(ABC):
    """Interface for engines that support caching."""
    
    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        pass
    
    @abstractmethod
    def clear_cache(self) -> bool:
        """Clear the translation cache."""
        pass
    
    @abstractmethod
    def warm_cache(self, texts: List[tuple[str, TranslationDirection]]) -> int:
        """
        Pre-populate cache with common translations.
        
        Args:
            texts: List of (text, direction) tuples to cache
            
        Returns:
            Number of items successfully cached
        """
        pass


class IBatchProcessingEngine(ABC):
    """Interface for engines that support batch processing."""
    
    @abstractmethod
    def translate_batch(
        self, 
        requests: List[tuple[str, TranslationDirection]], 
        context: Optional[TranslationContext] = None
    ) -> List[TranslationResult]:
        """
        Process multiple translations in batch.
        
        Args:
            requests: List of (text, direction) translation requests
            context: Optional context information
            
        Returns:
            List of TranslationResult objects
        """
        pass
    
    @abstractmethod
    def get_optimal_batch_size(self) -> int:
        """Get recommended batch size for optimal performance."""
        pass


class IMonitorableEngine(ABC):
    """Interface for engines that provide performance monitoring."""
    
    @abstractmethod
    def get_performance_metrics(self) -> EnginePerformanceMetrics:
        """Get current performance metrics."""
        pass
    
    @abstractmethod
    def reset_metrics(self) -> None:
        """Reset performance metrics to initial state."""
        pass
    
    @abstractmethod
    def health_check(self) -> tuple[bool, Optional[str]]:
        """
        Perform engine health check.
        
        Returns:
            Tuple of (is_healthy, error_message)
        """
        pass


class ILifecycleManaged(ABC):
    """Interface for engines that require lifecycle management."""
    
    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize the engine.
        
        Args:
            config: Optional initialization configuration
            
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Start the engine for operation."""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop the engine gracefully."""
        pass
    
    @abstractmethod
    def restart(self) -> bool:
        """Restart the engine."""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown the engine and cleanup resources."""
        pass


class IStreamingEngine(ABC):
    """Interface for engines that support streaming/real-time translation."""
    
    @abstractmethod
    def start_stream(self, direction: TranslationDirection, context: Optional[TranslationContext] = None) -> str:
        """
        Start a translation stream.
        
        Args:
            direction: Translation direction
            context: Optional context information
            
        Returns:
            Stream identifier
        """
        pass
    
    @abstractmethod
    def stream_translate(self, stream_id: str, text_chunk: str) -> Optional[str]:
        """
        Translate a chunk of text in an active stream.
        
        Args:
            stream_id: Stream identifier
            text_chunk: Partial text to translate
            
        Returns:
            Partial translation result or None if not ready
        """
        pass
    
    @abstractmethod
    def end_stream(self, stream_id: str) -> TranslationResult:
        """
        End translation stream and get final result.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Final translation result
        """
        pass


class BaseTranslationEngine(ITranslationEngine, IMonitorableEngine, ILifecycleManaged):
    """
    Abstract base implementation providing common functionality.
    
    Implements common patterns and provides default implementations
    for basic functionality.
    """
    
    def __init__(self, metadata: EngineMetadata):
        self._metadata = metadata
        self._state = EngineState.INITIALIZING
        self._is_available = False
        self._metrics = EnginePerformanceMetrics()
        self._last_error: Optional[str] = None
        self._start_time = time.time()
    
    @property
    def metadata(self) -> EngineMetadata:
        """Get engine metadata."""
        return self._metadata
    
    @property
    def state(self) -> EngineState:
        """Get current engine state."""
        return self._state
    
    @property
    def is_available(self) -> bool:
        """Check if engine is available."""
        return self._is_available and self._state == EngineState.READY
    
    def validate_input(self, text: str, direction: TranslationDirection) -> tuple[bool, Optional[str]]:
        """Default input validation."""
        if not text or not text.strip():
            return False, "Empty input text"
        
        if direction not in self.get_supported_directions():
            return False, f"Unsupported direction: {direction.value}"
        
        if self._metadata.max_text_length and len(text) > self._metadata.max_text_length:
            return False, f"Text too long: {len(text)} > {self._metadata.max_text_length}"
        
        return True, None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information."""
        return {
            'metadata': {
                'name': self._metadata.name,
                'version': self._metadata.version,
                'description': self._metadata.description,
                'capabilities': [cap.value for cap in self._metadata.capabilities]
            },
            'state': self._state.value,
            'is_available': self.is_available,
            'supported_directions': [d.value for d in self.get_supported_directions()],
            'performance': {
                'total_requests': self._metrics.total_requests,
                'success_rate': self._calculate_success_rate(),
                'average_response_time': self._metrics.average_response_time
            },
            'uptime_seconds': time.time() - self._start_time,
            'last_error': self._last_error
        }
    
    def get_performance_metrics(self) -> EnginePerformanceMetrics:
        """Get performance metrics."""
        return self._metrics
    
    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self._metrics = EnginePerformanceMetrics()
    
    def health_check(self) -> tuple[bool, Optional[str]]:
        """Basic health check implementation."""
        if not self.is_available:
            return False, f"Engine not available - state: {self._state.value}"
        
        # Perform basic translation test
        try:
            test_result = self.translate("test", TranslationDirection.TO_TAU)
            return test_result.success, test_result.error_message
        except Exception as e:
            return False, f"Health check failed: {str(e)}"
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Default initialization."""
        self._state = EngineState.READY
        self._is_available = True
        return True
    
    def start(self) -> bool:
        """Start the engine."""
        if self._state == EngineState.READY:
            return True
        return self.initialize()
    
    def stop(self) -> bool:
        """Stop the engine."""
        self._state = EngineState.MAINTENANCE
        self._is_available = False
        return True
    
    def restart(self) -> bool:
        """Restart the engine."""
        self.stop()
        return self.start()
    
    def shutdown(self) -> bool:
        """Shutdown the engine."""
        self._state = EngineState.SHUTDOWN
        self._is_available = False
        return True
    
    def _calculate_success_rate(self) -> float:
        """Calculate current success rate."""
        if self._metrics.total_requests == 0:
            return 0.0
        return (self._metrics.successful_requests / self._metrics.total_requests) * 100
    
    def _record_request_start(self) -> float:
        """Record start of request processing."""
        return time.time()
    
    def _record_request_end(self, start_time: float, success: bool, error_msg: Optional[str] = None) -> None:
        """Record end of request processing."""
        processing_time = time.time() - start_time
        
        self._metrics.total_requests += 1
        if success:
            self._metrics.successful_requests += 1
        else:
            self._metrics.failed_requests += 1
            self._last_error = error_msg
        
        # Update rolling average response time
        if self._metrics.total_requests == 1:
            self._metrics.average_response_time = processing_time
        else:
            # Weighted average
            weight = 0.1
            self._metrics.average_response_time = (
                self._metrics.average_response_time * (1 - weight) + 
                processing_time * weight
            )