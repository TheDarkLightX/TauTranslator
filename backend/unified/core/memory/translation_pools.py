"""
Translation-specific object pools for memory optimization.

Provides specialized pools for frequently created objects in the translation pipeline:
- Translation requests
- Pattern match results
- AST nodes
- Cache entries

Author: DarkLightX / Dana Edwards
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set
from .object_pools import PooledObject, ObjectPool, PoolPolicy, get_memory_manager
from .resource_tracker import ResourceType, get_resource_tracker


class TranslationRequest(PooledObject):
    """Poolable translation request object."""
    
    def __init__(self):
        super().__init__()
        self.source_text: str = ""
        self.source_language: str = ""
        self.target_language: str = ""
        self.options: Dict[str, Any] = {}
        self.timestamp: float = 0.0
        self.request_id: Optional[str] = None
    
    def reset(self) -> None:
        """Reset to initial state for reuse."""
        super().reset()
        self.source_text = ""
        self.source_language = ""
        self.target_language = ""
        self.options.clear()
        self.timestamp = 0.0
        self.request_id = None
    
    def get_memory_size(self) -> int:
        """Get approximate memory size."""
        # Base object size + string sizes + dict size
        size = 200  # Base object overhead
        size += len(self.source_text) * 2  # Unicode chars
        size += len(self.source_language) * 2
        size += len(self.target_language) * 2
        size += len(str(self.options)) * 2  # Rough estimate
        return size
    
    def configure(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> None:
        """Configure the request with new data."""
        self.source_text = source_text
        self.source_language = source_language
        self.target_language = target_language
        self.options = options or {}
        self.timestamp = time.time()
        self.request_id = request_id


class PatternMatchResult(PooledObject):
    """Poolable pattern match result object."""
    
    def __init__(self):
        super().__init__()
        self.pattern_name: str = ""
        self.matched_text: str = ""
        self.start_position: int = 0
        self.end_position: int = 0
        self.confidence: float = 0.0
        self.metadata: Dict[str, Any] = {}
        self.sub_matches: List['PatternMatchResult'] = []
    
    def reset(self) -> None:
        """Reset to initial state for reuse."""
        super().reset()
        self.pattern_name = ""
        self.matched_text = ""
        self.start_position = 0
        self.end_position = 0
        self.confidence = 0.0
        self.metadata.clear()
        self.sub_matches.clear()
    
    def get_memory_size(self) -> int:
        """Get approximate memory size."""
        size = 200  # Base object overhead
        size += len(self.pattern_name) * 2
        size += len(self.matched_text) * 2
        size += len(str(self.metadata)) * 2
        size += sum(sub.get_memory_size() for sub in self.sub_matches)
        return size
    
    def configure(
        self,
        pattern_name: str,
        matched_text: str,
        start_position: int,
        end_position: int,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Configure the match result with new data."""
        self.pattern_name = pattern_name
        self.matched_text = matched_text
        self.start_position = start_position
        self.end_position = end_position
        self.confidence = confidence
        if metadata:
            self.metadata.update(metadata)


