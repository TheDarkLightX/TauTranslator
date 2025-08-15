#!/usr/bin/env python3
"""Test different ways to create ILR nodes."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from domain.ilr_types import (
    NumericConstant, BooleanConstant, NodeType, ILRNode
)
from dataclasses import fields

def analyze_dataclass():
    """Analyze the dataclass structure."""
    print("=== Analyzing ILRNode Dataclass Structure ===\n")
    
    print("ILRNode fields:")
    for field in fields(ILRNode):
        print(f"  {field.name}: {field.type}, default={field.default}")
    
    print("\nNumericConstant fields:")
    for field in fields(NumericConstant):
        print(f"  {field.name}: {field.type}, default={field.default}")
    
    print("\nBooleanConstant fields:")  
    for field in fields(BooleanConstant):
        print(f"  {field.name}: {field.type}, default={field.default}")

def test_construction_methods():
    """Test different construction methods."""
    print("\n\n=== Testing Construction Methods ===\n")
    
    # Method 1: Provide node_type explicitly
    print("1. Explicit node_type:")
    try:
        nc1 = NumericConstant(node_type=NodeType.NUMERIC_CONSTANT, value=42)
        print(f"   ✓ Works! {nc1}")
        print(f"     {nc1.to_dict()}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Method 2: Try to bypass frozen restriction
    print("\n2. Using object.__setattr__ directly:")
    try:
        nc2 = object.__new__(NumericConstant)
        object.__setattr__(nc2, 'node_type', NodeType.NUMERIC_CONSTANT)
        object.__setattr__(nc2, 'value', 42)
        print(f"   ✓ Works! {nc2}")
        print(f"     {nc2.to_dict()}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Method 3: Check if __post_init__ is being called
    print("\n3. Understanding __post_init__ behavior:")
    
    class TestNode(ILRNode):
        value: int
        
        def __post_init__(self):
            print("   __post_init__ called!")
            object.__setattr__(self, 'node_type', NodeType.NUMERIC_CONSTANT)
    
    try:
        # This will fail because node_type is required
        tn = TestNode(value=42)
    except Exception as e:
        print(f"   ✗ Constructor failed (expected): {e}")
    
    # The correct way based on the dataclass structure
    print("\n4. Correct construction pattern:")
    try:
        # Since node_type is inherited from ILRNode, we must provide it
        nc3 = NumericConstant(node_type=NodeType.NUMERIC_CONSTANT, value=42)
        print(f"   ✓ NumericConstant created: {nc3.to_dict()}")
        
        bc3 = BooleanConstant(node_type=NodeType.BOOLEAN_CONSTANT, value=True)
        print(f"   ✓ BooleanConstant created: {bc3.to_dict()}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

if __name__ == "__main__":
    analyze_dataclass()
    test_construction_methods()