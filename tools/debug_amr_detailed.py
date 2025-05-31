#!/usr/bin/env python3
"""Debug AMR Analysis in Detail"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.amr_semantic_layer import (
    AMRSemanticAnalyzer
)
from tau_translator_omega.core_engine.nlp_enhanced.incremental_parser import (
    IncrementalTCEParser
)

def debug_amr_detailed():
    """Debug AMR analysis step by step"""
    parser = IncrementalTCEParser()
    analyzer = AMRSemanticAnalyzer()
    
    text = "x = 5."
    print(f"Parsing: {text}")
    
    ast, meta = parser.parse(text)
    print(f"AST: {ast}")
    print(f"AST type: {type(ast)}")
    
    if ast:
        print(f"AST attributes: {dir(ast)}")
        if hasattr(ast, '__dict__'):
            print(f"AST dict: {ast.__dict__}")
        
        try:
            graph = analyzer.analyze(ast)
            print(f"AMR Graph: {graph}")
            print(f"Graph instances: {len(graph.instances)}")
            print(f"Graph instance keys: {list(graph.instances.keys())}")
            
            for instance_id, instance in graph.instances.items():
                print(f"Instance {instance_id}: {instance}")
        except Exception as e:
            print(f"Error in AMR analysis: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_amr_detailed()