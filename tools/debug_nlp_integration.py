#!/usr/bin/env python3
"""Debug NLP Integration"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.amr_semantic_layer import (
    AMRSemanticAnalyzer
)
from tau_translator_omega.core_engine.nlp_enhanced.incremental_parser import (
    IncrementalTCEParser
)

def debug_complex_expression():
    """Debug parsing complex expressions"""
    parser = IncrementalTCEParser()
    analyzer = AMRSemanticAnalyzer()
    
    text = "prime(x) and even(y)"
    print(f"Parsing: {text}")
    
    ast, meta = parser.parse(text)
    print(f"AST result: {ast}")
    print(f"Metadata: {meta}")
    
    if ast:
        print(f"AST type: {type(ast)}")
        try:
            graph = analyzer.analyze(ast)
            print(f"AMR Graph instances: {len(graph.instances)}")
            
            roles = analyzer.get_semantic_roles(graph, "prime")
            print(f"Prime roles: {roles}")
            
            # Try a simpler expression
            simple_text = "prime(x)"
            simple_ast, _ = parser.parse(simple_text)
            if simple_ast:
                simple_graph = analyzer.analyze(simple_ast)
                simple_roles = analyzer.get_semantic_roles(simple_graph, "prime")
                print(f"Simple prime roles: {simple_roles}")
                
        except Exception as e:
            print(f"Error in AMR analysis: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Failed to parse - AST is None")

if __name__ == "__main__":
    debug_complex_expression()