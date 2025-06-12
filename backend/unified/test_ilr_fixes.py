#!/usr/bin/env python3
"""Test the fixes for ILR bugs."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from domain.ilr_types import (
    NumericConstant, BooleanConstant, StringConstant,
    ArithmeticExpression, ArithmeticOperator
)

def test_fixed_constructors():
    """Test the correct way to construct ILR nodes."""
    print("=== Testing Fixed Constructors ===\n")
    
    # Test NumericConstant with named parameter
    print("1. NumericConstant:")
    try:
        nc1 = NumericConstant(value=42)
        print(f"   ✓ NumericConstant(value=42) works!")
        print(f"     {nc1.to_dict()}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test BooleanConstant
    print("\n2. BooleanConstant:")
    try:
        bc1 = BooleanConstant(value=True)
        print(f"   ✓ BooleanConstant(value=True) works!")
        print(f"     {bc1.to_dict()}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test StringConstant
    print("\n3. StringConstant:")
    try:
        sc1 = StringConstant(value="hello")
        print(f"   ✓ StringConstant(value='hello') works!")
        print(f"     {sc1.to_dict()}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test ArithmeticExpression
    print("\n4. ArithmeticExpression:")
    try:
        left = NumericConstant(value=2)
        right = NumericConstant(value=3)
        ae1 = ArithmeticExpression(
            operator=ArithmeticOperator.ADD,
            operands=[left, right]
        )
        print(f"   ✓ ArithmeticExpression works!")
        print(f"     {ae1.to_dict()}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

def demonstrate_bug():
    """Demonstrate the original bug."""
    print("\n\n=== Demonstrating Original Bug ===\n")
    
    print("Trying: NumericConstant(42) without named parameter:")
    try:
        nc_bad = NumericConstant(42)
        print(f"   Unexpected success: {nc_bad}")
    except TypeError as e:
        print(f"   ✓ Expected TypeError: {e}")
    
    print("\nTrying: BooleanConstant(True) without named parameter:")
    try:
        bc_bad = BooleanConstant(True)
        print(f"   Unexpected success: {bc_bad}")
    except TypeError as e:
        print(f"   ✓ Expected TypeError: {e}")

def show_correct_patterns():
    """Show the correct construction patterns."""
    print("\n\n=== Correct Construction Patterns ===\n")
    
    print("For ilr_expression_service.py fixes:\n")
    
    print("1. Numeric constants:")
    print("   OLD: return Success(NumericConstant(float(text)))")
    print("   NEW: return Success(NumericConstant(value=float(text)))")
    print()
    
    print("2. Boolean constants:")
    print("   OLD: return Success(BooleanConstant(text.lower() == 'true'))")
    print("   NEW: return Success(BooleanConstant(value=(text.lower() == 'true')))")
    print()
    
    print("3. String constants:")
    print("   OLD: return Success(StringConstant(text[1:-1]))")
    print("   NEW: return Success(StringConstant(value=text[1:-1]))")

if __name__ == "__main__":
    test_fixed_constructors()
    demonstrate_bug()
    show_correct_patterns()