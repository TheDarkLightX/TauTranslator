#!/usr/bin/env python3
"""
Automated Code Review Checklist Tool
====================================

Automated code review tool that implements industry-standard code review checklists
and integrates with the enhanced quality analysis.

Author: DarklightX (Dana Edwards)
"""

import ast
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re


class ReviewCriteria(Enum):
    """Code review criteria based on industry standards"""
    CORRECTNESS = "correctness"
    SECURITY = "security"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    TESTABILITY = "testability"
    MAINTAINABILITY = "maintainability"
    REUSABILITY = "reusability"
    ERROR_HANDLING = "error_handling"
    LOGGING = "logging"
    DOCUMENTATION = "documentation"


@dataclass
class ReviewCheck:
    """Individual review check result"""
    criteria: ReviewCriteria
    passed: bool
    message: str
    file_path: str
    line: int = 0
    suggestion: str = ""
    priority: str = "medium"  # low, medium, high, critical


class CodeReviewChecker(ast.NodeVisitor):
    """Automated code review checker"""
    
    def __init__(self, file_path: str, source_code: str = None):
        self.file_path = file_path
        self.source_code = source_code or self._read_file()
        self.checks: List[ReviewCheck] = []
        
        # Tracking state
        self.functions_with_docstrings = set()
        self.functions_with_error_handling = set()
        self.functions_with_logging = set()
        self.current_function = None
        self.has_performance_issues = False
        
    def _read_file(self) -> str:
        """Read source file safely"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file {self.file_path}: {e}")
    
    def review_code(self) -> List[ReviewCheck]:
        """Perform comprehensive code review"""
        try:
            tree = ast.parse(self.source_code, filename=self.file_path)
            self.visit(tree)
            
            # Additional checks
            self._check_file_structure()
            self._check_naming_conventions()
            self._check_imports()
            self._check_performance_patterns()
            
            return self.checks
            
        except SyntaxError as e:
            self.checks.append(ReviewCheck(
                criteria=ReviewCriteria.CORRECTNESS,
                passed=False,
                message=f"Syntax error: {e.msg}",
                file_path=self.file_path,
                line=e.lineno or 1,
                suggestion="Fix syntax error before proceeding",
                priority="critical"
            ))
            return self.checks
    
    def visit_FunctionDef(self, node):
        """Review function definition"""
        old_function = self.current_function
        self.current_function = node.name
        
        # Check documentation
        self._check_function_documentation(node)
        
        # Check function length and complexity
        self._check_function_length(node)
        
        # Check parameter count
        self._check_parameter_count(node)
        
        # Visit function body
        self.generic_visit(node)
        
        # Check if function has error handling
        self._check_error_handling_completeness(node)
        
        # Check if function has appropriate logging
        self._check_logging_completeness(node)
        
        self.current_function = old_function
    
    def visit_Try(self, node):
        """Check try-except blocks"""
        if self.current_function:
            self.functions_with_error_handling.add(self.current_function)
        
        # Check for bare except clauses
        for handler in node.handlers:
            if handler.type is None:
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.ERROR_HANDLING,
                    passed=False,
                    message="Bare except clause should specify exception type",
                    file_path=self.file_path,
                    line=handler.lineno,
                    suggestion="Use specific exception types like 'except ValueError:' instead of 'except:'",
                    priority="medium"
                ))
        
        # Check for empty except blocks
        for handler in node.handlers:
            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.ERROR_HANDLING,
                    passed=False,
                    message="Empty except block - should handle or log the exception",
                    file_path=self.file_path,
                    line=handler.lineno,
                    suggestion="Add proper error handling or at least log the exception",
                    priority="high"
                ))
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Check function calls for various issues"""
        if isinstance(node.func, ast.Attribute):
            # Check for logging calls
            if (isinstance(node.func.value, ast.Name) and 
                node.func.value.id in ['logger', 'log', 'logging'] and
                node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']):
                if self.current_function:
                    self.functions_with_logging.add(self.current_function)
        
        elif isinstance(node.func, ast.Name):
            # Check for potentially dangerous functions
            dangerous_functions = ['eval', 'exec', 'compile', '__import__']
            if node.func.id in dangerous_functions:
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.SECURITY,
                    passed=False,
                    message=f"Potentially dangerous function: {node.func.id}()",
                    file_path=self.file_path,
                    line=node.lineno,
                    suggestion=f"Avoid using {node.func.id}() or ensure input is properly validated",
                    priority="critical"
                ))
            
            # Check for performance issues
            if node.func.id == 'len' and self._is_in_loop_condition(node):
                self.has_performance_issues = True
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.PERFORMANCE,
                    passed=False,
                    message="len() called in loop condition - consider caching",
                    file_path=self.file_path,
                    line=node.lineno,
                    suggestion="Cache len() result before loop: 'length = len(items)'",
                    priority="medium"
                ))
        
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Check for loop patterns"""
        # Check for nested loops (potential O(n²) complexity)
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)) and child != node:
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.PERFORMANCE,
                    passed=False,
                    message="Nested loop detected - check if O(n²) complexity can be reduced",
                    file_path=self.file_path,
                    line=node.lineno,
                    suggestion="Consider using hash tables, sets, or other data structures to reduce complexity",
                    priority="medium"
                ))
                break
        
        self.generic_visit(node)
    
    def visit_Compare(self, node):
        """Check comparison operations"""
        # Check for identity comparisons with literals
        for i, op in enumerate(node.ops):
            if isinstance(op, (ast.Is, ast.IsNot)):
                comparator = node.comparators[i]
                if isinstance(comparator, (ast.Num, ast.Str, ast.NameConstant)):
                    self.checks.append(ReviewCheck(
                        criteria=ReviewCriteria.CORRECTNESS,
                        passed=False,
                        message="Use '==' or '!=' instead of 'is' or 'is not' for value comparison",
                        file_path=self.file_path,
                        line=node.lineno,
                        suggestion="Use '==' for equality comparison with literals",
                        priority="medium"
                    ))
        
        self.generic_visit(node)
    
    def _check_function_documentation(self, node):
        """Check if function has proper documentation"""
        has_docstring = (len(node.body) > 0 and 
                        isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Str))
        
        if has_docstring:
            self.functions_with_docstrings.add(node.name)
            
            # Check docstring quality
            docstring = node.body[0].value.s
            if len(docstring) < 10:
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.DOCUMENTATION,
                    passed=False,
                    message=f"Function '{node.name}' has very short docstring",
                    file_path=self.file_path,
                    line=node.lineno,
                    suggestion="Provide a more detailed description of what the function does",
                    priority="low"
                ))
        else:
            # Public functions should have docstrings
            if not node.name.startswith('_'):
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.DOCUMENTATION,
                    passed=False,
                    message=f"Public function '{node.name}' missing docstring",
                    file_path=self.file_path,
                    line=node.lineno,
                    suggestion="Add a docstring describing the function's purpose, parameters, and return value",
                    priority="medium"
                ))
    
    def _check_function_length(self, node):
        """Check function length"""
        lines = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
        
        if lines > 50:
            self.checks.append(ReviewCheck(
                criteria=ReviewCriteria.MAINTAINABILITY,
                passed=False,
                message=f"Function '{node.name}' is too long ({lines} lines)",
                file_path=self.file_path,
                line=node.lineno,
                suggestion="Consider breaking this function into smaller, more focused functions",
                priority="medium"
            ))
    
    def _check_parameter_count(self, node):
        """Check parameter count"""
        param_count = len(node.args.args)
        
        if param_count > 5:
            self.checks.append(ReviewCheck(
                criteria=ReviewCriteria.MAINTAINABILITY,
                passed=False,
                message=f"Function '{node.name}' has too many parameters ({param_count})",
                file_path=self.file_path,
                line=node.lineno,
                suggestion="Consider using a configuration object or breaking the function down",
                priority="medium"
            ))
    
    def _check_error_handling_completeness(self, node):
        """Check if function properly handles errors"""
        # Complex functions should have error handling
        complexity = self._estimate_complexity(node)
        
        if (complexity > 5 and 
            node.name not in self.functions_with_error_handling and
            not node.name.startswith('_')):  # Skip private functions
            
            self.checks.append(ReviewCheck(
                criteria=ReviewCriteria.ERROR_HANDLING,
                passed=False,
                message=f"Complex function '{node.name}' lacks error handling",
                file_path=self.file_path,
                line=node.lineno,
                suggestion="Add try-except blocks to handle potential errors",
                priority="medium"
            ))
    
    def _check_logging_completeness(self, node):
        """Check if function has appropriate logging"""
        # Public functions that might fail should have logging
        has_external_calls = self._has_external_calls(node)
        
        if (has_external_calls and 
            node.name not in self.functions_with_logging and
            not node.name.startswith('_')):
            
            self.checks.append(ReviewCheck(
                criteria=ReviewCriteria.LOGGING,
                passed=False,
                message=f"Function '{node.name}' with external calls lacks logging",
                file_path=self.file_path,
                line=node.lineno,
                suggestion="Add logging for debugging and monitoring purposes",
                priority="low"
            ))
    
    def _check_file_structure(self):
        """Check overall file structure"""
        lines = self.source_code.split('\n')
        
        # Check for module docstring
        if not (len(lines) > 0 and lines[0].strip().startswith('"""') or 
                len(lines) > 1 and lines[1].strip().startswith('"""')):
            self.checks.append(ReviewCheck(
                criteria=ReviewCriteria.DOCUMENTATION,
                passed=False,
                message="Module missing docstring",
                file_path=self.file_path,
                line=1,
                suggestion="Add a module-level docstring explaining the purpose of this file",
                priority="low"
            ))
        
        # Check file length
        if len(lines) > 500:
            self.checks.append(ReviewCheck(
                criteria=ReviewCriteria.MAINTAINABILITY,
                passed=False,
                message=f"File too long ({len(lines)} lines)",
                file_path=self.file_path,
                line=1,
                suggestion="Consider splitting this file into smaller modules",
                priority="medium"
            ))
    
    def _check_naming_conventions(self):
        """Check naming conventions"""
        tree = ast.parse(self.source_code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function naming (should be snake_case)
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    self.checks.append(ReviewCheck(
                        criteria=ReviewCriteria.READABILITY,
                        passed=False,
                        message=f"Function '{node.name}' doesn't follow snake_case convention",
                        file_path=self.file_path,
                        line=node.lineno,
                        suggestion="Use snake_case for function names (e.g., 'my_function')",
                        priority="low"
                    ))
            
            elif isinstance(node, ast.ClassDef):
                # Check class naming (should be PascalCase)
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.checks.append(ReviewCheck(
                        criteria=ReviewCriteria.READABILITY,
                        passed=False,
                        message=f"Class '{node.name}' doesn't follow PascalCase convention",
                        file_path=self.file_path,
                        line=node.lineno,
                        suggestion="Use PascalCase for class names (e.g., 'MyClass')",
                        priority="low"
                    ))
    
    def _check_imports(self):
        """Check import statements"""
        tree = ast.parse(self.source_code)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        # Check for unused imports (simplified check)
        imported_names = set()
        for node in imports:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.name)
        
        # Check if imports are used (very basic check)
        for name in imported_names:
            if name not in self.source_code.replace(f"import {name}", ""):
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.MAINTAINABILITY,
                    passed=False,
                    message=f"Potentially unused import: {name}",
                    file_path=self.file_path,
                    line=1,
                    suggestion="Remove unused imports to keep code clean",
                    priority="low"
                ))
    
    def _check_performance_patterns(self):
        """Check for common performance anti-patterns"""
        lines = self.source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for string concatenation in loops
            if '+=' in line and any(loop in line for loop in ['for ', 'while ']):
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.PERFORMANCE,
                    passed=False,
                    message="String concatenation in loop detected",
                    file_path=self.file_path,
                    line=line_num,
                    suggestion="Use list.append() and ''.join() for better performance",
                    priority="medium"
                ))
            
            # Check for inefficient membership tests
            if ' in [' in line:
                self.checks.append(ReviewCheck(
                    criteria=ReviewCriteria.PERFORMANCE,
                    passed=False,
                    message="Inefficient membership test with list",
                    file_path=self.file_path,
                    line=line_num,
                    suggestion="Use sets or tuples for membership tests: 'item in {a, b, c}'",
                    priority="low"
                ))
    
    def _estimate_complexity(self, node) -> int:
        """Estimate function complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
        return complexity
    
    def _has_external_calls(self, node) -> bool:
        """Check if function makes external calls"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    return True
        return False
    
    def _is_in_loop_condition(self, node) -> bool:
        """Check if node is in a loop condition (simplified)"""
        # This is a simplified check - would need more sophisticated AST analysis
        return False


