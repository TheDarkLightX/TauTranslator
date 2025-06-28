#!/usr/bin/env python3
"""
Quick Mutation Testing Sample
============================

Runs mutation testing on a sample of modules to demonstrate 
the scaled approach without taking too long.
"""

import os
import sys
import subprocess
import time
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def run_quick_mutation_test(test_file, source_file, description):
    """Run a quick mutation test with limited mutants."""
    print(f"🧬 Quick mutation test: {description}")
    print(f"   Source: {source_file}")
    print(f"   Tests: {test_file}")
    
    # Create config with limited mutations
    config_content = f"""[mutmut]
paths_to_mutate = {source_file}
backup = False
runner = PYTHONPATH=src python3 -m pytest {test_file} -x --tb=no --disable-warnings -q
tests_dir = tests/
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
        f.write(config_content)
        config_file = f.name
    
    try:
        env = os.environ.copy()
        env['MUTMUT_CONFIG_FILE'] = config_file
        
        start_time = time.time()
        
        # Run limited mutmut (timeout after 60 seconds)
        print("   Running mutation testing (max 60s)...")
        
        result = subprocess.run([
            sys.executable, '-m', 'mutmut', 'run'
        ], 
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True, 
        text=True,
        timeout=60  # Short timeout for demo
        )
        
        test_time = time.time() - start_time
        
        # Get results
        results = subprocess.run([
            sys.executable, '-m', 'mutmut', 'results'
        ], 
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True, 
        text=True,
        timeout=10
        )
        
        print(f"   ✅ Completed in {test_time:.1f}s")
        
        # Clean up
        subprocess.run([
            sys.executable, '-m', 'mutmut', 'reset'
        ], 
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        timeout=10
        )
        
        return {
            'description': description,
            'time': test_time,
            'status': 'SUCCESS',
            'output': result.stdout[:500],
            'results': results.stdout[:500]
        }
        
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timed out after 60s")
        return {
            'description': description,
            'time': 60,
            'status': 'TIMEOUT',
            'output': 'Timed out',
            'results': ''
        }
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            'description': description,
            'time': time.time() - start_time,
            'status': 'ERROR',
            'output': str(e),
            'results': ''
        }
    finally:
        try:
            os.unlink(config_file)
        except:
            pass

def main():
    """Run quick mutation testing demonstration."""
    print("🧬 QUICK MUTATION TESTING DEMONSTRATION")
    print("=" * 50)
    print("Testing 2 sample modules with 60s timeout each")
    print()
    
    # Test cases
    test_cases = [
        {
            'test_file': 'tests/core_engine/ast_tests/test_boolean_literal_node_fixed.py',
            'source_file': 'src/tau_translator_omega/core_engine/ast/ast_nodes.py',
            'description': 'Boolean Literal Node (Enhanced)'
        },
        {
            'test_file': 'tests/core_engine/test_semantic_analyzer_refactored.py',
            'source_file': 'src/tau_translator_omega/core_engine/semantic_analyzer.py',
            'description': 'Semantic Analyzer (Refactored)'
        }
    ]
    
    results = []
    total_start = time.time()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {test_case['description']}")
        result = run_quick_mutation_test(
            test_case['test_file'],
            test_case['source_file'], 
            test_case['description']
        )
        results.append(result)
        print()
    
    total_time = time.time() - total_start
    
    # Summary
    print("=" * 50)
    print("📊 QUICK MUTATION TESTING RESULTS")
    print("=" * 50)
    
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] != 'SUCCESS']
    
    print(f"📈 SUMMARY:")
    print(f"   • Total tests: {len(results)}")
    print(f"   • Successful: {len(successful)}")
    print(f"   • Failed/Timeout: {len(failed)}")
    print(f"   • Total time: {total_time:.1f}s")
    print()
    
    for result in results:
        status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_emoji} {result['description']}")
        print(f"   Status: {result['status']}")
        print(f"   Time: {result['time']:.1f}s")
        if result['results']:
            print(f"   Results: {result['results'][:100]}...")
        print()
    
    print("🎯 DEMONSTRATION COMPLETE")
    print(f"This shows that mutation testing is working on {len(successful)}/{len(results)} modules.")
    print("For full project analysis, run the complete scaled mutation testing.")
    
    return len(successful) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)