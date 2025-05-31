#!/usr/bin/env python3
"""
Enhanced Code Quality Measurement Tool
=====================================

Advanced code quality analysis tool incorporating 2024 best practices, SQALE model,
cognitive complexity, and modern static analysis techniques.

Features:
- SQALE-inspired technical debt measurement
- Cognitive complexity calculation (per 2024 standards)
- Security vulnerability detection
- AST-based deep analysis
- Industry-standard metrics
- CI/CD integration ready

Author: DarklightX (Dana Edwards)
"""

import ast
import sys
import json
import os
import subprocess
import hashlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum
import re
import datetime


class Severity(Enum):
    """Issue severity levels based on industry standards"""
    BLOCKER = "BLOCKER"      # Must fix before release
    CRITICAL = "CRITICAL"    # High priority fix
    MAJOR = "MAJOR"         # Should fix soon
    MINOR = "MINOR"         # Nice to fix
    INFO = "INFO"           # Informational


class TechnicalDebtCategory(Enum):
    """SQALE-inspired technical debt categories"""
    TESTABILITY = "testability"
    RELIABILITY = "reliability"
    CHANGEABILITY = "changeability"
    EFFICIENCY = "efficiency"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    PORTABILITY = "portability"


@dataclass
class Issue:
    """Represents a code quality issue"""
    category: TechnicalDebtCategory
    severity: Severity
    message: str
    file_path: str
    line: int
    column: int = 0
    rule_id: str = ""
    effort_minutes: int = 5  # Remediation effort estimate


@dataclass
class SecurityIssue:
    """Security-specific issue"""
    cwe_id: str  # Common Weakness Enumeration ID
    confidence: str  # HIGH, MEDIUM, LOW
    severity: Severity
    message: str
    file_path: str
    line: int
    test_id: str = ""


@dataclass
class ComplexityMetrics:
    """Comprehensive complexity metrics"""
    cyclomatic_complexity: int
    cognitive_complexity: int
    essential_complexity: int
    halstead_volume: float
    maintainability_index: float
    lines_of_code: int
    logical_lines: int


@dataclass
class QualityGate:
    """Quality gate thresholds"""
    max_cyclomatic_complexity: int = 10
    max_cognitive_complexity: int = 15
    min_test_coverage: float = 80.0
    max_code_smells: int = 0
    max_security_hotspots: int = 0
    min_maintainability_rating: str = "A"


@dataclass
class TechnicalDebtMetrics:
    """SQALE-inspired technical debt metrics"""
    total_debt_minutes: int
    debt_ratio: float  # debt / development cost
    sqale_rating: str  # A-E rating
    issues_by_category: Dict[TechnicalDebtCategory, List[Issue]]
    remediation_cost: int  # minutes