def generate_review_report(checks: List[ReviewCheck]) -> Dict[str, Any]:
    """Generate comprehensive review report"""
    
    # Group checks by criteria
    checks_by_criteria = {}
    for criteria in ReviewCriteria:
        checks_by_criteria[criteria.value] = [c for c in checks if c.criteria == criteria]
    
    # Count by priority
    priority_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for check in checks:
        priority_counts[check.priority] += 1
    
    # Calculate pass rate
    total_checks = len(checks)
    passed_checks = len([c for c in checks if c.passed])
    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100
    
    return {
        'summary': {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'pass_rate': round(pass_rate, 1),
            'priority_counts': priority_counts
        },
        'checks_by_criteria': {
            criteria: [
                {
                    'passed': check.passed,
                    'message': check.message,
                    'line': check.line,
                    'suggestion': check.suggestion,
                    'priority': check.priority
                }
                for check in checks_list
            ]
            for criteria, checks_list in checks_by_criteria.items()
        },
        'recommendations': _generate_recommendations(checks_by_criteria, priority_counts)
    }


def _generate_recommendations(checks_by_criteria: Dict, priority_counts: Dict) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    if priority_counts['critical'] > 0:
        recommendations.append("🚨 Address all critical issues before merging")
    
    if priority_counts['high'] > 0:
        recommendations.append("⚠️ Review and fix high priority issues")
    
    # Specific recommendations by category
    if checks_by_criteria.get('security'):
        recommendations.append("🔒 Security issues found - review security practices")
    
    if checks_by_criteria.get('performance'):
        recommendations.append("⚡ Performance improvements possible")
    
    if len(checks_by_criteria.get('documentation', [])) > 5:
        recommendations.append("📝 Consider improving documentation coverage")
    
    if len(checks_by_criteria.get('maintainability', [])) > 5:
        recommendations.append("🔧 Code maintainability could be improved")
    
    return recommendations


