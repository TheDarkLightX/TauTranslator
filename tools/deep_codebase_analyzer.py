#!/usr/bin/env python3
"""
Deep Codebase Analysis Tool
===========================

Comprehensive analysis of algorithms, data structures, antipatterns, and architectural concerns
specifically designed for the TauTranslator project refactoring phase.

Analyzes:
- Algorithm complexity and efficiency
- Data structure usage patterns
- Common antipatterns and code smells
- LLM/API integration patterns
- Security vulnerabilities
- Architectural inconsistencies
- Performance bottlenecks
- Refactoring opportunities

Author: DarkLightX/Dana Edwards
"""

import ast
import os
import sys
import json
import re
import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter
import importlib.util
import networkx as nx

# Import our enhanced quality analyzer
sys.path.append(os.path.dirname(__file__))
from enhanced_code_quality_analyzer import EnhancedCodeQualityAnalyzer, QualityMetrics


@dataclass
class AlgorithmAnalysis:
    """Analysis of algorithm patterns and complexity."""
    file_path: str
    algorithms_detected: List[str]
    time_complexity_estimates: Dict[str, str]
    space_complexity_estimates: Dict[str, str]
    performance_concerns: List[str]
    optimization_opportunities: List[str]


@dataclass
class DataStructureAnalysis:
    """Analysis of data structure usage patterns."""
    file_path: str
    data_structures_used: Dict[str, int]
    inefficient_patterns: List[str]
    memory_concerns: List[str]
    suggested_alternatives: List[str]


@dataclass
class AntipatternAnalysis:
    """Analysis of antipatterns and code smells."""
    file_path: str
    antipatterns_found: List[str]
    code_smells: List[str]
    architectural_issues: List[str]
    refactoring_suggestions: List[str]
    severity_score: float


@dataclass
class LLMAPIAnalysis:
    """Analysis of LLM and API integration patterns."""
    file_path: str
    api_endpoints_found: List[str]
    llm_integrations: List[str]
    authentication_patterns: List[str]
    error_handling_quality: str
    security_concerns: List[str]
    async_patterns: List[str]
    rate_limiting: bool
    caching_strategy: Optional[str]


@dataclass
class SecurityAnalysis:
    """Security vulnerability analysis."""
    file_path: str
    vulnerabilities: List[str]
    insecure_patterns: List[str]
    missing_validations: List[str]
    hardcoded_secrets: List[str]
    sql_injection_risks: List[str]
    xss_risks: List[str]
    security_score: float


@dataclass
class ArchitecturalAnalysis:
    """Architectural pattern and dependency analysis."""
    file_path: str
    design_patterns: List[str]
    solid_violations: List[str]
    coupling_score: float
    cohesion_score: float
    dependency_cycles: List[List[str]]
    layer_violations: List[str]


