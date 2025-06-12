#!/usr/bin/env python3
"""
Focused Refactoring Analysis for TauTranslator
Analyzes specific directories for Intentional Disclosure Principle violations
Copyright: DarkLightX/Dana Edwards
"""

import ast
import os
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import radon.complexity as radon_cc
from radon.metrics import mi_visit
import re


@dataclass
class FileMetrics:
    """Comprehensive metrics for a single file."""
    file_path: str
    total_lines: int
    methods: List[Dict[str, any]]
    cyclomatic_complexity: int
    maintainability_index: float
    violations: List[str]
    priority_score: float


class IntentionalDisclosureAnalyzer:
    """Analyzes code for Intentional Disclosure Principle violations."""
    
    def __init__(self):
        self.results = []
        
    def analyze_file(self, file_path: str) -> Optional[FileMetrics]:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                
            if not source.strip():
                return None
                
            tree = ast.parse(source)
            
            # Get basic metrics
            lines = source.count('\n')
            
            # Analyze methods
            methods = self._analyze_methods(tree, source)
            
            # Calculate complexity
            cc_results = radon_cc.cc_visit(source)
            total_cc = sum(item.complexity for item in cc_results)
            
            # Maintainability index
            mi = mi_visit(source, True)
            
            # Check violations
            violations = self._check_violations(tree, source, methods)
            
            # Calculate priority score
            priority = self._calculate_priority(methods, total_cc, violations)
            
            return FileMetrics(
                file_path=file_path,
                total_lines=lines,
                methods=methods,
                cyclomatic_complexity=total_cc,
                maintainability_index=mi,
                violations=violations,
                priority_score=priority
            )
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
            
    def _analyze_methods(self, tree: ast.AST, source: str) -> List[Dict]:
        """Analyze all methods in the file."""
        methods = []
        
        class MethodVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                methods.append(self._analyze_single_method(node, False))
                self.generic_visit(node)
                
            def visit_AsyncFunctionDef(self, node):
                methods.append(self._analyze_single_method(node, True))
                self.generic_visit(node)
                
            def _analyze_single_method(self, node, is_async):
                # Calculate method lines
                method_lines = node.end_lineno - node.lineno + 1
                
                # Check for docstring
                has_docstring = (
                    node.body and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant)
                )
                
                # Calculate effective lines (excluding docstring)
                if has_docstring:
                    docstring_lines = node.body[0].end_lineno - node.body[0].lineno + 1
                    effective_lines = method_lines - docstring_lines
                else:
                    effective_lines = method_lines
                    
                # Count statements
                statement_count = len([
                    stmt for stmt in node.body 
                    if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
                ])
                
                # Check for I/O operations
                has_io = self._check_io_operations(node)
                
                # Check naming
                naming_issues = self._check_naming(node.name, is_async, has_io)
                
                # Check for mixed concerns
                has_mixed_concerns = self._check_mixed_concerns(node)
                
                # Check for primitive obsession
                has_primitives = self._check_primitive_obsession(node)
                
                return {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno,
                    'total_lines': method_lines,
                    'effective_lines': effective_lines,
                    'statement_count': statement_count,
                    'is_async': is_async,
                    'has_io': has_io,
                    'naming_issues': naming_issues,
                    'has_mixed_concerns': has_mixed_concerns,
                    'has_primitive_obsession': has_primitives,
                    'exceeds_10_lines': effective_lines > 10
                }
                
            def _check_io_operations(self, node):
                """Check if method contains I/O operations."""
                io_indicators = {
                    'open', 'read', 'write', 'load', 'save', 'fetch',
                    'requests', 'aiohttp', 'asyncio', 'subprocess',
                    'pathlib', 'json.load', 'json.dump', 'sqlite3',
                    'redis', 'mongodb', 'file', 'disk', 'network'
                }
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Name) and child.id in io_indicators:
                        return True
                    if isinstance(child, ast.Attribute) and child.attr in io_indicators:
                        return True
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id in io_indicators:
                            return True
                            
                return False
                
            def _check_naming(self, name, is_async, has_io):
                """Check naming conventions."""
                issues = []
                
                if is_async and not name.endswith('_async'):
                    issues.append('missing_async_suffix')
                    
                if has_io:
                    io_verbs = ['read', 'write', 'fetch', 'save', 'load', 'get', 'post']
                    if not any(verb in name.lower() for verb in io_verbs):
                        issues.append('undisclosed_io')
                        
                return issues
                
            def _check_mixed_concerns(self, node):
                """Check for mixed business logic and I/O."""
                has_business_logic = False
                has_io = False
                
                for child in ast.walk(node):
                    # Check for business logic indicators
                    if isinstance(child, (ast.If, ast.For, ast.While)):
                        has_business_logic = True
                        
                    # Check for I/O
                    if isinstance(child, ast.Call):
                        if hasattr(child.func, 'id') and child.func.id in ['open', 'read', 'write']:
                            has_io = True
                            
                return has_business_logic and has_io
                
            def _check_primitive_obsession(self, node):
                """Check for lack of domain types."""
                # Check parameters
                for arg in node.args.args:
                    if not arg.annotation:
                        return True
                        
                # Check return type
                if not node.returns:
                    return True
                    
                return False
                
        visitor = MethodVisitor()
        visitor.visit(tree)
        return methods
        
    def _check_violations(self, tree: ast.AST, source: str, methods: List[Dict]) -> List[str]:
        """Check for all violations."""
        violations = []
        
        # Check method length violations
        long_methods = [m for m in methods if m['exceeds_10_lines']]
        if long_methods:
            violations.append(f"{len(long_methods)} methods exceed 10 lines")
            
        # Check naming violations
        naming_issues = [m for m in methods if m['naming_issues']]
        if naming_issues:
            violations.append(f"{len(naming_issues)} methods have naming issues")
            
        # Check mixed concerns
        mixed_concerns = [m for m in methods if m['has_mixed_concerns']]
        if mixed_concerns:
            violations.append(f"{len(mixed_concerns)} methods have mixed concerns")
            
        # Check primitive obsession
        primitives = [m for m in methods if m['has_primitive_obsession']]
        if primitives:
            violations.append(f"{len(primitives)} methods lack proper type annotations")
            
        return violations
        
    def _calculate_priority(self, methods: List[Dict], complexity: int, violations: List[str]) -> float:
        """Calculate refactoring priority score (0-100)."""
        score = 0
        
        # Method length impact (40%)
        long_methods = sum(1 for m in methods if m['exceeds_10_lines'])
        score += (long_methods / max(len(methods), 1)) * 40
        
        # Complexity impact (30%)
        if complexity > 10:
            score += min(30, (complexity - 10) * 3)
            
        # Violations impact (30%)
        score += min(30, len(violations) * 10)
        
        return min(100, score)
        
    def analyze_directory(self, directory: str, pattern: str = "*.py") -> List[FileMetrics]:
        """Analyze all Python files in a directory."""
        results = []
        
        for root, dirs, files in os.walk(directory):
            # Skip test directories
            if 'test' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    metrics = self.analyze_file(file_path)
                    if metrics:
                        results.append(metrics)
                        
        return results
        
    def generate_report(self, results: List[FileMetrics]) -> str:
        """Generate a prioritized refactoring report."""
        # Sort by priority
        sorted_results = sorted(results, key=lambda x: x.priority_score, reverse=True)
        
        report = []
        report.append("# Intentional Disclosure Principle - Refactoring Analysis\n")
        report.append(f"Analyzed {len(results)} files\n")
        
        # Summary statistics
        total_violations = sum(len(r.violations) for r in results)
        files_needing_refactor = sum(1 for r in results if r.priority_score > 30)
        
        report.append("## Summary")
        report.append(f"- Files needing refactoring: {files_needing_refactor}")
        report.append(f"- Total violations: {total_violations}")
        report.append(f"- Average priority score: {sum(r.priority_score for r in results) / len(results):.1f}\n")
        
        # Top priority files
        report.append("## High Priority Files (Score > 50)\n")
        
        for result in sorted_results:
            if result.priority_score < 50:
                break
                
            report.append(f"### {result.file_path}")
            report.append(f"**Priority Score: {result.priority_score:.1f}/100**")
            report.append(f"- Lines: {result.total_lines}")
            report.append(f"- Cyclomatic Complexity: {result.cyclomatic_complexity}")
            report.append(f"- Maintainability Index: {result.maintainability_index:.2f}")
            
            if result.violations:
                report.append("\n**Violations:**")
                for violation in result.violations:
                    report.append(f"- {violation}")
                    
            # Detailed method analysis
            long_methods = [m for m in result.methods if m['exceeds_10_lines']]
            if long_methods:
                report.append("\n**Methods exceeding 10 lines:**")
                for method in long_methods:
                    report.append(f"- `{method['name']}` ({method['effective_lines']} lines)")
                    if method['naming_issues']:
                        report.append(f"  - Naming issues: {', '.join(method['naming_issues'])}")
                    if method['has_mixed_concerns']:
                        report.append(f"  - Mixed business logic with I/O")
                    if method['has_primitive_obsession']:
                        report.append(f"  - Missing type annotations")
                        
            report.append("")
            
        return '\n'.join(report)


