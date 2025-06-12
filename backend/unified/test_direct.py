#!/usr/bin/env python3
"""
Direct test of the unified backend translation functionality.

Run from the backend/unified directory to ensure proper imports.

Author: DarkLightX/Dana Edwards
"""

from translators.base import TranslationDirection
from translators.manager import TranslationManager
from translators.pattern_translator import PatternTranslationEngine
from translators.grammar_translator import GrammarTranslationEngine
from translators.nlp_translator import NLPTranslationEngine


def test_translations():
    """Test translation functionality with actual backend modules."""
    print("=== TauTranslator Backend Direct Test ===\n")
    
    # Initialize manager
    manager = TranslationManager()
    
    # Register engines
    print("Registering translation engines...")
    
    # Pattern engine (always available)
    pattern_engine = PatternTranslationEngine()
    manager.register_engine(pattern_engine, is_fallback=True)
    print(f"  ✓ {pattern_engine.name} - {pattern_engine.description}")
    
    # Grammar engine
    try:
        grammar_engine = GrammarTranslationEngine()
        manager.register_engine(grammar_engine, is_default=True)
        print(f"  ✓ {grammar_engine.name} - {grammar_engine.description}")
    except Exception as e:
        print(f"  ✗ Grammar engine failed: {e}")
    
    # NLP engine
    try:
        nlp_engine = NLPTranslationEngine()
        manager.register_engine(nlp_engine)
        print(f"  ✓ {nlp_engine.name} - {nlp_engine.description}")
    except Exception as e:
        print(f"  ✗ NLP engine failed: {e}")
    
    print(f"\nEngines ready: {len(manager.get_available_engines())} of {len(manager.engines)}")
    
    # Test cases
    test_cases = [
        # Basic logical operations
        ("x and y", TranslationDirection.TO_TAU),
        ("a or b", TranslationDirection.TO_TAU),
        ("not p", TranslationDirection.TO_TAU),
        
        # Mathematical operations
        ("x plus y equals z", TranslationDirection.TO_TAU),
        ("temperature greater than 25", TranslationDirection.TO_TAU),
        
        # Temporal logic
        ("x at time t", TranslationDirection.TO_TAU),
        ("always p", TranslationDirection.TO_TAU),
        ("eventually q", TranslationDirection.TO_TAU),
        
        # Reverse translations
        ("x & y", TranslationDirection.TO_TCE),
        ("a | b", TranslationDirection.TO_TCE),
        ("x + y = z", TranslationDirection.TO_TCE),
        
        # Complex expressions
        ("if x then y else z", TranslationDirection.TO_TAU),
        ("for all x in set S, property P holds", TranslationDirection.TO_TAU),
        
        # Natural language
        ("The temperature must be between 20 and 30 degrees", TranslationDirection.TO_TAU),
        ("All users must have valid passwords", TranslationDirection.TO_TAU),
    ]
    
    print("\n=== Running Translation Tests ===")
    
    for i, (text, direction) in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{text}'")
        print(f"   Direction: {direction.value}")
        
        result = manager.translate(text, direction)
        
        if result.success:
            print(f"   ✓ Output: '{result.translated_text}'")
            print(f"   Engine: {result.translation_method}")
            print(f"   Confidence: {result.confidence:.2%}")
            if result.processing_time:
                print(f"   Time: {result.processing_time:.3f}s")
        else:
            print(f"   ✗ Failed: {result.error_message}")
    
    # Show statistics
    print("\n=== Translation Statistics ===")
    stats = manager.get_statistics()
    print(f"Total: {stats['total_translations']}")
    print(f"Success: {stats['successful_translations']} ({stats['success_rate']:.1f}%)")
    print(f"Failed: {stats['failed_translations']}")
    
    print("\nEngine usage:")
    for engine, count in stats['engine_usage'].items():
        if count > 0:
            print(f"  {engine}: {count}")
    
    # Health check
    print("\n=== Engine Health Check ===")
    health = manager.health_check()
    print(f"Overall status: {health['overall_status']}")
    for engine_name, status in health['engines'].items():
        print(f"  {engine_name}: {status['status']}")
        if not status['is_available']:
            print(f"    Last error: {status['last_error']}")


def test_parallel():
    """Test parallel translation."""
    print("\n\n=== Parallel Translation Test ===")
    
    manager = TranslationManager()
    
    # Register engines
    pattern_engine = PatternTranslationEngine()
    manager.register_engine(pattern_engine)
    
    test_text = "x and y or not z"
    print(f"\nTesting parallel translation of: '{test_text}'")
    
    results = manager.translate_parallel(test_text, TranslationDirection.TO_TAU, max_engines=3)
    
    print(f"\nGot {len(results)} results:")
    for result in results:
        if result.success:
            print(f"  {result.translation_method}: '{result.translated_text}' (conf: {result.confidence:.2f})")


def main():
    """Main test function."""
    try:
        test_translations()
        test_parallel()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()