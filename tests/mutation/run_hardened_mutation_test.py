#!/usr/bin/env python3
"""
Enhanced mutation testing for hardened BooleanLiteralNode tests.
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
    """Run enhanced mutation testing on hardened BooleanLiteralNode tests."""
    print("🧬 Running Enhanced Mutation Testing on Hardened BooleanLiteralNode Tests")
    print("=" * 70)
    
    # Read original AST nodes file
    ast_file = "~/TauTranslator/src/tau_translator_omega/core_engine/ast/ast_nodes.py"
    with open(ast_file, 'r') as f:
        original_content = f.read()
    
    # Enhanced mutations targeting the previously surviving mutants
    mutations = [
        # ORIGINAL MUTATIONS
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
        
        # PREVIOUSLY SURVIVING MUTANTS (now targeted)
        ("Remove frozen=True (should be killed)", 
         "@dataclass(frozen=True, eq=True)", 
         "@dataclass(eq=True)"),
        
        ("Remove eq=True (targeted by new tests)", 
         "@dataclass(frozen=True, eq=True)", 
         "@dataclass(frozen=True)"),
        
        ("Change value type annotation (targeted by new tests)", 
         "value: bool", 
         "value: int"),
        
        # ADDITIONAL CHALLENGING MUTATIONS
        ("Invert boolean check", 
         "not isinstance(self.value, bool)", 
         "isinstance(self.value, bool)"),
        
        ("Allow None values", 
         "if not isinstance(self.value, bool):", 
         "if not isinstance(self.value, bool) and self.value is not None:"),
        
        ("Change isinstance to type check", 
         "isinstance(self.value, bool)", 
         "type(self.value) is bool"),
        
        ("Remove __post_init__ entirely", 
         "def __post_init__(self):", 
         "def __disabled_post_init__(self):"),
        
        ("Change ASTNode inheritance", 
         "class BooleanLiteralNode(ASTNode):", 
         "class BooleanLiteralNode():"),
        
        # SUBTLE MUTATIONS
        ("Change validation condition logic", 
         "if not isinstance(self.value, bool):", 
         "if isinstance(self.value, bool):"),
        
        ("Allow any value", 
         "@dataclass(frozen=True, eq=True)", 
         "@dataclass(frozen=True, eq=True, init=False)"),
    ]
    
    test_file = "tests/core_engine/ast_tests/test_boolean_literal_node_mutation_hardened.py"
    
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
    print("\n" + "=" * 70)
    print("🧬 ENHANCED MUTATION TEST RESULTS")
    print("=" * 70)
    
    total_mutants = len(mutated_files)
    killed_count = len(killed_mutants)
    survived_count = len(survived_mutants)
    
    mutation_score = (killed_count / total_mutants * 100) if total_mutants > 0 else 0
    
    print(f"Total Mutants: {total_mutants}")
    print(f"Killed: {killed_count}")
    print(f"Survived: {survived_count}")
    print(f"Mutation Score: {mutation_score:.1f}%")
    print()
    
    # Check if previously surviving mutants are now killed
    previously_surviving = ["Remove eq=True", "Change value type annotation"]
    now_killed = []
    still_surviving = []
    
    for mutant_id, description in survived_mutants:
        if any(prev in description for prev in previously_surviving):
            still_surviving.append(description)
        
    for mutant_id, description in killed_mutants:
        if any(prev in description for prev in previously_surviving):
            now_killed.append(description)
    
    if now_killed:
        print("🎯 PREVIOUSLY SURVIVING MUTANTS NOW KILLED:")
        for desc in now_killed:
            print(f"  ✅ {desc}")
        print()
    
    if still_surviving:
        print("⚠️  STILL SURVIVING MUTANTS:")
        for desc in still_surviving:
            print(f"  ❌ {desc}")
        print()
    
    if survived_mutants:
        print("❌ ALL SURVIVED MUTANTS (test weaknesses):")
        for mutant_id, description in survived_mutants:
            print(f"  - Mutant {mutant_id + 1}: {description}")
        print()
    
    print("✅ KILLED MUTANTS (test strengths):")
    for mutant_id, description in killed_mutants:
        print(f"  - Mutant {mutant_id + 1}: {description}")
    
    # Quality assessment
    print("\n" + "=" * 70)
    print("📊 ENHANCED TEST QUALITY ASSESSMENT")
    print("=" * 70)
    
    if mutation_score >= 95:
        quality = "EXCELLENT"
        emoji = "🟢"
    elif mutation_score >= 85:
        quality = "VERY GOOD"
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
        print("🏆 ACHIEVEMENT: Hardened test suite successfully eliminates all mutations!")
    elif mutation_score >= 90:
        print(f"🎯 Excellent mutation testing score! Only {survived_count} mutants survived.")
        print("✨ ACHIEVEMENT: High-quality test suite with strong mutation resistance!")
    else:
        print(f"🎯 {survived_count} mutants survived - test hardening was partially successful.")
    
    # Compare with previous results
    previous_score = 77.8
    improvement = mutation_score - previous_score
    print(f"\n📈 IMPROVEMENT ANALYSIS:")
    print(f"Previous Score: {previous_score:.1f}%")
    print(f"Current Score: {mutation_score:.1f}%")
    print(f"Improvement: {improvement:+.1f} percentage points")
    
    return mutation_score

if __name__ == "__main__":
    score = main()
    # More stringent exit criteria for enhanced tests
    sys.exit(0 if score >= 90 else 1)