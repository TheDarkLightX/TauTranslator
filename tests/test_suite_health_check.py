#!/usr/bin/env python3
"""
Test Suite Health Check for TauTranslator
Comprehensive analysis of which tests work and which need fixing.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_test_module(test_path, description):
    """Run a specific test module and return results."""
    print(f"🧪 Testing: {description}")
    print(f"   Path: {test_path}")
    
    start_time = time.time()
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', test_path, 
            '-v', '--tb=no', '--disable-warnings', '-q'
        ], 
        cwd='~/TauTranslator',
        env={**os.environ, 'PYTHONPATH': '~/TauTranslator/src'},
        capture_output=True, 
        text=True,
        timeout=30
        )
        
        test_time = time.time() - start_time
        
        # Parse results
        output_lines = result.stdout.split('\n')
        summary_line = [line for line in output_lines if 'passed' in line or 'failed' in line or 'error' in line]
        
        if result.returncode == 0:
            status = "✅ PASS"
            color = "green"
        else:
            status = "❌ FAIL" 
            color = "red"
        
        return {
            'path': test_path,
            'description': description,
            'status': status,
            'return_code': result.returncode,
            'time': test_time,
            'output': result.stdout[:500] if result.stdout else '',
            'summary': summary_line[-1] if summary_line else 'No summary',
            'working': result.returncode == 0
        }
        
    except subprocess.TimeoutExpired:
        return {
            'path': test_path,
            'description': description,
            'status': "⏰ TIMEOUT",
            'return_code': -1,
            'time': 30.0,
            'output': 'Test timed out after 30 seconds',
            'summary': 'TIMEOUT',
            'working': False
        }
    except Exception as e:
        return {
            'path': test_path,
            'description': description,
            'status': "💥 ERROR",
            'return_code': -2,
            'time': time.time() - start_time,
            'output': str(e),
            'summary': f'Exception: {str(e)[:100]}',
            'working': False
        }

def main():
    """Run comprehensive test suite health check."""
    print("🏥 TAUTRANSLATOR TEST SUITE HEALTH CHECK")
    print("=" * 60)
    
    # Test modules to check
    test_modules = [
        # Working AST tests
        ("tests/core_engine/ast_tests/test_boolean_literal_node.py", "Boolean Literal Node (Original)"),
        ("tests/core_engine/ast_tests/test_boolean_literal_node_fixed.py", "Boolean Literal Node (Fixed)"),
        ("tests/core_engine/ast_tests/test_boolean_literal_node_mutation_hardened.py", "Boolean Literal Node (Hardened)"),
        ("tests/core_engine/ast_tests/test_identifier_node.py", "Identifier Node (Original)"),
        ("tests/core_engine/ast_tests/test_binary_op_node.py", "Binary Op Node (Original)"),
        ("tests/core_engine/ast_tests/test_number_literal_node.py", "Number Literal Node (Original)"),
        ("tests/core_engine/ast_tests/test_unary_op_node.py", "Unary Op Node (Original)"),
        ("tests/core_engine/ast_tests/test_stream_variable_node.py", "Stream Variable Node (Original)"),
        
        # Refactored semantic analyzer
        ("tests/core_engine/test_semantic_analyzer_refactored.py", "Semantic Analyzer (Refactored)"),
        
        # Other core tests
        ("tests/core_engine/test_parser.py", "Core Parser"),
        ("tests/core_engine/cnl_parser/test_mock_parser.py", "Mock CNL Parser"),
        ("tests/core_engine/ebnf_parser/test_ebnf_parser.py", "EBNF Parser"),
        
        # Grammar tests  
        ("tests/core_engine/test_grammar_plugin_validator.py", "Grammar Plugin Validator"),
        ("tests/core_engine/test_tgf_preprocessor.py", "TGF Preprocessor"),
        
        # Advanced tests
        ("tests/test_advanced_translator.py", "Advanced Translator"),
        ("tests/test_security.py", "Security Tests"),
    ]
    
    results = []
    
    for test_path, description in test_modules:
        # Check if test file exists
        if not os.path.exists(test_path):
            results.append({
                'path': test_path,
                'description': description,
                'status': "📁 NOT FOUND",
                'return_code': -3,
                'time': 0.0,
                'output': 'Test file does not exist',
                'summary': 'File not found',
                'working': False
            })
            print(f"📁 {description}: NOT FOUND")
            continue
        
        result = run_test_module(test_path, description)
        results.append(result)
        print(f"   {result['status']} - {result['time']:.2f}s")
        if not result['working']:
            print(f"      {result['summary'][:100]}...")
        print()
    
    # Summary Report
    print("\n" + "=" * 60)
    print("📊 TEST SUITE HEALTH REPORT")
    print("=" * 60)
    
    working_tests = [r for r in results if r['working']]
    failing_tests = [r for r in results if not r['working'] and r['status'] != "📁 NOT FOUND"]
    missing_tests = [r for r in results if r['status'] == "📁 NOT FOUND"]
    
    total_tests = len(results)
    working_count = len(working_tests)
    failing_count = len(failing_tests)
    missing_count = len(missing_tests)
    
    health_score = (working_count / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 OVERALL HEALTH SCORE: {health_score:.1f}%")
    print(f"   ✅ Working: {working_count}/{total_tests}")
    print(f"   ❌ Failing: {failing_count}/{total_tests}")
    print(f"   📁 Missing: {missing_count}/{total_tests}")
    print()
    
    if working_tests:
        print("✅ WORKING TESTS (Ready for mutation testing):")
        for test in working_tests:
            print(f"   • {test['description']} ({test['time']:.2f}s)")
        print()
    
    if failing_tests:
        print("❌ FAILING TESTS (Need fixes):")
        for test in failing_tests:
            print(f"   • {test['description']}")
            print(f"     Issue: {test['summary'][:80]}...")
        print()
    
    if missing_tests:
        print("📁 MISSING TESTS (Need creation):")
        for test in missing_tests:
            print(f"   • {test['description']}")
        print()
    
    # Recommendations
    print("🎯 RECOMMENDATIONS:")
    
    if health_score >= 70:
        print("   🟢 Good test health - proceed with mutation testing on working tests")
        print("   📋 Focus on scaling mutation testing to working modules")
    elif health_score >= 50:
        print("   🟡 Moderate test health - fix critical failing tests first")
        print("   🔧 Fix import errors and basic test infrastructure")
    else:
        print("   🔴 Poor test health - major test suite repair needed")
        print("   ⚠️  Address fundamental testing infrastructure issues")
    
    if working_count >= 5:
        print(f"   🧬 Ready to run mutation testing on {working_count} working test modules")
        
    print(f"\n💾 Health check completed in {sum(r['time'] for r in results):.1f} seconds")
    
    # Save detailed results
    import json
    with open('test_suite_health_report.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'health_score': health_score,
            'summary': {
                'total': total_tests,
                'working': working_count,
                'failing': failing_count,
                'missing': missing_count
            },
            'results': results
        }, f, indent=2)
    
    print("📁 Detailed report saved to: test_suite_health_report.json")
    
    return health_score

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 50 else 1)  # Pass if >50% tests working