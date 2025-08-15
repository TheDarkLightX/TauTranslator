#!/usr/bin/env python3
"""
Test script to verify quantifier and conditional grammar fixes.

This script tests the specific fixes made to the TCE grammar:
1. Quantifiers with both colon and "such that" syntax
2. Conditional if-then-else expressions  
3. Arithmetic operators

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_tce_parser():
    """Test the fixed TCE parser with quantifiers and conditionals."""
    
    try:
        from lark import Lark, Tree
        
        # Load the fixed TCE grammar
        grammar_path = project_root / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
        
        if not grammar_path.exists():
            print(f"❌ Grammar file not found: {grammar_path}")
            return False
            
        with open(grammar_path, 'r') as f:
            grammar_content = f.read()
        
        # Create parser
        parser = Lark(
            grammar_content,
            parser='lalr',
            start='start',
            propagate_positions=True
        )
        
        print("✅ Parser created successfully")
        
        # Test cases for quantifiers
        quantifier_tests = [
            "forall x: p(x).",  # Tau style with colon
            "forall x such that p(x).",  # TCE style with such that
            "exists y: q(y).",  # Tau style exists
            "exists y such that q(y).",  # TCE style exists
        ]
        
        print("\n🔬 Testing Quantifiers:")
        for test_case in quantifier_tests:
            try:
                result = parser.parse(test_case)
                print(f"  ✅ '{test_case}' -> parsed successfully")
            except Exception as e:
                print(f"  ❌ '{test_case}' -> {e}")
                return False
        
        # Test cases for conditionals
        conditional_tests = [
            "if p(x) then q(x) else r(x).",  # Simple conditional
            "if x > 5 then true else false.",  # Conditional with comparison
        ]
        
        print("\n🔬 Testing Conditionals:")
        for test_case in conditional_tests:
            try:
                result = parser.parse(test_case)
                print(f"  ✅ '{test_case}' -> parsed successfully")
            except Exception as e:
                print(f"  ❌ '{test_case}' -> {e}")
                return False
        
        # Test cases for arithmetic
        arithmetic_tests = [
            "x + y.",  # Addition
            "x - y * z.",  # Mixed operations with precedence
            "x / (y + z).",  # Division with parentheses
            "x % 5.",  # Modulo
        ]
        
        print("\n🔬 Testing Arithmetic:")
        for test_case in arithmetic_tests:
            try:
                result = parser.parse(test_case)
                print(f"  ✅ '{test_case}' -> parsed successfully")
            except Exception as e:
                print(f"  ❌ '{test_case}' -> {e}")
                return False
        
        print("\n🎉 All grammar fixes verified successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure lark is installed: pip install lark")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_bidirectional_engine():
    """Test the bidirectional translation engine."""
    
    try:
        # Try to import the bidirectional engine
        backend_path = project_root / "backend/unified"
        sys.path.insert(0, str(backend_path))
        
        from translators.bidirectional_engine import BidirectionalTranslationEngine
        
        print("\n🔗 Testing Bidirectional Engine:")
        
        # Create engine
        engine = BidirectionalTranslationEngine()
        print("  ✅ Engine created successfully")
        
        # Test basic translation detection
        test_cases = [
            ("forall x: p(x)", "English"),
            ("∀x: p(x)", "TAU"),
            ("for all x such that p(x)", "English"),
        ]
        
        for text, expected_lang in test_cases:
            detected = engine.detect_language(text)
            print(f"  🔍 '{text}' detected as: {detected}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import bidirectional engine: {e}")
        return False
    except Exception as e:
        print(f"❌ Bidirectional engine test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Grammar Fixes")
    print("=" * 50)
    
    success = True
    
    # Test parser fixes
    if not test_tce_parser():
        success = False
    
    # Test bidirectional engine
    if not test_bidirectional_engine():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Grammar fixes are working.")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    sys.exit(0 if success else 1)