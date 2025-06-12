#!/usr/bin/env python3
"""
Method-level complexity analyzer for Python code.
Analyzes each method for line count and cyclomatic complexity.

Copyright: DarkLightX/Dana Edwards
"""

import ast
import sys
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class MethodMetrics:
    """Metrics for a single method."""
    class_name: str
    method_name: str
    start_line: int
    end_line: int
    line_count: int
    cyclomatic_complexity: int
    
    @property
    def full_name(self) -> str:
        if self.class_name:
            return f"{self.class_name}.{self.method_name}"
        return self.method_name


class MethodComplexityAnalyzer(ast.NodeVisitor):
    """Analyzes complexity at the method level."""
    
    def __init__(self):
        self.methods: List[MethodMetrics] = []
        self.current_class = None
        self.current_complexity = 0
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Track class context."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze function/method definition."""
        # Save current state
        saved_complexity = self.current_complexity
        self.current_complexity = 1  # Base complexity
        
        # Calculate complexity for this method
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                self.current_complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                self.current_complexity += 1
            elif isinstance(child, ast.BoolOp):
                self.current_complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                self.current_complexity += 1
        
        # Calculate line count
        line_count = node.end_lineno - node.lineno + 1
        
        # Record metrics
        self.methods.append(MethodMetrics(
            class_name=self.current_class or "",
            method_name=node.name,
            start_line=node.lineno,
            end_line=node.end_lineno,
            line_count=line_count,
            cyclomatic_complexity=self.current_complexity
        ))
        
        # Restore state
        self.current_complexity = saved_complexity
        
    visit_AsyncFunctionDef = visit_FunctionDef


def analyze_file(file_path: str) -> List[MethodMetrics]:
    """Analyze a Python file for method-level metrics."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    analyzer = MethodComplexityAnalyzer()
    analyzer.visit(tree)
    
    return analyzer.methods


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_method_complexity.py <file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    metrics = analyze_file(file_path)
    
    print(f"\nMethod Analysis for {file_path}")
    print("=" * 80)
    print(f"{'Method':<50} {'Lines':>8} {'CC':>5}")
    print("-" * 80)
    
    violations = []
    
    for method in sorted(metrics, key=lambda m: m.start_line):
        status = ""
        if method.line_count > 10:
            status += " [LONG]"
            violations.append((method, "exceeds 10 lines"))
        if method.cyclomatic_complexity > 10:
            status += " [COMPLEX]"
            violations.append((method, f"CC={method.cyclomatic_complexity}"))
            
        print(f"{method.full_name:<50} {method.line_count:>8} {method.cyclomatic_complexity:>5}{status}")
    
    print("-" * 80)
    print(f"Total methods: {len(metrics)}")
    
    if violations:
        print("\nViolations:")
        for method, reason in violations:
            print(f"  - {method.full_name} ({method.start_line}-{method.end_line}): {reason}")
    else:
        print("\nNo violations found!")


if __name__ == '__main__':
    main()
