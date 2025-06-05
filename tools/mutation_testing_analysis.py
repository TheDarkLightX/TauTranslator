#!/usr/bin/env python3
"""
Manual Mutation Testing Analysis for TauTranslator
==================================================

This tool demonstrates mutation testing principles by:
1. Analyzing test coverage gaps
2. Identifying weak test assertions 
3. Suggesting improvements for test suite quality

Following VibeArchitect's >80% mutation coverage target.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Set
import subprocess

class MutationAnalyzer:
    """Manual mutation testing analyzer following VibeArchitect principles."""
    
    def __init__(self, source_file: Path, test_dir: Path):
        self.source_file = source_file
        self.test_dir = test_dir
        self.weak_tests = []
        self.mutation_opportunities = []
        
    def analyze_source_mutations(self) -> Dict[str, List[str]]:
        """Identify potential mutation points in source code."""
        
        with open(self.source_file, 'r') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        
        mutations = {
            'comparison_operators': [],
            'arithmetic_operators': [],
            'logical_operators': [],
            'boundary_values': [],
            'conditional_mutations': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                # Comparison operator mutations (== -> !=, > -> <, etc.)
                for op in node.ops:
                    mutations['comparison_operators'].append(f"Line {node.lineno}: {type(op).__name__}")
            
            elif isinstance(node, ast.BinOp):
                # Arithmetic operator mutations (+ -> -, * -> /, etc.)
                mutations['arithmetic_operators'].append(f"Line {node.lineno}: {type(node.op).__name__}")
            
            elif isinstance(node, ast.BoolOp):
                # Logical operator mutations (and -> or, etc.)
                mutations['logical_operators'].append(f"Line {node.lineno}: {type(node.op).__name__}")
            
            elif isinstance(node, ast.If):
                # Conditional mutations (if -> if not, etc.)
                mutations['conditional_mutations'].append(f"Line {node.lineno}: if statement")
        
        return mutations
    
    def analyze_test_quality(self) -> Dict[str, any]:
        """Analyze test quality following VibeArchitect standards."""
        
        test_files = list(self.test_dir.glob("test_*.py"))
        
        analysis = {
            'total_tests': 0,
            'test_files': len(test_files),
            'weak_assertions': [],
            'missing_edge_cases': [],
            'test_quality_score': 0.0
        }
        
        for test_file in test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        analysis['total_tests'] += 1
                        
                        # Check for weak assertions
                        has_assertions = False
                        assertion_count = 0
                        
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                if hasattr(child.func, 'attr'):
                                    if child.func.attr.startswith('assert'):
                                        has_assertions = True
                                        assertion_count += 1
                        
                        if not has_assertions:
                            analysis['weak_assertions'].append(f"{test_file.name}::{node.name} - No assertions")
                        elif assertion_count == 1:
                            analysis['weak_assertions'].append(f"{test_file.name}::{node.name} - Single assertion (weak)")
        
        # Calculate quality score
        if analysis['total_tests'] > 0:
            weak_ratio = len(analysis['weak_assertions']) / analysis['total_tests']
            analysis['test_quality_score'] = max(0.0, 1.0 - weak_ratio)
        
        return analysis
    
    def suggest_improvements(self) -> List[str]:
        """Suggest test improvements based on VibeArchitect principles."""
        
        suggestions = []
        
        # Analyze mutation opportunities
        mutations = self.analyze_source_mutations()
        test_analysis = self.analyze_test_quality()
        
        suggestions.append("🎯 **MUTATION TESTING ANALYSIS RESULTS**")
        suggestions.append("")
        
        # File size violations first (VibeArchitect prime directive)
        if self.source_file.stat().st_size > 0:
            with open(self.source_file, 'r') as f:
                line_count = len(f.readlines())
                if line_count > 600:
                    suggestions.append(f"🚨 **CRITICAL**: File {self.source_file.name} has {line_count} lines (>600 limit)")
                    suggestions.append("   → REFACTOR IMMEDIATELY using Strategy/Factory patterns")
                    suggestions.append("")
        
        # Mutation opportunities
        suggestions.append(f"🔬 **Mutation Opportunities Found:**")
        total_mutations = sum(len(v) for v in mutations.values())
        suggestions.append(f"   - Total mutation points: {total_mutations}")
        
        for category, items in mutations.items():
            if items:
                suggestions.append(f"   - {category.replace('_', ' ').title()}: {len(items)}")
        
        suggestions.append("")
        
        # Test quality analysis
        quality_score = test_analysis['test_quality_score']
        suggestions.append(f"📊 **Test Quality Score: {quality_score:.2f}/1.0**")
        
        if quality_score < 0.8:  # VibeArchitect minimum
            suggestions.append("🚨 **QUALITY VIOLATION**: Test quality below 80% threshold")
        
        suggestions.append(f"   - Total tests: {test_analysis['total_tests']}")
        suggestions.append(f"   - Weak assertions: {len(test_analysis['weak_assertions'])}")
        
        # Specific improvements
        suggestions.append("")
        suggestions.append("🛠️ **Specific Improvements Needed:**")
        
        if test_analysis['weak_assertions']:
            suggestions.append("   **Weak Test Assertions:**")
            for weak in test_analysis['weak_assertions'][:5]:  # Show first 5
                suggestions.append(f"     - {weak}")
            if len(test_analysis['weak_assertions']) > 5:
                suggestions.append(f"     ... and {len(test_analysis['weak_assertions']) - 5} more")
        
        # VibeArchitect specific recommendations
        suggestions.append("")
        suggestions.append("📋 **VibeArchitect Compliance Recommendations:**")
        suggestions.append("   1. Add property-based tests using hypothesis")
        suggestions.append("   2. Implement boundary value analysis for all inputs")
        suggestions.append("   3. Add negative test cases for error paths")
        suggestions.append("   4. Use multiple assertions per test (AAA pattern)")
        suggestions.append("   5. Add performance assertions (<100ms per test)")
        suggestions.append("   6. Implement contract testing for public APIs")
        
        # Mutation testing recommendations
        suggestions.append("")
        suggestions.append("🧬 **Manual Mutation Testing Protocol:**")
        suggestions.append("   1. Replace == with != in comparisons")
        suggestions.append("   2. Change > to >= in boundary conditions") 
        suggestions.append("   3. Replace 'and' with 'or' in logical expressions")
        suggestions.append("   4. Change +1 to -1 in arithmetic operations")
        suggestions.append("   5. Replace 'if' with 'if not' in conditionals")
        
        return suggestions
    
    def run_baseline_tests(self) -> bool:
        """Run baseline tests to ensure they pass before mutation testing."""
        
        print("🧪 Running baseline tests...")
        
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(self.test_dir), 
            "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=self.source_file.parent.parent.parent.parent)
        
        if result.returncode == 0:
            print("✅ Baseline tests pass")
            return True
        else:
            print("❌ Baseline tests fail:")
            print(result.stdout)
            print(result.stderr)
            return False

def main():
    """Run mutation testing analysis on AST nodes."""
    
    project_root = Path(__file__).parent.parent
    source_file = project_root / "src/tau_translator_omega/core_engine/ast/ast_nodes.py"
    test_dir = project_root / "tests/core_engine/ast_tests"
    
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        return 1
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return 1
    
    analyzer = MutationAnalyzer(source_file, test_dir)
    
    # Run baseline tests first
    if not analyzer.run_baseline_tests():
        print("❌ Cannot proceed with mutation analysis - baseline tests failing")
        return 1
    
    # Generate improvement suggestions
    suggestions = analyzer.suggest_improvements()
    
    print("\n" + "\n".join(suggestions))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())