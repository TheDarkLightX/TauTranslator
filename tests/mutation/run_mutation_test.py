#!/usr/bin/env python3
"""
Simple mutation testing runner for TauTranslator
Focuses on specific modules to avoid import issues
"""
import os
import sys
import subprocess
from pathlib import Path

def run_mutation_test():
    """Run mutation testing on AST nodes with proper path setup"""
    
    # Set up environment
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    # Set PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path)
    
    # Test that our target tests work first
    print("🧪 Testing baseline test suite...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/core_engine/ast_tests/", 
        "-v", "--tb=short"
    ], cwd=project_root, env=env)
    
    if result.returncode != 0:
        print("❌ Baseline tests failed. Cannot proceed with mutation testing.")
        return False
    
    print("✅ Baseline tests pass. Starting mutation testing...")
    
    # Run mutation testing using a simple file-based approach
    ast_file = src_path / "tau_translator_omega/core_engine/ast/ast_nodes.py"
    
    print(f"🎯 Mutation testing target: {ast_file}")
    print(f"🧪 Test directory: tests/core_engine/ast_tests/")
    
    # Create a simple mutmut config for this run
    config_content = f"""[mutmut]
paths_to_mutate = {ast_file}
backup = False
runner = PYTHONPATH={src_path} python -m pytest tests/core_engine/ast_tests/ -x --tb=no --disable-warnings -q
tests_dir = tests/core_engine/ast_tests/
"""
    
    with open(project_root / "mutmut_config.cfg", "w") as f:
        f.write(config_content)
    
    # Run mutmut with the specific config
    result = subprocess.run([
        sys.executable, "-m", "mutmut", "run",
        "--config-file", "mutmut_config.cfg"
    ], cwd=project_root, env=env)
    
    if result.returncode == 0:
        print("✅ Mutation testing completed successfully")
        
        # Show results
        subprocess.run([
            sys.executable, "-m", "mutmut", "summary"
        ], cwd=project_root)
        
        return True
    else:
        print("❌ Mutation testing failed")
        return False

if __name__ == "__main__":
    success = run_mutation_test()
    sys.exit(0 if success else 1)