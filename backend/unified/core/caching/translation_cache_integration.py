"""
Translation Cache Integration

Integrates advanced caching with the translation pipeline for optimal performance.
Provides specialized caching for different translation components.

Author: DarkLightX / Dana Edwards
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, Callable, List, Tuple
from functools import wraps
from dataclasses import dataclass
import logging

from .advanced_cache import (
    SmartCacheManager, CachePolicy, get_cache_manager,
    LRUCache, LFUCache, TTLCache
)


logger = logging.getLogger(__name__)


@dataclass
class TranslationCacheConfig:
    """Configuration for translation caching."""
    # Cache sizes
    pattern_cache_size: int = 10000
    grammar_cache_size: int = 1000
    nlp_cache_size: int = 5000
    result_cache_size: int = 50000
    
    # TTL values (in seconds)
    pattern_ttl: float = 3600.0  # 1 hour
    grammar_ttl: float = 7200.0  # 2 hours
    nlp_ttl: float = 1800.0      # 30 minutes
    result_ttl: float = 300.0    # 5 minutes
    
    # Cache policies
    pattern_policy: CachePolicy = CachePolicy.LFU
    grammar_policy: CachePolicy = CachePolicy.LRU
    nlp_policy: CachePolicy = CachePolicy.ARC
    result_policy: CachePolicy = CachePolicy.TTL
    
    # Feature flags
    enable_compression: bool = True
    enable_statistics: bool = True
    enable_warmup: bool = True


class TranslationCacheManager:
    """
    Manages multiple specialized caches for the translation pipeline.
    
    Provides:
    - Pattern matching cache (LFU - patterns are reused frequently)
    - Grammar cache (LRU - recent grammars likely to be used again)
    - NLP cache (ARC - adaptive for varying workloads)
    - Result cache (TTL - results expire after short time)
    """
    
    def __init__(self, config: Optional[TranslationCacheConfig] = None):
        self.config = config or TranslationCacheConfig()
        
        # Initialize specialized caches
        self._initialize_caches()
        
        # Statistics tracking
        self.stats = {
            'pattern_lookups': 0,
            'grammar_lookups': 0,
            'nlp_lookups': 0,
            'result_lookups': 0,
            'total_time_saved': 0.0
        }
        
        logger.info("Translation cache manager initialized")
    
    def _initialize_caches(self) -> None:
        """Initialize all cache components."""
        # Pattern cache - frequently used patterns
        if self.config.pattern_policy == CachePolicy.LFU:
            self.pattern_cache = LFUCache(self.config.pattern_cache_size)
        else:
            self.pattern_cache = SmartCacheManager(self.config.pattern_cache_size)
            self.pattern_cache.force_strategy(self.config.pattern_policy)
        
        # Grammar cache - recent grammars
        if self.config.grammar_policy == CachePolicy.LRU:
            self.grammar_cache = LRUCache(self.config.grammar_cache_size)
        else:
            self.grammar_cache = SmartCacheManager(self.config.grammar_cache_size)
            self.grammar_cache.force_strategy(self.config.grammar_policy)
        
        # NLP cache - adaptive
        self.nlp_cache = SmartCacheManager(self.config.nlp_cache_size)
        if self.config.nlp_policy != CachePolicy.ARC:
            self.nlp_cache.force_strategy(self.config.nlp_policy)
        
        # Result cache - time-based
        if self.config.result_policy == CachePolicy.TTL:
            self.result_cache = TTLCache(
                self.config.result_cache_size,
                default_ttl=self.config.result_ttl
            )
        else:
            self.result_cache = SmartCacheManager(self.config.result_cache_size)
            self.result_cache.force_strategy(self.config.result_policy)
    
    def cache_pattern(self, pattern: str, result: Any) -> bool:
        """Cache a pattern matching result."""
        key = self._generate_key(pattern)
        return self.pattern_cache.put(key, result, ttl=self.config.pattern_ttl)
    
    def get_pattern(self, pattern: str) -> Optional[Any]:
        """Get cached pattern result."""
        self.stats['pattern_lookups'] += 1
        key = self._generate_key(pattern)
        return self.pattern_cache.get(key)
    
    def cache_grammar(self, grammar_id: str, parsed_grammar: Any) -> bool:
        """Cache a parsed grammar."""
        return self.grammar_cache.put(
            grammar_id, 
            parsed_grammar, 
            ttl=self.config.grammar_ttl
        )
    
    def get_grammar(self, grammar_id: str) -> Optional[Any]:
        """Get cached grammar."""
        self.stats['grammar_lookups'] += 1
        return self.grammar_cache.get(grammar_id)
    
    def cache_nlp_result(self, text: str, analysis: Any) -> bool:
        """Cache NLP analysis result."""
        key = self._generate_key(text)
        return self.nlp_cache.put(key, analysis, ttl=self.config.nlp_ttl)
    
    def get_nlp_result(self, text: str) -> Optional[Any]:
        """Get cached NLP result."""
        self.stats['nlp_lookups'] += 1
        key = self._generate_key(text)
        return self.nlp_cache.get(key)
    
    def cache_translation(
        self, 
        source: str, 
        target_format: str, 
        result: Any
    ) -> bool:
        """Cache translation result."""
        key = self._generate_translation_key(source, target_format)
        return self.result_cache.put(key, result, ttl=self.config.result_ttl)
    
    def get_translation(self, source: str, target_format: str) -> Optional[Any]:
        """Get cached translation."""
        self.stats['result_lookups'] += 1
        key = self._generate_translation_key(source, target_format)
        return self.result_cache.get(key)
    
    def warm_caches(self, warmup_data: Dict[str, Dict[str, Any]]) -> None:
        """Warm up caches with pre-computed data."""
        if not self.config.enable_warmup:
            return
        
        logger.info("Warming up translation caches...")
        
        # Warm pattern cache
        if 'patterns' in warmup_data:
            for pattern, result in warmup_data['patterns'].items():
                self.cache_pattern(pattern, result)
        
        # Warm grammar cache
        if 'grammars' in warmup_data:
            for grammar_id, parsed in warmup_data['grammars'].items():
                self.cache_grammar(grammar_id, parsed)
        
        # Warm NLP cache
        if 'nlp' in warmup_data:
            for text, analysis in warmup_data['nlp'].items():
                self.cache_nlp_result(text, analysis)
        
        logger.info("Cache warmup completed")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            'lookups': self.stats.copy(),
            'caches': {}
        }
        
        # Get individual cache stats
        if hasattr(self.pattern_cache, 'get_stats'):
            pattern_stats = self.pattern_cache.get_stats()
            stats['caches']['pattern'] = {
                'hit_rate': pattern_stats.hit_rate,
                'size': pattern_stats.current_size,
                'evictions': pattern_stats.evictions
            }
        
        if hasattr(self.grammar_cache, 'get_stats'):
            grammar_stats = self.grammar_cache.get_stats()
            stats['caches']['grammar'] = {
                'hit_rate': grammar_stats.hit_rate,
                'size': grammar_stats.current_size,
                'evictions': grammar_stats.evictions
            }
        
        if hasattr(self.nlp_cache, 'get_comprehensive_stats'):
            stats['caches']['nlp'] = self.nlp_cache.get_comprehensive_stats()
        elif hasattr(self.nlp_cache, 'get_stats'):
            nlp_stats = self.nlp_cache.get_stats()
            stats['caches']['nlp'] = {
                'hit_rate': nlp_stats.hit_rate,
                'size': nlp_stats.current_size
            }
        
        if hasattr(self.result_cache, 'get_stats'):
            result_stats = self.result_cache.get_stats()
            stats['caches']['result'] = {
                'hit_rate': result_stats.hit_rate,
                'size': result_stats.current_size,
                'expirations': result_stats.expirations
            }
        
        return stats
    
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        self.pattern_cache.clear()
        self.grammar_cache.clear()
        self.nlp_cache.clear()
        self.result_cache.clear()
        logger.info("All translation caches cleared")
    
    def _generate_key(self, content: str) -> str:
        """Generate cache key from content."""
        if self.config.enable_compression:
            # Use hash for long content
            if len(content) > 100:
                return hashlib.sha256(content.encode()).hexdigest()
        return content
    
    def _generate_translation_key(self, source: str, target: str) -> str:
        """Generate key for translation cache."""
        combined = f"{source}::{target}"
        return self._generate_key(combined)


def cached_translation(
    cache_type: str = 'result',
    ttl: Optional[float] = None
) -> Callable:
    """
    Decorator for caching translation operations.
    
    Args:
        cache_type: Type of cache to use ('pattern', 'grammar', 'nlp', 'result', 'translation')
        ttl: Optional TTL override
    
    Example:
        @cached_translation('pattern', ttl=3600)
        def match_pattern(pattern: str) -> PatternResult:
            # Expensive pattern matching
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get cache manager
            manager = get_translation_cache_manager()
            
            # Handle different cache types
            if cache_type == 'translation' and len(args) >= 2:
                # Special handling for translation cache
                cached = manager.get_translation(args[0], args[1])
                if cached is not None:
                    return cached
            else:
                # Generate cache key for other cache types
                cache_key = _generate_function_cache_key(func, args, kwargs)
                
                # Map cache types to methods
                cache_methods = {
                    'pattern': (manager.get_pattern, manager.cache_pattern),
                    'grammar': (manager.get_grammar, manager.cache_grammar),
                    'nlp': (manager.get_nlp_result, manager.cache_nlp_result),
                    'result': (manager.get_translation if cache_type == 'result' else None, 
                              manager.cache_translation if cache_type == 'result' else None)
                }
                
                if cache_type in cache_methods:
                    get_method, put_method = cache_methods[cache_type]
                    
                    if cache_type == 'result':
                        # For 'result' type, use the general result cache
                        # Create a pseudo translation key
                        cached = manager.result_cache.get(cache_key)
                        if cached is not None:
                            return cached
                    else:
                        # Try to get from cache
                        if get_method:
                            cached = get_method(cache_key)
                            if cached is not None:
                                return cached
            
            # Execute function
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # Cache result
            if cache_type == 'translation' and len(args) >= 2:
                manager.cache_translation(args[0], args[1], result)
            elif cache_type == 'result':
                # For 'result' type, use the result cache directly
                manager.result_cache.put(cache_key, result, ttl=ttl or manager.config.result_ttl)
            else:
                # Cache using appropriate method
                if cache_type in cache_methods:
                    _, put_method = cache_methods[cache_type]
                    if put_method:
                        put_method(cache_key, result)
            
            # Update statistics
            manager.stats['total_time_saved'] += elapsed
            
            return result
        
        return wrapper
    return decorator


