#!/usr/bin/env python3
"""Comprehensive code quality analyzer for TauTranslator project.

Measures:
- Method length (target: ≤10 lines)
- Cyclomatic complexity (target: ≤2.0)
- Missing Result[T] error handling
- Pure functions without @mutation_free decorator
"""

import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import json
from collections import defaultdict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class MethodMetrics:
    """Metrics for a single method."""
    name: str
    line_count: int
    cyclomatic_complexity: int
    has_error_handling: bool
    is_pure_candidate: bool
    has_mutation_free: bool
    start_line: int
    end_line: int


@dataclass
class ModuleMetrics:
    """Metrics for an entire module."""
    path: str
    methods: List[MethodMetrics] = field(default_factory=list)
    total_lines: int = 0
    imports_result: bool = False
    imports_mutation_free: bool = False
    
    @property
    def methods_over_10_lines(self) -> List[MethodMetrics]:
        return [m for m in self.methods if m.line_count > 10]
    
    @property
    def high_complexity_methods(self) -> List[MethodMetrics]:
        return [m for m in self.methods if m.cyclomatic_complexity > 2]
    
    @property
    def methods_needing_result(self) -> List[MethodMetrics]:
        return [m for m in self.methods if not m.has_error_handling and m.line_count > 5]
    
    @property
    def pure_functions_without_decorator(self) -> List[MethodMetrics]:
        return [m for m in self.methods if m.is_pure_candidate and not m.has_mutation_free]
    
    @property
    def refactoring_score(self) -> float:
        """Calculate refactoring priority score (higher = needs more refactoring)."""
        score = 0.0
        
        # Weight factors
        score += len(self.methods_over_10_lines) * 3.0
        score += len(self.high_complexity_methods) * 2.5
        score += len(self.methods_needing_result) * 1.5
        score += len(self.pure_functions_without_decorator) * 1.0
        
        # Normalize by total methods
        if self.methods:
            score = score / len(self.methods)
        
        return score


class QualityAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze code quality metrics."""
    
    def __init__(self):
        self.current_module: Optional[ModuleMetrics] = None
        self.current_method: Optional[MethodMetrics] = None
        self.in_try_except = False
        self.complexity_stack = []
        self.has_side_effects = False
        self.accesses_self = False
        self.decorators: List[str] = []
        
    def analyze_file(self, filepath: str) -> ModuleMetrics:
        """Analyze a single Python file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
            self.current_module = ModuleMetrics(path=filepath, total_lines=len(content.splitlines()))
            
            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and 'result' in node.module.lower():
                        self.current_module.imports_result = True
                    if node.module and ('ufo' in node.module or 'mutation_free' in str(node.names)):
                        self.current_module.imports_mutation_free = True
                        
            self.visit(tree)
            return self.current_module
        except SyntaxError:
            return ModuleMetrics(path=filepath, total_lines=0)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition."""
        self._visit_function(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definition."""
        self._visit_function(node)
        
    def _visit_function(self, node):
        """Process function/method definition."""
        # Store decorator names
        self.decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        # Calculate line count (excluding decorators and docstring)
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        # Skip docstring if present
        first_stmt = node.body[0] if node.body else None
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
            if isinstance(first_stmt.value.value, str):
                # This is a docstring, adjust start line
                if len(node.body) > 1:
                    start_line = node.body[1].lineno
                    
        line_count = end_line - start_line + 1
        
        # Reset analysis state
        self.in_try_except = False
        self.complexity_stack = [1]  # Base complexity
        self.has_side_effects = False
        self.accesses_self = False
        
        # Analyze method body
        for stmt in node.body:
            self.visit(stmt)
            
        # Determine if function is pure (candidate for @mutation_free)
        is_pure_candidate = (
            not self.has_side_effects and
            not self.accesses_self and
            not node.name.startswith('_') and
            not node.name.startswith('test_') and
            'property' not in self.decorators
        )
        
        # Check for error handling patterns
        has_error_handling = (
            self.in_try_except or
            any('Result' in str(node.returns) for node in ast.walk(node) if isinstance(node, ast.FunctionDef)) or
            'Result' in str(node.returns) if node.returns else False
        )
        
        # Create method metrics
        method = MethodMetrics(
            name=node.name,
            line_count=line_count,
            cyclomatic_complexity=max(self.complexity_stack),
            has_error_handling=has_error_handling,
            is_pure_candidate=is_pure_candidate,
            has_mutation_free='mutation_free' in self.decorators,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno
        )
        
        self.current_module.methods.append(method)
        
    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return ""
        
    def visit_If(self, node: ast.If):
        """Visit if statement (increases complexity)."""
        self.complexity_stack[-1] += 1
        self.generic_visit(node)
        
    def visit_While(self, node: ast.While):
        """Visit while loop (increases complexity)."""
        self.complexity_stack[-1] += 1
        self.generic_visit(node)
        
    def visit_For(self, node: ast.For):
        """Visit for loop (increases complexity)."""
        self.complexity_stack[-1] += 1
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Visit except handler (increases complexity)."""
        self.complexity_stack[-1] += 1
        self.in_try_except = True
        self.generic_visit(node)
        
    def visit_BoolOp(self, node: ast.BoolOp):
        """Visit boolean operation (and/or increases complexity)."""
        if isinstance(node.op, (ast.And, ast.Or)):
            self.complexity_stack[-1] += len(node.values) - 1
        self.generic_visit(node)
        
    def visit_Attribute(self, node: ast.Attribute):
        """Check for self access."""
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            self.accesses_self = True
        self.generic_visit(node)
        
    def visit_Call(self, node: ast.Call):
        """Check for side effects."""
        # Common side effect patterns
        if isinstance(node.func, ast.Name):
            if node.func.id in {'print', 'write', 'append', 'extend', 'remove', 'pop', 'clear'}:
                self.has_side_effects = True
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in {'write', 'append', 'extend', 'remove', 'pop', 'clear', 'update'}:
                self.has_side_effects = True
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign):
        """Check for mutations."""
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                self.has_side_effects = True
            elif isinstance(target, ast.Subscript):
                self.has_side_effects = True
        self.generic_visit(node)


def analyze_codebase(directories: List[str]) -> List[ModuleMetrics]:
    """Analyze all Python files in specified directories."""
    analyzer = QualityAnalyzer()
    results = []
    
    for directory in directories:
        base_path = Path(directory)
        if not base_path.exists():
            continue
            
        for py_file in base_path.rglob("*.py"):
            # Skip test files and __pycache__
            if ('test_' in py_file.name or 
                'tests' in py_file.parts or 
                '__pycache__' in str(py_file) or
                'deprecated' in str(py_file) or
                'backup' in str(py_file)):
                continue
                
            metrics = analyzer.analyze_file(str(py_file))
            if metrics.methods:  # Only include files with methods
                results.append(metrics)
                
    return results


def generate_report(modules: List[ModuleMetrics]) -> None:
    """Generate refactoring priority report."""
    # Sort by refactoring score
    modules.sort(key=lambda m: m.refactoring_score, reverse=True)
    
    print("=" * 80)
    print("TAUTRANSLATOR CODE QUALITY ANALYSIS - REFACTORING PRIORITIES")
    print("=" * 80)
    print()
    
    # Top 10 modules needing refactoring
    print("TOP 10 MODULES NEEDING REFACTORING:")
    print("-" * 80)
    
    for i, module in enumerate(modules[:10], 1):
        rel_path = str(Path(module.path).relative_to(PROJECT_ROOT))
        print(f"\n{i}. {rel_path}")
        print(f"   Refactoring Score: {module.refactoring_score:.2f}")
        print(f"   Total Methods: {len(module.methods)}")
        
        if module.methods_over_10_lines:
            print(f"   - Methods >10 lines: {len(module.methods_over_10_lines)}")
            for m in module.methods_over_10_lines[:3]:
                print(f"     • {m.name}: {m.line_count} lines")
                
        if module.high_complexity_methods:
            print(f"   - High complexity methods (CC >2): {len(module.high_complexity_methods)}")
            for m in module.high_complexity_methods[:3]:
                print(f"     • {m.name}: CC={m.cyclomatic_complexity}")
                
        if module.methods_needing_result:
            print(f"   - Methods needing Result[T]: {len(module.methods_needing_result)}")
            for m in module.methods_needing_result[:3]:
                print(f"     • {m.name}")
                
        if module.pure_functions_without_decorator:
            print(f"   - Pure functions without @mutation_free: {len(module.pure_functions_without_decorator)}")
            for m in module.pure_functions_without_decorator[:3]:
                print(f"     • {m.name}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("OVERALL STATISTICS:")
    print("-" * 80)
    
    total_methods = sum(len(m.methods) for m in modules)
    total_over_10 = sum(len(m.methods_over_10_lines) for m in modules)
    total_high_cc = sum(len(m.high_complexity_methods) for m in modules)
    total_need_result = sum(len(m.methods_needing_result) for m in modules)
    total_need_decorator = sum(len(m.pure_functions_without_decorator) for m in modules)
    
    print(f"Total modules analyzed: {len(modules)}")
    print(f"Total methods: {total_methods}")
    print(f"Methods over 10 lines: {total_over_10} ({total_over_10/total_methods*100:.1f}%)")
    print(f"High complexity methods: {total_high_cc} ({total_high_cc/total_methods*100:.1f}%)")
    print(f"Methods needing Result[T]: {total_need_result}")
    print(f"Pure functions without @mutation_free: {total_need_decorator}")
    
    # Save detailed results to JSON
    output_data = []
    for module in modules[:10]:
        output_data.append({
            'path': str(Path(module.path).relative_to(PROJECT_ROOT)),
            'refactoring_score': module.refactoring_score,
            'total_methods': len(module.methods),
            'methods_over_10_lines': len(module.methods_over_10_lines),
            'high_complexity_methods': len(module.high_complexity_methods),
            'methods_needing_result': len(module.methods_needing_result),
            'pure_functions_without_decorator': len(module.pure_functions_without_decorator),
            'details': {
                'long_methods': [{'name': m.name, 'lines': m.line_count} 
                               for m in module.methods_over_10_lines],
                'complex_methods': [{'name': m.name, 'complexity': m.cyclomatic_complexity} 
                                  for m in module.high_complexity_methods],
                'need_result': [m.name for m in module.methods_needing_result],
                'need_decorator': [m.name for m in module.pure_functions_without_decorator]
            }
        })
    
    with open('refactoring_priorities.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nDetailed results saved to: refactoring_priorities.json")


def main():
    """Main entry point."""
    directories = [
        str(PROJECT_ROOT / 'backend' / 'unified'),
        str(PROJECT_ROOT / 'src' / 'tau_translator_omega')
    ]
    
    print("Analyzing TauTranslator codebase...")
    modules = analyze_codebase(directories)
    generate_report(modules)


if __name__ == '__main__':
    main()