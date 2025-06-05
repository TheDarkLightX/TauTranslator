#!/usr/bin/env python3
"""
Run mutation testing on SimpleTCETranslator
==========================================
"""

import subprocess
import os
import sys
import tempfile
import time


def run_mutation_test():
    """Run mutation test on the simple translator."""
    print("🧬 Running Mutation Testing on SimpleTCETranslator")
    print("=" * 60)
    
    # Create mutmut config
    config_content = """[mutmut]
paths_to_mutate = tests/test_tce_translator_simple.py
backup = False
runner = python -m pytest tests/test_tce_translator_simple.py::TestSimpleTCETranslator -x --tb=no --disable-warnings -q
tests_dir = tests/
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
        f.write(config_content)
        config_file = f.name
    
    try:
        env = os.environ.copy()
        env['MUTMUT_CONFIG_FILE'] = config_file
        
        # Activate virtual environment
        venv_path = os.path.join(os.getcwd(), 'venv_bdd')
        if os.path.exists(venv_path):
            env['PATH'] = f"{venv_path}/bin:{env['PATH']}"
            env['VIRTUAL_ENV'] = venv_path
        
        print("⏳ Generating mutants and running tests...")
        start_time = time.time()
        
        # Run mutmut
        result = subprocess.run(
            [sys.executable, '-m', 'mutmut', 'run'],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        duration = time.time() - start_time
        
        # Show results
        print(f"\n✅ Completed in {duration:.1f} seconds")
        print("\n📊 MUTATION TESTING RESULTS:")
        print("-" * 40)
        
        # Get detailed results
        results = subprocess.run(
            [sys.executable, '-m', 'mutmut', 'results'],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True
        )
        
        print(results.stdout)
        
        # Parse and display summary
        if "killed" in results.stdout.lower():
            lines = results.stdout.split('\n')
            for line in lines:
                if "killed" in line.lower() or "survived" in line.lower():
                    print(f"\n📈 {line}")
        
        # Clean up
        subprocess.run(
            ['rm', '-rf', '.mutmut-cache'],
            cwd=os.getcwd()
        )
        
    finally:
        os.unlink(config_file)


if __name__ == "__main__":
    os.chdir('~/TauTranslator')
    run_mutation_test()