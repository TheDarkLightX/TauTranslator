"""
Simple test runner for parser-pattern fallback tests.

This runs the tests without requiring pytest.

Author: DarkLightX / Dana Edwards
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.grammar_translator import GrammarTranslationEngine
from backend.unified.translators.pattern_translator import PatternTranslationEngine
from backend.unified.translators.base import TranslationDirection


def setup_translation_manager():
    """Create a translation manager with grammar and pattern engines."""
    manager = TranslationManager()
    
    # Register grammar engine as default
    grammar_engine = GrammarTranslationEngine()
    manager.register_engine(grammar_engine, is_default=True)
    
    # Register pattern engine as fallback
    pattern_engine = PatternTranslationEngine()
    manager.register_engine(pattern_engine, is_fallback=True)
    
    return manager


def test_simple_translations():
    """Test basic translations."""
    print("\n=== Testing Simple Translations ===")
    manager = setup_translation_manager()
    
    # Test TCE to Tau
    test_cases = [
        ("x equals 5", TranslationDirection.TO_TAU, "TCE to Tau"),
        ("x > 5 & y < 10", TranslationDirection.TO_TCE, "Tau to TCE"),
        ("x equals 5 and y equals 10", TranslationDirection.TO_TAU, "Complex TCE to Tau"),
    ]
    
    for expr, direction, description in test_cases:
        print(f"\n{description}: '{expr}'")
        result = manager.translate(expr, direction)
        
        if result.success:
            print(f"✓ Success: '{result.translated_text}'")
            print(f"  Engine: {result.translation_method}")
            print(f"  Confidence: {result.confidence:.2f}")
            if result.metadata:
                print(f"  Metadata: {result.metadata}")
        else:
            print(f"✗ Failed: {result.error_message}")


def test_fallback_behavior():
    """Test that pattern fallback works when grammar fails."""
    print("\n\n=== Testing Fallback Behavior ===")
    manager = setup_translation_manager()
    
    # These should trigger fallback
    fallback_cases = [
        "x and and y or not z",  # Malformed
        "this is not valid syntax!!!",  # Invalid
        "x + + + y",  # Multiple operators
    ]
    
    for expr in fallback_cases:
        print(f"\nTesting fallback for: '{expr}'")
        result = manager.translate(expr, TranslationDirection.TO_TAU)
        
        if result.success:
            print(f"✓ Translation succeeded (likely via fallback)")
            print(f"  Result: '{result.translated_text}'")
            print(f"  Engine: {result.translation_method}")
            print(f"  Confidence: {result.confidence:.2f}")
        else:
            print(f"✗ Translation failed completely: {result.error_message}")


def test_engine_statistics():
    """Test that engine usage is tracked correctly."""
    print("\n\n=== Testing Engine Statistics ===")
    manager = setup_translation_manager()
    
    # Reset stats
    manager.reset_statistics()
    
    # Do various translations
    test_exprs = [
        ("x equals 5", TranslationDirection.TO_TAU),
        ("y > 10", TranslationDirection.TO_TCE),
        ("malformed expr", TranslationDirection.TO_TAU),
        ("a and b", TranslationDirection.TO_TAU),
    ]
    
    for expr, direction in test_exprs:
        manager.translate(expr, direction)
    
    stats = manager.get_statistics()
    print(f"\nTranslation Statistics:")
    print(f"  Total: {stats['total_translations']}")
    print(f"  Successful: {stats['successful_translations']}")
    print(f"  Failed: {stats['failed_translations']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Engine Usage: {stats['engine_usage']}")


def test_engine_specific_requests():
    """Test requesting specific engines."""
    print("\n\n=== Testing Engine-Specific Requests ===")
    manager = setup_translation_manager()
    
    expr = "x equals 5"
    
    # Try with grammar engine
    print(f"\nForcing grammar engine for: '{expr}'")
    grammar_result = manager.translate(expr, TranslationDirection.TO_TAU, engine_name="grammar_aware")
    print(f"  Engine used: {grammar_result.translation_method}")
    print(f"  Result: '{grammar_result.translated_text}'")
    
    # Try with pattern engine
    print(f"\nForcing pattern engine for: '{expr}'")
    pattern_result = manager.translate(expr, TranslationDirection.TO_TAU, engine_name="pattern_based")
    print(f"  Engine used: {pattern_result.translation_method}")
    print(f"  Result: '{pattern_result.translated_text}'")
    
    # Compare results
    if grammar_result.translated_text != pattern_result.translated_text:
        print("\n  Note: Different engines produced different results!")


def test_parallel_translation():
    """Test parallel translation with multiple engines."""
    print("\n\n=== Testing Parallel Translation ===")
    manager = setup_translation_manager()
    
    expr = "x equals 5 and y > 10"
    print(f"\nParallel translation of: '{expr}'")
    
    results = manager.translate_parallel(expr, TranslationDirection.TO_TAU)
    
    print(f"\nGot {len(results)} results:")
    for i, result in enumerate(results):
        print(f"\n  Result {i+1}:")
        print(f"    Engine: {result.translation_method}")
        print(f"    Success: {result.success}")
        if result.success:
            print(f"    Translation: '{result.translated_text}'")
            print(f"    Confidence: {result.confidence:.2f}")
        else:
            print(f"    Error: {result.error_message}")


def test_health_check():
    """Test health check functionality."""
    print("\n\n=== Testing Health Check ===")
    manager = setup_translation_manager()
    
    health = manager.health_check()
    
    print(f"\nOverall Status: {health['overall_status']}")
    print("\nEngine Health:")
    for engine_name, engine_health in health['engines'].items():
        print(f"  {engine_name}:")
        print(f"    Status: {engine_health['status']}")
        print(f"    Available: {engine_health['is_available']}")
        if engine_health['last_error']:
            print(f"    Last Error: {engine_health['last_error']}")


def main():
    """Run all tests."""
    print("Running Parser-Pattern Fallback Integration Tests")
    print("=" * 50)
    
    try:
        test_simple_translations()
        test_fallback_behavior()
        test_engine_statistics()
        test_engine_specific_requests()
        test_parallel_translation()
        test_health_check()
        
        print("\n\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()