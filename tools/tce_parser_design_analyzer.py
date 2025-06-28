#!/usr/bin/env python3
"""
TCE Parser Design Quality Analyzer
Comprehensive analysis of design patterns, algorithms, and architecture quality.

Copyright: DarkLightX / Dana Edwards
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class DesignPattern(Enum):
    """Design patterns identified in code."""
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    STRATEGY = "strategy"
    VISITOR = "visitor"
    PARSER_COMBINATOR = "parser_combinator"
    CHAIN_OF_RESPONSIBILITY = "chain_of_responsibility"
    FACTORY = "factory"
    SINGLETON = "singleton"
    REGEX_HEAVY = "regex_heavy"
    FUNCTIONAL = "functional"


class AlgorithmType(Enum):
    """Types of parsing algorithms."""
    REGEX_BASED = "regex_based"
    AST_BASED = "ast_based"
    RECURSIVE_DESCENT = "recursive_descent"
    FINITE_STATE = "finite_state"
    PATTERN_MATCHING = "pattern_matching"


@dataclass
class ParserCapability:
    """Capability analysis for a parser."""
    name: str
    handles_temporal: bool = False
    handles_quantifiers: bool = False
    handles_conditionals: bool = False
    handles_modals: bool = False
    handles_comparatives: bool = False
    handles_coreference: bool = False
    handles_negation: bool = False
    handles_semantic_types: bool = False
    extensible: bool = False
    user_customizable: bool = False


@dataclass
class PerformanceAnalysis:
    """Performance characteristics analysis."""
    regex_patterns_count: int = 0
    nested_loops_count: int = 0
    recursion_depth: int = 0
    pattern_compilation_cost: int = 0
    memory_usage_estimate: str = "low"
    scalability_rating: str = "unknown"


@dataclass
class ArchitectureAnalysis:
    """Architecture quality analysis."""
    inheritance_depth: int = 0
    coupling_score: float = 0.0
    cohesion_score: float = 0.0
    solid_violations: List[str] = field(default_factory=list)
    design_patterns: Set[DesignPattern] = field(default_factory=set)
    algorithm_types: Set[AlgorithmType] = field(default_factory=set)
    maintainability_score: float = 0.0


@dataclass
class ParserAnalysis:
    """Complete analysis of a parser."""
    file_path: str
    class_name: str
    line_count: int
    method_count: int
    capabilities: ParserCapability
    performance: PerformanceAnalysis
    architecture: ArchitectureAnalysis
    missing_features: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class TCEParserDesignAnalyzer(ast.NodeVisitor):
    """Analyzes TCE parser design quality."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.analysis = ParserAnalysis(
            file_path=file_path,
            class_name="",
            line_count=0,
            method_count=0,
            capabilities=ParserCapability(""),
            performance=PerformanceAnalysis(),
            architecture=ArchitectureAnalysis()
        )
        self.current_class = None
        self.imports = set()
        self.regex_patterns = []
        self.methods = []
        
    def analyze_file(self) -> ParserAnalysis:
        """Analyze the parser file."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
            self.analysis.line_count = len(content.splitlines())
            self.visit(tree)
            
            # Post-analysis processing
            self._analyze_capabilities()
            self._analyze_performance()
            self._analyze_architecture()
            self._generate_recommendations()
            
            return self.analysis
        except SyntaxError:
            return self.analysis
    
    def visit_Import(self, node: ast.Import):
        """Track imports."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from imports."""
        if node.module:
            self.imports.add(node.module)
            for alias in node.names:
                self.imports.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Analyze class definitions."""
        self.current_class = node.name
        self.analysis.class_name = node.name
        
        # Check inheritance
        if node.bases:
            self.analysis.architecture.inheritance_depth = len(node.bases)
            self.analysis.architecture.design_patterns.add(DesignPattern.INHERITANCE)
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze method definitions."""
        self.analysis.method_count += 1
        self.methods.append(node.name)
        
        # Check for regex usage
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                if self._is_regex_call(stmt):
                    self.analysis.performance.regex_patterns_count += 1
                    
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        """Track regex pattern assignments."""
        if isinstance(node.value, ast.Call):
            if self._is_regex_compile(node.value):
                self.regex_patterns.append(node)
                self.analysis.performance.regex_patterns_count += 1
        self.generic_visit(node)
    
    def _is_regex_call(self, node: ast.Call) -> bool:
        """Check if node is a regex-related call."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['match', 'search', 'sub', 'findall', 'finditer']:
                return True
        elif isinstance(node.func, ast.Name):
            if node.func.id in ['re', 'compile']:
                return True
        return False
    
    def _is_regex_compile(self, node: ast.Call) -> bool:
        """Check if node is regex compilation."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == 'compile'
        elif isinstance(node.func, ast.Name):
            return node.func.id == 'compile'
        return False
    
    def _analyze_capabilities(self):
        """Analyze parser capabilities."""
        file_content = Path(self.file_path).read_text()
        
        # Check for specific pattern types
        patterns = {
            'temporal': ['temporal', 'when', 'while', 'during', 'after', 'before'],
            'quantifiers': ['all', 'every', 'some', 'most', 'many', 'few'],
            'conditionals': ['if', 'then', 'conditional', 'whenever'],
            'modals': ['must', 'should', 'may', 'might', 'can', 'could'],
            'comparatives': ['more', 'less', 'greater', 'comparative'],
            'coreference': ['pronoun', 'resolve', 'coreference'],
            'negation': ['not', 'neither', 'nor', 'negation'],
            'semantic': ['semantic', 'lexicon', 'category', 'type']
        }
        
        caps = self.analysis.capabilities
        caps.name = self.analysis.class_name
        
        for capability, keywords in patterns.items():
            if any(kw in file_content.lower() for kw in keywords):
                setattr(caps, f'handles_{capability}', True)
        
        # Check extensibility
        caps.extensible = any(word in file_content for word in ['extend', 'inherit', 'override'])
        caps.user_customizable = any(word in file_content for word in ['user', 'custom', 'dictionary'])
    
    def _analyze_performance(self):
        """Analyze performance characteristics."""
        perf = self.analysis.performance
        
        # Count regex patterns
        perf.regex_patterns_count = len(self.regex_patterns)
        
        # Estimate performance characteristics
        if perf.regex_patterns_count > 20:
            perf.pattern_compilation_cost = 3  # High
            perf.memory_usage_estimate = "high"
            perf.scalability_rating = "poor"
        elif perf.regex_patterns_count > 10:
            perf.pattern_compilation_cost = 2  # Medium
            perf.memory_usage_estimate = "medium"
            perf.scalability_rating = "fair"
        else:
            perf.pattern_compilation_cost = 1  # Low
            perf.memory_usage_estimate = "low"
            perf.scalability_rating = "good"
    
    def _analyze_architecture(self):
        """Analyze architecture quality."""
        arch = self.analysis.architecture
        
        # Detect design patterns
        if 'regex' in str(self.imports) or self.analysis.performance.regex_patterns_count > 5:
            arch.design_patterns.add(DesignPattern.REGEX_HEAVY)
            arch.algorithm_types.add(AlgorithmType.REGEX_BASED)
        
        if any('pattern' in method for method in self.methods):
            arch.design_patterns.add(DesignPattern.STRATEGY)
        
        if any('factory' in method or 'create' in method for method in self.methods):
            arch.design_patterns.add(DesignPattern.FACTORY)
        
        # Check for functional programming
        if len([m for m in self.methods if not m.startswith('_')]) > 0:
            pure_functions = [m for m in self.methods if m.startswith('create_') or m.startswith('build_')]
            if len(pure_functions) > 3:
                arch.design_patterns.add(DesignPattern.FUNCTIONAL)
        
        # Calculate maintainability score
        complexity_penalty = min(self.analysis.performance.regex_patterns_count * 0.1, 1.0)
        method_bonus = min(self.analysis.method_count * 0.05, 0.5)
        arch.maintainability_score = max(0.0, 1.0 - complexity_penalty + method_bonus)
    
    def _generate_recommendations(self):
        """Generate improvement recommendations."""
        recommendations = []
        
        # Performance recommendations
        if self.analysis.performance.regex_patterns_count > 15:
            recommendations.append("Consider replacing regex patterns with AST-based parsing for better performance")
            recommendations.append("Implement pattern compilation caching to reduce startup costs")
        
        # Architecture recommendations
        if DesignPattern.REGEX_HEAVY in self.analysis.architecture.design_patterns:
            recommendations.append("Consider implementing Parser Combinator pattern for more maintainable parsing")
            recommendations.append("Evaluate Recursive Descent parsing for complex grammar rules")
        
        # Capability recommendations
        caps = self.analysis.capabilities
        missing = []
        
        if not caps.handles_temporal:
            missing.append("temporal reasoning")
        if not caps.handles_coreference:
            missing.append("coreference resolution")
        if not caps.handles_semantic_types:
            missing.append("semantic type checking")
        if not caps.handles_negation:
            missing.append("negation handling")
        
        if missing:
            recommendations.append(f"Add support for: {', '.join(missing)}")
        
        # Design pattern recommendations
        if self.analysis.architecture.inheritance_depth > 2:
            recommendations.append("Consider composition over deep inheritance for better flexibility")
        
        if not caps.extensible:
            recommendations.append("Implement plugin architecture for domain-specific extensions")
        
        self.analysis.recommendations = recommendations
        self.analysis.missing_features = missing


