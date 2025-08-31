#!/usr/bin/env python3
"""
Simple verification script to check if migration was successful.
Tests that core modules can be imported and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import unified modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all migrated modules can be imported."""
    print("Testing imports of migrated modules...")
    
    try:
        # Test core imports
        print("\n1. Testing core imports:")
        from unified.core.auth import AuthenticationService
        print("  ✓ unified.core.auth imported successfully")
        
        from unified.core.config import Settings, get_settings
        print("  ✓ unified.core.config imported successfully")
        
        from unified.core.pattern_loader import PatternLoader
        print("  ✓ unified.core.pattern_loader imported successfully")
        
        # Test API imports
        print("\n2. Testing API imports:")
        from unified.api.auth import router as auth_router
        print("  ✓ unified.api.auth imported successfully")
        
        # Test translator imports
        print("\n3. Testing translator imports:")
        from unified.translators.manager import TranslationManager
        print("  ✓ unified.translators.manager imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of migrated modules."""
    print("\n\nTesting basic functionality...")
    
    try:
        # Test config
        print("\n1. Testing config:")
        from unified.core.config import get_settings
        settings = get_settings()
        print(f"  ✓ Settings loaded: project_name={settings.project_name}")
        
        # Test pattern loader
        print("\n2. Testing pattern loader:")
        from unified.core.pattern_loader import PatternLoader
        from unified.core.interfaces import IPatternRepository
        
        # Create a mock repository for testing
        class MockPatternRepo(IPatternRepository):
            async def load_patterns_async(self, source_id):
                return {"test": {"pattern": "test", "tau": "τ_test"}}
            
            async def save_patterns_async(self, patterns, target_id):
                return True
        
        loader = PatternLoader(MockPatternRepo())
        print("  ✓ PatternLoader created successfully")
        
        # Test translation manager
        print("\n3. Testing translation manager:")
        from unified.translators.manager import TranslationManager
        manager = TranslationManager()
        print(f"  ✓ TranslationManager created with {len(manager.engines)} engines")
        
        print("\n✅ Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_removed_files():
    """Check that refactored files were removed."""
    print("\n\nChecking that refactored files were removed...")
    
    refactored_files = [
        "core/auth_refactored.py",
        "core/config_refactored.py", 
        "core/pattern_loader_refactored.py",
        "api/auth_refactored.py",
        "translators/manager_refactored.py"
    ]
    
    all_removed = True
    for file in refactored_files:
        if os.path.exists(file):
            print(f"  ✗ {file} still exists!")
            all_removed = False
        else:
            print(f"  ✓ {file} removed")
    
    if all_removed:
        print("\n✅ All refactored files removed!")
    else:
        print("\n⚠️  Some refactored files still exist")
    
    return all_removed

def check_backup():
    """Check that backup was created."""
    print("\n\nChecking backup directory...")
    
    deprecated_dir = Path("deprecated")
    if deprecated_dir.exists():
        backups = list(deprecated_dir.glob("backup_*"))
        if backups:
            latest_backup = sorted(backups)[-1]
            print(f"  ✓ Backup created at: {latest_backup}")
            
            # List backed up files
            backup_files = list(latest_backup.glob("*.py"))
            print(f"  ✓ {len(backup_files)} files backed up:")
            for f in backup_files:
                print(f"    - {f.name}")
            return True
    
    print("  ✗ No backup found")
    return False

def main():
    """Run all verification tests."""
    print("🔍 Verifying Phase 2 Migration")
    print("=" * 50)
    
    os.chdir(Path(__file__).parent)
    
    results = {
        "Imports": test_imports(),
        "Functionality": test_basic_functionality(),
        "Files Removed": check_removed_files(),
        "Backup Created": check_backup()
    }
    
    print("\n" + "=" * 50)
    print("📊 Migration Verification Summary:")
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✅ Migration verification complete - all tests passed!")
        print("\n📋 Next steps:")
        print("1. Run the full test suite: python -m pytest tests/")
        print("2. Start the backend server: python server.py")
        print("3. Test with the PWA frontend")
    else:
        print("\n⚠️  Some verification tests failed. Please review the output above.")

if __name__ == "__main__":
    main()