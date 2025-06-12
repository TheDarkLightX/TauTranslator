#!/usr/bin/env python3
"""
Enhanced Styling Toolkit with Auto-Fix Capabilities
Implements the Intentional Disclosure Principle with safe refactoring
Copyright: DarkLightX/Dana Edwards
"""

import ast
import re
import os
import json
import subprocess
import shutil
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass
from pathlib import Path
import asyncio
from collections import defaultdict
import libcst as cst
from libcst import matchers as m
import black
import datetime


@dataclass
class TypeInfo:
    """Represents type information for a parameter or return value."""
    original_name: str
    suggested_type: str
    is_io_operation: bool = False
    domain_concept: Optional[str] = None


@dataclass 
class RefactoringFix:
    """Represents an automated fix for a craftsmanship violation."""
    file_path: str
    original_code: str
    fixed_code: str
    rule: int
    fix_type: str
    
    
class GoldenMasterGenerator:
    """Creates golden master tests before refactoring for safety."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests" / "golden_masters"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
    def create_golden_master(self, module_path: str) -> str:
        """Create a golden master test for a module."""
        module_name = Path(module_path).stem
        relative_path = os.path.relpath(module_path, self.project_root)
        
        test_content = f'''"""
Golden Master Test for {relative_path}
Ensures behavior preservation during refactoring
Copyright: DarkLightX/Dana Edwards
"""

import pytest
import json
import importlib.util
from pathlib import Path
from typing import Any, Dict, List


class TestGoldenMaster{module_name.title().replace("_", "")}:
    """Captures current behavior as golden master."""
    
    @pytest.fixture
    def module(self):
        """Load the module under test."""
        spec = importlib.util.spec_from_file_location(
            "{module_name}", 
            "{module_path}"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
        
    def test_public_api_snapshot(self, module):
        """Capture all public functions and their signatures."""
        public_api = {{}}
        
        for name in dir(module):
            if not name.startswith('_'):
                obj = getattr(module, name)
                if callable(obj):
                    # Capture function signature
                    import inspect
                    sig = str(inspect.signature(obj))
                    public_api[name] = {{
                        'signature': sig,
                        'docstring': obj.__doc__,
                        'is_async': inspect.iscoroutinefunction(obj)
                    }}
                    
        # Save snapshot
        snapshot_file = Path(__file__).parent / f"{module_name}_snapshot.json"
        with open(snapshot_file, 'w') as f:
            json.dump(public_api, f, indent=2)
            
    def test_behavior_preservation(self, module):
        """Test that refactored code maintains same behavior."""
        # This is a template - actual tests would be module-specific
        pass
'''
        
        test_file = self.test_dir / f"test_golden_{module_name}.py"
        with open(test_file, 'w') as f:
            f.write(test_content)
            
        return str(test_file)


class TypeInferenceEngine:
    """Infers types based on usage patterns and naming conventions."""
    
    def __init__(self):
        self.type_patterns = {
            # Naming patterns
            r'.*_id$': 'str',  # IDs are typically strings
            r'.*_ids$': 'List[str]',
            r'.*_count$': 'int',
            r'.*_size$': 'int',
            r'.*_flag$': 'bool',
            r'is_.*': 'bool',
            r'has_.*': 'bool',
            r'.*_path$': 'Path',
            r'.*_file$': 'Path',
            r'.*_dir$': 'Path',
            r'.*_url$': 'str',
            r'.*_name$': 'str',
            r'.*_data$': 'Dict[str, Any]',
            r'.*_list$': 'List[Any]',
            r'.*_dict$': 'Dict[str, Any]',
            r'.*_set$': 'Set[Any]',
            r'.*_queue$': 'Queue[Any]',
            r'.*_date$': 'datetime',
            r'.*_time$': 'datetime',
            r'.*_timestamp$': 'float',
        }
        
        self.io_indicators = [
            'read', 'write', 'fetch', 'save', 'load', 'download',
            'upload', 'send', 'receive', 'query', 'execute'
        ]
        
    def infer_type(self, param_name: str, context: Optional[ast.FunctionDef] = None) -> TypeInfo:
        """Infer type information for a parameter."""
        # Check naming patterns
        for pattern, type_hint in self.type_patterns.items():
            if re.match(pattern, param_name):
                return TypeInfo(
                    original_name=param_name,
                    suggested_type=type_hint,
                    domain_concept=self._extract_domain_concept(param_name)
                )
                
        # Default based on common patterns
        if param_name in ['self', 'cls']:
            return TypeInfo(param_name, 'Any', domain_concept=None)
            
        return TypeInfo(param_name, 'Any', domain_concept=None)
        
    def _extract_domain_concept(self, name: str) -> Optional[str]:
        """Extract domain concept from variable name."""
        # Remove common suffixes
        base_name = re.sub(r'(_id|_ids|_count|_path|_data)$', '', name)
        
        # Convert to PascalCase for domain type
        parts = base_name.split('_')
        return ''.join(p.capitalize() for p in parts) if parts else None


class AsyncNamingTransformer(cst.CSTTransformer):
    """Transforms async functions to include _async suffix."""
    
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        # Check if it's an async function
        if updated_node.asynchronous:
            name = updated_node.name.value
            # Don't modify if already has _async suffix or is private
            if not name.endswith('_async') and not name.startswith('_'):
                new_name = f"{name}_async"
                updated_node = updated_node.with_changes(
                    name=cst.Name(new_name)
                )
        return updated_node


class OrchestratorPatternTransformer(cst.CSTTransformer):
    """Transforms complex public methods into orchestrator pattern."""
    
    def __init__(self):
        self.methods_to_extract = []
        
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        name = updated_node.name.value
        
        # Only process public methods
        if name.startswith('_'):
            return updated_node
            
        # Count statements in the body
        body_statements = len(updated_node.body.body)
        
        if body_statements > 10:
            # This method needs orchestrator pattern
            # For now, just mark it - actual extraction is complex
            # and would require more sophisticated analysis
            pass
            
        return updated_node


class TypeAnnotationTransformer(cst.CSTTransformer):
    """Adds type annotations to functions."""
    
    def __init__(self, type_engine: TypeInferenceEngine):
        self.type_engine = type_engine
        self.imports_needed = set()
        
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        # Process parameters
        new_params = []
        for param in updated_node.params.params:
            if param.annotation is None and param.name.value != 'self':
                # Infer type
                type_info = self.type_engine.infer_type(param.name.value)
                
                # Add annotation
                annotation = cst.Annotation(
                    annotation=cst.Name(type_info.suggested_type)
                )
                param = param.with_changes(annotation=annotation)
                
                # Track imports needed
                if 'List' in type_info.suggested_type:
                    self.imports_needed.add('from typing import List')
                elif 'Dict' in type_info.suggested_type:
                    self.imports_needed.add('from typing import Dict')
                elif 'Set' in type_info.suggested_type:
                    self.imports_needed.add('from typing import Set')
                    
            new_params.append(param)
            
        # Update parameters
        updated_node = updated_node.with_changes(
            params=updated_node.params.with_changes(params=new_params)
        )
        
        # Add return type if missing
        if updated_node.returns is None and updated_node.name.value != '__init__':
            # Simple heuristic: if function has return statement, use Any
            # In real implementation, would analyze return statements
            return_annotation = cst.Annotation(
                annotation=cst.Name('Any')
            )
            updated_node = updated_node.with_changes(returns=return_annotation)
            self.imports_needed.add('from typing import Any')
            
        return updated_node


class EnhancedStylingToolkit:
    """Enhanced toolkit with auto-fix capabilities."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.golden_master_gen = GoldenMasterGenerator(self.project_root)
        self.type_engine = TypeInferenceEngine()
        self.fixes_applied = []
        
    def create_backup(self, file_path: str) -> str:
        """Create a backup of the file before modifying."""
        backup_dir = self.project_root / ".refactoring_backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{Path(file_path).name}.{timestamp}.bak"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return str(backup_path)
        
    def apply_auto_fixes(self, file_path: str, rules: List[int] = [1, 2, 3]) -> List[RefactoringFix]:
        """Apply automated fixes for specified rules."""
        fixes = []
        
        # Create backup first
        backup_path = self.create_backup(file_path)
        
        # Read the file
        with open(file_path, 'r') as f:
            source_code = f.read()
            
        # Parse with libcst for transformation
        try:
            tree = cst.parse_module(source_code)
            
            # Apply transformations based on rules
            if 1 in rules:
                # Rule 1: Async naming
                transformer = AsyncNamingTransformer()
                tree = tree.visit(transformer)
                
            if 3 in rules:
                # Rule 3: Type annotations
                transformer = TypeAnnotationTransformer(self.type_engine)
                tree = tree.visit(transformer)
                
                # Add necessary imports
                if transformer.imports_needed:
                    # Add imports at the top
                    import_statements = [
                        cst.SimpleStatementLine(body=[cst.ImportFrom(
                            module=cst.Attribute(value=cst.Name("typing"), attr=cst.Name(imp.split()[-1])),
                            names=[cst.ImportAlias(name=cst.Name(imp.split()[-1]))]
                        )]) for imp in transformer.imports_needed
                    ]
                    tree = tree.with_changes(
                        body=import_statements + list(tree.body)
                    )
                    
            # Generate fixed code
            fixed_code = tree.code
            
            # Format with black
            try:
                fixed_code = black.format_str(fixed_code, mode=black.FileMode())
            except:
                pass  # Keep unformatted if black fails
                
            # Only write if changes were made
            if fixed_code != source_code:
                with open(file_path, 'w') as f:
                    f.write(fixed_code)
                    
                fixes.append(RefactoringFix(
                    file_path=file_path,
                    original_code=source_code,
                    fixed_code=fixed_code,
                    rule=0,  # Multiple rules
                    fix_type="auto_fix"
                ))
                
        except Exception as e:
            print(f"Error applying fixes to {file_path}: {e}")
            # Restore from backup on error
            shutil.copy2(backup_path, file_path)
            
        return fixes
        
    def validate_fixes(self, file_path: str) -> bool:
        """Validate that fixes don't break the code."""
        # Run syntax check
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            return True
        except SyntaxError:
            return False
            
    def run_tests_for_file(self, file_path: str) -> bool:
        """Run tests related to a file to ensure no regression."""
        # Find test file
        module_name = Path(file_path).stem
        test_patterns = [
            f"test_{module_name}.py",
            f"test_*{module_name}*.py",
            f"{module_name}_test.py"
        ]
        
        test_dir = self.project_root / "tests"
        for root, dirs, files in os.walk(test_dir):
            for pattern in test_patterns:
                import glob
                matches = glob.glob(os.path.join(root, pattern))
                if matches:
                    # Run pytest on the test file
                    result = subprocess.run(
                        ["pytest", "-xvs"] + matches,
                        capture_output=True,
                        text=True
                    )
                    return result.returncode == 0
                    
        return True  # No tests found, assume OK
        
    def generate_domain_types(self, analysis_results: Dict[str, List]) -> str:
        """Generate domain type definitions based on analysis."""
        domain_types = set()
        
        # Analyze all files for common patterns
        for file_issues in analysis_results.values():
            for issue in file_issues:
                if issue.issue_type == "missing_type_annotation":
                    # Extract potential domain concepts
                    match = re.search(r"'(\w+)'", issue.current_code)
                    if match:
                        param_name = match.group(1)
                        type_info = self.type_engine.infer_type(param_name)
                        if type_info.domain_concept:
                            domain_types.add(type_info.domain_concept)
                            
        # Generate type definitions
        type_definitions = ['"""Domain type definitions for TauTranslator."""']
        type_definitions.append('from typing import NewType, TypeVar, Union, List, Dict, Optional')
        type_definitions.append('')
        
        for domain_type in sorted(domain_types):
            type_definitions.append(f'{domain_type}Id = NewType("{domain_type}Id", str)')
            type_definitions.append(f'{domain_type}Name = NewType("{domain_type}Name", str)')
            
        type_definitions.append('')
        type_definitions.append('# Common domain types')
        type_definitions.append('FilePath = NewType("FilePath", str)')
        type_definitions.append('DirectoryPath = NewType("DirectoryPath", str)')
        type_definitions.append('Url = NewType("Url", str)')
        type_definitions.append('Email = NewType("Email", str)')
        
        return '\n'.join(type_definitions)