def _generate_function_cache_key(
    func: Callable,
    args: tuple,
    kwargs: dict
) -> str:
    """Generate cache key for function call."""
    # Create a unique key based on function name and arguments
    key_parts = [func.__name__]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            # For complex objects, use their string representation
            key_parts.append(repr(arg)[:50])  # Limit length
    
    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    
    return "::".join(key_parts)


# Global translation cache manager
_translation_cache_manager = None


def get_translation_cache_manager() -> TranslationCacheManager:
    """Get or create the global translation cache manager."""
    global _translation_cache_manager
    if _translation_cache_manager is None:
        _translation_cache_manager = TranslationCacheManager()
    return _translation_cache_manager


def configure_translation_cache(config: TranslationCacheConfig) -> None:
    """Configure the global translation cache manager."""
    global _translation_cache_manager
    _translation_cache_manager = TranslationCacheManager(config)
    logger.info("Translation cache reconfigured")


# Example usage patterns
if __name__ == "__main__":
    # Example: Configure custom cache settings
    config = TranslationCacheConfig(
        pattern_cache_size=20000,
        result_cache_size=100000,
        result_ttl=600.0,  # 10 minutes
        enable_compression=True
    )
    
    configure_translation_cache(config)
    
    # Example: Using the cache decorator
    @cached_translation('pattern')
    def expensive_pattern_match(pattern: str) -> dict:
        """Simulate expensive pattern matching."""
        time.sleep(0.1)  # Simulate work
        return {'matched': True, 'groups': []}
    
    # First call - slow
    result1 = expensive_pattern_match("test_pattern")
    
    # Second call - cached, fast
    result2 = expensive_pattern_match("test_pattern")
    
    # Get statistics
    manager = get_translation_cache_manager()
    stats = manager.get_statistics()
    print(f"Cache statistics: {json.dumps(stats, indent=2)}")