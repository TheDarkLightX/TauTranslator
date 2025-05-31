#!/usr/bin/env python3
"""
Advanced Development Tools for TauTranslator
===========================================

Comprehensive toolkit for code analysis, profiling, and debugging.
Following VibeArchitect principles for production-ready development.
"""

import subprocess
import sys
import json
import time
import cProfile
import pstats
import io
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import os


class CodeAnalyzer:
    """Advanced code analysis using multiple tools."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {}
    
    def run_all_analysis(self) -> Dict[str, Any]:
        """Run comprehensive code analysis."""
        print("🔍 Running comprehensive code analysis...")
        
        analyses = [
            ("complexity", self.analyze_complexity),
            ("security", self.analyze_security),
            ("quality", self.analyze_quality),
            ("dead_code", self.find_dead_code),
            ("documentation", self.check_documentation),
            ("performance", self.analyze_performance_patterns),
        ]
        
        for name, analyzer in analyses:
            print(f"   Running {name} analysis...")
            try:
                self.results[name] = analyzer()
                print(f"   ✓ {name} completed")
            except Exception as e:
                print(f"   ✗ {name} failed: {e}")
                self.results[name] = {"error": str(e)}
        
        return self.results
    
    def analyze_complexity(self) -> Dict[str, Any]:
        """Analyze cyclomatic complexity using radon."""
        try:
            cmd = [
                sys.executable, "-m", "radon", "cc", 
                str(self.project_root), "-j", "--min", "B"
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                if result.stdout.strip():
                    complexity_data = json.loads(result.stdout)
                else:
                    complexity_data = {}
                
                # Calculate summary stats
                total_functions = 0
                total_complexity = 0
                high_complexity = []
                
                for file_path, data in complexity_data.items():
                    if isinstance(data, list):
                        for item in data:
                            if item.get('type') == 'function':
                                total_functions += 1
                                complexity = item.get('complexity', 0)
                                total_complexity += complexity
                                
                                # VibeArchitect threshold
                                if complexity > 10:  
                                    high_complexity.append({
                                        'file': file_path,
                                        'function': item.get('name'),
                                        'complexity': complexity,
                                        'line': item.get('lineno')
                                    })
                
                if total_functions > 0:
                    avg_complexity = total_complexity / total_functions
                else:
                    avg_complexity = 0
                
                return {
                    "total_functions": total_functions,
                    "average_complexity": round(avg_complexity, 2),
                    "high_complexity_functions": high_complexity,
                    "complexity_threshold_violations": len(high_complexity),
                    "raw_data": complexity_data
                }
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_security(self) -> Dict[str, Any]:
        """Security analysis using bandit."""
        try:
            cmd = [
                sys.executable, "-m", "bandit", "-r", 
                str(self.project_root), "-x", 
                str(self.project_root / "venv"), "-f", "json"
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            
            if result.stdout.strip():
                security_data = json.loads(result.stdout)
                
                issues_by_severity = {}
                for result_item in security_data.get('results', []):
                    severity = result_item.get('issue_severity', 'UNKNOWN')
                    if severity not in issues_by_severity:
                        issues_by_severity[severity] = []
                    issues_by_severity[severity].append(result_item)
                
                severity_counts = {
                    k: len(v) for k, v in issues_by_severity.items()
                }
                
                return {
                    "total_issues": len(security_data.get('results', [])),
                    "issues_by_severity": severity_counts,
                    "high_severity_issues": len(issues_by_severity.get('HIGH', [])),
                    "medium_severity_issues": len(issues_by_severity.get('MEDIUM', [])),
                    "detailed_issues": issues_by_severity,
                    "metrics": security_data.get('metrics', {})
                }
            else:
                return {"total_issues": 0, "message": "No security issues found"}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_quality(self) -> Dict[str, Any]:
        """Code quality analysis using multiple tools."""
        quality_results = {}
        
        # Flake8 analysis
        try:
            result = subprocess.run([
                sys.executable, "-m", "flake8", str(self.project_root),
                "--exclude=venv,__pycache__", "--format=json"
            ], capture_output=True, text=True, timeout=30)
            
            # Flake8 doesn't output JSON by default, parse manually
            flake8_issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 4:
                            flake8_issues.append({
                                'file': parts[0],
                                'line': parts[1],
                                'column': parts[2],
                                'message': ':'.join(parts[3:]).strip()
                            })
            
            quality_results['flake8'] = {
                'total_issues': len(flake8_issues),
                'issues': flake8_issues
            }
        except Exception as e:
            quality_results['flake8'] = {"error": str(e)}
        
        # MyPy analysis
        try:
            result = subprocess.run([
                sys.executable, "-m", "mypy", str(self.project_root),
                "--ignore-missing-imports", "--json-report", "/tmp/mypy_report"
            ], capture_output=True, text=True, timeout=60)
            
            # MyPy outputs to stderr normally
            mypy_issues = []
            if result.stdout or result.stderr:
                output = result.stdout + result.stderr
                for line in output.split('\n'):
                    if ':' in line and ('error:' in line or 'warning:' in line):
                        mypy_issues.append(line.strip())
            
            quality_results['mypy'] = {
                'total_issues': len(mypy_issues),
                'issues': mypy_issues
            }
        except Exception as e:
            quality_results['mypy'] = {"error": str(e)}
        
        return quality_results
    
    def find_dead_code(self) -> Dict[str, Any]:
        """Find dead code using vulture."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "vulture", str(self.project_root),
                "--exclude=venv,__pycache__,tests", "--min-confidence", "80"
            ], capture_output=True, text=True, timeout=30)
            
            dead_code_items = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        dead_code_items.append(line.strip())
            
            return {
                "dead_code_items": len(dead_code_items),
                "items": dead_code_items,
                "confidence_threshold": 80
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_documentation(self) -> Dict[str, Any]:
        """Check documentation using pydocstyle."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pydocstyle", str(self.project_root),
                "--match-dir", "^(?!venv|__pycache__|tests).*"
            ], capture_output=True, text=True, timeout=30)
            
            doc_issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        doc_issues.append(line.strip())
            
            return {
                "documentation_issues": len(doc_issues),
                "issues": doc_issues
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_performance_patterns(self) -> Dict[str, Any]:
        """Analyze code for performance anti-patterns."""
        performance_issues = []
        
        # Scan for common performance anti-patterns
        patterns = {
            "nested_loops": r"for.*:\s*for",
            "string_concatenation": r"\+=.*str",
            "repeated_function_calls": r"len\([^)]+\)\s*in.*for",
            "inefficient_membership": r"in\s+\[.*\]",
        }
        
        import re
        
        for python_file in self.project_root.rglob("*.py"):
            if "venv" in str(python_file) or "__pycache__" in str(python_file):
                continue
            
            try:
                content = python_file.read_text()
                for pattern_name, pattern in patterns.items():
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        performance_issues.append({
                            'file': str(python_file.relative_to(self.project_root)),
                            'line': line_num,
                            'pattern': pattern_name,
                            'code': match.group().strip()
                        })
            except Exception:
                continue
        
        return {
            "performance_issues": len(performance_issues),
            "issues": performance_issues
        }


class PerformanceProfiler:
    """Advanced performance profiling tools."""
    
    def __init__(self):
        self.profiler = None
        self.profile_data = None
    
    def profile_function(self, func, *args, **kwargs):
        """Profile a specific function call."""
        print(f"🔬 Profiling function: {func.__name__}")
        
        # cProfile profiling
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        profiler.disable()
        
        # Capture profile stats
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        profile_output = stats_stream.getvalue()
        
        return {
            'result': result,
            'execution_time': end_time - start_time,
            'profile_stats': profile_output,
            'profiler': profiler
        }
    
    def memory_profile_function(self, func, *args, **kwargs):
        """Profile memory usage of a function."""
        try:
            from memory_profiler import profile as memory_profile
            import tracemalloc
            
            # Start memory tracing
            tracemalloc.start()
            
            # Run function
            result = func(*args, **kwargs)
            
            # Get memory stats
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return {
                'result': result,
                'current_memory_mb': current / 1024 / 1024,
                'peak_memory_mb': peak / 1024 / 1024
            }
        except ImportError:
            return {'error': 'memory_profiler not available'}
    
    def line_profile_function(self, func, *args, **kwargs):
        """Line-by-line profiling using line_profiler."""
        try:
            from line_profiler import LineProfiler
            
            profiler = LineProfiler()
            profiler.add_function(func)
            profiler.enable_by_count()
            
            result = func(*args, **kwargs)
            
            profiler.disable_by_count()
            
            # Capture line profile output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                profiler.print_stats(stream=f)
                temp_file = f.name
            
            with open(temp_file, 'r') as f:
                line_profile_output = f.read()
            
            os.unlink(temp_file)
            
            return {
                'result': result,
                'line_profile': line_profile_output
            }
        except ImportError:
            return {'error': 'line_profiler not available'}


class CodeInspector:
    """Advanced code inspection and analysis."""
    
    @staticmethod
    def inspect_ast(code: str) -> Dict[str, Any]:
        """Analyze code AST for patterns."""
        import ast
        
        try:
            tree = ast.parse(code)
            
            visitor = ASTAnalyzer()
            visitor.visit(tree)
            
            return visitor.get_analysis()
        except SyntaxError as e:
            return {'error': f'Syntax error: {e}'}
    
    @staticmethod
    def find_code_smells(file_path: Path) -> List[Dict[str, Any]]:
        """Find code smells in a Python file."""
        smells = []
        
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Long line smell
                if len(line) > 120:
                    smells.append({
                        'type': 'long_line',
                        'line': i,
                        'length': len(line),
                        'description': f'Line exceeds 120 characters ({len(line)} chars)'
                    })
                
                # TODO/FIXME smell
                if 'TODO' in line or 'FIXME' in line:
                    smells.append({
                        'type': 'todo_fixme',
                        'line': i,
                        'description': 'TODO/FIXME comment found'
                    })
                
                # Magic number smell
                magic_numbers = re.findall(r'\b\d{3,}\b', line)
                for number in magic_numbers:
                    if number not in ['1000', '1024']:  # Common acceptable numbers
                        smells.append({
                            'type': 'magic_number',
                            'line': i,
                            'number': number,
                            'description': f'Magic number {number} should be a named constant'
                        })
        
        except Exception as e:
            smells.append({
                'type': 'analysis_error',
                'description': str(e)
            })
        
        return smells


class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor for code analysis."""
    
    def __init__(self):
        self.stats = {
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'complexity': 0,
            'max_nesting': 0,
            'current_nesting': 0
        }
    
    def visit_FunctionDef(self, node):
        self.stats['functions'] += 1
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.stats['classes'] += 1
        self.generic_visit(node)
    
    def visit_Import(self, node):
        self.stats['imports'] += 1
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        self.stats['imports'] += 1
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.stats['complexity'] += 1
        self._enter_nested()
        self.generic_visit(node)
        self._exit_nested()
    
    def visit_For(self, node):
        self.stats['complexity'] += 1
        self._enter_nested()
        self.generic_visit(node)
        self._exit_nested()
    
    def visit_While(self, node):
        self.stats['complexity'] += 1
        self._enter_nested()
        self.generic_visit(node)
        self._exit_nested()
    
    def _enter_nested(self):
        self.stats['current_nesting'] += 1
        self.stats['max_nesting'] = max(
            self.stats['max_nesting'], 
            self.stats['current_nesting']
        )
    
    def _exit_nested(self):
        self.stats['current_nesting'] -= 1
    
    def get_analysis(self):
        return self.stats


def main():
    """Main function to run development tools."""
    project_root = Path(__file__).parent
    
    print("🛠️  TauTranslator Development Tools")
    print("=" * 60)
    
    # Code Analysis
    analyzer = CodeAnalyzer(project_root)
    analysis_results = analyzer.run_all_analysis()
    
    # Generate report
    print("\n📊 Analysis Summary:")
    print("-" * 40)
    
    for analysis_name, results in analysis_results.items():
        if 'error' not in results:
            if analysis_name == 'complexity':
                print(f"Complexity: {results.get('average_complexity', 'N/A')} avg, "
                      f"{results.get('complexity_threshold_violations', 0)} violations")
            elif analysis_name == 'security':
                print(f"Security: {results.get('total_issues', 0)} issues, "
                      f"{results.get('high_severity_issues', 0)} high severity")
            elif analysis_name == 'dead_code':
                print(f"Dead Code: {results.get('dead_code_items', 0)} items")
            elif analysis_name == 'documentation':
                print(f"Documentation: {results.get('documentation_issues', 0)} issues")
            elif analysis_name == 'performance':
                print(f"Performance: {results.get('performance_issues', 0)} potential issues")
        else:
            print(f"{analysis_name}: Error - {results['error']}")
    
    # Save detailed results
    results_file = project_root / "code_analysis_results.json"
    with open(results_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Performance profiling example
    print("\n🔬 Performance Profiling Available:")
    print("   - Use PerformanceProfiler.profile_function()")
    print("   - Use PerformanceProfiler.memory_profile_function()")
    print("   - Use PerformanceProfiler.line_profile_function()")
    
    print("\n🔍 Code Inspection Available:")
    print("   - Use CodeInspector.inspect_ast()")
    print("   - Use CodeInspector.find_code_smells()")


if __name__ == "__main__":
    main()