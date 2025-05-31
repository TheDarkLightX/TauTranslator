#!/usr/bin/env python3
"""Debug CNL Parser"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser

def debug_cnl_parser():
    """Test CNL parser directly"""
    parser = CNLParser(debug=True)
    
    expressions = [
        "prime(x)",
        "prime(x) and even(y)",
        "x = 5",
        "x > 0"
    ]
    
    for expr in expressions:
        print(f"\nParsing: {expr}")
        try:
            result = parser.parse(expr)
            print(f"Result: {result}")
            print(f"Type: {type(result)}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_cnl_parser()