#!/usr/bin/env python3
"""
Manual mutation testing for BooleanLiteralNode to verify enhanced test quality.
"""

import sys
import os
import subprocess
import tempfile
import time
from pathlib import Path

def create_mutated_ast_nodes(original_content, mutations):
    """Create mutated versions of the AST nodes file."""
    mutated_files = []
    
    for i, (description, find_str, replace_str) in enumerate(mutations):
        mutated_content = original_content.replace(find_str, replace_str)
        if mutated_content != original_content:
            mutated_files.append((i, description, mutated_content))
    
    return mutated_files

def run_test_against_mutant(mutated_content, test_file):
    """Run tests against a mutated version of the code."""
    # Create temporary file with mutated content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(mutated_content)
        temp_file = f.name
    
    try:
        # Replace the original file temporarily
        original_ast_file = "~/TauTranslator/src/tau_translator_omega/core_engine/ast/ast_nodes.py"
        
        # Backup original
        with open(original_ast_file, 'r') as f:
            original_content = f.read()
        
        # Write mutated version
        with open(original_ast_file, 'w') as f:
            f.write(mutated_content)
        
        # Run test
        env = os.environ.copy()
        env['PYTHONPATH'] = '~/TauTranslator/src'
        
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            test_file, 
            '-x', '--tb=no', '--disable-warnings', '-q'
        ], 
        cwd='~/TauTranslator',
        env=env,
        capture_output=True, 
        text=True)
        
        return result.returncode == 0  # True if tests passed (mutant survived)
        
    finally:
        # Restore original file
        with open(original_ast_file, 'w') as f:
            f.write(original_content)
        
        # Clean up temp file
        os.unlink(temp_file)

def main():
    """Run manual mutation testing on BooleanLiteralNode."""
    print("🧬 Running Manual Mutation Testing on BooleanLiteralNode")
    print("=" * 60)
    
    # Read original AST nodes file
    ast_file = "~/TauTranslator/src/tau_translator_omega/core_engine/ast/ast_nodes.py"
    with open(ast_file, 'r') as f:
        original_content = f.read()
    
    # Define mutations targeting BooleanLiteralNode
    mutations = [
        # Validation mutations
        ("Remove boolean type check", 
         "if not isinstance(self.value, bool):", 
         "if False:"),
        
        ("Change boolean validation to int", 
         "isinstance(self.value, bool)", 
         "isinstance(self.value, int)"),
        
        ("Remove validation entirely", 
         'raise ValueError("BooleanLiteralNode value must be a boolean.")', 
         'pass'),
        
        ("Change error message", 
         "BooleanLiteralNode value must be a boolean.", 
         "BooleanLiteralNode value must be a string."),
        
        # Dataclass mutations
        ("Remove frozen=True", 
         "@dataclass(frozen=True, eq=True)", 
         "@dataclass(eq=True)"),
        
        ("Remove eq=True", 
         "@dataclass(frozen=True, eq=True)", 
         "@dataclass(frozen=True)"),
        
        # Logic mutations
        ("Invert boolean check", 
         "not isinstance(self.value, bool)", 
         "isinstance(self.value, bool)"),
        
        ("Change value type annotation", 
         "value: bool", 
         "value: int"),
        
        # Edge case mutations
        ("Allow None values", 
         "if not isinstance(self.value, bool):", 
         "if not isinstance(self.value, bool) and self.value is not None:"),
        
        ("Change to always True", 
         "self.value: bool", 
         "True  # bool"),
    ]
    
    test_file = "tests/core_engine/ast_tests/test_boolean_literal_node_fixed.py"
    
    print(f"Testing against: {test_file}")
    print(f"Total mutations to test: {len(mutations)}")
    print()
    
    # Create mutated files
    mutated_files = create_mutated_ast_nodes(original_content, mutations)
    
    survived_mutants = []
    killed_mutants = []
    
    for mutant_id, description, mutated_content in mutated_files:
        print(f"🧪 Testing mutant {mutant_id + 1}: {description}")
        
        start_time = time.time()
        survived = run_test_against_mutant(mutated_content, test_file)
        test_time = time.time() - start_time
        
        if survived:
            print(f"  ❌ SURVIVED (tests passed) - {test_time:.2f}s")
            survived_mutants.append((mutant_id, description))
        else:
            print(f"  ✅ KILLED (tests failed) - {test_time:.2f}s")
            killed_mutants.append((mutant_id, description))
    
    # Results summary
    print("\n" + "=" * 60)
    print("🧬 MUTATION TEST RESULTS")
    print("=" * 60)
    
    total_mutants = len(mutated_files)
    killed_count = len(killed_mutants)
    survived_count = len(survived_mutants)
    
    mutation_score = (killed_count / total_mutants * 100) if total_mutants > 0 else 0
    
    print(f"Total Mutants: {total_mutants}")
    print(f"Killed: {killed_count}")
    print(f"Survived: {survived_count}")
    print(f"Mutation Score: {mutation_score:.1f}%")
    print()
    
    if survived_mutants:
        print("❌ SURVIVED MUTANTS (test weaknesses):")
        for mutant_id, description in survived_mutants:
            print(f"  - Mutant {mutant_id + 1}: {description}")
        print()
    
    print("✅ KILLED MUTANTS (test strengths):")
    for mutant_id, description in killed_mutants:
        print(f"  - Mutant {mutant_id + 1}: {description}")
    
    # Quality assessment
    print("\n" + "=" * 60)
    print("📊 TEST QUALITY ASSESSMENT")
    print("=" * 60)
    
    if mutation_score >= 90:
        quality = "EXCELLENT"
        emoji = "🟢"
    elif mutation_score >= 80:
        quality = "GOOD"
        emoji = "🟡"
    elif mutation_score >= 70:
        quality = "ACCEPTABLE"
        emoji = "🟠"
    else:
        quality = "NEEDS IMPROVEMENT"
        emoji = "🔴"
    
    print(f"{emoji} Test Suite Quality: {quality}")
    print(f"Mutation Score: {mutation_score:.1f}%")
    
    if survived_count == 0:
        print("🎯 Perfect mutation testing score! All mutants killed.")
    else:
        print(f"🎯 {survived_count} mutants survived - consider strengthening tests.")
    
    return mutation_score

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 80 else 1)  # Exit code based on quality threshold