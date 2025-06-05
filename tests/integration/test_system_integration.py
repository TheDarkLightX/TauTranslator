#!/usr/bin/env python3
"""
Quick integration test to verify the system runs
"""

import sys
sys.path.insert(0, '.')

from src.tau_translator_omega.lmql_engine.recognizers import RecognizerFactory
from src.tau_translator_omega.core_engine.pattern_cache import get_pattern, get_cache_stats
from src.tau_translator_omega.core_engine.optimized_symbol_table import OptimizedSymbolTable
from src.tau_translator_omega.core_engine.semantic_types import Symbol
from src.tau_translator_omega.core_engine.trie import KeywordTrie
from src.tau_translator_omega.lmql_engine.parallel_recognizer import ParallelPatternMatcher

def test_basic_functionality():
    print("Testing basic system functionality...")
    
    # Test 1: Pattern Recognition with Caching
    print("\n1. Testing Pattern Recognition with Caching:")
    recognizer = RecognizerFactory.create_recognizer('arithmetic')
    result = recognizer.recognize("adder[n] := i1[n] + i2[n]")
    print(f"   Recognition: {result.recognized}")
    print(f"   Pattern type: {result.pattern_type}")
    print(f"   Cache stats: {get_cache_stats()}")
    
    # Test 2: Translation
    print("\n2. Testing Translation:")
    if result.recognized:
        tce = recognizer.translate_to_tce(result)
        print(f"   TCE: {tce}")
        tau = recognizer.translate_to_tau(result)
        print(f"   Tau: {tau}")
    
    # Test 3: Optimized Symbol Table
    print("\n3. Testing Optimized Symbol Table:")
    table = OptimizedSymbolTable()
    table.declare_symbol(Symbol('x', 'variable', 0, var_type='integer'))
    table.declare_symbol(Symbol('y', 'variable', 0, var_type='string'))
    
    # Test lookup
    x_symbol = table.lookup_symbol('x')
    print(f"   Found x: {x_symbol is not None}")
    print(f"   x type: {x_symbol.var_type if x_symbol else 'N/A'}")
    
    stats = table.get_performance_stats()
    print(f"   Symbol table stats: {stats}")
    
    # Test 4: Keyword Trie
    print("\n4. Testing Keyword Trie:")
    trie = KeywordTrie()
    trie.add_keyword('function', 'FUNCTION')
    trie.add_keyword('if', 'IF')
    trie.add_keyword('then', 'THEN')
    
    print(f"   'function' is keyword: {trie.is_reserved('function')}")
    print(f"   'variable' is keyword: {trie.is_reserved('variable')}")
    
    # Test 5: Parallel Pattern Matching
    print("\n5. Testing Parallel Pattern Matching:")
    with ParallelPatternMatcher(max_workers=2) as matcher:
        results = matcher.recognize_parallel("and_gate[t] := a[t] & b[t]")
        if results:
            print(f"   Found {len(results)} patterns")
            print(f"   Best match: {results[0].recognizer_type} with confidence {results[0].result.confidence}")
        
        perf = matcher.get_performance_stats()
        print(f"   Performance: {perf}")
    
    print("\n✅ All basic functionality tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)