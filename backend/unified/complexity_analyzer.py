"""
Code Complexity Analyzer - Measures cyclomatic complexity, cognitive complexity, and entropy.

Copyright: DarkLightX / Dana Edwards
"""

import ast
import math
from typing import Dict, List, Tuple
from pathlib import Path
from collections import Counter


class ComplexityAnalyzer(ast.NodeVisitor):
    """Analyzes Python code complexity."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset analyzer state."""
        self.cyclomatic = 1  # Base complexity
        self.cognitive = 0
        self.nesting_level = 0
        self.methods = []
        self.current_method = None
        self.current_method_lines = 0
        self.tokens = []
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a Python file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        self.reset()
        self.visit(tree)
        
        # Calculate Shannon entropy
        token_counts = Counter(self.tokens)
        total_tokens = len(self.tokens)
        entropy = -sum((count/total_tokens) * math.log2(count/total_tokens) 
                      for count in token_counts.values())
        
        return {
            'file': file_path.name,
            'cyclomatic_complexity': self.cyclomatic,
            'cognitive_complexity': self.cognitive,
            'shannon_entropy': entropy,
            'total_lines': content.count('\n') + 1,
            'total_tokens': total_tokens,
            'methods': self.methods,
            'avg_method_length': sum(m['lines'] for m in self.methods) / max(len(self.methods), 1)
        }
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        # Save previous method context
        prev_method = self.current_method
        prev_lines = self.current_method_lines
        prev_cognitive = self.cognitive
        
        # Start new method analysis
        self.current_method = node.name
        self.current_method_lines = node.end_lineno - node.lineno + 1
        self.cognitive = 0
        method_cyclomatic = 1
        
        # Analyze method body
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, 
                                ast.Try, ast.ExceptHandler)):
                method_cyclomatic += 1
            elif isinstance(child, (ast.BoolOp, ast.Compare)):
                method_cyclomatic += len(child.ops) if hasattr(child, 'ops') else 1
        
        # Record method info
        self.methods.append({
            'name': node.name,
            'lines': self.current_method_lines,
            'cyclomatic': method_cyclomatic,
            'cognitive': self.cognitive
        })
        
        # Update total complexity
        self.cyclomatic += method_cyclomatic - 1
        
        # Continue visiting
        self.generic_visit(node)
        
        # Restore previous context
        self.current_method = prev_method
        self.current_method_lines = prev_lines
        self.cognitive = prev_cognitive
    
    def visit_If(self, node):
        """Visit if statement."""
        self.cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_While(self, node):
        """Visit while loop."""
        self.cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_For(self, node):
        """Visit for loop."""
        self.cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_Try(self, node):
        """Visit try statement."""
        self.cognitive += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        """Visit except handler."""
        self.cognitive += 1 + self.nesting_level
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        """Visit boolean operation."""
        self.cognitive += len(node.values) - 1
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Collect tokens for entropy calculation."""
        self.tokens.append(node.id)
        self.generic_visit(node)
    
    def visit_Constant(self, node):
        """Collect constant tokens."""
        self.tokens.append(str(node.value))
        self.generic_visit(node)


def analyze_parser_files():
    """Analyze all parser files."""
    base_path = Path(__file__).resolve().parent
    parser_files = [
        "tce_parser_v1_01.py",
        "tce_parser_v1_51.py", 
        "tce_parser_semantic.py",
        "tce_parser_enhanced.py"
    ]
    
    analyzer = ComplexityAnalyzer()
    results = []
    
    for file_name in parser_files:
        file_path = base_path / file_name
        if file_path.exists():
            result = analyzer.analyze_file(file_path)
            results.append(result)
    
    return results


def print_analysis(results: List[Dict]):
    """Print complexity analysis results."""
    print("🔍 CODE COMPLEXITY ANALYSIS")
    print("=" * 80)
    
    for result in results:
        print(f"\n📁 {result['file']}")
        print(f"   Cyclomatic Complexity: {result['cyclomatic_complexity']:.1f}")
        print(f"   Cognitive Complexity:  {result['cognitive_complexity']:.1f}")
        print(f"   Shannon Entropy:       {result['shannon_entropy']:.2f}")
        print(f"   Lines of Code:         {result['total_lines']}")
        print(f"   Average Method Length: {result['avg_method_length']:.1f}")
        
        # Show worst methods
        if result['methods']:
            worst_methods = sorted(result['methods'], 
                                 key=lambda m: m['lines'], reverse=True)[:3]
            print(f"   Longest Methods:")
            for method in worst_methods:
                print(f"     • {method['name']}: {method['lines']} lines, "
                      f"CC={method['cyclomatic']}")
    
    # Summary
    print(f"\n📊 SUMMARY")
    print(f"   Total Files: {len(results)}")
    avg_cyclomatic = sum(r['cyclomatic_complexity'] for r in results) / len(results)
    avg_cognitive = sum(r['cognitive_complexity'] for r in results) / len(results)
    avg_entropy = sum(r['shannon_entropy'] for r in results) / len(results)
    print(f"   Average Cyclomatic: {avg_cyclomatic:.1f}")
    print(f"   Average Cognitive:  {avg_cognitive:.1f}")
    print(f"   Average Entropy:    {avg_entropy:.2f}")


if __name__ == "__main__":
    results = analyze_parser_files()
    print_analysis(results)