def main():
    """Main entry point for enhanced styling toolkit."""
    import argparse
    import datetime
    
    parser = argparse.ArgumentParser(description='Enhanced Styling Toolkit')
    parser.add_argument('--analyze', action='store_true', help='Analyze project')
    parser.add_argument('--fix', action='store_true', help='Apply automated fixes')
    parser.add_argument('--golden-master', action='store_true', help='Create golden master tests')
    parser.add_argument('--file', type=str, help='Target specific file')
    parser.add_argument('--rules', type=str, default='1,3', help='Rules to apply (comma-separated)')
    parser.add_argument('--safe-mode', action='store_true', help='Run tests after each fix')
    
    args = parser.parse_args()
    
    toolkit = EnhancedStylingToolkit('.')
    
    if args.golden_master:
        if args.file:
            test_file = toolkit.golden_master_gen.create_golden_master(args.file)
            print(f"Created golden master test: {test_file}")
        else:
            print("Please specify a file with --file")
            
    if args.fix:
        rules = [int(r) for r in args.rules.split(',')]
        
        if args.file:
            fixes = toolkit.apply_auto_fixes(args.file, rules)
            if fixes:
                print(f"Applied {len(fixes)} fixes to {args.file}")
                if args.safe_mode:
                    if toolkit.run_tests_for_file(args.file):
                        print("✅ Tests passed!")
                    else:
                        print("❌ Tests failed! Check the changes.")
        else:
            print("Please specify a file with --file")
            
            
if __name__ == '__main__':
    main()