class AlgorithmDetector(ast.NodeVisitor):
    """Detects algorithm patterns and estimates complexity."""
    
    def __init__(self):
        self.algorithms = []
        self.complexity_estimates = {}
        self.performance_concerns = []
        self.loop_depth = 0
        self.recursive_functions = set()
    
    def visit_For(self, node):
        self.loop_depth += 1
        
        # Detect nested loops
        if self.loop_depth > 1:
            self.algorithms.append(f"Nested loop (depth {self.loop_depth})")
            if self.loop_depth == 2:
                self.complexity_estimates["nested_loop"] = "O(n²)"
            elif self.loop_depth == 3:
                self.complexity_estimates["nested_loop"] = "O(n³)"
                self.performance_concerns.append("Triple nested loop - consider optimization")
            elif self.loop_depth > 3:
                self.complexity_estimates["nested_loop"] = f"O(n^{self.loop_depth})"
                self.performance_concerns.append(f"Deep nesting ({self.loop_depth} levels) - major performance concern")
        
        # Check for list comprehensions in loops
        for child in ast.walk(node):
            if isinstance(child, ast.ListComp):
                self.performance_concerns.append("List comprehension inside loop - potential memory issue")
        
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_While(self, node):
        self.loop_depth += 1
        self.algorithms.append("While loop")
        
        # Check for infinite loop patterns
        if not self._has_break_or_return(node):
            self.performance_concerns.append("While loop without clear termination condition")
        
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_FunctionDef(self, node):
        # Check for recursion
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == node.name:
                    self.recursive_functions.add(node.name)
                    self.algorithms.append(f"Recursive function: {node.name}")
                    self.complexity_estimates[f"recursion_{node.name}"] = "Depends on recursion depth"
        
        # Check for sorting algorithms
        if any(keyword in node.name.lower() for keyword in ['sort', 'order', 'rank']):
            self.algorithms.append(f"Potential sorting algorithm: {node.name}")
        
        # Check for search algorithms
        if any(keyword in node.name.lower() for keyword in ['search', 'find', 'lookup', 'query']):
            self.algorithms.append(f"Potential search algorithm: {node.name}")
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        # Detect common algorithmic operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'sort':
                self.algorithms.append("Built-in sort")
                self.complexity_estimates["sort"] = "O(n log n)"
            elif node.func.attr in ['reverse', 'reversed']:
                self.algorithms.append("List reversal")
                self.complexity_estimates["reverse"] = "O(n)"
        
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ['sorted', 'min', 'max']:
                self.algorithms.append(f"Built-in {func_name}")
                if func_name == 'sorted':
                    self.complexity_estimates["sorted"] = "O(n log n)"
                else:
                    self.complexity_estimates[func_name] = "O(n)"
        
        self.generic_visit(node)
    
    def _has_break_or_return(self, node):
        """Check if a node contains break or return statements."""
        for child in ast.walk(node):
            if isinstance(child, (ast.Break, ast.Return)):
                return True
        return False


class DataStructureDetector(ast.NodeVisitor):
    """Detects data structure usage patterns."""
    
    def __init__(self):
        self.data_structures = Counter()
        self.inefficient_patterns = []
        self.memory_concerns = []
    
    def visit_List(self, node):
        self.data_structures['list'] += 1
        
        # Check for large literal lists
        if len(node.elts) > 100:
            self.memory_concerns.append(f"Large list literal with {len(node.elts)} elements")
        
        self.generic_visit(node)
    
    def visit_Dict(self, node):
        self.data_structures['dict'] += 1
        
        # Check for large literal dicts
        if len(node.keys) > 50:
            self.memory_concerns.append(f"Large dict literal with {len(node.keys)} keys")
        
        self.generic_visit(node)
    
    def visit_Set(self, node):
        self.data_structures['set'] += 1
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            # Detect collection types
            if func_name in ['list', 'dict', 'set', 'tuple']:
                self.data_structures[func_name] += 1
            
            # Detect advanced data structures
            elif func_name in ['deque', 'defaultdict', 'Counter', 'OrderedDict']:
                self.data_structures[func_name] += 1
            
            # Detect inefficient patterns
            elif func_name == 'append':
                # Check if in a loop
                parent = getattr(node, 'parent', None)
                if self._is_in_loop(node):
                    self.inefficient_patterns.append("List append in loop - consider list comprehension")
        
        self.generic_visit(node)
    
    def visit_Subscript(self, node):
        # Check for inefficient list access patterns
        if isinstance(node.slice, ast.Slice):
            self.data_structures['slice'] += 1
            
            # Check for full list copying
            if (node.slice.lower is None and node.slice.upper is None):
                self.inefficient_patterns.append("Full list slice copy - consider explicit copy()")
        
        self.generic_visit(node)
    
    def _is_in_loop(self, node):
        """Check if a node is inside a loop."""
        # This is a simplified check - in real implementation,
        # we'd need to track the AST hierarchy
        return False  # Placeholder


