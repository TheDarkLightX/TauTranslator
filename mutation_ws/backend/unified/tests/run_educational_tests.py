#!/usr/bin/env python3
"""
Run educational autocomplete tests.

This script runs the educational autocomplete API tests and
provides a summary of the results.

Copyright: DarkLightX / Dana Edwards
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run the educational autocomplete tests."""
    test_dir = Path(__file__).parent
    
    # Run pytest on the educational autocomplete tests
    test_files = [
        "test_educational_autocomplete_api.py",
        "test_educational_autocomplete_integration.py"
    ]
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"Running tests in {test_file}")
        print('='*60)
        
        test_path = test_dir / test_file
        cmd = [
            sys.executable, "-m", "pytest", "-v", 
            str(test_path),
            "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print(f"\nTests in {test_file} FAILED!")
        else:
            print(f"\nTests in {test_file} PASSED!")
    
    print("\n" + "="*60)
    print("Test run complete!")


if __name__ == "__main__":
    run_tests()