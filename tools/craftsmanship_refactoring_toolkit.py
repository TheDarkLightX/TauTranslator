#!/usr/bin/env python3
"""
Craftsmanship Refactoring Toolkit
Automated tools for applying the Intentional Disclosure Principle to the codebase.
Copyright: DarkLightX/Dana Edwards
"""

import ast
import re
import os
import json
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import asyncio
from collections import defaultdict


@dataclass
class RefactoringIssue:
    """Represents a code issue that violates craftsmanship principles."""
    file_path: str
    line_number: int
    issue_type: str
    rule_violated: int
    current_code: str
    suggested_fix: str
    severity: str  # 'high', 'medium', 'low'
    
    
@dataclass
class MethodComplexity:
    """Tracks method complexity metrics."""
    name: str
    line_count: int
    cyclomatic_complexity: int
    has_orchestrator_pattern: bool
    

class CraftsmanshipAnalyzer(ast.NodeVisitor):
    """AST visitor that analyzes code for craftsmanship principle violations."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues: List[RefactoringIssue] = []
        self.current_class = None
        self.methods: List[MethodComplexity] = []
        self.imports: Set[str] = set()
        self.type_annotations: Dict[str, str] = {}
        
    def visit_Import(self, node):
        """Track imports to understand dependencies."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Track from imports."""
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        """Track class context."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_AsyncFunctionDef(self, node):
        """Check async function naming (Rule 1)."""
        self._check_function_naming(node, is_async=True)
        self._check_orchestrator_pattern(node)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        """Check function naming and structure."""
        self._check_function_naming(node, is_async=False)
        self._check_orchestrator_pattern(node)
        self._check_type_annotations(node)
        self.generic_visit(node)
        
    def _check_function_naming(self, node, is_async: bool):
        """Rule 1: Check function naming conventions."""
        name = node.name
        
        # Skip private methods and special methods
        if name.startswith('_'):
            return
            
        # Check for async suffix
        if is_async and not name.endswith('_async'):
            self.issues.append(RefactoringIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="async_naming",
                rule_violated=1,
                current_code=f"async def {name}",
                suggested_fix=f"async def {name}_async",
                severity="high"
            ))
            
        # Check for I/O operations in name
        io_keywords = ['read', 'write', 'fetch', 'save', 'load', 'get', 'post', 'delete', 'update']
        has_io = any(keyword in name.lower() for keyword in io_keywords)
        
        # Analyze function body for I/O operations
        body_has_io = self._function_has_io(node)
        
        if body_has_io and not has_io:
            suggested_name = self._suggest_descriptive_name(name, node)
            self.issues.append(RefactoringIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="undisclosed_io",
                rule_violated=1,
                current_code=f"def {name}",
                suggested_fix=f"def {suggested_name}",
                severity="high"
            ))
            
    def _function_has_io(self, node) -> bool:
        """Check if function contains I/O operations."""
        io_patterns = [
            'open(', 'read(', 'write(', 'requests.', 'aiohttp.',
            'asyncio.', 'subprocess.', 'os.', 'pathlib.',
            'json.load', 'json.dump', 'pickle.', 'sqlite3.',
            'psycopg2.', 'redis.', 'mongodb.'
        ]
        
        # Convert AST to source code
        try:
            source = ast.unparse(node)
            return any(pattern in source for pattern in io_patterns)
        except:
            return False
            
    def _suggest_descriptive_name(self, current_name: str, node) -> str:
        """Suggest a better name following naming conventions."""
        # Analyze what the function does
        verbs = ['read', 'write', 'fetch', 'save', 'load', 'create', 'update', 'delete']
        
        # Simple heuristic: if function returns something, likely a 'fetch' or 'read'
        has_return = any(isinstance(stmt, ast.Return) and stmt.value for stmt in ast.walk(node))
        
        if has_return:
            return f"fetch_{current_name}_from_storage"
        else:
            return f"save_{current_name}_to_storage"
            
    def _check_orchestrator_pattern(self, node):
        """Rule 2: Check if method follows orchestrator pattern."""
        # Count lines (excluding docstring)
        line_count = node.end_lineno - node.lineno
        
        # Count direct statements (not counting nested)
        direct_statements = len([stmt for stmt in node.body if not isinstance(stmt, ast.Expr)])
        
        # Check if it's a public method
        is_public = not node.name.startswith('_')
        
        if is_public and direct_statements > 15:
            self.issues.append(RefactoringIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="orchestrator_too_complex",
                rule_violated=2,
                current_code=f"def {node.name} with {direct_statements} statements",
                suggested_fix=f"Break down into smaller private methods",
                severity="medium"
            ))
            
        # Check for mixed abstraction levels
        has_low_level = self._has_low_level_operations(node)
        has_high_level = self._has_high_level_calls(node)
        
        if is_public and has_low_level and has_high_level:
            self.issues.append(RefactoringIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="mixed_abstraction_levels",
                rule_violated=2,
                current_code=f"def {node.name} mixes high and low level operations",
                suggested_fix=f"Extract low-level operations to private methods",
                severity="medium"
            ))
            
    def _has_low_level_operations(self, node) -> bool:
        """Check for low-level operations like loops, conditionals."""
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While, ast.ListComp, ast.DictComp)):
                return True
        return False
        
    def _has_high_level_calls(self, node) -> bool:
        """Check for method calls suggesting high-level orchestration."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    return True
        return False
        
    def _check_type_annotations(self, node):
        """Rule 3: Check type system usage."""
        # Check parameters
        for arg in node.args.args:
            if not arg.annotation:
                self.issues.append(RefactoringIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    issue_type="missing_type_annotation",
                    rule_violated=3,
                    current_code=f"Parameter '{arg.arg}' without type",
                    suggested_fix=f"Add type annotation to '{arg.arg}'",
                    severity="medium"
                ))
                
        # Check return type
        if not node.returns and node.name != '__init__':
            self.issues.append(RefactoringIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="missing_return_type",
                rule_violated=3,
                current_code=f"def {node.name} without return type",
                suggested_fix=f"Add return type annotation",
                severity="medium"
            ))
            

