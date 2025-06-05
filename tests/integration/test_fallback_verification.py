"""
Verify parser-pattern fallback behavior in detail.

Author: DarkLightX / Dana Edwards
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_fallback_verification():
    """Verify the fallback behavior in detail."""
    
    from backend.unified.translators.base import TranslationDirection
    from backend.unified.translators.pattern_translator import PatternTranslationEngine
    from backend.unified.translators.manager import TranslationManager
    
    print("Fallback Behavior Verification")
    print("=" * 50)
    
    # Create manager
    manager = TranslationManager()
    
    # Only register pattern engine to start
    pattern_engine = PatternTranslationEngine()
    manager.register_engine(pattern_engine, is_fallback=True)
    
    print("\n1. With only pattern engine registered:")
    result = manager.translate("x equals 5", TranslationDirection.TO_TAU)
    print(f"   Result: {result.success}, Engine: {result.translation_method}, Translation: '{result.translated_text}'")
    
    # Now add a mock failing engine as default
    class FailingEngine:
        """Engine that always fails to test fallback."""
        def __init__(self):
            self.name = "failing_engine"
            self.description = "Always fails"
            self.is_available = True
            self.last_error = None
        
        def can_translate(self, text, direction):
            return True
        
        def get_supported_directions(self):
            return [TranslationDirection.TO_TAU, TranslationDirection.TO_TCE]
        
        def translate(self, text, direction, **kwargs):
            from backend.unified.translators.base import TranslationResult
            return TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method=self.name,
                direction=direction,
                error_message="Intentional failure for testing"
            )
        
        def get_status(self):
            return {
                "name": self.name,
                "available": self.is_available,
                "last_error": self.last_error
            }
    
    failing_engine = FailingEngine()
    manager.register_engine(failing_engine, is_default=True)
    
    print("\n2. With failing engine as default and pattern as fallback:")
    manager.reset_statistics()
    
    test_cases = [
        "x equals 5",
        "y > 10", 
        "a and b or c",
        "solve x > 5"
    ]
    
    for expr in test_cases:
        result = manager.translate(expr, TranslationDirection.TO_TAU)
        print(f"\n   Input: '{expr}'")
        print(f"   Success: {result.success}")
        print(f"   Engine: {result.translation_method}")
        print(f"   Translation: '{result.translated_text}'")
        if not result.success:
            print(f"   Error: {result.error_message}")
    
    # Check statistics
    stats = manager.get_statistics()
    print(f"\n3. Statistics after {stats['total_translations']} translations:")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    print(f"   Engine usage: {stats['engine_usage']}")
    
    # Test with fallback disabled
    print("\n4. Testing with fallback disabled:")
    result = manager.translate("x equals 5", TranslationDirection.TO_TAU, use_fallback=False)
    print(f"   Success: {result.success}")
    print(f"   Engine: {result.translation_method}")
    print(f"   Error: {result.error_message}")
    
    # Test parallel mode
    print("\n5. Testing parallel translation mode:")
    results = manager.translate_parallel("x equals 5 and y > 10", TranslationDirection.TO_TAU)
    print(f"   Got {len(results)} results:")
    for i, res in enumerate(results):
        print(f"   [{i+1}] Engine: {res.translation_method}, Success: {res.success}, " +
              f"Confidence: {res.confidence:.2f}")
        if res.success:
            print(f"       Translation: '{res.translated_text}'")
    
    # Test engine health check
    print("\n6. Engine health check:")
    health = manager.health_check()
    print(f"   Overall status: {health['overall_status']}")
    for engine_name, status in health['engines'].items():
        print(f"   {engine_name}: {status['status']} (available: {status['is_available']})")
    
    print("\n" + "=" * 50)
    print("Verification complete!")


if __name__ == "__main__":
    # Mock settings if needed
    import os
    os.environ['TAU_ENABLE_GRAMMAR'] = 'true'
    
    class MockSettings:
        enable_grammar = True
        log_level = "INFO"
        log_format = "%(message)s"
        
        def ensure_directories(self):
            pass
    
    import backend.unified.core.config as config_module
    if not hasattr(config_module, 'settings'):
        config_module.settings = MockSettings()
    
    test_fallback_verification()