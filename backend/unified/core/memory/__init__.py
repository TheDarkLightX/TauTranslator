"""
Memory Optimization and Resource Management Package

Provides comprehensive memory management tools including:
- Object pooling for reduced allocations
- Resource tracking and leak detection
- Memory pressure monitoring
- Automatic cleanup strategies

Author: DarkLightX / Dana Edwards
"""

from .object_pools import (
    ObjectPool,
    MemoryManager,
    PooledObject,
    StringBuilderPool,
    BufferPool,
    PoolPolicy,
    MemoryPressure,
    get_memory_manager,
    get_string_builder_pool,
    get_buffer_pool,
    start_memory_management,
    stop_memory_management
)

from .resource_tracker import (
    ResourceTracker,
    ResourceContext,
    ResourceType,
    AllocationEvent,
    ResourceInfo,
    MemorySnapshot,
    get_resource_tracker,
    track_resource,
    untrack_resource,
    resource_context
)

from .translation_pools import (
    TranslationRequest,
    PatternMatchResult,
    ASTNode,
    CacheEntry,
    TranslationPools,
    get_translation_pools,
    initialize_translation_pools
)

__all__ = [
    # Object Pools
    'ObjectPool',
    'MemoryManager',
    'PooledObject',
    'StringBuilderPool', 
    'BufferPool',
    'PoolPolicy',
    'MemoryPressure',
    'get_memory_manager',
    'get_string_builder_pool',
    'get_buffer_pool',
    'start_memory_management',
    'stop_memory_management',
    
    # Resource Tracking
    'ResourceTracker',
    'ResourceContext',
    'ResourceType',
    'AllocationEvent',
    'ResourceInfo',
    'MemorySnapshot',
    'get_resource_tracker',
    'track_resource',
    'untrack_resource',
    'resource_context',
    
    # Translation Pools
    'TranslationRequest',
    'PatternMatchResult',
    'ASTNode',
    'CacheEntry',
    'TranslationPools',
    'get_translation_pools',
    'initialize_translation_pools'
]