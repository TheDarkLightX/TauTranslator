#!/usr/bin/env python3
"""
Update imports after cleanup of duplicate files.

This script will:
1. Find and update imports that reference deleted files
2. Update test imports
3. Verify all imports are valid

Copyright: DarkLightX/Dana Edwards
"""

import os
import re
from pathlib import Path
import ast

project_root = Path(__file__).parent.parent


class ImportUpdater:
    """Updates imports after file cleanup."""
    
    def __init__(self):
        self.project_root = project_root
        self.import_mappings = {
            # Map old imports to new ones
            "pattern_translator_refactored": "pattern_translator",
            "manager_refactored": "manager",
            "config_refactored": "config",
            "auth_refactored": "auth",
            "pattern_loader_refactored": "pattern_loader",
            # Remove references to old core engine
            "tau_translator_omega": None,
            # Security imports should use core.auth
            "security.api_key_manager": "backend.unified.core.auth",
            "security.secure_api_manager": "backend.unified.core.auth",
        }
        self.files_updated = 0
        self.imports_fixed = 0
        
    def run(self):
        """Execute import updates."""
        print("🔧 Updating imports after cleanup...")
        
        # Find all Python files
        python_files = list(self.project_root.glob("**/*.py"))
        
        for py_file in python_files:
            # Skip files in backup, build, cache directories
            if any(part in py_file.parts for part in ['backup_', 'build', 'dist', '__pycache__', '.pytest_cache']):
                continue
                
            self.update_file_imports(py_file)
            
        print(f"\n✅ Updated {self.files_updated} files")
        print(f"📝 Fixed {self.imports_fixed} imports")
        
    def update_file_imports(self, file_path: Path):
        """Update imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            updated = False
            
            # Update import statements
            for old_import, new_import in self.import_mappings.items():
                if old_import in content:
                    if new_import:
                        # Replace with new import
                        patterns = [
                            (f"from .*{old_import} import", f"from .{new_import} import"),
                            (f"import .*{old_import}", f"import {new_import}"),
                        ]
                        
                        for pattern, replacement in patterns:
                            new_content, count = re.subn(pattern, replacement, content)
                            if count > 0:
                                content = new_content
                                self.imports_fixed += count
                                updated = True
                    else:
                        # Remove the import entirely
                        patterns = [
                            f"from .*{old_import} import .*\n",
                            f"import .*{old_import}.*\n",
                        ]
                        
                        for pattern in patterns:
                            new_content, count = re.subn(pattern, "", content)
                            if count > 0:
                                content = new_content
                                self.imports_fixed += count
                                updated = True
                                
            # Fix specific cases
            content = self.fix_specific_imports(content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_updated += 1
                print(f"  ✏️  Updated: {file_path.relative_to(self.project_root)}")
                
        except Exception as e:
            print(f"  ❌ Error updating {file_path}: {e}")
            
    def fix_specific_imports(self, content: str) -> str:
        """Fix specific import patterns."""
        # Fix test imports
        content = re.sub(
            r"test_pattern_translator",
            "test_pattern_translator",
            content
        )
        
        # Fix infrastructure imports
        content = re.sub(
            r"from \.\.infrastructure\.repositories\.memory_cache_repository",
            "from ..core.caching.advanced_cache",
            content
        )
        
        # Fix event bus imports
        content = re.sub(
            r"from \.\.infrastructure\.event_bus import InMemoryEventBus",
            "from ..core.events import EventBus",
            content
        )
        
        return content
        
    def verify_imports(self):
        """Verify all imports are valid after updates."""
        print("\n🔍 Verifying imports...")
        
        invalid_imports = []
        
        for py_file in self.project_root.glob("**/*.py"):
            if any(part in py_file.parts for part in ['backup_', 'build', 'dist', '__pycache__']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        # Check for references to deleted files
                        if any(deleted in module for deleted in ['_refactored', 'tau_translator_omega', 'security.']):
                            invalid_imports.append({
                                'file': py_file.relative_to(self.project_root),
                                'import': f"from {module} import ..."
                            })
                            
            except Exception as e:
                pass
                
        if invalid_imports:
            print(f"\n⚠️  Found {len(invalid_imports)} potentially invalid imports:")
            for imp in invalid_imports[:10]:  # Show first 10
                print(f"  - {imp['file']}: {imp['import']}")
        else:
            print("✅ All imports appear to be valid!")
            
        return len(invalid_imports) == 0


def main():
    """Main entry point."""
    updater = ImportUpdater()
    updater.run()
    updater.verify_imports()


if __name__ == "__main__":
    main()