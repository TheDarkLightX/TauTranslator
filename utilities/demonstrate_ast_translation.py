#!/usr/bin/env python3
"""
Demonstrate AST-based Translation
=================================

Shows how TCE text is parsed to AST and then translated to Tau.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    # Import parser and translator
    from src.tau_translator_omega.core_engine.cnl_parser.parser import Parser
    from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
    
    # Create instances
    parser = Parser()
    translator = TCETauTranslator()
    
    # Examples to demonstrate
    examples = [
        "Always x and y.",
        "For all x such that P(x).",
        "x at time t implies y at time t+1.",
        "If x greater than 0 then f(x) else g(x).",
    ]
    
    print("TCE → AST → TAU TRANSLATION DEMONSTRATION")
    print("=" * 50)
    print()
    
    for tce_text in examples:
        print(f"TCE Input: {tce_text}")
        
        try:
            # Stage 1: Parse TCE to AST
            ast = parser.parse(tce_text)
            print(f"AST Type: {type(ast).__name__}")
            
            # Show AST structure
            if hasattr(ast, 'content'):
                content = ast.content
                if hasattr(content, 'statement'):
                    stmt = content.statement
                    print(f"  └─ Statement: {type(stmt).__name__}")
                    
                    # Show more detail for complex expressions
                    if hasattr(stmt, 'operator'):
                        print(f"      └─ Operator: {stmt.operator}")
                    if hasattr(stmt, 'quant_type'):
                        print(f"      └─ Quantifier: {stmt.quant_type}")
            
            # Stage 2: Translate AST to Tau
            result = translator.translate(ast)
            print(f"Tau Output: {result.tau_code}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 50)
        print()
    
except ImportError as e:
    print("Parser not available, showing conceptual AST flow:")
    print()
    
    # Show conceptual flow
    print("1. TCE: 'Always x and y.'")
    print("   ↓ (Parser)")
    print("2. AST: SentenceNode(")
    print("          FactNode(")
    print("            AlwaysNode(")
    print("              BooleanBinaryOpNode(op='and', left='x', right='y')")
    print("            )")
    print("          )")
    print("        )")
    print("   ↓ (Translator)")
    print("3. Tau: 'always (x & y)'")
    print()
    
    print("The AST is the intermediate logic representation that:")
    print("- Captures the semantic structure")
    print("- Is independent of surface syntax")
    print("- Can be validated and transformed")
    print("- Enables bidirectional translation")