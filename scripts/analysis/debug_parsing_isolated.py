#!/usr/bin/env python3
"""
Isolated test for parsing debugging
"""
import sys
sys.path.insert(0, 'src')

from tau_translator_omega.core_engine.ilr_translator import (
    NaturalLanguageToILRTranslator,
    ILRToTauTranslator
)

def test_parsing():
    """Test the parsing directly."""
    translator = NaturalLanguageToILRTranslator()
    
    # Test the expression parsing directly
    expr = "(a and b) or (a and c) or (b and c)"
    print(f"Testing expression: {expr}")
    
    # Test parameter context
    param_context = {"a": "VARIABLE", "b": "VARIABLE", "c": "VARIABLE"}
    
    result = translator._parse_expression(expr, param_context)
    print(f"Parse result: {result}")
    
    print(f"Operator: {result.get('operator')}")
    print(f"Operands count: {len(result.get('operands', []))}")
    
    for i, operand in enumerate(result.get('operands', [])):
        print(f"Operand {i}: {operand}")
    
    # Test the full function
    print("\n" + "="*50)
    print("Testing full function definition:")
    
    input_text = 'fullAdderCarry(a, b, c) := (a and b) or (a and c) or (b and c).'
    print(f"Input: {input_text}")
    
    ilr = translator.translate_to_ilr(input_text)
    print(f"ILR: {ilr}")
    
    tau_translator = ILRToTauTranslator()
    tau_output = tau_translator.translate_to_tau(ilr)
    print(f"TAU: {tau_output}")
    
    expected = 'fullAdderCarry(a, b, c) := (a & b) \\\\ (a & c) \\\\ (b & c)'
    print(f"Expected: {expected}")
    print(f"Match: {tau_output == expected}")

if __name__ == "__main__":
    test_parsing()