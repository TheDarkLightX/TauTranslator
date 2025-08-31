"""
Example Usage of Advanced Caching in Translation Pipeline

Demonstrates how to integrate the caching system with actual translation components.

Author: DarkLightX / Dana Edwards
"""

import time
import random
from typing import Dict, Any, List

from translation_cache_integration import (
    TranslationCacheConfig, TranslationCacheManager,
    cached_translation, get_translation_cache_manager,
    configure_translation_cache
)
from advanced_cache import CachePolicy


# Example translation functions that would normally be expensive

@cached_translation('pattern')
def match_complex_pattern(pattern: str, text: str) -> Dict[str, Any]:
    """Simulate expensive pattern matching operation."""
    print(f"[SLOW] Matching pattern '{pattern}' against text...")
    time.sleep(0.1)  # Simulate computation
    
    # Mock result
    return {
        'matched': True,
        'groups': ['group1', 'group2'],
        'confidence': 0.95
    }


@cached_translation('grammar')
def parse_grammar_file(grammar_id: str) -> Dict[str, Any]:
    """Simulate parsing a grammar file."""
    print(f"[SLOW] Parsing grammar '{grammar_id}'...")
    time.sleep(0.2)  # Simulate parsing
    
    return {
        'rules': [
            {'name': 'rule1', 'pattern': 'pattern1'},
            {'name': 'rule2', 'pattern': 'pattern2'}
        ],
        'version': '1.0',
        'compiled': True
    }


@cached_translation('nlp')
def analyze_natural_language(text: str) -> Dict[str, Any]:
    """Simulate NLP analysis."""
    print(f"[SLOW] Analyzing text: '{text[:50]}...'")
    time.sleep(0.15)  # Simulate NLP processing
    
    return {
        'entities': ['user', 'system', 'data'],
        'intent': 'requirement_specification',
        'sentiment': 'neutral',
        'keywords': text.split()[:5]
    }


@cached_translation('translation')
def translate_to_tau(source: str, target_format: str) -> str:
    """Simulate translation to Tau language."""
    print(f"[SLOW] Translating to {target_format}: '{source[:30]}...'")
    time.sleep(0.3)  # Simulate translation
    
    # Mock translation
    if target_format == 'tau':
        return f"∀x ∈ Domain: {source}"
    elif target_format == 'lmql':
        return f"query: {source}"
    else:
        return f"[{target_format}] {source}"


class TranslationPipeline:
    """Example translation pipeline with integrated caching."""
    
    def __init__(self):
        # Configure caching for optimal performance
        config = TranslationCacheConfig(
            pattern_cache_size=20000,
            grammar_cache_size=2000,
            nlp_cache_size=10000,
            result_cache_size=100000,
            result_ttl=600.0,  # 10 minutes for results
            pattern_policy=CachePolicy.LFU,  # Patterns are reused frequently
            grammar_policy=CachePolicy.LRU,  # Recent grammars likely used again
            nlp_policy=CachePolicy.ARC,      # Adaptive for varying workloads
            result_policy=CachePolicy.TTL     # Time-based for final results
        )
        
        configure_translation_cache(config)
        self.cache_manager = get_translation_cache_manager()
    
    def translate(self, text: str, target_format: str = 'tau') -> Dict[str, Any]:
        """Full translation pipeline with caching."""
        start_time = time.time()
        
        # Step 1: NLP Analysis (cached)
        nlp_result = analyze_natural_language(text)
        
        # Step 2: Pattern Matching (cached)
        patterns_matched = []
        for keyword in nlp_result['keywords']:
            pattern_result = match_complex_pattern(f".*{keyword}.*", text)
            if pattern_result['matched']:
                patterns_matched.append(pattern_result)
        
        # Step 3: Grammar Selection (cached)
        grammar = parse_grammar_file(f"grammar_{target_format}_v1")
        
        # Step 4: Final Translation (cached)
        translation = translate_to_tau(text, target_format)
        
        elapsed = time.time() - start_time
        
        return {
            'source': text,
            'target_format': target_format,
            'translation': translation,
            'nlp_analysis': nlp_result,
            'patterns': patterns_matched,
            'grammar_used': grammar['version'],
            'processing_time': elapsed
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report."""
        stats = self.cache_manager.get_statistics()
        
        # Calculate overall performance metrics
        total_lookups = sum(stats['lookups'].values())
        
        # Get cache hit rates
        cache_performance = {}
        for cache_name, cache_stats in stats['caches'].items():
            if isinstance(cache_stats, dict) and 'hit_rate' in cache_stats:
                cache_performance[cache_name] = {
                    'hit_rate': cache_stats['hit_rate'],
                    'size': cache_stats.get('size', 0)
                }
        
        return {
            'total_lookups': total_lookups,
            'time_saved': stats['lookups']['total_time_saved'],
            'cache_performance': cache_performance,
            'detailed_stats': stats
        }


def demonstrate_caching_benefits():
    """Demonstrate the performance benefits of caching."""
    print("=== Translation Pipeline Caching Demo ===\n")
    
    pipeline = TranslationPipeline()
    
    # Test sentences
    test_sentences = [
        "The user must provide valid authentication credentials",
        "System shall process requests within 100 milliseconds",
        "All data must be encrypted using AES-256",
        "The user must provide valid authentication credentials",  # Duplicate
        "System shall process requests within 100 milliseconds",  # Duplicate
    ]
    
    print("Processing sentences...\n")
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n--- Request {i} ---")
        result = pipeline.translate(sentence, 'tau')
        print(f"Translation: {result['translation']}")
        print(f"Processing time: {result['processing_time']:.3f}s")
        
        if i > 3:  # Show cache benefits on duplicates
            print("(✓ Cache hit - much faster!)")
    
    # Show performance report
    print("\n\n=== Performance Report ===")
    report = pipeline.get_performance_report()
    
    print(f"\nTotal API calls: {report['total_lookups']}")
    print(f"Time saved by caching: {report['time_saved']:.2f}s")
    
    print("\nCache Performance:")
    for cache_name, perf in report['cache_performance'].items():
        print(f"  {cache_name}:")
        print(f"    - Hit Rate: {perf['hit_rate']:.1f}%")
        print(f"    - Size: {perf['size']} entries")
    
    # Demonstrate cache warming
    print("\n\n=== Cache Warming Demo ===")
    
    # Prepare warmup data
    warmup_data = {
        'patterns': {
            '.*security.*': {'matched': True, 'groups': ['security']},
            '.*performance.*': {'matched': True, 'groups': ['performance']},
        },
        'grammars': {
            'grammar_tau_v2': {'rules': [], 'version': '2.0', 'compiled': True},
            'grammar_lmql_v1': {'rules': [], 'version': '1.0', 'compiled': True},
        },
        'nlp': {
            'Security is important': {'entities': ['security'], 'intent': 'statement'},
            'Performance matters': {'entities': ['performance'], 'intent': 'statement'},
        }
    }
    
    print("Warming caches with common patterns...")
    pipeline.cache_manager.warm_caches(warmup_data)
    print("Cache warming complete!")
    
    # Test with warmed cache
    print("\nTesting with warmed cache:")
    result = match_complex_pattern('.*security.*', 'Security is critical')
    print(f"Pattern match result (should be instant): {result}")


if __name__ == "__main__":
    demonstrate_caching_benefits()