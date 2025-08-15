#!/usr/bin/env python3
"""Direct test to identify ILR translation bugs."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now test the specific parsing issue
def test_numeric_constant_bug():
    """Test the NumericConstant construction bug."""
    from domain.ilr_types import NumericConstant
    
    print("=== Testing NumericConstant Construction ===")
    
    # This is what the error shows - a stray "T" is being added
    test_cases = [
        42,
        3.14,
        -10,
        0,
        1.0
    ]
    
    for value in test_cases:
        try:
            # According to ilr_types.py, NumericConstant only takes value parameter
            node = NumericConstant(value=value)
            print(f"✓ NumericConstant({value}) created successfully")
            print(f"  Type: {node.node_type.value}")
            print(f"  Dict: {node.to_dict()}")
        except Exception as e:
            print(f"✗ NumericConstant({value}) failed: {e}")
        print()

def test_arithmetic_expression_bug():
    """Test ArithmeticExpression construction."""
    from domain.ilr_types import ArithmeticExpression, ArithmeticOperator, NumericConstant
    
    print("\n=== Testing ArithmeticExpression Construction ===")
    
    # Create operands
    left = NumericConstant(value=2)
    right = NumericConstant(value=3)
    
    # Test creating arithmetic expression
    try:
        # According to ilr_types.py, ArithmeticExpression takes operator and operands list
        expr = ArithmeticExpression(
            operator=ArithmeticOperator.ADD,
            operands=[left, right]
        )
        print(f"✓ ArithmeticExpression created successfully")
        print(f"  Dict: {expr.to_dict()}")
    except Exception as e:
        print(f"✗ ArithmeticExpression failed: {e}")
        import traceback
        traceback.print_exc()

def test_expression_parsing():
    """Test expression parsing service."""
    try:
        # We need to handle the import issue properly
        import domain.ilr_expression_service as expr_service
        import domain.ilr_types as types
        import infrastructure.ilr_infrastructure as infra
        
        # Patch the imports in the module
        expr_service.ExpressionTokenizer = infra.ExpressionTokenizer
        expr_service.TemporalReferenceParser = infra.TemporalReferenceParser
        expr_service.ParenthesesSplitter = infra.ParenthesesSplitter
        expr_service.OperatorMapper = infra.OperatorMapper
        
        print("\n=== Testing Expression Parsing ===")
        
        service = expr_service.ExpressionParsingService()
        
        # Test simple numeric parsing
        test_cases = [
            "42",
            "3.14",
            "x + y",
            "f(x)",
            "2 * 3"
        ]
        
        for test_case in test_cases:
            print(f"\nParsing: '{test_case}'")
            try:
                result = service.parse_expression(test_case)
                if hasattr(result, 'unwrap'):
                    node = result.unwrap()
                    print(f"  ✓ Success: {type(node).__name__}")
                else:
                    print(f"  ✗ Failed: {result}")
            except Exception as e:
                print(f"  ✗ Exception: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
    
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        print("Trying alternate approach...")
        
        # Load the file content and check for the bug
        with open('domain/ilr_expression_service.py', 'r') as f:
            content = f.read()
            
        print("\n=== Analyzing ilr_expression_service.py for bugs ===")
        
        # Look for the stray "T" issue
        import re
        
        # Find NumericConstant constructions
        numeric_pattern = r'NumericConstant\([^)]+\)'
        matches = re.findall(numeric_pattern, content)
        
        print(f"\nFound {len(matches)} NumericConstant constructions:")
        for match in matches:
            print(f"  {match}")
            if 'T' in match and 'int' not in match and 'float' not in match:
                print(f"    ⚠️  Suspicious 'T' found!")

if __name__ == "__main__":
    test_numeric_constant_bug()
    test_arithmetic_expression_bug()
    test_expression_parsing()