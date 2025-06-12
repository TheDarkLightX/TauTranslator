#!/usr/bin/env python3
"""Quick quality check for refactored code."""

import ast
import os
from pathlib import Path

def analyze_file(filepath):
    """Analyze basic metrics for a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    # Count various elements
    classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    async_functions = sum(1 for node in ast.walk(tree) 
                         if isinstance(node, ast.AsyncFunctionDef))
    lines = len(content.splitlines())
    
    # Count complexity indicators
    if_statements = sum(1 for node in ast.walk(tree) if isinstance(node, ast.If))
    for_loops = sum(1 for node in ast.walk(tree) if isinstance(node, ast.For))
    while_loops = sum(1 for node in ast.walk(tree) if isinstance(node, ast.While))
    try_blocks = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Try))
    
    # Estimate cyclomatic complexity (simplified)
    complexity = if_statements + for_loops + while_loops + try_blocks + 1
    
    return {
        'file': os.path.basename(filepath),
        'lines': lines,
        'classes': classes,
        'functions': functions,
        'async_functions': async_functions,
        'complexity_estimate': complexity,
        'avg_complexity': complexity / max(functions + async_functions, 1)
    }

# Analyze refactored files
files = [
    'backend/unified/translators/pattern_translator.py',
    'backend/unified/translators/manager.py',
    'backend/unified/core/auth.py',
    'backend/unified/core/config.py',
    'backend/unified/core/pattern_loader.py'
]

print("=== Code Quality Summary for Refactored Files ===\n")

total_lines = 0
total_complexity = 0
total_functions = 0

for file in files:
    if os.path.exists(file):
        metrics = analyze_file(file)
        print(f"{metrics['file']}:")
        print(f"  Lines: {metrics['lines']}")
        print(f"  Classes: {metrics['classes']}")
        print(f"  Functions: {metrics['functions']} (async: {metrics['async_functions']})")
        print(f"  Complexity: {metrics['complexity_estimate']} (avg: {metrics['avg_complexity']:.1f})")
        print()
        
        total_lines += metrics['lines']
        total_complexity += metrics['complexity_estimate']
        total_functions += metrics['functions'] + metrics['async_functions']

print(f"Total Lines: {total_lines}")
print(f"Total Functions: {total_functions}")
print(f"Average Complexity per Function: {total_complexity/max(total_functions,1):.1f}")
print(f"\nQuality Assessment: {'GOOD' if total_complexity/max(total_functions,1) < 10 else 'NEEDS IMPROVEMENT'}")