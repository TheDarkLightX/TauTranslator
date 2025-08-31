#!/usr/bin/env python3
"""
Phase 2 migration script for completing the refactored → production migration.
Handles: manager, auth (both api and core), config, and pattern_loader
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Files to migrate
MIGRATION_PAIRS = [
    # Core files
    ("core/auth_refactored.py", "core/auth.py"),
    ("core/config_refactored.py", "core/config.py"),
    ("core/pattern_loader_refactored.py", "core/pattern_loader.py"),
    
    # API files
    ("api/auth_refactored.py", "api/auth.py"),
    
    # Translator files
    ("translators/manager_refactored.py", "translators/manager.py"),
]

# Import mappings to update
IMPORT_UPDATES = {
    # Old import → New import
    "from .auth import": "from .auth import",
    "from .config import": "from .config import",
    "from .pattern_loader import": "from .pattern_loader import",
    "from .manager import": "from .manager import",
    "from ..core.auth import": "from ..core.auth import",
    "from ..core.config import": "from ..core.config import",
    "from ..core.pattern_loader import": "from ..core.pattern_loader import",
    "from unified.core.auth import": "from unified.core.auth import",
    "from unified.core.config import": "from unified.core.config import",
    "from unified.core.pattern_loader import": "from unified.core.pattern_loader import",
    "from unified.translators.manager import": "from unified.translators.manager import",
    "import auth": "import auth",
    "import config": "import config",
    "import pattern_loader": "import pattern_loader",
    "import manager": "import manager",
}

def create_backup_folder():
    """Create deprecated folder if it doesn't exist."""
    deprecated_dir = Path("deprecated")
    deprecated_dir.mkdir(exist_ok=True)
    
    # Create timestamp subdirectory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = deprecated_dir / f"backup_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    
    return backup_dir

def check_watchdog_dependency():
    """Check if watchdog is installed for auth module."""
    try:
        import watchdog
        print("✓ watchdog is installed")
        return True
    except ImportError:
        print("✗ watchdog is not installed")
        print("  The auth module requires watchdog. Install with: pip install watchdog")
        response = input("  Install watchdog now? [y/N]: ")
        if response.lower() == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install", "watchdog"])
            return True
        return False

def backup_original_file(filepath, backup_dir):
    """Backup original file if it exists."""
    if os.path.exists(filepath):
        backup_path = backup_dir / Path(filepath).name
        shutil.copy2(filepath, backup_path)
        print(f"  Backed up {filepath} → {backup_path}")
        return True
    return False

def update_imports_in_file(filepath):
    """Update imports in the given file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        for old_import, new_import in IMPORT_UPDATES.items():
            content = content.replace(old_import, new_import)
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  Error updating imports in {filepath}: {e}")
        return False

def update_all_imports():
    """Update imports in all Python files."""
    print("\n📝 Updating imports in all Python files...")
    updated_files = []
    
    for root, dirs, files in os.walk("."):
        # Skip test directories and deprecated folder
        if 'deprecated' in root or '__pycache__' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if update_imports_in_file(filepath):
                    updated_files.append(filepath)
    
    if updated_files:
        print(f"  Updated imports in {len(updated_files)} files")
        for f in updated_files[:10]:  # Show first 10
            print(f"    - {f}")
        if len(updated_files) > 10:
            print(f"    ... and {len(updated_files) - 10} more")
    else:
        print("  No import updates needed")

def migrate_file(source, target, backup_dir):
    """Migrate a single file."""
    print(f"\n📦 Migrating {source} → {target}")
    
    # Check if source exists
    if not os.path.exists(source):
        print(f"  ✗ Source file {source} not found")
        return False
    
    # Backup target if it exists
    if os.path.exists(target):
        backup_original_file(target, backup_dir)
    
    # Copy refactored file to target
    try:
        shutil.copy2(source, target)
        print(f"  ✓ Copied {source} → {target}")
        
        # Update imports in the newly copied file
        if update_imports_in_file(target):
            print(f"  ✓ Updated imports in {target}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error migrating {source}: {e}")
        return False

def remove_refactored_files():
    """Remove all _refactored.py files after successful migration."""
    print("\n🗑️  Removing refactored files...")
    for source, _ in MIGRATION_PAIRS:
        if os.path.exists(source):
            try:
                os.remove(source)
                print(f"  ✓ Removed {source}")
            except Exception as e:
                print(f"  ✗ Error removing {source}: {e}")

def run_tests():
    """Run tests to verify migration."""
    print("\n🧪 Running tests to verify migration...")
    
    test_commands = [
        # Unit tests for migrated modules
        "python -m pytest tests/unit/test_translation_manager.py -xvs",
        "python -m pytest tests/unit/test_dependency_injection.py -xvs",
        "python -m pytest tests/integration/test_unified_backend.py -xvs",
        
        # Quick integration test
        "python backend/unified/test_direct.py",
    ]
    
    all_passed = True
    for cmd in test_commands:
        print(f"\n  Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Test passed")
        else:
            print(f"  ✗ Test failed")
            print(f"    stdout: {result.stdout[:500]}...")
            print(f"    stderr: {result.stderr[:500]}...")
            all_passed = False
    
    return all_passed

def main():
    """Main migration function."""
    print("🚀 Starting Phase 2 Migration")
    print("=" * 50)
    
    # Skip watchdog check - refactored auth doesn't use it
    print("\n🔍 Skipping dependency checks (refactored code has no watchdog dependency)")
    
    # Create backup directory
    backup_dir = create_backup_folder()
    print(f"\n📁 Created backup directory: {backup_dir}")
    
    # Migrate each file
    success_count = 0
    for source, target in MIGRATION_PAIRS:
        if migrate_file(source, target, backup_dir):
            success_count += 1
    
    print(f"\n📊 Migration summary: {success_count}/{len(MIGRATION_PAIRS)} files migrated")
    
    # Update imports in all files
    update_all_imports()
    
    # Remove refactored files if all migrations successful
    if success_count == len(MIGRATION_PAIRS):
        print("\n🗑️  Removing refactored files...")
        remove_refactored_files()
    else:
        print("\n⚠️  Not all files migrated successfully, keeping refactored files")
    
    # Run tests
    print("\n" + "=" * 50)
    if run_tests():
        print("\n✅ All tests passed! Migration complete.")
    else:
        print("\n⚠️  Some tests failed. Please review and fix.")
        print(f"   Backups are available in: {backup_dir}")
    
    print("\n📋 Next steps:")
    print("1. Review any test failures")
    print("2. Test the unified backend manually: python backend/unified/server.py")
    print("3. Test the PWA frontend integration")
    print("4. Remove deprecated folder once everything is verified")

if __name__ == "__main__":
    # Change to backend/unified directory
    os.chdir(Path(__file__).parent)
    main()