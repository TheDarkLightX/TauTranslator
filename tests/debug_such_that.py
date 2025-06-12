#!/usr/bin/env python3
"""
Debug the 'such that' quantifier syntax specifically.
"""

import os
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def debug_such_that():
    """Debug the 'such that' parsing."""
    
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
        
        # Test the specific failing case
        test_input = "exists y such that q(y)."
        
        print(f"🔍 Debugging parse tree for: '{test_input}'")
        
        parse_tree = parser.parse(test_input)
        print(f"\nParse Tree Structure:")
        print(parse_tree.pretty())
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

if __name__ == "__main__":
    debug_such_that()