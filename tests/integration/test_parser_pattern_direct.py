"""
Direct test of parser-pattern fallback without config dependencies.

Author: DarkLightX / Dana Edwards
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_parser_pattern_fallback():
    """Test the parser-first, pattern-fallback integration directly."""
    
    # Import engines directly to avoid config issues
    from backend.unified.translators.base import TranslationDirection
    
    print("Running Parser-Pattern Fallback Integration Tests")
    print("=" * 50)
    
    # Test 1: Pattern translator alone
    print("\n=== Test 1: Pattern Translator ===")
    try:
        from backend.unified.translators.pattern_translator import PatternTranslationEngine
        
        pattern_engine = PatternTranslationEngine()
        
        test_cases = [
            ("x equals 5", TranslationDirection.TO_TAU),
            ("x and y", TranslationDirection.TO_TAU),
            ("x > 5 & y < 10", TranslationDirection.TO_TCE),
        ]
        
        for expr, direction in test_cases:
            result = pattern_engine.translate(expr, direction)
            print(f"\nPattern: '{expr}' -> {direction.value}")
            print(f"  Success: {result.success}")
            if result.success:
                print(f"  Result: '{result.translated_text}'")
                print(f"  Confidence: {result.confidence:.2f}")
            else:
                print(f"  Error: {result.error_message}")
    
    except Exception as e:
        print(f"Pattern engine error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Grammar translator
    print("\n\n=== Test 2: Grammar Translator ===")
    try:
        # We need to mock the settings for grammar translator
        import os
        os.environ['TAU_ENABLE_GRAMMAR'] = 'true'
        
        # Create a minimal settings mock
        class MockSettings:
            enable_grammar = True
            log_level = "INFO"
            log_format = "%(message)s"
            
            def ensure_directories(self):
                pass
        
        # Temporarily replace settings
        import backend.unified.core.config as config_module
        original_settings = getattr(config_module, 'settings', None)
        config_module.settings = MockSettings()
        
        from backend.unified.translators.grammar_translator import GrammarTranslationEngine
        
        grammar_engine = GrammarTranslationEngine()
        
        test_cases = [
            ("x equals 5", TranslationDirection.TO_TAU),
            ("x > 5 & y < 10", TranslationDirection.TO_TCE),
        ]
        
        for expr, direction in test_cases:
            result = grammar_engine.translate(expr, direction)
            print(f"\nGrammar: '{expr}' -> {direction.value}")
            print(f"  Success: {result.success}")
            if result.success:
                print(f"  Result: '{result.translated_text}'")
                print(f"  Confidence: {result.confidence:.2f}")
                print(f"  Method: {result.metadata.get('engine_type', 'unknown')}")
            else:
                print(f"  Error: {result.error_message}")
        
        # Restore original settings
        if original_settings:
            config_module.settings = original_settings
            
    except Exception as e:
        print(f"Grammar engine error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Manager with fallback
    print("\n\n=== Test 3: Translation Manager with Fallback ===")
    try:
        # Ensure we have settings available
        import backend.unified.core.config as config_module
        if not hasattr(config_module, 'settings'):
            config_module.settings = MockSettings()
        
        from backend.unified.translators.manager import TranslationManager
        
        manager = TranslationManager()
        
        # Register engines
        pattern_engine = PatternTranslationEngine()
        manager.register_engine(pattern_engine, is_fallback=True)
        
        try:
            grammar_engine = GrammarTranslationEngine()
            manager.register_engine(grammar_engine, is_default=True)
            print("Grammar engine registered as default")
        except:
            print("Could not register grammar engine")
        
        # Test translations
        test_cases = [
            ("x equals 5", TranslationDirection.TO_TAU, "Simple TCE"),
            ("x and and y", TranslationDirection.TO_TAU, "Malformed (should use fallback)"),
            ("x > 5 & y < 10", TranslationDirection.TO_TCE, "Tau to TCE"),
        ]
        
        for expr, direction, description in test_cases:
            print(f"\n{description}: '{expr}'")
            result = manager.translate(expr, direction)
            
            if result.success:
                print(f"  ✓ Success via {result.translation_method}")
                print(f"  Result: '{result.translated_text}'")
                print(f"  Confidence: {result.confidence:.2f}")
            else:
                print(f"  ✗ Failed: {result.error_message}")
        
        # Show statistics
        stats = manager.get_statistics()
        print(f"\nStatistics:")
        print(f"  Total: {stats['total_translations']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Engine usage: {stats['engine_usage']}")
        
    except Exception as e:
        print(f"Manager error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    test_parser_pattern_fallback()