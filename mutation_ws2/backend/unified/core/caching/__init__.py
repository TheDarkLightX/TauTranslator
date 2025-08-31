"""
Advanced Caching System for Tau Translator

Provides high-performance caching strategies with adaptive selection,
thread-safe operations, and comprehensive monitoring.

Author: DarkLightX / Dana Edwards
"""

from .advanced_cache import (
    # Enums
    CachePolicy,
    CacheEvent,
    
    # Data classes
    CacheEntry,
    CacheStats,
    
    # Cache interfaces
    ICacheStrategy,
    
    # Cache implementations
    LRUCache,
    LFUCache,
    TTLCache,
    AdaptiveReplacementCache,
    SmartCacheManager,
    
    # Global manager
    get_cache_manager
)

from .translation_cache_integration import (
    # Configuration
    TranslationCacheConfig,
    
    # Manager
    TranslationCacheManager,
    get_translation_cache_manager,
    configure_translation_cache,
    
    # Decorators
    cached_translation
)

__all__ = [
    # From advanced_cache
    'CachePolicy',
    'CacheEvent',
    'CacheEntry',
    'CacheStats',
    'ICacheStrategy',
    'LRUCache',
    'LFUCache',
    'TTLCache',
    'AdaptiveReplacementCache',
    'SmartCacheManager',
    'get_cache_manager',
    
    # From translation_cache_integration
    'TranslationCacheConfig',
    'TranslationCacheManager',
    'get_translation_cache_manager',
    'configure_translation_cache',
    'cached_translation',
]

__version__ = '1.0.0'