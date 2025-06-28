#!/usr/bin/env python3
"""Direct test of ILR expression parsing to identify bugs."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.unified.domain.ilr_expression_service import ExpressionParsingService
from domain.ilr_types import NumericConstant

def test_expression_parsing():
    """Test expression parsing to identify errors."""
    print("=== ILR Expression Parser Bug Test ===\n")
    
    service = ExpressionParsingService()
    
    # Test cases based on the errors mentioned
    test_cases = [
        # Basic numeric constants
        "42",
        "3.14",
        "-10",
        
        # Arithmetic expressions
        "x + y",
        "a - b",
        "2 * 3",
        "10 / 2",
        
        # Function calls
        "f(x)",
        "max(a, b)",
        "sum(1, 2, 3)",
        
        # Complex expressions
        "x + f(y)",
        "a * (b + c)",
        "(x + y) * z",
    ]
    
    for test_case in test_cases:
        print(f"Testing: '{test_case}'")
        try:
            result = service.parse_expression(test_case)
            if hasattr(result, 'unwrap'):
                node = result.unwrap()
                print(f"  ✓ Success: {type(node).__name__}")
                print(f"    {node.to_dict()}")
            else:
                print(f"  ✗ Failed: {result.failure()}")
        except Exception as e:
            print(f"  ✗ Exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        print()

if __name__ == "__main__":
    test_expression_parsing()