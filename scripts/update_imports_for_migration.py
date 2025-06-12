#!/usr/bin/env python3
"""
Update imports and references after migrating scripts to internal/scripts.

This script updates Python imports and shell script references to point
to the new locations of migrated scripts.

Copyright: DarkLightX/Dana Edwards
"""

import re
import os
from pathlib import Path
from typing import List, Set, Tuple
import argparse

class ImportUpdater:
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.updated_files = []
        self.script_mappings = self._build_script_mappings()
        
    def _build_script_mappings(self) -> dict:
        """Build mappings of old to new script locations."""
        mappings = {}
        
        # Common moved scripts
        moved_scripts = {
            # Tools
            "tools/code_quality_tool": "internal/scripts/quality/code_quality_tool",
            "tools/debug_utilities": "internal/scripts/tools/debug_utilities",
            "tools/analyze_complexity": "internal/scripts/analysis/analyze_complexity",
            
            # Scripts
            "scripts/migrate_to_refactored": "internal/scripts/migration/migrate_to_refactored",
            "scripts/cleanup_duplicates": "internal/scripts/utilities/cleanup_duplicates",
            
            # Utilities
            "utilities/run_tests": "internal/scripts/utilities/run_tests",
            "utilities/verify_refactoring": "internal/scripts/utilities/verify_refactoring",
            
            # Backend
            "backend/unified/migration_phase2": "internal/scripts/migration/migration_phase2",
            "backend/unified/verify_migration": "internal/scripts/migration/verify_migration",
        }
        
        for old, new in moved_scripts.items():
            mappings[old] = new
            
        return mappings
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files that might need updating."""
        python_files = []
        
        # Skip virtual environments and build directories
        skip_dirs = {
            'venv', 'venv_bdd', '.git', '__pycache__', 
            'build', 'dist', 'node_modules', '.next',
            'internal/scripts'  # Skip the destination directory
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove skip directories from traversal
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
                    
        return python_files
    
    def find_shell_scripts(self) -> List[Path]:
        """Find all shell scripts that might need updating."""
        shell_files = []
        
        for ext in ['.sh', '.bash']:
            shell_files.extend(self.project_root.rglob(f'*{ext}'))
            
        return shell_files
    
    def update_python_imports(self, file_path: Path) -> bool:
        """Update Python imports in a single file."""
        try:
            content = file_path.read_text()
            original_content = content
            updated = False
            
            # Pattern for various import styles
            patterns = [
                # from X import Y
                (r'from\s+(\w+)\s+import\s+(\w+)', 'from'),
                # import X
                (r'import\s+(\w+\.?\w*)', 'import'),
                # subprocess calls
                (r'subprocess\.\w+\(\[.*?["\'](\w+/\w+\.py)["\']', 'subprocess'),
                # Path references
                (r'Path\(["\'](\w+/\w+\.py)["\']\)', 'path'),
            ]
            
            for pattern, import_type in patterns:
                for match in re.finditer(pattern, content):
                    module_path = match.group(1)
                    
                    # Check if this module was moved
                    for old_path, new_path in self.script_mappings.items():
                        if old_path in module_path or module_path.endswith(old_path.split('/')[-1]):
                            # Update the import
                            if import_type == 'from':
                                new_import = f"from {new_path.replace('/', '.')} import {match.group(2)}"
                                content = content.replace(match.group(0), new_import)
                            elif import_type == 'import':
                                new_import = f"import {new_path.replace('/', '.')}"
                                content = content.replace(match.group(0), new_import)
                            else:
                                # For subprocess and path references
                                new_ref = match.group(0).replace(module_path, f"{new_path}.py")
                                content = content.replace(match.group(0), new_ref)
                            
                            updated = True
            
            if updated and content != original_content:
                if not self.dry_run:
                    file_path.write_text(content)
                self.updated_files.append(file_path)
                return True
                
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            
        return False
    
    def update_shell_references(self, file_path: Path) -> bool:
        """Update references in shell scripts."""
        try:
            content = file_path.read_text()
            original_content = content
            updated = False
            
            # Patterns for shell script references
            patterns = [
                r'python3?\s+(\w+/\w+\.py)',
                r'\./(\w+/\w+\.py)',
                r'[\'"](tools/\w+\.py)[\'"]',
                r'[\'"](scripts/\w+\.py)[\'"]',
                r'[\'"](utilities/\w+\.py)[\'"]',
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    script_path = match.group(1)
                    
                    # Check if this script was moved
                    for old_path, new_path in self.script_mappings.items():
                        if old_path in script_path or script_path.endswith(old_path.split('/')[-1]):
                            new_ref = match.group(0).replace(script_path, f"{new_path}.py")
                            content = content.replace(match.group(0), new_ref)
                            updated = True
            
            if updated and content != original_content:
                if not self.dry_run:
                    file_path.write_text(content)
                self.updated_files.append(file_path)
                return True
                
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            
        return False
    
    def update_documentation(self):
        """Update references in documentation files."""
        doc_files = list(self.project_root.rglob('*.md'))
        doc_files.extend(self.project_root.rglob('*.rst'))
        doc_files.extend(self.project_root.rglob('*.txt'))
        
        for doc_file in doc_files:
            try:
                content = doc_file.read_text()
                original_content = content
                updated = False
                
                # Update references to moved scripts
                for old_path, new_path in self.script_mappings.items():
                    if old_path in content:
                        content = content.replace(old_path, new_path)
                        updated = True
                
                if updated and content != original_content:
                    if not self.dry_run:
                        doc_file.write_text(content)
                    self.updated_files.append(doc_file)
                    
            except Exception as e:
                print(f"Error updating {doc_file}: {e}")
    
    def run(self):
        """Execute the import update process."""
        print(f"Import Update Tool - {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Project root: {self.project_root}\n")
        
        # Update Python files
        print("Scanning Python files...")
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files")
        
        updated_count = 0
        for py_file in python_files:
            if self.update_python_imports(py_file):
                updated_count += 1
                print(f"  Updated: {py_file.relative_to(self.project_root)}")
        
        # Update shell scripts
        print("\nScanning shell scripts...")
        shell_files = self.find_shell_scripts()
        print(f"Found {len(shell_files)} shell scripts")
        
        for sh_file in shell_files:
            if self.update_shell_references(sh_file):
                updated_count += 1
                print(f"  Updated: {sh_file.relative_to(self.project_root)}")
        
        # Update documentation
        print("\nUpdating documentation references...")
        self.update_documentation()
        
        # Summary
        print(f"\n{'='*60}")
        print(f"Update Summary:")
        print(f"  Files scanned: {len(python_files) + len(shell_files)}")
        print(f"  Files updated: {len(self.updated_files)}")
        
        if self.dry_run:
            print("\nThis was a dry run. No files were modified.")
            print("Run without --dry-run to perform the actual updates.")
        else:
            print("\nImport updates complete!")
            print("Please run tests to ensure all imports are working correctly.")


def main():
    parser = argparse.ArgumentParser(
        description="Update imports after script migration"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without modifying files"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent,
        help="Project root directory"
    )
    
    args = parser.parse_args()
    
    updater = ImportUpdater(args.project_root, args.dry_run)
    updater.run()


if __name__ == "__main__":
    main()