class LayerViolationChecker:
    """Checks for Rule 4 violations - impurity isolation."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.layer_mappings = self._identify_layers()
        
    def _identify_layers(self) -> Dict[str, str]:
        """Identify architectural layers in the project."""
        layers = {}
        
        # Common layer patterns
        core_patterns = ['core', 'domain', 'business', 'model']
        infra_patterns = ['infrastructure', 'adapters', 'repository', 'api', 'db']
        app_patterns = ['application', 'services', 'handlers', 'controllers']
        
        for root, dirs, files in os.walk(self.project_root):
            for dir_name in dirs:
                lower_name = dir_name.lower()
                if any(pattern in lower_name for pattern in core_patterns):
                    layers[os.path.join(root, dir_name)] = 'core'
                elif any(pattern in lower_name for pattern in infra_patterns):
                    layers[os.path.join(root, dir_name)] = 'infrastructure'
                elif any(pattern in lower_name for pattern in app_patterns):
                    layers[os.path.join(root, dir_name)] = 'application'
                    
        return layers
        
    def check_layer_violations(self, file_path: str, imports: Set[str]) -> List[RefactoringIssue]:
        """Check if file violates layer boundaries."""
        issues = []
        
        # Determine which layer this file belongs to
        file_layer = None
        for layer_path, layer_type in self.layer_mappings.items():
            if file_path.startswith(layer_path):
                file_layer = layer_type
                break
                
        if not file_layer:
            return issues
            
        # Check imports
        if file_layer == 'core':
            # Core should not import from infrastructure or application
            infra_imports = [imp for imp in imports if any(
                pattern in imp for pattern in ['api', 'db', 'repository', 'http', 'sql']
            )]
            
            for imp in infra_imports:
                issues.append(RefactoringIssue(
                    file_path=file_path,
                    line_number=1,
                    issue_type="layer_violation",
                    rule_violated=4,
                    current_code=f"Core layer imports '{imp}'",
                    suggested_fix=f"Move I/O operations to infrastructure layer",
                    severity="high"
                ))
                
        return issues


class RefactoringToolkit:
    """Main toolkit for analyzing and refactoring code."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.layer_checker = LayerViolationChecker(self.project_root)
        
    def analyze_file(self, file_path: str) -> List[RefactoringIssue]:
        """Analyze a single Python file for craftsmanship violations."""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                source = f.read()
                
            tree = ast.parse(source)
            analyzer = CraftsmanshipAnalyzer(file_path)
            analyzer.visit(tree)
            
            issues.extend(analyzer.issues)
            
            # Check layer violations
            layer_issues = self.layer_checker.check_layer_violations(
                file_path, analyzer.imports
            )
            issues.extend(layer_issues)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return issues
        
    def analyze_project(self) -> Dict[str, List[RefactoringIssue]]:
        """Analyze entire project for craftsmanship violations."""
        all_issues = {}
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', '.git', 'venv', 'node_modules', '.next'
            ]]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    issues = self.analyze_file(file_path)
                    if issues:
                        all_issues[file_path] = issues
                        
        return all_issues
        
    def generate_report(self, issues: Dict[str, List[RefactoringIssue]]) -> str:
        """Generate a refactoring report."""
        report = []
        report.append("# Craftsmanship Refactoring Report\n")
        report.append(f"Total files with issues: {len(issues)}\n")
        
        # Count by rule
        rule_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for file_issues in issues.values():
            for issue in file_issues:
                rule_counts[issue.rule_violated] += 1
                severity_counts[issue.severity] += 1
                
        report.append("\n## Summary by Rule")
        for rule, count in sorted(rule_counts.items()):
            rule_names = {
                1: "Name for Consequence and Asynchronicity",
                2: "Structure for Scannability",
                3: "Maximize Disclosure via Type System",
                4: "Isolate Impurity"
            }
            report.append(f"- Rule {rule} ({rule_names.get(rule, 'Unknown')}): {count} violations")
            
        report.append("\n## Summary by Severity")
        for severity, count in severity_counts.items():
            report.append(f"- {severity.capitalize()}: {count} issues")
            
        report.append("\n## Detailed Issues by File\n")
        
        for file_path, file_issues in sorted(issues.items()):
            report.append(f"\n### {file_path}")
            report.append(f"Issues found: {len(file_issues)}\n")
            
            for issue in sorted(file_issues, key=lambda x: (x.severity, x.line_number)):
                report.append(f"- **Line {issue.line_number}** [{issue.severity}] Rule {issue.rule_violated}")
                report.append(f"  - Type: {issue.issue_type}")
                report.append(f"  - Current: `{issue.current_code}`")
                report.append(f"  - Suggested: `{issue.suggested_fix}`")
                
        return '\n'.join(report)
        
    def create_golden_master_test(self, file_path: str, output_path: str):
        """Create a golden master test for a file before refactoring."""
        # This would capture current behavior for safety
        test_content = f'''"""
Golden Master Test for {file_path}
Generated to ensure behavior preservation during refactoring.
"""

import pytest
import json
from pathlib import Path

# Import the module to test
# This needs to be adjusted based on the actual module

class TestGoldenMaster:
    """Captures current behavior as golden master."""
    
    def test_golden_master_snapshot(self):
        """Compare current behavior against snapshot."""
        # This is a template - actual implementation would
        # capture real behavior based on the module type
        pass
'''
        
        with open(output_path, 'w') as f:
            f.write(test_content)
            

def main():
    """Main entry point for the refactoring toolkit."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Craftsmanship Refactoring Toolkit')
    parser.add_argument('--analyze', action='store_true', help='Analyze project')
    parser.add_argument('--file', type=str, help='Analyze specific file')
    parser.add_argument('--report', type=str, help='Output report file')
    parser.add_argument('--fix', action='store_true', help='Apply automated fixes (careful!)')
    
    args = parser.parse_args()
    
    toolkit = RefactoringToolkit('.')
    
    if args.file:
        issues = {args.file: toolkit.analyze_file(args.file)}
    else:
        issues = toolkit.analyze_project()
        
    if issues:
        report = toolkit.generate_report(issues)
        
        if args.report:
            with open(args.report, 'w') as f:
                f.write(report)
        else:
            print(report)
            
        print(f"\nTotal issues found: {sum(len(v) for v in issues.values())}")
    else:
        print("No craftsmanship violations found!")
        

if __name__ == '__main__':
    main()