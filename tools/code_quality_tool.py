#!/usr/bin/env python3
"""
Comprehensive Code Quality Measurement Tool
==========================================

A comprehensive tool for measuring and improving code quality in the TauTranslator project.
Measures cyclomatic complexity, maintainability, test coverage, and provides refactoring recommendations.

Author: DarklightX (Dana Edwards)
"""

import ast
import sys
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import re


@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for a file or project"""
    cyclomatic_complexity: float
    cognitive_complexity: float
    maintainability_index: float
    lines_of_code: int
    logical_lines: int
    comment_ratio: float
    test_coverage: float
    duplication_percentage: float
    technical_debt_ratio: float
    code_smells: List[str]
    
    def overall_score(self) -> float:
        """Calculate overall quality score (0-100)"""
        # Weighted scoring system
        complexity_score = max(0, 100 - (self.cyclomatic_complexity * 5))
        maintainability_score = self.maintainability_index
        coverage_score = self.test_coverage
        smell_penalty = min(50, len(self.code_smells) * 5)
        
        return max(0, (complexity_score * 0.3 + maintainability_score * 0.3 + 
                      coverage_score * 0.3 - smell_penalty * 0.1))


@dataclass 
class FunctionMetrics:
    """Metrics for a single function"""
    name: str
    file_path: str
    start_line: int
    end_line: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    parameters: int
    nesting_depth: int
    issues: List[str]


class CodeQualityAnalyzer(ast.NodeVisitor):
    """Advanced code quality analyzer using AST analysis"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: List[FunctionMetrics] = []
        self.current_function = None
        self.complexity = 0
        self.cognitive_complexity = 0
        self.nesting_depth = 0
        self.max_nesting = 0
        self.lines_of_code = 0
        
    def analyze_file(self) -> Tuple[List[FunctionMetrics], QualityMetrics]:
        """Analyze a Python file for quality metrics"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=self.file_path)
            self.visit(tree)
            
            # Calculate file-level metrics
            file_metrics = self._calculate_file_metrics(source)
            
            return self.functions, file_metrics
            
        except Exception as e:
            print(f"Error analyzing {self.file_path}: {e}")
            return [], QualityMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, [f"Analysis error: {e}"])
    
    def visit_FunctionDef(self, node):
        """Analyze function definition"""
        old_function = self.current_function
        old_complexity = self.complexity
        old_cognitive = self.cognitive_complexity
        old_nesting = self.nesting_depth
        old_max_nesting = self.max_nesting
        
        self.current_function = node.name
        self.complexity = 1  # Base complexity
        self.cognitive_complexity = 0
        self.nesting_depth = 0
        self.max_nesting = 0
        
        # Visit function body
        self.generic_visit(node)
        
        # Calculate metrics
        lines_of_code = (getattr(node, 'end_lineno', node.lineno) - node.lineno + 1)
        parameters = len(node.args.args)
        
        # Identify issues
        issues = self._identify_function_issues(node, parameters, lines_of_code)
        
        # Create function metrics
        func_metrics = FunctionMetrics(
            name=node.name,
            file_path=self.file_path,
            start_line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            cyclomatic_complexity=self.complexity,
            cognitive_complexity=self.cognitive_complexity,
            lines_of_code=lines_of_code,
            parameters=parameters,
            nesting_depth=self.max_nesting,
            issues=issues
        )
        
        self.functions.append(func_metrics)
        
        # Restore previous state
        self.current_function = old_function
        self.complexity = old_complexity
        self.cognitive_complexity = old_cognitive
        self.nesting_depth = old_nesting
        self.max_nesting = old_max_nesting
    
    def visit_AsyncFunctionDef(self, node):
        """Handle async functions same as regular functions"""
        self.visit_FunctionDef(node)
    
    def visit_If(self, node):
        """Visit if statement - increases complexity"""
        self.complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()
    
    def visit_While(self, node):
        """Visit while loop - increases complexity"""
        self.complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()
    
    def visit_For(self, node):
        """Visit for loop - increases complexity"""
        self.complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()
    
    def visit_ExceptHandler(self, node):
        """Visit exception handler - increases complexity"""
        self.complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()
    
    def visit_With(self, node):
        """Visit with statement - increases complexity"""
        self.complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()
    
    def visit_BoolOp(self, node):
        """Visit boolean operation - increases complexity"""
        # Each additional condition adds complexity
        additional_complexity = len(node.values) - 1
        self.complexity += additional_complexity
        self.cognitive_complexity += additional_complexity
        self.generic_visit(node)
    
    def _enter_nesting(self):
        """Enter nested block"""
        self.nesting_depth += 1
        self.max_nesting = max(self.max_nesting, self.nesting_depth)
    
    def _exit_nesting(self):
        """Exit nested block"""
        self.nesting_depth = max(0, self.nesting_depth - 1)
    
    def _identify_function_issues(self, node, parameters: int, lines_of_code: int) -> List[str]:
        """Identify issues with function quality"""
        issues = []
        
        if self.complexity > 15:
            issues.append(f"Very high cyclomatic complexity: {self.complexity}")
        elif self.complexity > 10:
            issues.append(f"High cyclomatic complexity: {self.complexity}")
        
        if self.cognitive_complexity > 15:
            issues.append(f"High cognitive complexity: {self.cognitive_complexity}")
        
        if lines_of_code > 100:
            issues.append(f"Very long function: {lines_of_code} lines")
        elif lines_of_code > 50:
            issues.append(f"Long function: {lines_of_code} lines")
        
        if parameters > 7:
            issues.append(f"Too many parameters: {parameters}")
        elif parameters > 5:
            issues.append(f"Many parameters: {parameters}")
        
        if self.max_nesting > 5:
            issues.append(f"Deep nesting: {self.max_nesting} levels")
        elif self.max_nesting > 3:
            issues.append(f"High nesting: {self.max_nesting} levels")
        
        return issues
    
    def _calculate_file_metrics(self, source: str) -> QualityMetrics:
        """Calculate file-level quality metrics"""
        lines = source.split('\n')
        total_lines = len(lines)
        
        # Count logical lines (non-empty, non-comment)
        logical_lines = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                if stripped.startswith('#'):
                    comment_lines += 1
                else:
                    logical_lines += 1
        
        # Calculate metrics
        comment_ratio = (comment_lines / max(1, total_lines)) * 100
        
        # Aggregate function complexities
        if self.functions:
            avg_complexity = sum(f.cyclomatic_complexity for f in self.functions) / len(self.functions)
            avg_cognitive = sum(f.cognitive_complexity for f in self.functions) / len(self.functions)
        else:
            avg_complexity = 0
            avg_cognitive = 0
        
        # Maintainability index (simplified)
        maintainability = max(0, 171 - 5.2 * (avg_complexity ** 0.23) - 
                             0.23 * avg_cognitive - 16.2 * (total_lines ** 0.5))
        
        # Identify code smells
        code_smells = self._identify_code_smells(source)
        
        return QualityMetrics(
            cyclomatic_complexity=avg_complexity,
            cognitive_complexity=avg_cognitive,
            maintainability_index=maintainability,
            lines_of_code=total_lines,
            logical_lines=logical_lines,
            comment_ratio=comment_ratio,
            test_coverage=0.0,  # Would need coverage tool integration
            duplication_percentage=0.0,  # Would need duplication analysis
            technical_debt_ratio=len(code_smells) * 0.1,
            code_smells=code_smells
        )
    
    def _identify_code_smells(self, source: str) -> List[str]:
        """Identify code smells in source code"""
        smells = []
        lines = source.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Long line smell
            if len(line) > 120:
                smells.append(f"Line {i}: Long line ({len(line)} chars)")
            
            # TODO/FIXME smell
            if any(marker in line.upper() for marker in ['TODO', 'FIXME', 'HACK', 'XXX']):
                smells.append(f"Line {i}: Technical debt marker")
            
            # Magic number smell
            magic_numbers = re.findall(r'\b\d{3,}\b', line)
            for number in magic_numbers:
                if number not in ['1000', '1024', '100']:
                    smells.append(f"Line {i}: Magic number {number}")
            
            # Complex boolean expression
            if line.count(' and ') + line.count(' or ') > 2:
                smells.append(f"Line {i}: Complex boolean expression")
            
            # Deep nesting (approximate)
            indent_level = (len(line) - len(line.lstrip())) // 4
            if indent_level > 4:
                smells.append(f"Line {i}: Deep nesting (level {indent_level})")
        
        return smells


class RepositoryOrganizer:
    """Tool for organizing repository structure"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.issues = []
        
    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze repository structure and identify issues"""
        structure_analysis = {
            'directory_structure': self._analyze_directories(),
            'file_organization': self._analyze_file_organization(),
            'naming_conventions': self._analyze_naming_conventions(),
            'documentation_structure': self._analyze_documentation(),
            'test_organization': self._analyze_test_structure(),
            'issues': self.issues,
            'recommendations': self._generate_recommendations()
        }
        
        return structure_analysis
    
    def _analyze_directories(self) -> Dict[str, Any]:
        """Analyze directory structure"""
        directories = []
        
        for item in self.root_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                size = sum(1 for _ in item.rglob('*') if _.is_file())
                directories.append({
                    'name': item.name,
                    'path': str(item.relative_to(self.root_path)),
                    'file_count': size,
                    'subdirs': len([d for d in item.iterdir() if d.is_dir()])
                })
        
        # Check for standard structure
        expected_dirs = {'src', 'tests', 'docs', 'scripts'}
        present_dirs = {d['name'] for d in directories}
        missing_dirs = expected_dirs - present_dirs
        
        if missing_dirs:
            self.issues.append(f"Missing standard directories: {missing_dirs}")
        
        return {
            'directories': directories,
            'total_directories': len(directories),
            'missing_standard_dirs': list(missing_dirs)
        }
    
    def _analyze_file_organization(self) -> Dict[str, Any]:
        """Analyze file organization"""
        files_by_type = defaultdict(list)
        root_files = []
        
        # Analyze root-level files
        for item in self.root_path.iterdir():
            if item.is_file():
                root_files.append({
                    'name': item.name,
                    'size': item.stat().st_size,
                    'extension': item.suffix
                })
                files_by_type[item.suffix].append(item.name)
        
        # Check for too many root files
        if len(root_files) > 20:
            self.issues.append(f"Too many root-level files: {len(root_files)}")
        
        # Check for misplaced files
        code_files_in_root = [f for f in root_files if f['extension'] in ['.py', '.js', '.ts']]
        if len(code_files_in_root) > 5:
            self.issues.append("Too many code files in root directory")
        
        return {
            'root_files': root_files,
            'root_file_count': len(root_files),
            'files_by_type': dict(files_by_type),
            'code_files_in_root': len(code_files_in_root)
        }
    
    def _analyze_naming_conventions(self) -> Dict[str, Any]:
        """Analyze naming conventions"""
        naming_issues = []
        
        # Check Python files for naming conventions
        for py_file in self.root_path.rglob('*.py'):
            if not py_file.name.islower() or '-' in py_file.name:
                naming_issues.append(f"Non-standard Python file name: {py_file.relative_to(self.root_path)}")
        
        # Check for inconsistent naming patterns
        all_files = list(self.root_path.rglob('*'))
        snake_case_count = sum(1 for f in all_files if '_' in f.name)
        kebab_case_count = sum(1 for f in all_files if '-' in f.name)
        
        if snake_case_count > 0 and kebab_case_count > 0:
            naming_issues.append("Mixed naming conventions (snake_case and kebab-case)")
        
        return {
            'naming_issues': naming_issues,
            'snake_case_files': snake_case_count,
            'kebab_case_files': kebab_case_count
        }
    
    def _analyze_documentation(self) -> Dict[str, Any]:
        """Analyze documentation structure"""
        readme_files = list(self.root_path.glob('README*'))
        doc_files = list(self.root_path.rglob('*.md'))
        
        if not readme_files:
            self.issues.append("Missing README file")
        
        return {
            'readme_files': [str(f.relative_to(self.root_path)) for f in readme_files],
            'documentation_files': len(doc_files),
            'has_docs_directory': (self.root_path / 'docs').exists()
        }
    
    def _analyze_test_structure(self) -> Dict[str, Any]:
        """Analyze test structure"""
        test_files = list(self.root_path.rglob('test_*.py'))
        test_dirs = [d for d in self.root_path.rglob('*') if d.is_dir() and 'test' in d.name.lower()]
        
        return {
            'test_files': len(test_files),
            'test_directories': len(test_dirs),
            'has_tests_directory': (self.root_path / 'tests').exists()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for repository improvement"""
        recommendations = []
        
        # Directory structure recommendations
        if not (self.root_path / 'src').exists():
            recommendations.append("Create 'src' directory for source code")
        
        if not (self.root_path / 'tests').exists():
            recommendations.append("Create 'tests' directory for test files")
        
        if not (self.root_path / 'docs').exists():
            recommendations.append("Create 'docs' directory for documentation")
        
        # File organization recommendations
        root_py_files = list(self.root_path.glob('*.py'))
        if len(root_py_files) > 5:
            recommendations.append("Move Python files to 'src' directory")
        
        # Documentation recommendations
        if not list(self.root_path.glob('README*')):
            recommendations.append("Add README.md file")
        
        return recommendations


