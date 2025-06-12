#!/usr/bin/env python3
"""
Migration script for requirements_analyzer refactoring.

Updates imports and usage patterns from old to new implementation.

Copyright: DarkLightX / Dana Edwards
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def find_files_with_imports(root_dir: Path, old_module: str) -> List[Path]:
    """Find all Python files importing the old module."""
    files_with_imports = []
    
    for py_file in root_dir.rglob("*.py"):
        # Skip the old file itself and this migration script
        if py_file.name in ["requirements_analyzer.py", "migrate_requirements_analyzer.py"]:
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for imports
            if re.search(rf'from\s+{re.escape(old_module)}\s+import', content) or \
               re.search(rf'import\s+{re.escape(old_module)}', content):
                files_with_imports.append(py_file)
                
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return files_with_imports

def update_imports(file_path: Path) -> Tuple[bool, str]:
    """Update imports in a file from old to new module."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update import statements
        old_patterns = [
            (r'from\s+(.*)\.requirements_analyzer\s+import',
             r'from \1.requirements_analyzer_refactored import'),
            (r'import\s+(.*)\.requirements_analyzer\s+as',
             r'import \1.requirements_analyzer_refactored as'),
            (r'import\s+(.*)\.requirements_analyzer',
             r'import \1.requirements_analyzer_refactored'),
        ]
        
        for old_pattern, new_pattern in old_patterns:
            content = re.sub(old_pattern, new_pattern, content)
        
        # Update any direct references if module was imported as-is
        content = re.sub(r'requirements_analyzer\.RequirementsAnalyzer',
                        r'requirements_analyzer_refactored.RequirementsAnalyzer', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Updated successfully"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def create_compatibility_shim(old_file_path: Path) -> None:
    """Create a compatibility shim at the old location."""
    shim_content = '''#!/usr/bin/env python3
"""
Compatibility shim for requirements_analyzer.

This module has been refactored. Please update your imports to use
requirements_analyzer_refactored instead.

This shim provides backward compatibility during the migration period.

Copyright: DarkLightX / Dana Edwards
"""

import warnings
from .requirements_analyzer_refactored import *

warnings.warn(
    "requirements_analyzer has been refactored. "
    "Please update your imports to use requirements_analyzer_refactored.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all public symbols
__all__ = [
    'RequirementsAnalyzer',
    'RequirementItem',
    'RequirementType',
    'LogicalStructure',
    'FormalConstraint',
    'create_requirements_analyzer'
]
'''
    
    # Rename old file
    backup_path = old_file_path.with_suffix('.py.backup')
    if old_file_path.exists():
        old_file_path.rename(backup_path)
        print(f"Backed up original file to: {backup_path}")
    
    # Create shim
    with open(old_file_path, 'w', encoding='utf-8') as f:
        f.write(shim_content)
    print(f"Created compatibility shim at: {old_file_path}")

def main():
    """Run the migration."""
    project_root = Path(__file__).parent.parent
    
    print("Requirements Analyzer Migration Script")
    print("=" * 50)
    
    # Define the module paths
    old_module = "src.tau_translator_omega.core_engine.nlp_enhanced.requirements_analyzer"
    old_file = project_root / "src/tau_translator_omega/core_engine/nlp_enhanced/requirements_analyzer.py"
    new_file = project_root / "src/tau_translator_omega/core_engine/nlp_enhanced/requirements_analyzer_refactored.py"
    
    # Check if new file exists
    if not new_file.exists():
        print(f"ERROR: New refactored file not found at {new_file}")
        return
    
    print(f"Migrating from: {old_module}")
    print(f"           to: {old_module}_refactored")
    print()
    
    # Find files that need updating
    print("Scanning for files to update...")
    files_to_update = find_files_with_imports(project_root, old_module)
    
    if not files_to_update:
        print("No files found that import the old module.")
    else:
        print(f"Found {len(files_to_update)} files to update:")
        for file in files_to_update:
            print(f"  - {file.relative_to(project_root)}")
        print()
        
        # Update each file
        print("Updating imports...")
        success_count = 0
        for file in files_to_update:
            success, message = update_imports(file)
            if success:
                success_count += 1
                print(f"  ✓ {file.relative_to(project_root)}")
            else:
                print(f"  ✗ {file.relative_to(project_root)}: {message}")
        
        print(f"\nUpdated {success_count}/{len(files_to_update)} files successfully.")
    
    # Create compatibility shim
    print("\nCreating compatibility shim...")
    create_compatibility_shim(old_file)
    
    print("\nMigration complete!")
    print("\nNext steps:")
    print("1. Run tests to ensure everything still works")
    print("2. Update any documentation referencing the old module")
    print("3. After verification, remove the compatibility shim and backup file")

if __name__ == "__main__":
    main()