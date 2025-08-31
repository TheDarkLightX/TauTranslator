"""
Integration example for memory optimization in translation pipeline.

Demonstrates how to integrate object pooling and resource tracking
into the existing translation workflow.

Author: DarkLightX / Dana Edwards
"""

import time
import logging
from typing import Dict, List, Optional, Any
from .translation_pools import get_translation_pools
from .object_pools import get_memory_manager, start_memory_management, MemoryPressure
from .resource_tracker import get_resource_tracker, ResourceType


class MemoryOptimizedTranslator:
    """
    Example translator that uses memory optimization features.
    
    This shows how to integrate object pooling into a real translation pipeline.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pools = get_translation_pools()
        self.memory_manager = get_memory_manager()
        self.resource_tracker = get_resource_tracker()
        
        # Start memory management
        start_memory_management()
        
        # Register memory pressure callbacks
        self.memory_manager.add_pressure_callback(
            MemoryPressure.HIGH,
            self._handle_high_memory_pressure
        )
        
        self.memory_manager.add_pressure_callback(
            MemoryPressure.CRITICAL,
            self._handle_critical_memory_pressure
        )
        
        self.logger.info("Memory-optimized translator initialized")
    
    def translate(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Translate text with memory-optimized pipeline.
        
        This method demonstrates:
        1. Using pooled translation requests
        2. Using pooled pattern matches
        3. Using pooled AST nodes
        4. Using pooled cache entries
        5. Proper resource tracking
        """
        
        # 1. Acquire translation request from pool
        request = self.pools.acquire_translation_request(
            source_text=source_text,
            source_language=source_language,
            target_language=target_language,
            options=options,
            request_id=f"req_{int(time.time() * 1000)}"
        )
        
        try:
            # 2. Check cache using pooled cache entry
            cache_key = f"{source_language}_{target_language}_{hash(source_text)}"
            cached_result = self._check_cache(cache_key)
            
            if cached_result:
                self.logger.info(f"Cache hit for request {request.request_id}")
                return cached_result
            
            # 3. Parse source text using pooled AST nodes
            ast_root = self._parse_text(source_text, source_language)
            
            # 4. Pattern matching using pooled match results
            patterns = self._match_patterns(source_text)
            
            # 5. Perform translation (simplified)
            translated_text = self._perform_translation(
                ast_root, patterns, target_language
            )
            
            # 6. Cache result using pooled cache entry
            result = {
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "timestamp": time.time(),
                "patterns_matched": len(patterns)
            }
            
            self._cache_result(cache_key, result)
            
            return result
            
        finally:
            # Always release resources
            self.pools.release_translation_request(request)
    
    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Check cache using pooled cache entry."""
        # In a real implementation, this would check an actual cache
        # For demo, we'll just show the pooling pattern
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache result using pooled cache entry."""
        entry = self.pools.acquire_cache_entry(
            key=cache_key,
            value=result,
            ttl=3600.0,  # 1 hour TTL
            metadata={"cached_at": time.time()}
        )
        
        try:
            # In a real implementation, store in cache backend
            self.logger.debug(f"Cached result for key: {cache_key}")
        finally:
            self.pools.release_cache_entry(entry)
    
    def _parse_text(self, text: str, language: str) -> Any:
        """Parse text into AST using pooled nodes."""
        # Create root node
        root = self.pools.acquire_ast_node(
            node_type="Program",
            attributes={"language": language}
        )
        
        # Simulate parsing - create some child nodes
        sentences = text.split('. ')
        for i, sentence in enumerate(sentences):
            sentence_node = self.pools.acquire_ast_node(
                node_type="Sentence",
                value=sentence,
                line_number=i + 1
            )
            
            # Add word nodes
            words = sentence.split()
            for j, word in enumerate(words):
                word_node = self.pools.acquire_ast_node(
                    node_type="Word",
                    value=word,
                    column_number=j
                )
                sentence_node.add_child(word_node)
            
            root.add_child(sentence_node)
        
        return root
    
    def _match_patterns(self, text: str) -> List[Any]:
        """Match patterns using pooled match results."""
        patterns = []
        
        # Simulate pattern matching
        # Example: Find email patterns
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for match in re.finditer(email_pattern, text):
            pattern_match = self.pools.acquire_pattern_match(
                pattern_name="email",
                matched_text=match.group(),
                start_position=match.start(),
                end_position=match.end(),
                confidence=0.95,
                metadata={"type": "email_address"}
            )
            patterns.append(pattern_match)
        
        # Example: Find number patterns
        number_pattern = r'\b\d+\b'
        
        for match in re.finditer(number_pattern, text):
            pattern_match = self.pools.acquire_pattern_match(
                pattern_name="number",
                matched_text=match.group(),
                start_position=match.start(),
                end_position=match.end(),
                confidence=1.0,
                metadata={"type": "numeric"}
            )
            patterns.append(pattern_match)
        
        return patterns
    
    def _perform_translation(
        self,
        ast_root: Any,
        patterns: List[Any],
        target_language: str
    ) -> str:
        """Perform translation (simplified for demo)."""
        # In a real implementation, this would use the AST and patterns
        # to generate proper translation
        
        # For demo, just collect words from AST
        words = []
        
        def collect_words(node):
            if node.node_type == "Word":
                words.append(node.value)
            for child in node.children:
                collect_words(child)
        
        collect_words(ast_root)
        
        # Clean up AST nodes after use
        self.pools.release_ast_node(ast_root)
        
        # Clean up pattern matches
        for pattern in patterns:
            self.pools.release_pattern_match(pattern)
        
        # Return simulated translation
        return f"[{target_language}] " + " ".join(words)
    
    def _handle_high_memory_pressure(self, pressure: MemoryPressure) -> None:
        """Handle high memory pressure."""
        self.logger.warning("High memory pressure detected - optimizing pools")
        
        # Reduce pool sizes
        self.pools.cleanup(aggressive=False)
        
        # Take memory snapshot for analysis
        snapshot = self.resource_tracker.take_snapshot()
        self.logger.info(
            f"Memory snapshot: {snapshot.tracked_resources} resources, "
            f"{snapshot.process_memory / (1024*1024):.1f}MB used"
        )
    
    def _handle_critical_memory_pressure(self, pressure: MemoryPressure) -> None:
        """Handle critical memory pressure."""
        self.logger.error("Critical memory pressure - aggressive cleanup")
        
        # Aggressive cleanup
        self.pools.cleanup(aggressive=True)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Export diagnostic data
        self.resource_tracker.export_snapshot_data("memory_critical_dump.json")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        return {
            "pool_stats": self.pools.get_pool_statistics(),
            "resource_stats": self.resource_tracker.get_resource_stats(),
            "memory_stats": self.memory_manager.get_memory_stats().__dict__,
            "cleanup_suggestions": self.resource_tracker.cleanup_suggestions()
        }


