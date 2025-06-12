#!/usr/bin/env python3
"""
Pre-commit checks for Craftsmanship Principles.
Runs quick checks to ensure code follows the Intentional Disclosure Principle.

Copyright: DarkLightX/Dana Edwards
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List, Tuple


class CraftsmanshipChecker:
    """Quick checks for craftsmanship principles."""
    
    def __init__(self):
        self.violations = []
    
    def check_async_naming(self, files: List[str]) -> bool:
        """Rule 1: Check async methods end with _async."""
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.AsyncFunctionDef):
                        # Skip private methods and dunder methods
                        if node.name.startswith('_') or node.name.startswith('__'):
                            continue
                        
                        # Skip FastAPI route handlers (they're special)
                        is_route = self._is_fastapi_route(node)
                        if is_route:
                            continue
                        
                        if not node.name.endswith('_async'):
                            self.violations.append(
                                f"{file_path}:{node.lineno} - "
                                f"Async method '{node.name}' should end with '_async'"
                            )
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return len(self.violations) == 0
    
    def _is_fastapi_route(self, node: ast.AsyncFunctionDef) -> bool:
        """Check if function is a FastAPI route handler."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                # Check for @router.get, @router.post, etc.
                if hasattr(decorator.value, 'id') and decorator.value.id == 'router':
                    return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if hasattr(decorator.func.value, 'id') and decorator.func.value.id == 'router':
                        return True
        return False
    
    def check_method_complexity(self, files: List[str]) -> bool:
        """Rule 2: Check method complexity and length."""
        max_complexity = 10
        max_length = 50
        
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Calculate complexity
                        complexity = self._calculate_complexity(node)
                        if complexity > max_complexity:
                            self.violations.append(
                                f"{file_path}:{node.lineno} - "
                                f"Method '{node.name}' has complexity {complexity} (max: {max_complexity})"
                            )
                        
                        # Check length
                        if hasattr(node, 'end_lineno'):
                            length = node.end_lineno - node.lineno
                            if length > max_length:
                                self.violations.append(
                                    f"{file_path}:{node.lineno} - "
                                    f"Method '{node.name}' is {length} lines (max: {max_length})"
                                )
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return len(self.violations) == 0
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Simple cyclomatic complexity calculation."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def check_type_coverage(self, files: List[str]) -> bool:
        """Rule 3: Check type annotation coverage."""
        min_coverage = 0.7  # 70% minimum
        
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    tree = ast.parse(f.read())
                
                total_params = 0
                annotated_params = 0
                total_functions = 0
                annotated_returns = 0
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Skip __init__ for return type
                        if node.name != '__init__':
                            total_functions += 1
                            if node.returns:
                                annotated_returns += 1
                        
                        for arg in node.args.args:
                            if arg.arg != 'self' and arg.arg != 'cls':
                                total_params += 1
                                if arg.annotation:
                                    annotated_params += 1
                
                if total_params > 0:
                    param_coverage = annotated_params / total_params
                    if param_coverage < min_coverage:
                        self.violations.append(
                            f"{file_path} - Type annotation coverage {param_coverage:.1%} "
                            f"(min: {min_coverage:.0%})"
                        )
                
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return len(self.violations) == 0
    
    def check_layer_violations(self, files: List[str]) -> bool:
        """Rule 4: Check for I/O operations in core layer."""
        io_patterns = [
            'open(', 'with open',
            'json.load', 'json.dump',
            'yaml.load', 'yaml.dump',
            'requests.', 'urllib.',
            'redis.', 'sqlite3.', 'psycopg2.',
            'asyncio.to_thread', 'asyncio.run',
            'subprocess.', 'os.system'
        ]
        
        for file_path in files:
            # Skip allowed files
            if any(skip in file_path for skip in ['interfaces.py', 'domain_types.py', '_refactored.py']):
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                for pattern in io_patterns:
                    if pattern in content:
                        # Find line number
                        lines = content.splitlines()
                        for i, line in enumerate(lines, 1):
                            if pattern in line:
                                self.violations.append(
                                    f"{file_path}:{i} - "
                                    f"I/O operation '{pattern}' found in core layer"
                                )
                                break
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return len(self.violations) == 0
    
    def print_violations(self):
        """Print all violations found."""
        if self.violations:
            print("\n❌ Craftsmanship violations found:\n")
            for violation in self.violations:
                print(f"  - {violation}")
            print(f"\nTotal violations: {len(self.violations)}")
        else:
            print("✅ No violations found!")


def main():
    """Main entry point for pre-commit checks."""
    parser = argparse.ArgumentParser(description='Craftsmanship pre-commit checks')
    parser.add_argument('check', choices=[
        'check-async-naming',
        'check-complexity', 
        'check-types',
        'check-layers'
    ])
    parser.add_argument('files', nargs='*', help='Files to check')
    
    args = parser.parse_args()
    
    if not args.files:
        print("No files to check")
        sys.exit(0)
    
    checker = CraftsmanshipChecker()
    
    # Run the appropriate check
    if args.check == 'check-async-naming':
        success = checker.check_async_naming(args.files)
    elif args.check == 'check-complexity':
        success = checker.check_method_complexity(args.files)
    elif args.check == 'check-types':
        success = checker.check_type_coverage(args.files)
    elif args.check == 'check-layers':
        success = checker.check_layer_violations(args.files)
    else:
        print(f"Unknown check: {args.check}")
        sys.exit(1)
    
    checker.print_violations()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()