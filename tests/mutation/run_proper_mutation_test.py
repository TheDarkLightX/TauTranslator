#!/usr/bin/env python3
"""
Run Mutation Testing on SimpleTCETranslator
==========================================
"""

import subprocess
import os
import sys
import tempfile


def main():
    """Run mutation testing properly."""
    print("🧬 Running Mutation Testing on SimpleTCETranslator")
    print("=" * 60)
    
    # Dynamically find the project root
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    # First, let's extract SimpleTCETranslator to its own file
    # to properly test mutations on the implementation
    
    translator_code = '''"""
Simple TCE to TAU Translator
===========================

Extracted for mutation testing.
"""


class SimpleTCETranslator:
    """Simple TCE to TAU translator - GREEN phase of TDD."""
    
    def translate(self, tce_input: str) -> str:
        """Translate TCE to TAU."""
        # GREEN: Make tests pass with minimal implementation
        
        # Validation
        if not tce_input:
            raise ValueError("Input cannot be empty")
        
        if not tce_input.strip().endswith('.'):
            raise ValueError("Input must end with period")
        
        # Remove period for processing
        text = tce_input.strip()[:-1]
        
        # Simple string replacements
        text = text.replace(" xor ", " + ")
        text = text.replace(" and ", " & ")
        text = text.replace(" or ", " \\\\ ")
        
        # Handle "not" prefix
        if text.startswith("not "):
            text = text[4:] + "'"
        
        return text
'''
    
    # Write translator to separate file
    with open('simple_tce_translator.py', 'w') as f:
        f.write(translator_code)
    
    # Update test file to import from separate module
    test_code = '''"""
Simple TDD Tests for TCE to TAU Translation
==========================================

Minimal tests to drive implementation without complex dependencies.
"""

import pytest
from simple_tce_translator import SimpleTCETranslator


class TestSimpleTCETranslator:
    """TDD tests for simple TCE translator."""
    
    def test_translate_basic_fact(self):
        """Test: x = 5. -> x = 5"""
        translator = SimpleTCETranslator()
        result = translator.translate("x = 5.")
        assert result == "x = 5"
    
    def test_translate_and_operation(self):
        """Test: x and y. -> x & y"""
        translator = SimpleTCETranslator()
        result = translator.translate("x and y.")
        assert result == "x & y"
    
    def test_translate_or_operation(self):
        """Test: x or y. -> x \\\\ y"""
        translator = SimpleTCETranslator()
        result = translator.translate("x or y.")
        assert result == "x \\\\ y"
    
    def test_translate_xor_operation(self):
        """Test: x xor y. -> x + y"""
        translator = SimpleTCETranslator()
        result = translator.translate("x xor y.")
        assert result == "x + y"
    
    def test_translate_not_operation(self):
        """Test: not x. -> x'"""
        translator = SimpleTCETranslator()
        result = translator.translate("not x.")
        assert result == "x'"
    
    def test_translate_complex_boolean(self):
        """Test: (x and y) or z. -> (x & y) \\\\ z"""
        translator = SimpleTCETranslator()
        result = translator.translate("(x and y) or z.")
        assert result == "(x & y) \\\\ z"
    
    def test_missing_period_error(self):
        """Test error on missing period."""
        translator = SimpleTCETranslator()
        with pytest.raises(ValueError, match="^Input must end with period$"):
            translator.translate("x = 5")
    
    def test_empty_input_error(self):
        """Test error on empty input."""
        translator = SimpleTCETranslator()
        with pytest.raises(ValueError, match="^Input cannot be empty$"):
            translator.translate("")
'''
    
    with open('test_simple_tce_translator.py', 'w') as f:
        f.write(test_code)
    
    # Run tests to ensure they pass
    print("\n📋 Running baseline tests...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'test_simple_tce_translator.py', '-v'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Baseline tests failed!")
        print(result.stdout)
        print(result.stderr)
        return 1
    
    print("✅ Baseline tests passed!")
    
    # Run mutation testing
    print("\n🧬 Running mutation testing...")
    
    # Clean cache
    subprocess.run(['rm', '-rf', '.mutmut-cache'])
    
    # Run mutmut
    result = subprocess.run(
        [sys.executable, '-m', 'mutmut', 'run', 
         '--paths-to-mutate', 'simple_tce_translator.py',
         '--runner', 'python -m pytest test_simple_tce_translator.py -x --tb=no -q'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # Get results
    print("\n📊 Mutation Testing Results:")
    result = subprocess.run(
        [sys.executable, '-m', 'mutmut', 'results'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    # Clean up
    subprocess.run(['rm', 'simple_tce_translator.py'])
    subprocess.run(['rm', 'test_simple_tce_translator.py'])
    subprocess.run(['rm', '-rf', '.mutmut-cache'])
    
    return 0


if __name__ == "__main__":
    sys.exit(main())