class AntipatternDetector(ast.NodeVisitor):
    """Detects antipatterns and code smells."""
    
    def __init__(self):
        self.antipatterns = []
        self.code_smells = []
        self.architectural_issues = []
        self.function_lengths = {}
        self.class_sizes = {}
        self.parameter_counts = {}
    
    def visit_FunctionDef(self, node):
        # Calculate function length
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            length = node.end_lineno - node.lineno
            self.function_lengths[node.name] = length
            
            if length > 50:
                self.code_smells.append(f"Long function '{node.name}' ({length} lines)")
            elif length > 100:
                self.antipatterns.append(f"God function '{node.name}' ({length} lines)")
        
        # Check parameter count
        param_count = len(node.args.args)
        self.parameter_counts[node.name] = param_count
        
        if param_count > 5:
            self.code_smells.append(f"Too many parameters in '{node.name}' ({param_count})")
        elif param_count > 8:
            self.antipatterns.append(f"Parameter explosion in '{node.name}' ({param_count})")
        
        # Check for dead code (unreachable after return)
        self._check_dead_code(node)
        
        # Check for nested functions (potential code smell)
        nested_functions = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef) and n != node]
        if len(nested_functions) > 2:
            self.code_smells.append(f"Too many nested functions in '{node.name}'")
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        # Calculate class size
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        self.class_sizes[node.name] = len(methods)
        
        if len(methods) > 20:
            self.code_smells.append(f"Large class '{node.name}' ({len(methods)} methods)")
        elif len(methods) > 50:
            self.antipatterns.append(f"God class '{node.name}' ({len(methods)} methods)")
        
        # Check for data classes without methods
        if len(methods) == 0:
            attributes = [n for n in node.body if isinstance(n, ast.Assign)]
            if len(attributes) > 5:
                self.architectural_issues.append(f"Data class '{node.name}' with many attributes but no methods")
        
        self.generic_visit(node)
    
    def visit_Try(self, node):
        # Check for bare except clauses
        for handler in node.handlers:
            if handler.type is None:
                self.antipatterns.append("Bare except clause - catches all exceptions")
        
        # Check for empty exception handlers
        for handler in node.handlers:
            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                self.code_smells.append("Empty exception handler")
        
        self.generic_visit(node)
    
    def visit_If(self, node):
        # Check for deeply nested conditions
        depth = self._calculate_nesting_depth(node)
        if depth > 4:
            self.code_smells.append(f"Deeply nested conditions (depth {depth})")
        
        # Check for magic numbers in conditions
        for child in ast.walk(node.test):
            if isinstance(child, ast.Constant) and isinstance(child.value, (int, float)):
                if child.value not in [0, 1, -1]:  # Common acceptable magic numbers
                    self.code_smells.append(f"Magic number in condition: {child.value}")
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        # Check for string concatenation in loops
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'join':
            # This is actually good - joining is efficient
            pass
        elif isinstance(node.func, ast.Name) and node.func.id == 'print':
            # Check for print statements (should use logging)
            self.code_smells.append("Print statement found - consider using logging")
        
        self.generic_visit(node)
    
    def _check_dead_code(self, node):
        """Check for unreachable code after return statements."""
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Return) and i < len(node.body) - 1:
                self.code_smells.append(f"Dead code after return in function '{node.name}'")
                break
    
    def _calculate_nesting_depth(self, node, depth=0):
        """Calculate the maximum nesting depth of conditions."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth


class LLMAPIAnalyzer(ast.NodeVisitor):
    """Analyzes LLM and API integration patterns."""
    
    def __init__(self):
        self.api_endpoints = []
        self.llm_integrations = []
        self.auth_patterns = []
        self.error_handling = "poor"
        self.security_concerns = []
        self.async_patterns = []
        self.has_rate_limiting = False
        self.caching_strategy = None
        self.http_methods = Counter()
        self.api_keys_found = []
    
    def visit_Call(self, node):
        # Detect HTTP/API calls
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            
            # HTTP method calls
            if method_name.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                self.http_methods[method_name.upper()] += 1
                
                # Extract endpoint URLs
                if node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        self.api_endpoints.append(arg.value)
            
            # Detect LLM service calls
            elif method_name in ['generate', 'complete', 'chat', 'translate']:
                if isinstance(node.func.value, ast.Name):
                    service_name = node.func.value.id
                    self.llm_integrations.append(f"{service_name}.{method_name}")
        
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            # Detect specific LLM/AI libraries
            if func_name in ['openai', 'anthropic', 'cohere', 'huggingface']:
                self.llm_integrations.append(func_name)
            
            # Detect async patterns
            elif func_name in ['asyncio', 'aiohttp', 'async_timeout']:
                self.async_patterns.append(func_name)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.async_patterns.append(f"async function: {node.name}")
        self.generic_visit(node)
    
    def visit_Await(self, node):
        self.async_patterns.append("await expression")
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        # Look for API key assignments
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value
            
            # Detect potential API keys
            if any(pattern in value.lower() for pattern in ['sk-', 'api_key', 'bearer', 'token']):
                if len(value) > 20:  # Likely an actual key
                    self.security_concerns.append("Hardcoded API key found")
                    self.api_keys_found.append(value[:10] + "...")
        
        self.generic_visit(node)
    
    def visit_Try(self, node):
        # Check error handling quality
        has_specific_handlers = any(
            handler.type and isinstance(handler.type, ast.Name)
            for handler in node.handlers
        )
        
        if has_specific_handlers:
            if self.error_handling == "poor":
                self.error_handling = "fair"
        
        # Check for retry logic
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Name) and stmt.id in ['retry', 'backoff', 'sleep']:
                if self.error_handling in ["poor", "fair"]:
                    self.error_handling = "good"
        
        self.generic_visit(node)


class SecurityAnalyzer(ast.NodeVisitor):
    """Analyzes security vulnerabilities."""
    
    def __init__(self):
        self.vulnerabilities = []
        self.insecure_patterns = []
        self.missing_validations = []
        self.hardcoded_secrets = []
        self.sql_injection_risks = []
        self.xss_risks = []
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            # SQL injection risks
            if func_name in ['execute', 'query', 'exec']:
                # Check if using string formatting
                if node.args and isinstance(node.args[0], ast.BinOp):
                    if isinstance(node.args[0].op, ast.Mod):  # % formatting
                        self.sql_injection_risks.append("SQL query with % formatting")
                elif node.args and isinstance(node.args[0], ast.JoinedStr):  # f-strings
                    self.sql_injection_risks.append("SQL query with f-string")
            
            # Unsafe functions
            elif func_name in ['eval', 'exec', 'compile']:
                self.vulnerabilities.append(f"Dangerous function: {func_name}")
            
            # Pickle security issues
            elif func_name in ['pickle', 'cPickle'] and node.args:
                self.vulnerabilities.append("Pickle deserialization - potential code execution")
        
        elif isinstance(node.func, ast.Attribute):
            # Hash/crypto analysis
            if node.func.attr in ['md5', 'sha1']:
                self.insecure_patterns.append(f"Weak hash algorithm: {node.func.attr}")
        
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        # Look for hardcoded secrets
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value.lower()
            
            if any(secret in value for secret in ['password', 'secret', 'key', 'token']):
                if len(node.value.value) > 8:  # Likely actual secret
                    self.hardcoded_secrets.append("Hardcoded secret detected")
        
        self.generic_visit(node)


class DependencyAnalyzer:
    """Analyzes module dependencies and architectural patterns."""
    
    def __init__(self):
        self.dependencies = defaultdict(set)
        self.imports = defaultdict(list)
        self.circular_deps = []
    
    def analyze_file(self, file_path: str, content: str):
        """Analyze dependencies in a single file."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[file_path].append(alias.name)
                        self.dependencies[file_path].add(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports[file_path].append(node.module)
                        self.dependencies[file_path].add(node.module)
        
        except SyntaxError:
            pass
    
    def find_circular_dependencies(self):
        """Find circular dependencies using graph analysis."""
        # Create directed graph
        G = nx.DiGraph()
        
        for file_path, deps in self.dependencies.items():
            for dep in deps:
                G.add_edge(file_path, dep)
        
        # Find cycles
        try:
            cycles = list(nx.simple_cycles(G))
            self.circular_deps = cycles
        except:
            # networkx not available or other error
            pass
        
        return self.circular_deps


class DeepCodebaseAnalyzer:
    """Main deep analysis coordinator."""
    
    def __init__(self):
        self.quality_analyzer = EnhancedCodeQualityAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of a single file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {
                'file_path': file_path,
                'error': f"Syntax error: {e}",
                'analysis_completed': False
            }
        
        # Basic quality metrics
        quality_metrics = self.quality_analyzer.analyze_file(file_path)
        
        # Algorithm analysis
        algo_detector = AlgorithmDetector()
        algo_detector.visit(tree)
        algorithm_analysis = AlgorithmAnalysis(
            file_path=file_path,
            algorithms_detected=algo_detector.algorithms,
            time_complexity_estimates=algo_detector.complexity_estimates,
            space_complexity_estimates={},  # Would need more sophisticated analysis
            performance_concerns=algo_detector.performance_concerns,
            optimization_opportunities=[]  # Would be derived from concerns
        )
        
        # Data structure analysis
        ds_detector = DataStructureDetector()
        ds_detector.visit(tree)
        data_structure_analysis = DataStructureAnalysis(
            file_path=file_path,
            data_structures_used=dict(ds_detector.data_structures),
            inefficient_patterns=ds_detector.inefficient_patterns,
            memory_concerns=ds_detector.memory_concerns,
            suggested_alternatives=[]  # Would be derived from patterns
        )
        
        # Antipattern analysis
        antipattern_detector = AntipatternDetector()
        antipattern_detector.visit(tree)
        antipattern_analysis = AntipatternAnalysis(
            file_path=file_path,
            antipatterns_found=antipattern_detector.antipatterns,
            code_smells=antipattern_detector.code_smells,
            architectural_issues=antipattern_detector.architectural_issues,
            refactoring_suggestions=[],  # Would be derived from issues
            severity_score=self._calculate_severity_score(antipattern_detector)
        )
        
        # LLM/API analysis
        llm_analyzer = LLMAPIAnalyzer()
        llm_analyzer.visit(tree)
        llm_api_analysis = LLMAPIAnalysis(
            file_path=file_path,
            api_endpoints_found=llm_analyzer.api_endpoints,
            llm_integrations=llm_analyzer.llm_integrations,
            authentication_patterns=llm_analyzer.auth_patterns,
            error_handling_quality=llm_analyzer.error_handling,
            security_concerns=llm_analyzer.security_concerns,
            async_patterns=llm_analyzer.async_patterns,
            rate_limiting=llm_analyzer.has_rate_limiting,
            caching_strategy=llm_analyzer.caching_strategy
        )
        
        # Security analysis
        security_analyzer = SecurityAnalyzer()
        security_analyzer.visit(tree)
        security_analysis = SecurityAnalysis(
            file_path=file_path,
            vulnerabilities=security_analyzer.vulnerabilities,
            insecure_patterns=security_analyzer.insecure_patterns,
            missing_validations=security_analyzer.missing_validations,
            hardcoded_secrets=security_analyzer.hardcoded_secrets,
            sql_injection_risks=security_analyzer.sql_injection_risks,
            xss_risks=security_analyzer.xss_risks,
            security_score=self._calculate_security_score(security_analyzer)
        )
        
        # Dependency analysis
        self.dependency_analyzer.analyze_file(file_path, content)
        
        return {
            'file_path': file_path,
            'analysis_completed': True,
            'timestamp': datetime.now().isoformat(),
            'quality_metrics': asdict(quality_metrics),
            'algorithm_analysis': asdict(algorithm_analysis),
            'data_structure_analysis': asdict(data_structure_analysis),
            'antipattern_analysis': asdict(antipattern_analysis),
            'llm_api_analysis': asdict(llm_api_analysis),
            'security_analysis': asdict(security_analysis)
        }
    
    def analyze_directory(self, directory: str, pattern: str = "*.py") -> Dict[str, Any]:
        """Analyze all Python files in a directory."""
        results = {}
        
        for file_path in Path(directory).rglob(pattern):
            if '__pycache__' in str(file_path) or '.git' in str(file_path):
                continue
            
            try:
                result = self.analyze_file(str(file_path))
                results[str(file_path)] = result
            except Exception as e:
                results[str(file_path)] = {
                    'file_path': str(file_path),
                    'error': str(e),
                    'analysis_completed': False
                }
        
        # Analyze circular dependencies
        circular_deps = self.dependency_analyzer.find_circular_dependencies()
        
        # Generate comprehensive report
        return self._generate_comprehensive_report(results, circular_deps)
    
    def _calculate_severity_score(self, detector: AntipatternDetector) -> float:
        """Calculate severity score based on antipatterns found."""
        score = 0.0
        score += len(detector.antipatterns) * 10  # High impact
        score += len(detector.code_smells) * 3    # Medium impact
        score += len(detector.architectural_issues) * 5  # High impact
        return min(100.0, score)
    
    def _calculate_security_score(self, analyzer: SecurityAnalyzer) -> float:
        """Calculate security score (0-100, higher is worse)."""
        score = 0.0
        score += len(analyzer.vulnerabilities) * 20
        score += len(analyzer.insecure_patterns) * 10
        score += len(analyzer.hardcoded_secrets) * 15
        score += len(analyzer.sql_injection_risks) * 25
        return min(100.0, score)
    
    def _generate_comprehensive_report(self, results: Dict[str, Any], circular_deps: List) -> Dict[str, Any]:
        """Generate a comprehensive analysis report."""
        successful_analyses = [r for r in results.values() if r.get('analysis_completed', False)]
        
        # Aggregate statistics
        total_files = len(results)
        successful_files = len(successful_analyses)
        
        # LLM/API statistics
        llm_files = [r for r in successful_analyses 
                    if r.get('llm_api_analysis', {}).get('llm_integrations')]
        api_files = [r for r in successful_analyses 
                    if r.get('llm_api_analysis', {}).get('api_endpoints_found')]
        
        # Security statistics
        vulnerable_files = [r for r in successful_analyses 
                           if r.get('security_analysis', {}).get('security_score', 0) > 10]
        
        # Quality statistics
        low_quality_files = [r for r in successful_analyses 
                            if r.get('quality_metrics', {}).get('quality_score', 100) < 70]
        
        # Refactoring priorities
        refactoring_priorities = self._identify_refactoring_priorities(successful_analyses)
        
        return {
            'summary': {
                'total_files_analyzed': total_files,
                'successful_analyses': successful_files,
                'failed_analyses': total_files - successful_files,
                'llm_integration_files': len(llm_files),
                'api_endpoint_files': len(api_files),
                'security_risk_files': len(vulnerable_files),
                'low_quality_files': len(low_quality_files),
                'circular_dependencies': len(circular_deps)
            },
            'refactoring_priorities': refactoring_priorities,
            'circular_dependencies': circular_deps,
            'detailed_results': results,
            'recommendations': self._generate_recommendations(successful_analyses),
            'generated_at': datetime.now().isoformat()
        }
    
    def _identify_refactoring_priorities(self, analyses: List[Dict]) -> List[Dict]:
        """Identify top refactoring priorities."""
        priorities = []
        
        for analysis in analyses:
            file_path = analysis['file_path']
            priority_score = 0
            issues = []
            
            # Quality score impact
            quality_score = analysis.get('quality_metrics', {}).get('quality_score', 100)
            if quality_score < 50:
                priority_score += 30
                issues.append(f"Very low quality score: {quality_score:.1f}")
            elif quality_score < 70:
                priority_score += 15
                issues.append(f"Low quality score: {quality_score:.1f}")
            
            # Security impact
            security_score = analysis.get('security_analysis', {}).get('security_score', 0)
            if security_score > 20:
                priority_score += 40
                issues.append(f"High security risk: {security_score:.1f}")
            
            # Complexity impact
            complexity = analysis.get('quality_metrics', {}).get('cyclomatic_complexity', 0)
            if complexity > 15:
                priority_score += 20
                issues.append(f"High complexity: {complexity}")
            
            # Antipattern impact
            antipattern_score = analysis.get('antipattern_analysis', {}).get('severity_score', 0)
            if antipattern_score > 20:
                priority_score += 25
                issues.append(f"Multiple antipatterns: {antipattern_score:.1f}")
            
            if priority_score > 20:  # Only include files with significant issues
                priorities.append({
                    'file_path': file_path,
                    'priority_score': priority_score,
                    'issues': issues,
                    'recommended_actions': self._get_recommended_actions(analysis)
                })
        
        # Sort by priority score
        priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        return priorities[:20]  # Top 20 priorities
    
    def _get_recommended_actions(self, analysis: Dict) -> List[str]:
        """Get recommended refactoring actions for a file."""
        actions = []
        
        quality = analysis.get('quality_metrics', {})
        antipattern = analysis.get('antipattern_analysis', {})
        security = analysis.get('security_analysis', {})
        
        # Quality-based actions
        if quality.get('lines_of_code', 0) > 600:
            actions.append("Split into smaller modules")
        
        if quality.get('cyclomatic_complexity', 0) > 15:
            actions.append("Reduce cyclomatic complexity")
        
        # Antipattern-based actions
        if antipattern.get('antipatterns_found'):
            actions.append("Refactor antipatterns: " + ", ".join(antipattern['antipatterns_found'][:3]))
        
        # Security-based actions
        if security.get('vulnerabilities'):
            actions.append("Fix security vulnerabilities")
        
        if security.get('hardcoded_secrets'):
            actions.append("Move secrets to environment variables")
        
        return actions
    
    def _generate_recommendations(self, analyses: List[Dict]) -> Dict[str, List[str]]:
        """Generate overall recommendations for the codebase."""
        recommendations = {
            'immediate_actions': [],
            'architectural_improvements': [],
            'security_enhancements': [],
            'performance_optimizations': [],
            'code_quality_improvements': []
        }
        
        # Analyze overall patterns
        total_security_issues = sum(
            len(a.get('security_analysis', {}).get('vulnerabilities', []))
            for a in analyses
        )
        
        total_llm_integrations = sum(
            len(a.get('llm_api_analysis', {}).get('llm_integrations', []))
            for a in analyses
        )
        
        if total_security_issues > 5:
            recommendations['immediate_actions'].append(
                "Critical: Address security vulnerabilities across the codebase"
            )
        
        if total_llm_integrations > 10:
            recommendations['architectural_improvements'].append(
                "Consider creating a unified LLM integration service"
            )
        
        # More recommendations would be added based on patterns found
        
        return recommendations


def main():
    """Main entry point for deep codebase analysis."""
    if len(sys.argv) < 2:
        print("Usage: python deep_codebase_analyzer.py <directory> [--output-file <file>]")
        sys.exit(1)
    
    directory = sys.argv[1]
    output_file = None
    
    if "--output-file" in sys.argv:
        idx = sys.argv.index("--output-file")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)
    
    print(f"Starting deep analysis of {directory}...")
    analyzer = DeepCodebaseAnalyzer()
    
    results = analyzer.analyze_directory(directory)
    
    # Save results
    if not output_file:
        output_file = f"deep_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    summary = results['summary']
    print(f"\n{'='*60}")
    print("DEEP CODEBASE ANALYSIS REPORT")
    print(f"{'='*60}")
    print(f"Files analyzed: {summary['total_files_analyzed']}")
    print(f"Successful analyses: {summary['successful_analyses']}")
    print(f"LLM integration files: {summary['llm_integration_files']}")
    print(f"API endpoint files: {summary['api_endpoint_files']}")
    print(f"Security risk files: {summary['security_risk_files']}")
    print(f"Low quality files: {summary['low_quality_files']}")
    print(f"Circular dependencies: {summary['circular_dependencies']}")
    
    # Show top refactoring priorities
    priorities = results['refactoring_priorities']
    if priorities:
        print(f"\nTOP REFACTORING PRIORITIES:")
        for i, priority in enumerate(priorities[:5], 1):
            print(f"\n{i}. {priority['file_path']} (Score: {priority['priority_score']})")
            for issue in priority['issues'][:3]:
                print(f"   - {issue}")
    
    print(f"\nFull report saved to: {output_file}")


if __name__ == '__main__':
    main()