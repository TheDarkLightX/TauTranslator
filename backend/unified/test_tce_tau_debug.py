#!/usr/bin/env python3
"""
Debug TCE to Tau translation issue
Copyright: DarkLightX/Dana Edwards
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
from src.tau_translator_omega.core_engine.cnl_parser.ast_nodes import SentenceNode
from backend.unified.tce_to_tau_wrapper import TCEToTauWrapper

def debug_parser_output():
    """Debug what the parser returns."""
    parser = CNLParser()
    
    test_cases = [
        "x = 5.",
        "x and y.",
        "x > 10.",
    ]
    
    for tce in test_cases:
        print(f"\nTCE: {tce}")
        try:
            ast = parser.parse(tce)
            print(f"AST type: {type(ast).__name__}")
            
            if hasattr(ast, 'content'):
                print(f"Content type: {type(ast.content).__name__}")
                print(f"Content is list: {isinstance(ast.content, list)}")
                if not isinstance(ast.content, list):
                    print(f"Content value: {ast.content}")
                
            # Test wrapper fix
            wrapper = TCEToTauWrapper()
            if isinstance(ast, SentenceNode):
                fixed = wrapper._fix_sentence_node(ast)
                print(f"After fix - Content is list: {isinstance(fixed.content, list)}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_parser_output()