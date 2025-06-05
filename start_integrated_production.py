#!/usr/bin/env python3
"""
Production startup script for TauTranslator with integrated parser-first translation.

This script demonstrates the complete integration of the parser-first approach
with pattern-based fallback into the production system.

Author: DarkLightX / Dana Edwards
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🚀 Starting TauTranslator with Parser-First Integration")
print("=" * 60)

def test_integration():
    """Test the integrated system before starting the server."""
    print("🔍 Testing Integration...")
    
    try:
        from backend.unified.translators.manager import TranslationManager
        from backend.unified.translators.grammar_translator import GrammarTranslationEngine
        from backend.unified.translators.pattern_translator import PatternTranslationEngine
        from backend.unified.translators.base import TranslationDirection
        
        # Initialize manager
        manager = TranslationManager()
        
        # Register engines (parser-first approach)
        print("🔧 Registering translation engines...")
        
        # 1. Grammar engine (parser-first)
        try:
            grammar_engine = GrammarTranslationEngine()
            manager.register_engine(grammar_engine, is_default=True)
            print("  ✅ Grammar engine registered as default")
        except Exception as e:
            print(f"  ⚠️  Grammar engine failed (will use fallback): {str(e)[:80]}...")
        
        # 2. Pattern engine (reliable fallback)
        pattern_engine = PatternTranslationEngine()
        manager.register_engine(pattern_engine, is_fallback=True)
        print("  ✅ Pattern engine registered as fallback")
        
        # Test translations
        print("\n📝 Testing translations...")
        test_cases = [
            ("x equals 5", TranslationDirection.TO_TAU),
            ("x and y", TranslationDirection.TO_TAU),
            ("not z", TranslationDirection.TO_TAU),
            ("x=5", TranslationDirection.TO_TCE),
            ("x&y", TranslationDirection.TO_TCE),
            ("!z", TranslationDirection.TO_TCE)
        ]
        
        success_count = 0
        for text, direction in test_cases:
            result = manager.translate(text, direction)
            status = "✅" if result.success else "❌"
            print(f"  {status} '{text}' → '{result.translated_text}' ({result.translation_method})")
            if result.success:
                success_count += 1
        
        success_rate = (success_count / len(test_cases)) * 100
        print(f"\n📊 Integration Test Results:")
        print(f"  Success rate: {success_rate:.1f}% ({success_count}/{len(test_cases)})")
        print(f"  Engine usage: {manager.get_statistics()['engine_usage']}")
        
        if success_rate == 100:
            print("  🎉 Integration test PASSED - System ready for production!")
            return True
        else:
            print("  ⚠️  Integration test had issues - Check configuration")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def start_server():
    """Start the production server."""
    print("\n🌐 Starting production server...")
    
    try:
        from backend.unified.server import main
        print("📡 Server starting on http://localhost:8000")
        print("📖 API documentation: http://localhost:8000/docs")
        print("🔧 Translation endpoint: http://localhost:8000/api/translate")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 60)
        
        # Start the server
        main()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("\nTroubleshooting:")
        print("1. Check if port 8000 is available")
        print("2. Install missing dependencies: pip install python-multipart")
        print("3. Check logs for detailed error information")

def main():
    """Main entry point."""
    # Test integration first
    if test_integration():
        print("\n" + "=" * 60)
        
        # Ask user if they want to start the server
        try:
            response = input("Start the production server? (y/N): ").lower().strip()
            if response in ['y', 'yes']:
                start_server()
            else:
                print("👍 Integration test completed successfully!")
                print("💡 To start the server later, run: python backend/unified/server.py")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("\n❌ Integration test failed - Server not started")
        print("🔧 Please check the configuration and try again")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())