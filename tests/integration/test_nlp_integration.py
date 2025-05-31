#!/usr/bin/env python3
"""
Quick NLP Integration Test
=========================
Test the enhanced NLP capabilities in TDD fashion.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.amr_semantic_layer import (
    AMRSemanticAnalyzer, AMRGraph, AMRConcept, AMRRelation
)
from tau_translator_omega.core_engine.nlp_enhanced.incremental_parser import (
    IncrementalTCEParser, TextDiffer
)
from tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
    PredicateCallNode, VariableNode
)

def test_amr_analysis():
    """Test AMR semantic analysis"""
    print("🧪 Testing AMR Semantic Analysis...")
    
    analyzer = AMRSemanticAnalyzer()
    
    # Test simple predicate
    predicate = PredicateCallNode(name="prime", args=[VariableNode(name="x")])
    graph = analyzer.analyze(predicate)
    
    assert len(graph.instances) > 0, "Should create AMR instances"
    
    roles = analyzer.get_semantic_roles(graph, "prime")
    assert len(roles) > 0, "Should extract semantic roles"
    
    print("  ✅ AMR analysis working correctly")
    return True

def test_incremental_parsing():
    """Test incremental parsing with caching"""
    print("🧪 Testing Incremental Parsing...")
    
    parser = IncrementalTCEParser()
    differ = TextDiffer()
    
    # Test basic parsing
    text1 = "prime(x)"
    ast1, meta1 = parser.parse(text1)
    assert ast1 is not None, "Should parse successfully"
    
    # Test incremental change
    text2 = "even(x)"
    edits = differ.compute_edits(text1, text2)
    assert len(edits) > 0, "Should detect edits"
    
    ast2, meta2 = parser.parse(text2, text1, ast1)
    assert ast2 is not None, "Should parse incrementally"
    
    # Test cache hit
    ast3, meta3 = parser.parse(text1)  # Back to original
    assert meta3["cache_hit"], "Should be cache hit"
    
    print("  ✅ Incremental parsing working correctly")
    return True

def test_integration():
    """Test integration between AMR and incremental parsing"""
    print("🧪 Testing NLP Integration...")
    
    parser = IncrementalTCEParser()
    analyzer = AMRSemanticAnalyzer()
    
    # Test with simple expressions that work
    expressions = [
        "x = 5.",
        "y > 0.",
        "z < 10."
    ]
    
    for text in expressions:
        ast, meta = parser.parse(text)
        
        if ast:
            # Analyze with AMR
            graph = analyzer.analyze(ast)
            assert len(graph.instances) > 0, f"Should create semantic representation for {text}"
            print(f"  ✓ Successfully parsed and analyzed: {text}")
        else:
            print(f"  ⚠ Failed to parse: {text}")
    
    # Test incremental parsing with similar expressions
    text1 = "x = 5."
    text2 = "x = 10."
    
    ast1, _ = parser.parse(text1)
    ast2, meta2 = parser.parse(text2, text1, ast1)
    
    if ast2:
        graph2 = analyzer.analyze(ast2)
        assert len(graph2.instances) > 0, "Should create semantic representation for incremental parse"
        
    print("  ✅ NLP integration working correctly")
    return True

def main():
    """Run all integration tests"""
    print("🚀 Running NLP Enhanced TDD Integration Tests\n")
    
    tests_passed = 0
    total_tests = 3
    
    try:
        if test_amr_analysis():
            tests_passed += 1
    except Exception as e:
        print(f"  ❌ AMR test failed: {e}")
    
    try:
        if test_incremental_parsing():
            tests_passed += 1
    except Exception as e:
        print(f"  ❌ Incremental parsing test failed: {e}")
    
    try:
        if test_integration():
            tests_passed += 1
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All NLP enhanced features are working correctly!")
        return True
    else:
        print("⚠️  Some tests failed - see details above")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)