class ASTNode(PooledObject):
    """Base class for poolable AST nodes."""
    
    def __init__(self):
        super().__init__()
        self.node_type: str = ""
        self.value: Any = None
        self.children: List['ASTNode'] = []
        self.attributes: Dict[str, Any] = {}
        self.line_number: int = 0
        self.column_number: int = 0
    
    def reset(self) -> None:
        """Reset to initial state for reuse."""
        super().reset()
        self.node_type = ""
        self.value = None
        self.children.clear()
        self.attributes.clear()
        self.line_number = 0
        self.column_number = 0
    
    def get_memory_size(self) -> int:
        """Get approximate memory size."""
        size = 300  # Base object overhead
        size += len(self.node_type) * 2
        size += len(str(self.value)) * 2 if self.value else 0
        size += len(str(self.attributes)) * 2
        size += sum(child.get_memory_size() for child in self.children)
        return size
    
    def configure(
        self,
        node_type: str,
        value: Any = None,
        line_number: int = 0,
        column_number: int = 0,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """Configure the AST node with new data."""
        self.node_type = node_type
        self.value = value
        self.line_number = line_number
        self.column_number = column_number
        if attributes:
            self.attributes.update(attributes)
    
    def add_child(self, child: 'ASTNode') -> None:
        """Add a child node."""
        self.children.append(child)
    
    def add_children(self, children: List['ASTNode']) -> None:
        """Add multiple child nodes."""
        self.children.extend(children)


class CacheEntry(PooledObject):
    """Poolable cache entry object."""
    
    def __init__(self):
        super().__init__()
        self.key: str = ""
        self.value: Any = None
        self.created_at: float = 0.0
        self.last_accessed: float = 0.0
        self.access_count: int = 0
        self.ttl: float = 3600.0  # Default 1 hour TTL
        self.metadata: Dict[str, Any] = {}
    
    def reset(self) -> None:
        """Reset to initial state for reuse."""
        super().reset()
        self.key = ""
        self.value = None
        self.created_at = 0.0
        self.last_accessed = 0.0
        self.access_count = 0
        self.ttl = 3600.0
        self.metadata.clear()
    
    def is_valid(self) -> bool:
        """Check if cache entry is still valid."""
        if not super().is_valid():
            return False
        
        # Check TTL
        if self.ttl > 0:
            age = time.time() - self.created_at
            return age < self.ttl
        
        return True
    
    def get_memory_size(self) -> int:
        """Get approximate memory size."""
        size = 300  # Base object overhead
        size += len(self.key) * 2
        size += len(str(self.value)) * 2 if self.value else 0
        size += len(str(self.metadata)) * 2
        return size
    
    def configure(
        self,
        key: str,
        value: Any,
        ttl: float = 3600.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Configure the cache entry with new data."""
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.ttl = ttl
        if metadata:
            self.metadata.update(metadata)
    
    def access(self) -> Any:
        """Access the cached value and update stats."""
        self.last_accessed = time.time()
        self.access_count += 1
        return self.value


class TranslationPools:
    """
    Manager for translation-specific object pools.
    
    Provides centralized access to all translation-related pools
    and handles their lifecycle management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Create pools with appropriate sizes and policies
        self.translation_request_pool = ObjectPool(
            factory=TranslationRequest,
            max_size=100,
            policy=PoolPolicy.LIFO,
            validate_objects=True
        )
        
        self.pattern_match_pool = ObjectPool(
            factory=PatternMatchResult,
            max_size=500,
            policy=PoolPolicy.LIFO,
            validate_objects=True
        )
        
        self.ast_node_pool = ObjectPool(
            factory=ASTNode,
            max_size=1000,
            policy=PoolPolicy.LIFO,
            validate_objects=True
        )
        
        self.cache_entry_pool = ObjectPool(
            factory=CacheEntry,
            max_size=200,
            policy=PoolPolicy.LRU,  # LRU for cache entries
            validate_objects=True
        )
        
        # Register pools with memory manager
        memory_manager = get_memory_manager()
        memory_manager.register_pool("translation_requests", self.translation_request_pool)
        memory_manager.register_pool("pattern_matches", self.pattern_match_pool)
        memory_manager.register_pool("ast_nodes", self.ast_node_pool)
        memory_manager.register_pool("cache_entries", self.cache_entry_pool)
        
        self.logger.info("Initialized translation object pools")
    
    def acquire_translation_request(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> TranslationRequest:
        """Acquire and configure a translation request from pool."""
        request = self.translation_request_pool.acquire()
        request.configure(source_text, source_language, target_language, options, request_id)
        
        # Track resource
        tracker = get_resource_tracker()
        tracker.track_resource(
            f"translation_request_{id(request)}",
            ResourceType.TRANSLATION_CONTEXT,
            request.get_memory_size(),
            request
        )
        
        return request
    
    def release_translation_request(self, request: TranslationRequest) -> bool:
        """Release translation request back to pool."""
        # Untrack resource
        tracker = get_resource_tracker()
        tracker.untrack_resource(f"translation_request_{id(request)}", reused=True)
        
        return self.translation_request_pool.release(request)
    
    def acquire_pattern_match(
        self,
        pattern_name: str,
        matched_text: str,
        start_position: int,
        end_position: int,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PatternMatchResult:
        """Acquire and configure a pattern match result from pool."""
        match = self.pattern_match_pool.acquire()
        match.configure(pattern_name, matched_text, start_position, end_position, confidence, metadata)
        
        # Track resource
        tracker = get_resource_tracker()
        tracker.track_resource(
            f"pattern_match_{id(match)}",
            ResourceType.PATTERN_MATCHER,
            match.get_memory_size(),
            match
        )
        
        return match
    
    def release_pattern_match(self, match: PatternMatchResult) -> bool:
        """Release pattern match result back to pool."""
        # Untrack resource
        tracker = get_resource_tracker()
        tracker.untrack_resource(f"pattern_match_{id(match)}", reused=True)
        
        return self.pattern_match_pool.release(match)
    
    def acquire_ast_node(
        self,
        node_type: str,
        value: Any = None,
        line_number: int = 0,
        column_number: int = 0,
        attributes: Optional[Dict[str, Any]] = None
    ) -> ASTNode:
        """Acquire and configure an AST node from pool."""
        node = self.ast_node_pool.acquire()
        node.configure(node_type, value, line_number, column_number, attributes)
        
        # Track resource
        tracker = get_resource_tracker()
        tracker.track_resource(
            f"ast_node_{id(node)}",
            ResourceType.MEMORY,
            node.get_memory_size(),
            node
        )
        
        return node
    
    def release_ast_node(self, node: ASTNode) -> bool:
        """Release AST node back to pool."""
        # Release children first (recursive)
        for child in node.children:
            self.release_ast_node(child)
        
        # Untrack resource
        tracker = get_resource_tracker()
        tracker.untrack_resource(f"ast_node_{id(node)}", reused=True)
        
        return self.ast_node_pool.release(node)
    
    def acquire_cache_entry(
        self,
        key: str,
        value: Any,
        ttl: float = 3600.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CacheEntry:
        """Acquire and configure a cache entry from pool."""
        entry = self.cache_entry_pool.acquire()
        entry.configure(key, value, ttl, metadata)
        
        # Track resource
        tracker = get_resource_tracker()
        tracker.track_resource(
            f"cache_entry_{id(entry)}",
            ResourceType.CACHE_ENTRY,
            entry.get_memory_size(),
            entry
        )
        
        return entry
    
    def release_cache_entry(self, entry: CacheEntry) -> bool:
        """Release cache entry back to pool."""
        # Untrack resource
        tracker = get_resource_tracker()
        tracker.untrack_resource(f"cache_entry_{id(entry)}", reused=True)
        
        return self.cache_entry_pool.release(entry)
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get statistics for all translation pools."""
        return {
            "translation_requests": self.translation_request_pool.get_stats().__dict__,
            "pattern_matches": self.pattern_match_pool.get_stats().__dict__,
            "ast_nodes": self.ast_node_pool.get_stats().__dict__,
            "cache_entries": self.cache_entry_pool.get_stats().__dict__
        }
    
    def optimize_pools(self) -> None:
        """Optimize pool sizes based on usage patterns."""
        memory_manager = get_memory_manager()
        memory_manager.optimize_pools()
    
    def cleanup(self, aggressive: bool = False) -> Dict[str, int]:
        """Clean up all pools."""
        cleanup_stats = {}
        
        if aggressive:
            cleanup_stats["translation_requests"] = self.translation_request_pool.clear()
            cleanup_stats["pattern_matches"] = self.pattern_match_pool.clear()
            cleanup_stats["ast_nodes"] = self.ast_node_pool.clear()
            cleanup_stats["cache_entries"] = self.cache_entry_pool.clear()
        else:
            # Gentle cleanup - just resize based on current usage
            for name, pool in [
                ("translation_requests", self.translation_request_pool),
                ("pattern_matches", self.pattern_match_pool),
                ("ast_nodes", self.ast_node_pool),
                ("cache_entries", self.cache_entry_pool)
            ]:
                current_size = len(pool.pool)
                if current_size > pool.max_size // 2:
                    pool.resize(pool.max_size // 2)
                    cleanup_stats[name] = current_size - len(pool.pool)
                else:
                    cleanup_stats[name] = 0
        
        return cleanup_stats


# Global translation pools instance
_translation_pools: Optional[TranslationPools] = None


def get_translation_pools() -> TranslationPools:
    """Get or create the global translation pools instance."""
    global _translation_pools
    if _translation_pools is None:
        _translation_pools = TranslationPools()
    return _translation_pools


def initialize_translation_pools() -> TranslationPools:
    """Initialize and return the translation pools."""
    global _translation_pools
    _translation_pools = TranslationPools()
    return _translation_pools