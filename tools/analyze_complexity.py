#!/usr/bin/env python3
"""
Code Complexity Analysis Tool
============================
Analyze cyclomatic complexity and identify refactoring opportunities
in the enhanced NLP system.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ComplexityResult:
    """Result of complexity analysis for a function/method"""
    name: str
    file_path: str
    line_number: int
    complexity: int
    lines_of_code: int
    issues: List[str]

class ComplexityAnalyzer(ast.NodeVisitor):
    """Analyzes cyclomatic complexity of Python code"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.results: List[ComplexityResult] = []
        self.current_function = None
        self.complexity = 0
        self.lines_of_code = 0
        
    def visit_FunctionDef(self, node):
        """Analyze function/method complexity"""
        old_function = self.current_function
        old_complexity = self.complexity
        old_lines = self.lines_of_code
        
        self.current_function = node.name
        self.complexity = 1  # Base complexity
        self.lines_of_code = 0
        
        # Visit function body
        self.generic_visit(node)
        
        # Calculate lines of code
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            self.lines_of_code = node.end_lineno - node.lineno + 1
        
        # Identify issues
        issues = []
        if self.complexity > 10:
            issues.append(f"High cyclomatic complexity: {self.complexity}")
        if self.lines_of_code > 50:
            issues.append(f"Long function: {self.lines_of_code} lines")
        if len(node.args.args) > 5:
            issues.append(f"Too many parameters: {len(node.args.args)}")
        
        # Store result
        result = ComplexityResult(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno,
            complexity=self.complexity,
            lines_of_code=self.lines_of_code,
            issues=issues
        )
        self.results.append(result)
        
        # Restore previous state
        self.current_function = old_function
        self.complexity = old_complexity
        self.lines_of_code = old_lines
    
    # Count complexity-increasing constructs
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        # Count 'and' and 'or' operations
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

def analyze_file(file_path: Path) -> List[ComplexityResult]:
    """Analyze complexity of a single Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(file_path))
        analyzer = ComplexityAnalyzer(str(file_path))
        analyzer.visit(tree)
        
        return analyzer.results
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return []

def analyze_project():
    """Analyze complexity of the entire NLP enhanced project"""
    
    # Target files to analyze
    target_files = [
        "src/tau_translator_omega/core_engine/nlp_enhanced/english_to_tau_translator.py",
        "src/tau_translator_omega/core_engine/nlp_enhanced/requirements_analyzer.py", 
        "src/tau_translator_omega/core_engine/nlp_enhanced/amr_semantic_layer.py",
        "src/tau_translator_omega/core_engine/nlp_enhanced/incremental_parser.py"
    ]
    
    all_results = []
    
    print("🔍 Analyzing Code Complexity")
    print("=" * 50)
    
    for file_path in target_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"\n📁 Analyzing: {file_path}")
            results = analyze_file(full_path)
            all_results.extend(results)
            
            # Show file summary
            if results:
                avg_complexity = sum(r.complexity for r in results) / len(results)
                max_complexity = max(r.complexity for r in results)
                print(f"  Functions: {len(results)}")
                print(f"  Avg Complexity: {avg_complexity:.1f}")
                print(f"  Max Complexity: {max_complexity}")
        else:
            print(f"❌ File not found: {file_path}")
    
    # Overall analysis
    print(f"\n" + "=" * 50)
    print("📊 Overall Analysis")
    print("=" * 50)
    
    if all_results:
        # Sort by complexity
        all_results.sort(key=lambda r: r.complexity, reverse=True)
        
        print(f"Total functions analyzed: {len(all_results)}")
        print(f"Average complexity: {sum(r.complexity for r in all_results) / len(all_results):.1f}")
        
        # Top complex functions
        print(f"\n🔥 Top 10 Most Complex Functions:")
        print("-" * 60)
        print("Function".ljust(25) + "Complexity".ljust(12) + "Lines".ljust(8) + "File")
        print("-" * 60)
        
        for result in all_results[:10]:
            file_name = Path(result.file_path).name
            print(f"{result.name[:24]:25} {result.complexity:11} {result.lines_of_code:7} {file_name}")
        
        # Functions needing refactoring
        high_complexity = [r for r in all_results if r.complexity > 10]
        long_functions = [r for r in all_results if r.lines_of_code > 50]
        
        print(f"\n⚠️  Refactoring Candidates:")
        print(f"  High complexity (>10): {len(high_complexity)} functions")
        print(f"  Long functions (>50 lines): {len(long_functions)} functions")
        
        if high_complexity:
            print(f"\n🎯 Priority Refactoring Targets:")
            for result in high_complexity[:5]:
                print(f"  • {result.name} (complexity: {result.complexity}, lines: {result.lines_of_code})")
                for issue in result.issues:
                    print(f"    - {issue}")
    
    return all_results

if __name__ == "__main__":
    analyze_project()