def demonstrate_memory_optimization():
    """
    Demonstration of memory optimization in action.
    """
    logging.basicConfig(level=logging.INFO)
    
    # Create translator
    translator = MemoryOptimizedTranslator()
    
    # Perform multiple translations to show pooling benefits
    test_texts = [
        "Hello world! This is a test email: user@example.com",
        "The quick brown fox jumps over the lazy dog.",
        "Python 3.9 was released in 2020 with many improvements.",
        "Contact us at support@company.com or call 555-1234.",
        "Machine translation has improved significantly in recent years."
    ]
    
    print("Starting translation demonstrations...\n")
    
    for i, text in enumerate(test_texts):
        print(f"Translation {i+1}:")
        print(f"Source: {text}")
        
        result = translator.translate(
            source_text=text,
            source_language="en",
            target_language="es"
        )
        
        print(f"Result: {result['translated_text']}")
        print(f"Patterns matched: {result['patterns_matched']}")
        print()
    
    # Show memory statistics
    print("\nMemory Statistics:")
    stats = translator.get_memory_stats()
    
    print("\nPool Statistics:")
    for pool_name, pool_stats in stats['pool_stats'].items():
        print(f"\n{pool_name}:")
        print(f"  - Created objects: {pool_stats['created_objects']}")
        print(f"  - Reused objects: {pool_stats['reused_objects']}")
        print(f"  - Reuse rate: {pool_stats['reuse_rate']:.1f}%")
        print(f"  - Current pool size: {pool_stats['current_size']}")
    
    print("\nResource Tracking:")
    resource_stats = stats['resource_stats']
    print(f"  - Active resources: {resource_stats['active_resources']}")
    print(f"  - Total allocations: {resource_stats['total_allocations']}")
    print(f"  - Reuse count: {resource_stats['reuse_count']}")
    print(f"  - Current memory: {resource_stats['current_memory'] / (1024*1024):.1f}MB")
    
    print("\nCleanup Suggestions:")
    for suggestion in stats['cleanup_suggestions']:
        print(f"  - {suggestion}")
    
    # Simulate memory pressure
    print("\nSimulating memory pressure...")
    translator._handle_high_memory_pressure(MemoryPressure.HIGH)
    
    # Final statistics
    print("\nFinal Pool Statistics After Optimization:")
    final_stats = translator.get_memory_stats()
    for pool_name, pool_stats in final_stats['pool_stats'].items():
        print(f"{pool_name}: {pool_stats['current_size']} objects in pool")


if __name__ == "__main__":
    demonstrate_memory_optimization()