def main():
    """Main entry point."""
    analyzer = IntentionalDisclosureAnalyzer()
    
    # Analyze specific directories
    directories = [
        "backend/unified/api",
        "backend/unified/core",
        "backend/unified/translators",
        "src/tau_translator_omega/core_engine"
    ]
    
    all_results = []
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"Analyzing {directory}...")
            results = analyzer.analyze_directory(directory)
            all_results.extend(results)
            
    # Generate report
    if all_results:
        report = analyzer.generate_report(all_results)
        
        # Save report
        with open('intentional_disclosure_analysis.md', 'w') as f:
            f.write(report)
            
        print(report)
        
        # Also save JSON for further processing
        json_data = []
        for result in all_results:
            json_data.append({
                'file_path': result.file_path,
                'priority_score': result.priority_score,
                'total_lines': result.total_lines,
                'cyclomatic_complexity': result.cyclomatic_complexity,
                'maintainability_index': result.maintainability_index,
                'violations': result.violations,
                'methods': result.methods
            })
            
        with open('intentional_disclosure_analysis.json', 'w') as f:
            json.dump(json_data, f, indent=2)
            
        print(f"\nAnalysis complete. Results saved to:")
        print("- intentional_disclosure_analysis.md")
        print("- intentional_disclosure_analysis.json")
    else:
        print("No Python files found to analyze.")


if __name__ == '__main__':
    main()