def analyze_project_quality(project_root: Path) -> Dict[str, Any]:
    """Comprehensive project quality analysis"""
    print("🔍 Analyzing project quality...")
    
    # Find all Python files, excluding venv and node_modules
    python_files = []
    for py_file in project_root.rglob('*.py'):
        path_str = str(py_file)
        if not any(exclude in path_str for exclude in ['venv', 'node_modules', '__pycache__']):
            python_files.append(py_file)
    
    print(f"Found {len(python_files)} Python files")
    
    all_functions = []
    file_metrics = {}
    
    # Analyze each file
    for py_file in python_files:
        print(f"  Analyzing: {py_file.relative_to(project_root)}")
        analyzer = CodeQualityAnalyzer(str(py_file))
        functions, metrics = analyzer.analyze_file()
        
        all_functions.extend(functions)
        file_metrics[str(py_file.relative_to(project_root))] = asdict(metrics)
    
    # Calculate project-wide metrics
    if all_functions:
        avg_complexity = sum(f.cyclomatic_complexity for f in all_functions) / len(all_functions)
        max_complexity = max(f.cyclomatic_complexity for f in all_functions)
        
        # Find most complex functions
        complex_functions = sorted(all_functions, 
                                 key=lambda f: f.cyclomatic_complexity, 
                                 reverse=True)[:10]
    else:
        avg_complexity = 0
        max_complexity = 0
        complex_functions = []
    
    # Repository structure analysis
    print("📁 Analyzing repository structure...")
    organizer = RepositoryOrganizer(project_root)
    structure_analysis = organizer.analyze_structure()
    
    # Generate summary
    quality_summary = {
        'project_metrics': {
            'total_files': len(python_files),
            'total_functions': len(all_functions),
            'average_complexity': round(avg_complexity, 2),
            'max_complexity': max_complexity,
            'files_needing_attention': len([f for f in file_metrics.values() 
                                          if f['cyclomatic_complexity'] > 10])
        },
        'most_complex_functions': [asdict(f) for f in complex_functions],
        'file_metrics': file_metrics,
        'repository_structure': structure_analysis,
        'recommendations': generate_quality_recommendations(file_metrics, structure_analysis)
    }
    
    return quality_summary


