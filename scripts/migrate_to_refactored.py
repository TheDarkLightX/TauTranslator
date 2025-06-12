#!/usr/bin/env python3
"""
Migration script to replace current implementations with refactored versions.

This script will:
1. Run tests on both current and refactored versions
2. Move current versions to deprecated folder
3. Rename refactored versions to become current
4. Update imports throughout the codebase

Copyright: DarkLightX/Dana Edwards
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class RefactoredMigration:
    """Handles migration from current to refactored implementations."""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.project_root = project_root
        self.deprecated_dir = self.project_root / "deprecated" / f"pre_refactor_{datetime.now().strftime('%Y%m%d')}"
        self.test_results = {}
        self.migration_pairs = [
            {
                'current': 'backend/unified/translators/pattern_translator.py',
                'refactored': 'backend/unified/translators/pattern_translator_refactored.py',
                'tests_current': ['tests/unit/test_pattern_translator.py'],
                'tests_refactored': ['tests/unit/test_pattern_translator.py']
            },
            {
                'current': 'backend/unified/translators/manager.py',
                'refactored': 'backend/unified/translators/manager_refactored.py',
                'tests_current': ['tests/unit/test_translation_manager.py'],
                'tests_refactored': []  # No specific test file yet
            },
            {
                'current': 'backend/unified/api/auth.py',
                'refactored': 'backend/unified/api/auth_refactored.py',
                'tests_current': [],  # No specific test file
                'tests_refactored': ['tests/unit/test_auth_refactored.py']
            },
            {
                'current': 'backend/unified/core/config.py',
                'refactored': 'backend/unified/core/config_refactored.py',
                'tests_current': [],
                'tests_refactored': []
            },
            {
                'current': None,  # No current version
                'refactored': 'backend/unified/core/pattern_loader_refactored.py',
                'tests_current': [],
                'tests_refactored': ['tests/unit/test_pattern_loader_refactored.py']
            }
        ]
        
    def run(self):
        """Execute the migration process."""
        print("🔄 TauTranslator Refactored Migration")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'ACTUAL MIGRATION'}")
        print(f"Deprecated directory: {self.deprecated_dir}\n")
        
        # Phase 1: Test current implementations
        print("Phase 1: Testing current implementations...")
        if not self.test_current_implementations():
            print("❌ Current implementation tests failed. Fix before migrating.")
            return False
            
        # Phase 2: Test refactored implementations
        print("\nPhase 2: Testing refactored implementations...")
        if not self.test_refactored_implementations():
            print("❌ Refactored implementation tests failed. Fix before migrating.")
            return False
            
        # Phase 3: Create deprecated directory
        print("\nPhase 3: Creating deprecated directory...")
        if not self.dry_run:
            self.deprecated_dir.mkdir(parents=True, exist_ok=True)
            
        # Phase 4: Move current to deprecated
        print("\nPhase 4: Moving current implementations to deprecated...")
        self.move_current_to_deprecated()
        
        # Phase 5: Rename refactored to current
        print("\nPhase 5: Renaming refactored implementations to current...")
        self.rename_refactored_to_current()
        
        # Phase 6: Update imports
        print("\nPhase 6: Updating imports throughout codebase...")
        self.update_imports()
        
        # Phase 7: Final test
        print("\nPhase 7: Running final tests...")
        if not self.dry_run:
            self.run_final_tests()
            
        # Summary
        self.print_summary()
        
    def run_tests(self, test_files: list, name: str) -> bool:
        """Run tests and return success status."""
        if not test_files:
            print(f"  ⚠️  No tests defined for {name}")
            return True
            
        for test_file in test_files:
            test_path = self.project_root / test_file
            if not test_path.exists():
                print(f"  ⚠️  Test file not found: {test_file}")
                self.test_results[test_file] = "not_found"
                continue
                
            print(f"  🧪 Running {test_file}...")
            
            if self.dry_run:
                print(f"     [DRY RUN] Would run: pytest {test_file}")
                self.test_results[test_file] = "dry_run"
            else:
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", str(test_path), "-v"],
                        capture_output=True,
                        text=True,
                        cwd=str(self.project_root)
                    )
                    
                    if result.returncode == 0:
                        print(f"     ✅ Tests passed")
                        self.test_results[test_file] = "passed"
                    else:
                        print(f"     ❌ Tests failed")
                        print(result.stdout[-500:])  # Last 500 chars
                        self.test_results[test_file] = "failed"
                        return False
                        
                except Exception as e:
                    print(f"     ❌ Error running tests: {e}")
                    self.test_results[test_file] = f"error: {e}"
                    return False
                    
        return True
        
    def test_current_implementations(self) -> bool:
        """Test all current implementations."""
        all_passed = True
        
        for pair in self.migration_pairs:
            if pair['current'] and (self.project_root / pair['current']).exists():
                name = Path(pair['current']).stem
                print(f"\n  Testing {name} (current)...")
                if not self.run_tests(pair['tests_current'], name):
                    all_passed = False
                    
        return all_passed
        
    def test_refactored_implementations(self) -> bool:
        """Test all refactored implementations."""
        all_passed = True
        
        for pair in self.migration_pairs:
            if pair['refactored'] and (self.project_root / pair['refactored']).exists():
                name = Path(pair['refactored']).stem.replace('_refactored', '')
                print(f"\n  Testing {name} (refactored)...")
                if not self.run_tests(pair['tests_refactored'], name):
                    all_passed = False
                    
        return all_passed
        
    def move_current_to_deprecated(self):
        """Move current implementations to deprecated folder."""
        for pair in self.migration_pairs:
            if pair['current'] and (self.project_root / pair['current']).exists():
                current_path = self.project_root / pair['current']
                deprecated_path = self.deprecated_dir / pair['current']
                
                print(f"  📦 {pair['current']} -> deprecated/")
                
                if not self.dry_run:
                    deprecated_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(current_path), str(deprecated_path))
                    
    def rename_refactored_to_current(self):
        """Rename refactored files to current names."""
        for pair in self.migration_pairs:
            if pair['refactored'] and (self.project_root / pair['refactored']).exists():
                refactored_path = self.project_root / pair['refactored']
                
                if pair['current']:
                    # Use the current name
                    new_path = self.project_root / pair['current']
                else:
                    # Remove _refactored suffix
                    new_name = refactored_path.name.replace('_refactored', '')
                    new_path = refactored_path.parent / new_name
                    
                print(f"  ✏️  {pair['refactored']} -> {new_path.relative_to(self.project_root)}")
                
                if not self.dry_run:
                    shutil.move(str(refactored_path), str(new_path))
                    
            # Also rename test files
            for test_file in pair['tests_refactored']:
                test_path = self.project_root / test_file
                if test_path.exists():
                    new_test_name = test_path.name.replace('_refactored', '')
                    new_test_path = test_path.parent / new_test_name
                    
                    # Only rename if target doesn't exist
                    if not new_test_path.exists():
                        print(f"  ✏️  {test_file} -> {new_test_path.relative_to(self.project_root)}")
                        if not self.dry_run:
                            shutil.move(str(test_path), str(new_test_path))
                            
    def update_imports(self):
        """Update imports throughout the codebase."""
        replacements = [
            ('pattern_translator_refactored', 'pattern_translator'),
            ('manager_refactored', 'manager'),
            ('auth_refactored', 'auth'),
            ('config_refactored', 'config'),
            ('pattern_loader_refactored', 'pattern_loader'),
            ('test_pattern_translator', 'test_pattern_translator'),
            ('test_auth_refactored', 'test_auth'),
            ('test_pattern_loader_refactored', 'test_pattern_loader'),
        ]
        
        print("\n  🔍 Scanning for imports to update...")
        
        files_updated = 0
        for py_file in self.project_root.rglob("*.py"):
            # Skip deprecated and experimental folders
            if any(part in py_file.parts for part in ['deprecated', 'experiments', '__pycache__', 'venv']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                original_content = content
                for old, new in replacements:
                    content = content.replace(old, new)
                    
                if content != original_content:
                    print(f"  ✏️  Updating imports in {py_file.relative_to(self.project_root)}")
                    if not self.dry_run:
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                    files_updated += 1
                    
            except Exception as e:
                print(f"  ❌ Error updating {py_file}: {e}")
                
        print(f"  📝 Updated imports in {files_updated} files")
        
    def run_final_tests(self):
        """Run tests after migration to ensure everything works."""
        print("\n  🧪 Running integration tests...")
        
        test_commands = [
            "pytest tests/unit/test_pattern_translator.py -v",
            "pytest tests/unit/test_dependency_injection.py -v",
            "pytest tests/integration/test_unified_backend.py -v"
        ]
        
        for cmd in test_commands:
            print(f"\n  Running: {cmd}")
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root)
                )
                
                if result.returncode == 0:
                    print("  ✅ Passed")
                else:
                    print("  ❌ Failed")
                    print(result.stdout[-500:])
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                
    def print_summary(self):
        """Print migration summary."""
        print(f"\n{'='*60}")
        print("Migration Summary")
        print(f"{'='*60}")
        
        print("\nTest Results:")
        for test, result in self.test_results.items():
            emoji = "✅" if result == "passed" else "❌" if result == "failed" else "⚠️"
            print(f"  {emoji} {test}: {result}")
            
        if self.dry_run:
            print(f"\n⚠️  This was a DRY RUN. No files were actually moved.")
            print(f"To perform actual migration, run with --execute flag")
            
            # Save migration plan
            plan_file = self.project_root / "migration_plan.json"
            with open(plan_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'migration_pairs': self.migration_pairs,
                    'test_results': self.test_results
                }, f, indent=2)
            print(f"\nMigration plan saved to: {plan_file}")
        else:
            print(f"\n✅ Migration completed!")
            print(f"Old versions backed up to: {self.deprecated_dir}")
            print("\nNext steps:")
            print("1. Run full test suite: pytest tests/")
            print("2. Test the application manually")
            print("3. Commit the changes")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate to refactored implementations")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the migration (default is dry run)"
    )
    
    args = parser.parse_args()
    
    migration = RefactoredMigration(dry_run=not args.execute)
    migration.run()


if __name__ == "__main__":
    main()