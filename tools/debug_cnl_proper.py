#!/usr/bin/env python3
"""Debug CNL Parser with proper format"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser

def debug_proper_cnl():
    """Test CNL parser with proper format"""
    parser = CNLParser(debug=True)
    
    expressions = [
        "prime(x).",
        "prime(x) and even(y).",
        "x = 5.",
        "x > 0."
    ]
    
    for expr in expressions:
        print(f"\nParsing: {expr}")
        try:
            result = parser.parse(expr)
            print(f"Result: {result}")
            print(f"Type: {type(result)}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_proper_cnl()