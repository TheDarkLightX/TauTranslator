#!/usr/bin/env python3
"""
Debug the transformer to understand why it's returning None values.
"""

import os
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def debug_parse_tree():
    """Debug by examining the parse tree structure."""
    
    try:
        from lark import Lark
        
        # Load the fixed TCE grammar
        grammar_path = project_root / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
        
        with open(grammar_path, 'r') as f:
            grammar_content = f.read()
        
        # Create parser
        parser = Lark(
            grammar_content,
            parser='lalr',
            start='start',
            propagate_positions=True
        )
        
        # Test a simple case
        test_input = "x + y."
        
        print(f"🔍 Debugging parse tree for: '{test_input}'")
        
        parse_tree = parser.parse(test_input)
        print(f"\nParse Tree Structure:")
        print(parse_tree.pretty())
        
        # Now test quantifier
        test_input2 = "forall x: p(x)."
        print(f"\n🔍 Debugging parse tree for: '{test_input2}'")
        
        parse_tree2 = parser.parse(test_input2)
        print(f"\nParse Tree Structure:")
        print(parse_tree2.pretty())
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

if __name__ == "__main__":
    debug_parse_tree()