def analyze_tce_parsers() -> Dict[str, ParserAnalysis]:
    """Analyze all TCE parsers."""
    project_root = Path(__file__).resolve().parent.parent
    parser_files = [
        project_root / 'backend' / 'unified' / 'tce_parser_v1_01.py',
        project_root / 'backend' / 'unified' / 'tce_parser_v1_51.py',
        project_root / 'backend' / 'unified' / 'tce_parser_semantic.py'
    ]
    
    results = {}
    
    for file_path in parser_files:
        if Path(file_path).exists():
            analyzer = TCEParserDesignAnalyzer(file_path)
            analysis = analyzer.analyze_file()
            results[Path(file_path).stem] = analysis
    
    return results


def generate_comparison_report(analyses: Dict[str, ParserAnalysis]) -> None:
    """Generate comprehensive comparison report."""
    print("=" * 100)
    print("TCE PARSER DESIGN QUALITY ANALYSIS")
    print("=" * 100)
    print()
    
    # Parser Overview
    print("PARSER OVERVIEW:")
    print("-" * 50)
    for name, analysis in analyses.items():
        print(f"\n{name.upper()}:")
        print(f"  Class: {analysis.class_name}")
        print(f"  Lines: {analysis.line_count}")
        print(f"  Methods: {analysis.method_count}")
        print(f"  Inheritance Depth: {analysis.architecture.inheritance_depth}")
    
    # Capability Comparison
    print("\n\nCAPABILITY COMPARISON:")
    print("-" * 50)
    capabilities = [
        'handles_temporal', 'handles_quantifiers', 'handles_conditionals',
        'handles_modals', 'handles_comparatives', 'handles_coreference',
        'handles_negation', 'handles_semantic_types', 'extensible', 'user_customizable'
    ]
    
    print(f"{'Capability':<20}", end="")
    for name in analyses.keys():
        print(f"{name:<15}", end="")
    print()
    print("-" * (20 + 15 * len(analyses)))
    
    for cap in capabilities:
        print(f"{cap.replace('handles_', ''):<20}", end="")
        for analysis in analyses.values():
            value = getattr(analysis.capabilities, cap, False)
            print(f"{'✓' if value else '✗':<15}", end="")
        print()
    
    # Performance Analysis
    print("\n\nPERFORMANCE ANALYSIS:")
    print("-" * 50)
    print(f"{'Metric':<25}", end="")
    for name in analyses.keys():
        print(f"{name:<15}", end="")
    print()
    print("-" * (25 + 15 * len(analyses)))
    
    metrics = ['regex_patterns_count', 'pattern_compilation_cost', 'memory_usage_estimate', 'scalability_rating']
    for metric in metrics:
        print(f"{metric.replace('_', ' ').title():<25}", end="")
        for analysis in analyses.values():
            value = getattr(analysis.performance, metric, 'N/A')
            print(f"{str(value):<15}", end="")
        print()
    
    # Design Patterns
    print("\n\nDESIGN PATTERNS:")
    print("-" * 50)
    for name, analysis in analyses.items():
        print(f"\n{name.upper()}:")
        patterns = [p.value for p in analysis.architecture.design_patterns]
        algorithms = [a.value for a in analysis.architecture.algorithm_types]
        print(f"  Patterns: {', '.join(patterns) if patterns else 'None detected'}")
        print(f"  Algorithms: {', '.join(algorithms) if algorithms else 'None detected'}")
        print(f"  Maintainability: {analysis.architecture.maintainability_score:.2f}")
    
    # Recommendations
    print("\n\nRECOMMENDATIONS:")
    print("-" * 50)
    for name, analysis in analyses.items():
        print(f"\n{name.upper()}:")
        if analysis.recommendations:
            for i, rec in enumerate(analysis.recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  No specific recommendations")
    
    # Best Practices Summary
    print("\n\nBEST PRACTICES ANALYSIS:")
    print("-" * 50)
    
    # Find the most feature-complete parser
    feature_scores = {}
    for name, analysis in analyses.items():
        caps = analysis.capabilities
        score = sum([
            caps.handles_temporal, caps.handles_quantifiers, caps.handles_conditionals,
            caps.handles_modals, caps.handles_comparatives, caps.handles_coreference,
            caps.handles_negation, caps.handles_semantic_types, caps.extensible, caps.user_customizable
        ])
        feature_scores[name] = score
    
    best_features = max(feature_scores, key=feature_scores.get)
    
    # Find the best performance
    perf_scores = {}
    for name, analysis in analyses.items():
        score = 0
        if analysis.performance.scalability_rating == "good": score += 3
        elif analysis.performance.scalability_rating == "fair": score += 2
        else: score += 1
        
        if analysis.performance.pattern_compilation_cost == 1: score += 2
        elif analysis.performance.pattern_compilation_cost == 2: score += 1
        
        perf_scores[name] = score
    
    best_performance = max(perf_scores, key=perf_scores.get)
    
    print(f"Most Feature-Complete: {best_features} ({feature_scores[best_features]}/10 features)")
    print(f"Best Performance: {best_performance}")
    print(f"Best for Production: {best_features if feature_scores[best_features] >= 7 else 'None - needs improvement'}")
    
    # Save detailed analysis
    output_data = {}
    for name, analysis in analyses.items():
        output_data[name] = {
            'file_path': analysis.file_path,
            'class_name': analysis.class_name,
            'metrics': {
                'line_count': analysis.line_count,
                'method_count': analysis.method_count,
                'inheritance_depth': analysis.architecture.inheritance_depth,
                'maintainability_score': analysis.architecture.maintainability_score
            },
            'capabilities': {
                'handles_temporal': analysis.capabilities.handles_temporal,
                'handles_quantifiers': analysis.capabilities.handles_quantifiers,
                'handles_conditionals': analysis.capabilities.handles_conditionals,
                'handles_modals': analysis.capabilities.handles_modals,
                'handles_comparatives': analysis.capabilities.handles_comparatives,
                'handles_coreference': analysis.capabilities.handles_coreference,
                'handles_negation': analysis.capabilities.handles_negation,
                'handles_semantic_types': analysis.capabilities.handles_semantic_types,
                'extensible': analysis.capabilities.extensible,
                'user_customizable': analysis.capabilities.user_customizable
            },
            'performance': {
                'regex_patterns_count': analysis.performance.regex_patterns_count,
                'pattern_compilation_cost': analysis.performance.pattern_compilation_cost,
                'memory_usage_estimate': analysis.performance.memory_usage_estimate,
                'scalability_rating': analysis.performance.scalability_rating
            },
            'design_patterns': [p.value for p in analysis.architecture.design_patterns],
            'algorithm_types': [a.value for a in analysis.architecture.algorithm_types],
            'missing_features': analysis.missing_features,
            'recommendations': analysis.recommendations
        }
    
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / 'tce_parser_design_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nDetailed analysis saved to: {output_path}")


def main():
    """Main entry point."""
    print("Analyzing TCE Parser Design Quality...")
    analyses = analyze_tce_parsers()
    generate_comparison_report(analyses)


if __name__ == '__main__':
    main()