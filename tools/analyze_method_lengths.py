#!/usr/bin/env python3
"""
Analyze method lengths in a Python file.

Author: DarkLightX/Dana Edwards
"""

import ast
import sys
from typing import List, Dict, Any


class MethodAnalyzer(ast.NodeVisitor):
    """Analyze method lengths and complexity."""
    
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.methods = []
        
    def visit_FunctionDef(self, node):
        # Calculate method length
        start_line = node.lineno - 1  # 0-indexed
        end_line = node.end_lineno - 1 if hasattr(node, 'end_lineno') else start_line
        
        # Get method body (excluding decorators and signature)
        body_start = start_line
        for i in range(start_line, min(end_line + 1, len(self.lines))):
            if self.lines[i].strip().endswith(':'):
                body_start = i + 1
                break
        
        # Count non-empty, non-comment lines in body
        body_lines = []
        for i in range(body_start, end_line + 1):
            line = self.lines[i].strip()
            if line and not line.startswith('#'):
                body_lines.append((i + 1, self.lines[i]))
        
        self.methods.append({
            'name': node.name,
            'start_line': node.lineno,
            'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            'body_lines': len(body_lines),
            'total_lines': end_line - start_line + 1,
            'body_content': body_lines
        })
        
        self.generic_visit(node)


def analyze_file(file_path: str):
    """Analyze method lengths in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    tree = ast.parse(content)
    analyzer = MethodAnalyzer(lines)
    analyzer.visit(tree)
    
    print(f"\nMethod Length Analysis for {file_path}")
    print("=" * 80)
    
    methods_over_10 = []
    
    for method in analyzer.methods:
        status = "❌" if method['body_lines'] > 10 else "✅"
        print(f"\n{status} {method['name']} (lines {method['start_line']}-{method['end_line']})")
        print(f"   Body lines: {method['body_lines']} | Total lines: {method['total_lines']}")
        
        if method['body_lines'] > 10:
            methods_over_10.append(method)
            print("   First 5 body lines:")
            for line_no, line in method['body_content'][:5]:
                print(f"   {line_no}: {line}")
            if len(method['body_content']) > 5:
                print(f"   ... ({len(method['body_content']) - 5} more lines)")
    
    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"Total methods: {len(analyzer.methods)}")
    print(f"Methods over 10 lines: {len(methods_over_10)}")
    
    if methods_over_10:
        print("\nMethods needing refactoring:")
        for method in sorted(methods_over_10, key=lambda m: m['body_lines'], reverse=True):
            print(f"  - {method['name']}: {method['body_lines']} lines")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_method_lengths.py <file_path>")
        sys.exit(1)
    
    analyze_file(sys.argv[1])