def generate_quality_recommendations(file_metrics: Dict, structure_analysis: Dict) -> List[str]:
    """Generate actionable quality improvement recommendations"""
    recommendations = []
    
    # Code quality recommendations
    high_complexity_files = [f for f, m in file_metrics.items() 
                           if m['cyclomatic_complexity'] > 10]
    
    if high_complexity_files:
        recommendations.append(f"Refactor {len(high_complexity_files)} files with high complexity")
    
    low_maintainability_files = [f for f, m in file_metrics.items() 
                                if m['maintainability_index'] < 50]
    
    if low_maintainability_files:
        recommendations.append(f"Improve maintainability of {len(low_maintainability_files)} files")
    
    # Add structure recommendations
    recommendations.extend(structure_analysis.get('recommendations', []))
    
    return recommendations


def main():
    """Main function to run quality analysis"""
    project_root = Path(__file__).parent.parent
    
    print("🛠️  TauTranslator Code Quality Analysis")
    print("=" * 60)
    
    # Run comprehensive analysis
    quality_results = analyze_project_quality(project_root)
    
    # Save results
    results_file = project_root / "quality_analysis_results.json"
    with open(results_file, 'w') as f:
        json.dump(quality_results, f, indent=2)
    
    # Print summary
    print("\n📊 Quality Summary:")
    print("-" * 40)
    metrics = quality_results['project_metrics']
    print(f"Total Files: {metrics['total_files']}")
    print(f"Total Functions: {metrics['total_functions']}")
    print(f"Average Complexity: {metrics['average_complexity']}")
    print(f"Max Complexity: {metrics['max_complexity']}")
    print(f"Files Needing Attention: {metrics['files_needing_attention']}")
    
    print(f"\n🔥 Top Complex Functions:")
    print("-" * 40)
    for func in quality_results['most_complex_functions'][:5]:
        print(f"{func['name']} (complexity: {func['cyclomatic_complexity']}) - {Path(func['file_path']).name}")
    
    print(f"\n📁 Repository Issues:")
    print("-" * 40)
    for issue in quality_results['repository_structure']['issues']:
        print(f"• {issue}")
    
    print(f"\n💡 Recommendations:")
    print("-" * 40)
    for rec in quality_results['recommendations'][:10]:
        print(f"• {rec}")
    
    print(f"\n💾 Detailed results saved to: {results_file}")


if __name__ == "__main__":
    main()