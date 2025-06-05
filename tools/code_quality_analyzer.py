#!/usr/bin/env python3
"""
Code Quality Analyzer
=====================

Analyzes code quality metrics including cyclomatic complexity,
maintainability index, test coverage, and adherence to clean code principles.

Author: DarkLightX/Dana Edwards
"""

import ast
import os
import sys
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class QualityMetrics:
    """Container for code quality metrics."""
    file_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    maintainability_index: float
    method_count: int
    class_count: int
    max_method_length: int
    average_method_length: float
    test_coverage: Optional[float] = None
    violations: List[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []
    
    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        score = 100.0
        
        # Cyclomatic complexity penalties
        if self.cyclomatic_complexity > 10:
            score -= (self.cyclomatic_complexity - 10) * 2
        
        # Cognitive complexity penalties
        if self.cognitive_complexity > 15:
            score -= (self.cognitive_complexity - 15) * 1.5
        
        # File size penalties
        if self.lines_of_code > 600:
            score -= (self.lines_of_code - 600) * 0.1
        
        # Method length penalties
        if self.max_method_length > 50:
            score -= (self.max_method_length - 50) * 0.5
        
        # Maintainability index bonus/penalty
        if self.maintainability_index < 20:
            score -= 20
        elif self.maintainability_index > 50:
            score += 5
        
        # Test coverage bonus
        if self.test_coverage and self.test_coverage >= 95:
            score += 10
        
        return max(0, min(100, score))


class ComplexityCalculator(ast.NodeVisitor):
    """Calculates cyclomatic and cognitive complexity."""
    
    def __init__(self):
        self.cyclomatic = 1  # Base complexity
        self.cognitive = 0
        self.nesting_level = 0
        self.method_complexities = []
        self.current_method_complexity = 0
        
    def visit_If(self, node):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_While(self, node):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_For(self, node):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_ExceptHandler(self, node):
        self.cyclomatic += 1
        self.cognitive += 1 + self.nesting_level
        self.generic_visit(node)
        
    def visit_BoolOp(self, node):
        # Each boolean operator adds to complexity
        self.cyclomatic += len(node.values) - 1
        self.cognitive += len(node.values) - 1
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        # Save current complexity for nested functions
        saved_cyclomatic = self.cyclomatic
        saved_cognitive = self.cognitive
        
        # Reset for this function
        self.cyclomatic = 1
        self.cognitive = 0
        
        # Visit function body
        self.generic_visit(node)
        
        # Record this function's complexity
        self.method_complexities.append({
            'name': node.name,
            'cyclomatic': self.cyclomatic,
            'cognitive': self.cognitive
        })
        
        # Restore parent complexity
        self.cyclomatic = saved_cyclomatic
        self.cognitive = saved_cognitive


class CodeQualityAnalyzer:
    """Main code quality analyzer."""
    
    def __init__(self):
        self.metrics = {}
        self.best_practices_violations = []
        
    def analyze_file(self, file_path: str) -> QualityMetrics:
        """Analyze a single Python file."""
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Parse AST
        tree = ast.parse(content)
        
        # Calculate basic metrics
        lines = content.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Calculate complexity
        complexity_calc = ComplexityCalculator()
        complexity_calc.visit(tree)
        
        # Count classes and methods
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        method_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        
        # Calculate method lengths
        method_lengths = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    length = node.end_lineno - node.lineno + 1
                    method_lengths.append(length)
        
        max_method_length = max(method_lengths) if method_lengths else 0
        avg_method_length = sum(method_lengths) / len(method_lengths) if method_lengths else 0
        
        # Calculate maintainability index
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(L)
        # Simplified version: V=volume, G=cyclomatic complexity, L=lines
        import math
        volume = loc * math.log2(method_count + 1) if method_count > 0 else 1
        maintainability = 171 - 5.2 * math.log(volume) - 0.23 * complexity_calc.cyclomatic - 16.2 * math.log(loc)
        maintainability = max(0, min(100, maintainability))
        
        # Check for violations
        violations = self._check_violations(tree, content, loc, complexity_calc)
        
        return QualityMetrics(
            file_path=file_path,
            lines_of_code=loc,
            cyclomatic_complexity=complexity_calc.cyclomatic,
            cognitive_complexity=complexity_calc.cognitive,
            maintainability_index=maintainability,
            method_count=method_count,
            class_count=class_count,
            max_method_length=max_method_length,
            average_method_length=avg_method_length,
            violations=violations
        )
    
    def _check_violations(self, tree: ast.AST, content: str, loc: int, 
                         complexity: ComplexityCalculator) -> List[str]:
        """Check for clean code violations."""
        violations = []
        
        # File size check
        if loc > 600:
            violations.append(f"File exceeds 600 lines ({loc} lines)")
            
        # Complexity checks
        if complexity.cyclomatic > 10:
            violations.append(f"Cyclomatic complexity too high ({complexity.cyclomatic} > 10)")
            
        if complexity.cognitive > 15:
            violations.append(f"Cognitive complexity too high ({complexity.cognitive} > 15)")
            
        # Method complexity checks
        for method in complexity.method_complexities:
            if method['cyclomatic'] > 10:
                violations.append(f"Method '{method['name']}' has high cyclomatic complexity ({method['cyclomatic']})")
            if method['cognitive'] > 15:
                violations.append(f"Method '{method['name']}' has high cognitive complexity ({method['cognitive']})")
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    violations.append(f"Missing docstring for {type(node).__name__} '{node.name}'")
        
        # Check for too many parameters
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 5:
                    violations.append(f"Method '{node.name}' has too many parameters ({param_count} > 5)")
        
        return violations
    
    def analyze_directory(self, directory: str, pattern: str = "*.py") -> Dict[str, QualityMetrics]:
        """Analyze all Python files in a directory."""
        results = {}
        
        for file_path in Path(directory).rglob(pattern):
            if '__pycache__' in str(file_path):
                continue
                
            try:
                metrics = self.analyze_file(str(file_path))
                results[str(file_path)] = metrics
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                
        return results
    
    def generate_report(self, results: Dict[str, QualityMetrics]) -> Dict[str, Any]:
        """Generate a comprehensive quality report."""
        total_files = len(results)
        total_loc = sum(m.lines_of_code for m in results.values())
        avg_complexity = sum(m.cyclomatic_complexity for m in results.values()) / total_files if total_files > 0 else 0
        avg_quality = sum(m.quality_score for m in results.values()) / total_files if total_files > 0 else 0
        
        # Find problem files
        problem_files = [
            (path, metrics) for path, metrics in results.items() 
            if metrics.quality_score < 70 or len(metrics.violations) > 3
        ]
        
        # Sort by quality score
        problem_files.sort(key=lambda x: x[1].quality_score)
        
        return {
            'summary': {
                'total_files': total_files,
                'total_lines': total_loc,
                'average_complexity': round(avg_complexity, 2),
                'average_quality_score': round(avg_quality, 2),
                'problem_files_count': len(problem_files)
            },
            'problem_files': [
                {
                    'path': path,
                    'quality_score': metrics.quality_score,
                    'violations': metrics.violations,
                    'metrics': asdict(metrics)
                }
                for path, metrics in problem_files[:10]  # Top 10 problem files
            ],
            'all_results': {
                path: asdict(metrics) for path, metrics in results.items()
            }
        }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python code_quality_analyzer.py <file_or_directory>")
        sys.exit(1)
        
    target = sys.argv[1]
    analyzer = CodeQualityAnalyzer()
    
    if os.path.isfile(target):
        # Analyze single file
        metrics = analyzer.analyze_file(target)
        print(f"\nQuality Analysis for {target}")
        print("=" * 50)
        print(f"Lines of Code: {metrics.lines_of_code}")
        print(f"Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
        print(f"Cognitive Complexity: {metrics.cognitive_complexity}")
        print(f"Maintainability Index: {metrics.maintainability_index:.2f}")
        print(f"Quality Score: {metrics.quality_score:.2f}/100")
        
        if metrics.violations:
            print("\nViolations:")
            for violation in metrics.violations:
                print(f"  - {violation}")
    else:
        # Analyze directory
        results = analyzer.analyze_directory(target)
        report = analyzer.generate_report(results)
        
        # Save report
        report_file = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\nQuality Analysis Report")
        print("=" * 50)
        print(f"Total Files: {report['summary']['total_files']}")
        print(f"Total Lines: {report['summary']['total_lines']}")
        print(f"Average Complexity: {report['summary']['average_complexity']}")
        print(f"Average Quality Score: {report['summary']['average_quality_score']}/100")
        print(f"Problem Files: {report['summary']['problem_files_count']}")
        
        if report['problem_files']:
            print("\nTop Problem Files:")
            for pf in report['problem_files'][:5]:
                print(f"\n  {pf['path']} (Score: {pf['quality_score']:.2f})")
                for violation in pf['violations'][:3]:
                    print(f"    - {violation}")
        
        print(f"\nFull report saved to: {report_file}")


if __name__ == '__main__':
    main()