def review_file(file_path: Path) -> Dict[str, Any]:
    """Review a single file"""
    checker = CodeReviewChecker(str(file_path))
    checks = checker.review_code()
    
    return {
        'file_path': str(file_path),
        'review_report': generate_review_report(checks),
        'all_checks': [
            {
                'criteria': check.criteria.value,
                'passed': check.passed,
                'message': check.message,
                'line': check.line,
                'suggestion': check.suggestion,
                'priority': check.priority
            }
            for check in checks
        ]
    }


def main():
    """Main function for command-line usage"""
    if len(sys.argv) != 2:
        print("Usage: python code_review_checklist.py <file_path>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    # Perform review
    result = review_file(file_path)
    report = result['review_report']
    
    # Print summary
    print(f"📋 Code Review Report for {file_path.name}")
    print("=" * 50)
    print(f"Pass Rate: {report['summary']['pass_rate']}%")
    print(f"Total Checks: {report['summary']['total_checks']}")
    print(f"Failed: {report['summary']['failed_checks']}")
    
    print(f"\n📊 Issues by Priority:")
    for priority, count in report['summary']['priority_counts'].items():
        if count > 0:
            print(f"  {priority.upper()}: {count}")
    
    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    
    # Save detailed report
    output_file = file_path.parent / f"{file_path.stem}_review.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: {output_file}")


if __name__ == "__main__":
    main()