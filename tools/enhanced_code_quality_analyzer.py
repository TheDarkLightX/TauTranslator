#!/usr/bin/env python3
"""
Enhanced Code Quality Analyzer with Shannon Entropy
===================================================

Analyzes code quality metrics including cyclomatic complexity, maintainability index,
test coverage, Shannon entropy, and tracks iterative improvements over time.

Shannon entropy measures the information content and complexity of code:
- Low entropy: repetitive, predictable code (potentially good for consistency)
- High entropy: complex, varied code (potentially harder to understand)
- Optimal range: 3.5 - 5.5 (balanced between simplicity and expressiveness)

Author: DarkLightX/Dana Edwards
"""

import ast
import os
import sys
import json
import math
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import Counter, defaultdict
import hashlib


@dataclass
class QualityMetrics:
    """Container for code quality metrics."""
    file_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    maintainability_index: float
    shannon_entropy: float
    token_diversity: float
    method_count: int
    class_count: int
    max_method_length: int
    average_method_length: float
    test_coverage: Optional[float] = None
    violations: List[str] = None
    timestamp: str = None
    file_hash: str = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-100) including entropy."""
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
        elif self.lines_of_code > 300:
            score -= (self.lines_of_code - 300) * 0.05
        
        # Method length penalties
        if self.max_method_length > 50:
            score -= (self.max_method_length - 50) * 0.5
        
        # Maintainability index bonus/penalty
        if self.maintainability_index < 20:
            score -= 20
        elif self.maintainability_index > 50:
            score += 5
        
        # Shannon entropy scoring (optimal range: 3.5 - 5.5)
        if self.shannon_entropy < 3.0:
            score -= (3.0 - self.shannon_entropy) * 5  # Too simple/repetitive
        elif self.shannon_entropy > 6.0:
            score -= (self.shannon_entropy - 6.0) * 3  # Too complex
        elif 3.5 <= self.shannon_entropy <= 5.5:
            score += 5  # Optimal range bonus
        
        # Token diversity scoring (optimal: 0.3 - 0.7)
        if self.token_diversity < 0.2:
            score -= 10  # Too repetitive
        elif self.token_diversity > 0.8:
            score -= 5   # Too varied
        elif 0.3 <= self.token_diversity <= 0.7:
            score += 3   # Good balance
        
        # Test coverage bonus
        if self.test_coverage and self.test_coverage >= 95:
            score += 10
        elif self.test_coverage and self.test_coverage >= 80:
            score += 5
        
        return max(0, min(100, score))


class ShannonEntropyCalculator:
    """Calculates Shannon entropy and related metrics for code."""
    
    def calculate_entropy(self, content: str) -> Tuple[float, float]:
        """
        Calculate Shannon entropy and token diversity.
        
        Returns:
            (shannon_entropy, token_diversity)
        """
        # Tokenize the content
        tokens = self._tokenize(content)
        if not tokens:
            return 0.0, 0.0
        
        # Calculate token frequencies
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        unique_tokens = len(token_counts)
        
        # Calculate Shannon entropy
        entropy = 0.0
        for count in token_counts.values():
            probability = count / total_tokens
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Calculate token diversity (unique/total ratio)
        diversity = unique_tokens / total_tokens if total_tokens > 0 else 0
        
        return entropy, diversity
    
    def _tokenize(self, content: str) -> List[str]:
        """Tokenize Python code into meaningful tokens."""
        tokens = []
        
        try:
            tree = ast.parse(content)
            
            # Walk the AST and extract tokens
            for node in ast.walk(tree):
                # Extract identifiers
                if isinstance(node, ast.Name):
                    tokens.append(f"ID:{node.id}")
                
                # Extract function calls
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    tokens.append(f"CALL:{node.func.id}")
                
                # Extract operators
                elif isinstance(node, ast.BinOp):
                    tokens.append(f"OP:{type(node.op).__name__}")
                elif isinstance(node, ast.UnaryOp):
                    tokens.append(f"UOP:{type(node.op).__name__}")
                elif isinstance(node, ast.BoolOp):
                    tokens.append(f"BOOL:{type(node.op).__name__}")
                
                # Extract control flow
                elif isinstance(node, ast.If):
                    tokens.append("CTRL:If")
                elif isinstance(node, ast.For):
                    tokens.append("CTRL:For")
                elif isinstance(node, ast.While):
                    tokens.append("CTRL:While")
                elif isinstance(node, ast.Try):
                    tokens.append("CTRL:Try")
                
                # Extract literals
                elif isinstance(node, ast.Constant):
                    if isinstance(node.value, str):
                        tokens.append("LIT:Str")
                    elif isinstance(node.value, (int, float)):
                        tokens.append("LIT:Num")
                    elif isinstance(node.value, bool):
                        tokens.append("LIT:Bool")
                
        except SyntaxError:
            # Fallback to simple word tokenization
            import re
            words = re.findall(r'\b\w+\b', content)
            tokens = [w.lower() for w in words if len(w) > 1]
        
        return tokens


class ImprovementTracker:
    """Tracks code quality improvements over time."""
    
    def __init__(self, db_path: str = "code_quality_history.db"):
        """Initialize the improvement tracker with a database."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for tracking metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                lines_of_code INTEGER,
                cyclomatic_complexity INTEGER,
                cognitive_complexity INTEGER,
                maintainability_index REAL,
                shannon_entropy REAL,
                token_diversity REAL,
                quality_score REAL,
                violations TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_timestamp 
            ON quality_metrics(file_path, timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def record_metrics(self, metrics: QualityMetrics):
        """Record metrics in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quality_metrics (
                file_path, timestamp, file_hash, lines_of_code,
                cyclomatic_complexity, cognitive_complexity,
                maintainability_index, shannon_entropy, token_diversity,
                quality_score, violations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.file_path,
            metrics.timestamp,
            metrics.file_hash,
            metrics.lines_of_code,
            metrics.cyclomatic_complexity,
            metrics.cognitive_complexity,
            metrics.maintainability_index,
            metrics.shannon_entropy,
            metrics.token_diversity,
            metrics.quality_score,
            json.dumps(metrics.violations)
        ))
        
        conn.commit()
        conn.close()
    
    def get_improvement_report(self, file_path: str) -> Dict[str, Any]:
        """Get improvement report for a specific file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, lines_of_code, cyclomatic_complexity,
                   cognitive_complexity, maintainability_index,
                   shannon_entropy, token_diversity, quality_score
            FROM quality_metrics
            WHERE file_path = ?
            ORDER BY timestamp
        ''', (file_path,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 2:
            return {"status": "insufficient_data"}
        
        # Calculate improvements
        first = rows[0]
        last = rows[-1]
        
        improvements = {
            "file_path": file_path,
            "iterations": len(rows),
            "first_timestamp": first[0],
            "last_timestamp": last[0],
            "improvements": {
                "quality_score": {
                    "initial": first[7],
                    "current": last[7],
                    "change": last[7] - first[7],
                    "improved": last[7] > first[7]
                },
                "cyclomatic_complexity": {
                    "initial": first[2],
                    "current": last[2],
                    "change": last[2] - first[2],
                    "improved": last[2] <= first[2]  # Lower is better
                },
                "shannon_entropy": {
                    "initial": first[5],
                    "current": last[5],
                    "change": last[5] - first[5],
                    "optimal_distance": abs(last[5] - 4.5) - abs(first[5] - 4.5)
                },
                "maintainability_index": {
                    "initial": first[4],
                    "current": last[4],
                    "change": last[4] - first[4],
                    "improved": last[4] > first[4]
                }
            },
            "trend": self._calculate_trend(rows)
        }
        
        return improvements
    
    def _calculate_trend(self, rows: List[Tuple]) -> str:
        """Calculate overall trend (improving/declining/stable)."""
        if len(rows) < 3:
            return "insufficient_data"
        
        # Get quality scores
        scores = [row[7] for row in rows]
        
        # Calculate linear regression slope
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = sum(scores) / n
        
        numerator = sum((i - x_mean) * (score - y_mean) for i, score in enumerate(scores))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.5:
            return "improving"
        elif slope < -0.5:
            return "declining"
        else:
            return "stable"


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


class EnhancedCodeQualityAnalyzer:
    """Enhanced code quality analyzer with entropy and tracking."""
    
    def __init__(self, track_improvements: bool = True):
        self.metrics = {}
        self.entropy_calculator = ShannonEntropyCalculator()
        self.tracker = ImprovementTracker() if track_improvements else None
        
    def analyze_file(self, file_path: str) -> QualityMetrics:
        """Analyze a single Python file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Calculate file hash for tracking changes
        file_hash = hashlib.md5(content.encode()).hexdigest()
            
        # Parse AST
        tree = ast.parse(content)
        
        # Calculate basic metrics
        lines = content.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Calculate complexity
        complexity_calc = ComplexityCalculator()
        complexity_calc.visit(tree)
        
        # Calculate Shannon entropy
        shannon_entropy, token_diversity = self.entropy_calculator.calculate_entropy(content)
        
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
        import math
        volume = loc * math.log2(method_count + 1) if method_count > 0 else 1
        maintainability = 171 - 5.2 * math.log(volume) - 0.23 * complexity_calc.cyclomatic - 16.2 * math.log(loc)
        maintainability = max(0, min(100, maintainability))
        
        # Check for violations
        violations = self._check_violations(tree, content, loc, complexity_calc, shannon_entropy)
        
        metrics = QualityMetrics(
            file_path=file_path,
            lines_of_code=loc,
            cyclomatic_complexity=complexity_calc.cyclomatic,
            cognitive_complexity=complexity_calc.cognitive,
            maintainability_index=maintainability,
            shannon_entropy=shannon_entropy,
            token_diversity=token_diversity,
            method_count=method_count,
            class_count=class_count,
            max_method_length=max_method_length,
            average_method_length=avg_method_length,
            violations=violations,
            file_hash=file_hash
        )
        
        # Track metrics if enabled
        if self.tracker:
            self.tracker.record_metrics(metrics)
        
        return metrics
    
    def _check_violations(self, tree: ast.AST, content: str, loc: int, 
                         complexity: ComplexityCalculator, entropy: float) -> List[str]:
        """Check for clean code violations including entropy."""
        violations = []
        
        # File size check
        if loc > 600:
            violations.append(f"File exceeds 600 lines ({loc} lines)")
        elif loc > 300:
            violations.append(f"File exceeds 300 lines ({loc} lines) - consider splitting")
            
        # Complexity checks
        if complexity.cyclomatic > 10:
            violations.append(f"Cyclomatic complexity too high ({complexity.cyclomatic} > 10)")
            
        if complexity.cognitive > 15:
            violations.append(f"Cognitive complexity too high ({complexity.cognitive} > 15)")
            
        # Entropy checks
        if entropy < 3.0:
            violations.append(f"Shannon entropy too low ({entropy:.2f} < 3.0) - code may be too repetitive")
        elif entropy > 6.0:
            violations.append(f"Shannon entropy too high ({entropy:.2f} > 6.0) - code may be too complex")
        
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
        """Generate a comprehensive quality report with entropy analysis."""
        total_files = len(results)
        total_loc = sum(m.lines_of_code for m in results.values())
        avg_complexity = sum(m.cyclomatic_complexity for m in results.values()) / total_files if total_files > 0 else 0
        avg_entropy = sum(m.shannon_entropy for m in results.values()) / total_files if total_files > 0 else 0
        avg_quality = sum(m.quality_score for m in results.values()) / total_files if total_files > 0 else 0
        
        # Find problem files
        problem_files = [
            (path, metrics) for path, metrics in results.items() 
            if metrics.quality_score < 70 or len(metrics.violations) > 3
        ]
        
        # Sort by quality score
        problem_files.sort(key=lambda x: x[1].quality_score)
        
        # Entropy distribution
        entropy_buckets = defaultdict(int)
        for metrics in results.values():
            bucket = int(metrics.shannon_entropy)
            entropy_buckets[bucket] += 1
        
        return {
            'summary': {
                'total_files': total_files,
                'total_lines': total_loc,
                'average_complexity': round(avg_complexity, 2),
                'average_entropy': round(avg_entropy, 2),
                'average_quality_score': round(avg_quality, 2),
                'problem_files_count': len(problem_files),
                'entropy_distribution': dict(entropy_buckets)
            },
            'problem_files': [
                {
                    'path': path,
                    'quality_score': metrics.quality_score,
                    'shannon_entropy': round(metrics.shannon_entropy, 2),
                    'violations': metrics.violations,
                    'metrics': asdict(metrics)
                }
                for path, metrics in problem_files[:10]  # Top 10 problem files
            ],
            'all_results': {
                path: asdict(metrics) for path, metrics in results.items()
            }
        }
    
    def get_improvement_summary(self, directory: str) -> Dict[str, Any]:
        """Get improvement summary for all files in directory."""
        if not self.tracker:
            return {"error": "Improvement tracking not enabled"}
        
        improvements = {}
        for file_path in Path(directory).rglob("*.py"):
            if '__pycache__' in str(file_path):
                continue
            
            report = self.tracker.get_improvement_report(str(file_path))
            if report.get("status") != "insufficient_data":
                improvements[str(file_path)] = report
        
        # Calculate overall statistics
        total_improved = sum(1 for r in improvements.values() 
                           if r['improvements']['quality_score']['improved'])
        total_declined = sum(1 for r in improvements.values() 
                           if not r['improvements']['quality_score']['improved'])
        
        return {
            'total_tracked_files': len(improvements),
            'improved_files': total_improved,
            'declined_files': total_declined,
            'file_improvements': improvements
        }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_code_quality_analyzer.py <file_or_directory> [--show-improvements]")
        sys.exit(1)
        
    target = sys.argv[1]
    show_improvements = "--show-improvements" in sys.argv
    
    analyzer = EnhancedCodeQualityAnalyzer()
    
    if os.path.isfile(target):
        # Analyze single file
        metrics = analyzer.analyze_file(target)
        print(f"\nQuality Analysis for {target}")
        print("=" * 60)
        print(f"Lines of Code: {metrics.lines_of_code}")
        print(f"Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
        print(f"Cognitive Complexity: {metrics.cognitive_complexity}")
        print(f"Maintainability Index: {metrics.maintainability_index:.2f}")
        print(f"Shannon Entropy: {metrics.shannon_entropy:.2f}")
        print(f"Token Diversity: {metrics.token_diversity:.2f}")
        print(f"Quality Score: {metrics.quality_score:.2f}/100")
        
        if metrics.violations:
            print("\nViolations:")
            for violation in metrics.violations:
                print(f"  - {violation}")
        
        # Show improvement history if requested
        if show_improvements and analyzer.tracker:
            report = analyzer.tracker.get_improvement_report(target)
            if report.get("status") != "insufficient_data":
                print(f"\nImprovement History ({report['iterations']} iterations):")
                for metric, data in report['improvements'].items():
                    if isinstance(data, dict) and 'change' in data:
                        symbol = "↑" if data.get('improved', data['change'] > 0) else "↓"
                        print(f"  {metric}: {data['initial']:.2f} → {data['current']:.2f} "
                              f"({symbol} {abs(data['change']):.2f})")
                print(f"  Overall trend: {report['trend']}")
    else:
        # Analyze directory
        results = analyzer.analyze_directory(target)
        report = analyzer.generate_report(results)
        
        # Save report
        report_file = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\nQuality Analysis Report")
        print("=" * 60)
        print(f"Total Files: {report['summary']['total_files']}")
        print(f"Total Lines: {report['summary']['total_lines']}")
        print(f"Average Complexity: {report['summary']['average_complexity']}")
        print(f"Average Shannon Entropy: {report['summary']['average_entropy']}")
        print(f"Average Quality Score: {report['summary']['average_quality_score']}/100")
        print(f"Problem Files: {report['summary']['problem_files_count']}")
        
        print("\nEntropy Distribution:")
        for bucket, count in sorted(report['summary']['entropy_distribution'].items()):
            print(f"  {bucket}.0-{bucket}.9: {'█' * count} ({count} files)")
        
        if report['problem_files']:
            print("\nTop Problem Files:")
            for pf in report['problem_files'][:5]:
                print(f"\n  {pf['path']} (Score: {pf['quality_score']:.2f}, Entropy: {pf['shannon_entropy']})")
                for violation in pf['violations'][:3]:
                    print(f"    - {violation}")
        
        print(f"\nFull report saved to: {report_file}")
        
        # Show improvement summary if requested
        if show_improvements:
            improvements = analyzer.get_improvement_summary(target)
            if improvements.get('total_tracked_files', 0) > 0:
                print(f"\nImprovement Summary:")
                print(f"  Files with history: {improvements['total_tracked_files']}")
                print(f"  Improved: {improvements['improved_files']}")
                print(f"  Declined: {improvements['declined_files']}")


if __name__ == '__main__':
    main()