class EnhancedCodeAnalyzer(ast.NodeVisitor):
    """Enhanced AST-based code analyzer with 2024 standards"""
    
    def __init__(self, file_path: str, source_code: str = None):
        self.file_path = file_path
        self.source_code = source_code or self._read_file()
        self.issues: List[Issue] = []
        self.security_issues: List[SecurityIssue] = []
        
        # Function-level tracking
        self.current_function = None
        self.function_metrics: Dict[str, ComplexityMetrics] = {}
        
        # Complexity tracking
        self.cyclomatic_complexity = 0
        self.cognitive_complexity = 0
        self.nesting_depth = 0
        self.logical_lines = 0
        
        # Code patterns
        self.imports: Set[str] = set()
        self.defined_functions: Set[str] = set()
        self.used_functions: Set[str] = set()
        self.magic_numbers: List[Tuple[int, str]] = []
        
        # Security patterns
        self.security_patterns = self._load_security_patterns()
    
    def _read_file(self) -> str:
        """Read source file safely"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Cannot read file {self.file_path}: {e}")
    
    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security vulnerability patterns"""
        return {
            'hardcoded_secrets': [
                r'(?i)(password|pwd|pass|secret|key|token)\s*=\s*["\'][^"\']{8,}["\']',
                r'(?i)(api_key|apikey|auth_token)\s*=\s*["\'][^"\']+["\']',
            ],
            'sql_injection': [
                r'(?i)execute\s*\(\s*["\'].*%.*["\']',
                r'(?i)cursor\.execute\s*\(\s*["\'].*\+.*["\']',
            ],
            'shell_injection': [
                r'(?i)(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*shell\s*=\s*True',
                r'(?i)eval\s*\(',
                r'(?i)exec\s*\(',
            ],
            'unsafe_deserialization': [
                r'(?i)pickle\.loads?\s*\(',
                r'(?i)cPickle\.loads?\s*\(',
            ]
        }
    
    def analyze(self) -> Tuple[Dict[str, ComplexityMetrics], List[Issue], List[SecurityIssue]]:
        """Perform comprehensive analysis"""
        try:
            tree = ast.parse(self.source_code, filename=self.file_path)
            self.visit(tree)
            
            # Security analysis
            self._analyze_security()
            
            # Code smell detection
            self._detect_code_smells()
            
            return self.function_metrics, self.issues, self.security_issues
            
        except SyntaxError as e:
            issue = Issue(
                category=TechnicalDebtCategory.RELIABILITY,
                severity=Severity.BLOCKER,
                message=f"Syntax error: {e.msg}",
                file_path=self.file_path,
                line=e.lineno or 1,
                column=e.offset or 0,
                rule_id="syntax_error",
                effort_minutes=30
            )
            return {}, [issue], []
    
    def visit_FunctionDef(self, node):
        """Analyze function definition with enhanced metrics"""
        old_function = self.current_function
        old_cyclomatic = self.cyclomatic_complexity
        old_cognitive = self.cognitive_complexity
        old_nesting = self.nesting_depth
        
        self.current_function = node.name
        self.cyclomatic_complexity = 1  # Base complexity
        self.cognitive_complexity = 0
        self.nesting_depth = 0
        
        # Track function definition
        self.defined_functions.add(node.name)
        
        # Visit function body
        self.generic_visit(node)
        
        # Calculate metrics
        lines_of_code = (getattr(node, 'end_lineno', node.lineno) - node.lineno + 1)
        
        # Essential complexity (simplified)
        essential_complexity = max(1, self.cyclomatic_complexity - len(node.args.args))
        
        # Halstead volume (simplified)
        halstead_volume = self._calculate_halstead_volume(node)
        
        # Maintainability index
        maintainability_index = self._calculate_maintainability_index(
            halstead_volume, self.cyclomatic_complexity, lines_of_code
        )
        
        metrics = ComplexityMetrics(
            cyclomatic_complexity=self.cyclomatic_complexity,
            cognitive_complexity=self.cognitive_complexity,
            essential_complexity=essential_complexity,
            halstead_volume=halstead_volume,
            maintainability_index=maintainability_index,
            lines_of_code=lines_of_code,
            logical_lines=self._count_logical_lines(node)
        )
        
        self.function_metrics[node.name] = metrics
        
        # Check for issues
        self._check_function_issues(node, metrics)
        
        # Restore state
        self.current_function = old_function
        self.cyclomatic_complexity = old_cyclomatic
        self.cognitive_complexity = old_cognitive
        self.nesting_depth = old_nesting
    
    def visit_If(self, node):
        """Enhanced if statement analysis"""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()
    
    def visit_For(self, node):
        """Enhanced for loop analysis"""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()
    
    def visit_While(self, node):
        """Enhanced while loop analysis"""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1 + self.nesting_depth
        
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()
    
    def visit_Try(self, node):
        """Try-except complexity analysis"""
        self.cyclomatic_complexity += 1
        
        for handler in node.handlers:
            self.cyclomatic_complexity += 1
            self.cognitive_complexity += 1 + self.nesting_depth
        
        if node.orelse:
            self.cyclomatic_complexity += 1
            
        if node.finalbody:
            self.cognitive_complexity += 1
        
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        """Boolean operation complexity"""
        additional = len(node.values) - 1
        self.cyclomatic_complexity += additional
        self.cognitive_complexity += additional
        self.generic_visit(node)
    
    def visit_Num(self, node):
        """Detect magic numbers"""
        if isinstance(node.n, (int, float)) and abs(node.n) > 1:
            if node.n not in [0, 1, -1, 100, 1000, 1024]:  # Common acceptable numbers
                self.magic_numbers.append((node.lineno, str(node.n)))
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Track imports"""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Track from imports"""
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Track function calls and detect security issues"""
        if isinstance(node.func, ast.Name):
            self.used_functions.add(node.func.id)
            
            # Check for security issues
            if node.func.id in ['eval', 'exec']:
                self.security_issues.append(SecurityIssue(
                    cwe_id="CWE-95",
                    confidence="HIGH",
                    severity=Severity.CRITICAL,
                    message=f"Use of {node.func.id}() can lead to code injection",
                    file_path=self.file_path,
                    line=node.lineno,
                    test_id="B701"
                ))
        
        self.generic_visit(node)
    
    def _enter_nesting(self):
        """Enter nested block"""
        self.nesting_depth += 1
    
    def _exit_nesting(self):
        """Exit nested block"""
        self.nesting_depth = max(0, self.nesting_depth - 1)
    
    def _calculate_halstead_volume(self, node) -> float:
        """Calculate simplified Halstead volume"""
        # This is a simplified version
        operators = 0
        operands = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
                                ast.Pow, ast.LShift, ast.RShift, ast.BitOr,
                                ast.BitXor, ast.BitAnd, ast.FloorDiv)):
                operators += 1
            elif isinstance(child, (ast.Name, ast.Num, ast.Str)):
                operands += 1
        
        vocabulary = operators + operands
        length = operators + operands
        
        if vocabulary == 0:
            return 0.0
        
        import math
        return length * math.log2(vocabulary) if vocabulary > 0 else 0.0
    
    def _calculate_maintainability_index(self, halstead_volume: float, 
                                       cyclomatic_complexity: int, 
                                       lines_of_code: int) -> float:
        """Calculate maintainability index using industry standard formula"""
        import math
        
        if lines_of_code == 0:
            return 100.0
        
        # Standard formula: 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        if halstead_volume <= 0:
            halstead_volume = 1
        
        mi = (171 - 5.2 * math.log(halstead_volume) - 
              0.23 * cyclomatic_complexity - 
              16.2 * math.log(lines_of_code))
        
        return max(0, min(100, mi))
    
    def _count_logical_lines(self, node) -> int:
        """Count logical lines of code"""
        logical_lines = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.stmt)):
                logical_lines += 1
        return logical_lines
    
    def _check_function_issues(self, node, metrics: ComplexityMetrics):
        """Check for function-level issues"""
        # Cognitive complexity check (2024 standard: max 15)
        if metrics.cognitive_complexity > 15:
            self.issues.append(Issue(
                category=TechnicalDebtCategory.MAINTAINABILITY,
                severity=Severity.MAJOR if metrics.cognitive_complexity > 25 else Severity.MINOR,
                message=f"Cognitive complexity too high: {metrics.cognitive_complexity} (max: 15)",
                file_path=self.file_path,
                line=node.lineno,
                rule_id="cognitive_complexity",
                effort_minutes=metrics.cognitive_complexity * 2
            ))
        
        # Cyclomatic complexity check
        if metrics.cyclomatic_complexity > 10:
            self.issues.append(Issue(
                category=TechnicalDebtCategory.TESTABILITY,
                severity=Severity.MAJOR if metrics.cyclomatic_complexity > 20 else Severity.MINOR,
                message=f"Cyclomatic complexity too high: {metrics.cyclomatic_complexity} (max: 10)",
                file_path=self.file_path,
                line=node.lineno,
                rule_id="cyclomatic_complexity",
                effort_minutes=metrics.cyclomatic_complexity * 3
            ))
        
        # Function length check
        if metrics.lines_of_code > 50:
            self.issues.append(Issue(
                category=TechnicalDebtCategory.MAINTAINABILITY,
                severity=Severity.MINOR,
                message=f"Function too long: {metrics.lines_of_code} lines (max: 50)",
                file_path=self.file_path,
                line=node.lineno,
                rule_id="function_length",
                effort_minutes=10
            ))
        
        # Parameter count check
        param_count = len(node.args.args)
        if param_count > 5:
            self.issues.append(Issue(
                category=TechnicalDebtCategory.MAINTAINABILITY,
                severity=Severity.MINOR,
                message=f"Too many parameters: {param_count} (max: 5)",
                file_path=self.file_path,
                line=node.lineno,
                rule_id="parameter_count",
                effort_minutes=15
            ))
        
        # Maintainability index check
        if metrics.maintainability_index < 20:
            self.issues.append(Issue(
                category=TechnicalDebtCategory.MAINTAINABILITY,
                severity=Severity.MAJOR,
                message=f"Low maintainability index: {metrics.maintainability_index:.1f} (min: 20)",
                file_path=self.file_path,
                line=node.lineno,
                rule_id="maintainability_index",
                effort_minutes=30
            ))
    
    def _analyze_security(self):
        """Analyze security vulnerabilities using pattern matching"""
        lines = self.source_code.split('\n')
        
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        severity = self._get_security_severity(category)
                        cwe_id = self._get_cwe_id(category)
                        
                        self.security_issues.append(SecurityIssue(
                            cwe_id=cwe_id,
                            confidence="MEDIUM",
                            severity=severity,
                            message=f"Potential {category.replace('_', ' ')}: {line.strip()}",
                            file_path=self.file_path,
                            line=line_num,
                            test_id=f"B{category[:3].upper()}"
                        ))
    
    def _get_security_severity(self, category: str) -> Severity:
        """Map security categories to severity levels"""
        severity_map = {
            'hardcoded_secrets': Severity.CRITICAL,
            'sql_injection': Severity.CRITICAL,
            'shell_injection': Severity.CRITICAL,
            'unsafe_deserialization': Severity.MAJOR,
        }
        return severity_map.get(category, Severity.MINOR)
    
    def _get_cwe_id(self, category: str) -> str:
        """Map security categories to CWE IDs"""
        cwe_map = {
            'hardcoded_secrets': 'CWE-798',
            'sql_injection': 'CWE-89',
            'shell_injection': 'CWE-78',
            'unsafe_deserialization': 'CWE-502',
        }
        return cwe_map.get(category, 'CWE-1000')
    
    def _detect_code_smells(self):
        """Detect common code smells"""
        lines = self.source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Long line
            if len(line) > 120:
                self.issues.append(Issue(
                    category=TechnicalDebtCategory.MAINTAINABILITY,
                    severity=Severity.INFO,
                    message=f"Line too long: {len(line)} characters (max: 120)",
                    file_path=self.file_path,
                    line=line_num,
                    rule_id="line_length",
                    effort_minutes=1
                ))
            
            # TODO/FIXME comments
            if any(marker in line.upper() for marker in ['TODO', 'FIXME', 'HACK', 'XXX']):
                self.issues.append(Issue(
                    category=TechnicalDebtCategory.MAINTAINABILITY,
                    severity=Severity.INFO,
                    message="Technical debt marker found",
                    file_path=self.file_path,
                    line=line_num,
                    rule_id="tech_debt_marker",
                    effort_minutes=5
                ))
        
        # Magic numbers
        for line_num, number in self.magic_numbers:
            self.issues.append(Issue(
                category=TechnicalDebtCategory.MAINTAINABILITY,
                severity=Severity.MINOR,
                message=f"Magic number: {number}",
                file_path=self.file_path,
                line=line_num,
                rule_id="magic_number",
                effort_minutes=5
            ))
        
        # Unused imports/functions
        unused_functions = self.defined_functions - self.used_functions
        for func in unused_functions:
            self.issues.append(Issue(
                category=TechnicalDebtCategory.MAINTAINABILITY,
                severity=Severity.MINOR,
                message=f"Unused function: {func}",
                file_path=self.file_path,
                line=1,  # Would need AST traversal to get exact line
                rule_id="unused_function",
                effort_minutes=2
            ))


class TechnicalDebtCalculator:
    """Calculate technical debt using SQALE-inspired methodology"""
    
    def __init__(self):
        self.effort_multipliers = {
            TechnicalDebtCategory.TESTABILITY: 1.0,
            TechnicalDebtCategory.RELIABILITY: 1.5,
            TechnicalDebtCategory.CHANGEABILITY: 1.2,
            TechnicalDebtCategory.EFFICIENCY: 1.3,
            TechnicalDebtCategory.SECURITY: 2.0,
            TechnicalDebtCategory.MAINTAINABILITY: 1.1,
            TechnicalDebtCategory.PORTABILITY: 0.8,
        }
    
    def calculate_debt(self, issues: List[Issue]) -> TechnicalDebtMetrics:
        """Calculate technical debt metrics"""
        issues_by_category = defaultdict(list)
        total_debt_minutes = 0
        
        for issue in issues:
            issues_by_category[issue.category].append(issue)
            multiplier = self.effort_multipliers.get(issue.category, 1.0)
            total_debt_minutes += issue.effort_minutes * multiplier
        
        # Calculate debt ratio (simplified)
        # In real implementation, this would be debt / development cost
        debt_ratio = min(100, total_debt_minutes / 1000) if total_debt_minutes > 0 else 0
        
        # SQALE rating (A-E)
        sqale_rating = self._calculate_sqale_rating(debt_ratio)
        
        return TechnicalDebtMetrics(
            total_debt_minutes=int(total_debt_minutes),
            debt_ratio=debt_ratio,
            sqale_rating=sqale_rating,
            issues_by_category=dict(issues_by_category),
            remediation_cost=int(total_debt_minutes * 1.2)  # Add overhead
        )
    
    def _calculate_sqale_rating(self, debt_ratio: float) -> str:
        """Calculate SQALE rating based on debt ratio"""
        if debt_ratio <= 5:
            return "A"
        elif debt_ratio <= 10:
            return "B"
        elif debt_ratio <= 20:
            return "C"
        elif debt_ratio <= 50:
            return "D"
        else:
            return "E"


class QualityGateChecker:
    """Check code against quality gates"""
    
    def __init__(self, quality_gate: QualityGate):
        self.quality_gate = quality_gate
    
    def check_quality_gate(self, metrics: Dict[str, ComplexityMetrics], 
                          issues: List[Issue], 
                          security_issues: List[SecurityIssue],
                          debt_metrics: TechnicalDebtMetrics) -> Tuple[bool, List[str]]:
        """Check if code passes quality gate"""
        failures = []
        
        # Check complexity thresholds
        for func_name, func_metrics in metrics.items():
            if func_metrics.cyclomatic_complexity > self.quality_gate.max_cyclomatic_complexity:
                failures.append(
                    f"Function '{func_name}' exceeds cyclomatic complexity limit: "
                    f"{func_metrics.cyclomatic_complexity} > {self.quality_gate.max_cyclomatic_complexity}"
                )
            
            if func_metrics.cognitive_complexity > self.quality_gate.max_cognitive_complexity:
                failures.append(
                    f"Function '{func_name}' exceeds cognitive complexity limit: "
                    f"{func_metrics.cognitive_complexity} > {self.quality_gate.max_cognitive_complexity}"
                )
        
        # Check issue counts
        major_issues = [i for i in issues if i.severity in [Severity.MAJOR, Severity.CRITICAL, Severity.BLOCKER]]
        if len(major_issues) > self.quality_gate.max_code_smells:
            failures.append(f"Too many major code issues: {len(major_issues)} > {self.quality_gate.max_code_smells}")
        
        # Check security issues
        critical_security = [s for s in security_issues if s.severity in [Severity.CRITICAL, Severity.BLOCKER]]
        if len(critical_security) > self.quality_gate.max_security_hotspots:
            failures.append(f"Critical security issues found: {len(critical_security)}")
        
        # Check SQALE rating
        if debt_metrics.sqale_rating not in ['A', 'B'] and self.quality_gate.min_maintainability_rating == 'A':
            failures.append(f"SQALE rating too low: {debt_metrics.sqale_rating}")
        
        return len(failures) == 0, failures


def analyze_project(project_root: Path, quality_gate: QualityGate = None) -> Dict[str, Any]:
    """Analyze entire project with enhanced metrics"""
    if quality_gate is None:
        quality_gate = QualityGate()
    
    print("🔍 Enhanced Code Quality Analysis")
    print("=" * 50)
    
    # Find Python files
    python_files = []
    for py_file in project_root.rglob('*.py'):
        path_str = str(py_file)
        if not any(exclude in path_str for exclude in ['venv', 'node_modules', '__pycache__']):
            python_files.append(py_file)
    
    print(f"Found {len(python_files)} Python files")
    
    all_metrics = {}
    all_issues = []
    all_security_issues = []
    
    # Analyze each file
    for py_file in python_files:
        print(f"  Analyzing: {py_file.relative_to(project_root)}")
        try:
            analyzer = EnhancedCodeAnalyzer(str(py_file))
            metrics, issues, security_issues = analyzer.analyze()
            
            all_metrics[str(py_file.relative_to(project_root))] = metrics
            all_issues.extend(issues)
            all_security_issues.extend(security_issues)
            
        except Exception as e:
            print(f"    Error analyzing {py_file}: {e}")
    
    # Calculate technical debt
    debt_calculator = TechnicalDebtCalculator()
    debt_metrics = debt_calculator.calculate_debt(all_issues)
    
    # Check quality gate
    gate_checker = QualityGateChecker(quality_gate)
    gate_passed, gate_failures = gate_checker.check_quality_gate(
        {f: m for file_metrics in all_metrics.values() for f, m in file_metrics.items()},
        all_issues,
        all_security_issues,
        debt_metrics
    )
    
    # Generate summary
    results = {
        'timestamp': datetime.datetime.now().isoformat(),
        'analysis_summary': {
            'files_analyzed': len(python_files),
            'total_functions': sum(len(fm) for fm in all_metrics.values()),
            'total_issues': len(all_issues),
            'security_issues': len(all_security_issues),
            'technical_debt_minutes': debt_metrics.total_debt_minutes,
            'sqale_rating': debt_metrics.sqale_rating,
            'quality_gate_passed': gate_passed
        },
        'metrics_by_file': {
            file_path: {
                func_name: asdict(func_metrics) 
                for func_name, func_metrics in file_metrics.items()
            }
            for file_path, file_metrics in all_metrics.items()
        },
        'issues': [
            {
                'category': issue.category.value,
                'severity': issue.severity.value,
                'message': issue.message,
                'file_path': issue.file_path,
                'line': issue.line,
                'column': issue.column,
                'rule_id': issue.rule_id,
                'effort_minutes': issue.effort_minutes
            }
            for issue in all_issues
        ],
        'security_issues': [
            {
                'cwe_id': issue.cwe_id,
                'confidence': issue.confidence,
                'severity': issue.severity.value,
                'message': issue.message,
                'file_path': issue.file_path,
                'line': issue.line,
                'test_id': issue.test_id
            }
            for issue in all_security_issues
        ],
        'technical_debt': {
            'total_debt_minutes': debt_metrics.total_debt_minutes,
            'debt_ratio': debt_metrics.debt_ratio,
            'sqale_rating': debt_metrics.sqale_rating,
            'remediation_cost': debt_metrics.remediation_cost,
            'issues_by_category': {
                category.value: [
                    {
                        'category': issue.category.value,
                        'severity': issue.severity.value,
                        'message': issue.message,
                        'file_path': issue.file_path,
                        'line': issue.line,
                        'rule_id': issue.rule_id,
                        'effort_minutes': issue.effort_minutes
                    }
                    for issue in issues_list
                ]
                for category, issues_list in debt_metrics.issues_by_category.items()
            }
        },
        'quality_gate': {
            'passed': gate_passed,
            'failures': gate_failures,
            'thresholds': asdict(quality_gate)
        }
    }
    
    return results


def main():
    """Main analysis function"""
    project_root = Path(__file__).parent.parent
    
    print("🛠️  Enhanced TauTranslator Code Quality Analysis")
    print("=" * 60)
    
    # Configure quality gate
    quality_gate = QualityGate(
        max_cyclomatic_complexity=10,
        max_cognitive_complexity=15,
        min_test_coverage=70.0,  # Reduced for current state
        max_code_smells=5,       # Allow some issues during development
        max_security_hotspots=0,
        min_maintainability_rating="B"  # Relaxed for development
    )
    
    # Run analysis
    results = analyze_project(project_root, quality_gate)
    
    # Save results
    results_file = project_root / "enhanced_quality_analysis.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    summary = results['analysis_summary']
    print(f"\n📊 Analysis Results:")
    print(f"  Files analyzed: {summary['files_analyzed']}")
    print(f"  Functions: {summary['total_functions']}")
    print(f"  Issues found: {summary['total_issues']}")
    print(f"  Security issues: {summary['security_issues']}")
    print(f"  Technical debt: {summary['technical_debt_minutes']} minutes")
    print(f"  SQALE rating: {summary['sqale_rating']}")
    print(f"  Quality gate: {'✅ PASSED' if summary['quality_gate_passed'] else '❌ FAILED'}")
    
    if not summary['quality_gate_passed']:
        print(f"\n❌ Quality Gate Failures:")
        for failure in results['quality_gate']['failures']:
            print(f"  • {failure}")
    
    # Top issues
    issues_by_severity = defaultdict(list)
    for issue in results['issues']:
        issues_by_severity[issue['severity']].append(issue)
    
    print(f"\n📋 Issues by Severity:")
    for severity in ['BLOCKER', 'CRITICAL', 'MAJOR', 'MINOR', 'INFO']:
        count = len(issues_by_severity[severity])
        if count > 0:
            print(f"  {severity}: {count}")
    
    print(f"\n💾 Detailed results saved to: {results_file}")


if __name__ == "__main__":
    main()