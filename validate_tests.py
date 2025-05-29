#!/usr/bin/env python3
"""
Test Validation Script
======================

Validates that the test suite is properly structured and can run.
"""

import sys
import os
import importlib.util
from pathlib import Path

def validate_test_structure():
    """Validate test file structure."""
    print("🔍 Validating Test Structure...")
    
    # Check if test file exists
    test_file = Path("test_secure_core.py")
    if not test_file.exists():
        print("❌ test_secure_core.py not found")
        return False
    
    print("✅ test_secure_core.py exists")
    
    # Check if secure_core exists
    core_file = Path("secure_core.py")
    if not core_file.exists():
        print("❌ secure_core.py not found")
        return False
    
    print("✅ secure_core.py exists")
    
    return True

def validate_imports():
    """Validate that imports work."""
    print("\n🔍 Validating Imports...")
    
    try:
        # Test secure_core import
        spec = importlib.util.spec_from_file_location("secure_core", "secure_core.py")
        secure_core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(secure_core)
        
        print("✅ secure_core imports successfully")
        
        # Check CRYPTO_AVAILABLE
        if hasattr(secure_core, 'CRYPTO_AVAILABLE'):
            print(f"✅ CRYPTO_AVAILABLE: {secure_core.CRYPTO_AVAILABLE}")
        else:
            print("❌ CRYPTO_AVAILABLE not found")
            return False
        
        # Check SecureStorage class
        if hasattr(secure_core, 'SecureStorage'):
            print("✅ SecureStorage class found")
            
            # Try to instantiate (this will test basic functionality)
            if secure_core.CRYPTO_AVAILABLE:
                storage = secure_core.SecureStorage()
                print("✅ SecureStorage instantiates successfully")
                
                # Test basic methods
                info = storage.get_storage_info()
                print("✅ get_storage_info() works")
                print(f"   Directory: {info['directory']}")
                print(f"   Encryption: {info['encryption']}")
                
                # Test is_first_time
                first_time = storage.is_first_time()
                print(f"✅ is_first_time(): {first_time}")
                
            else:
                print("⚠️  Cryptography not available - limited testing")
        else:
            print("❌ SecureStorage class not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_test_file():
    """Validate test file structure."""
    print("\n🔍 Validating Test File Structure...")
    
    try:
        # Read test file
        with open("test_secure_core.py", 'r') as f:
            content = f.read()
        
        # Check for required imports
        required_imports = [
            'import pytest',
            'from secure_core import SecureStorage',
            'from unittest.mock import Mock, patch'
        ]
        
        for imp in required_imports:
            if imp in content:
                print(f"✅ Found: {imp}")
            else:
                print(f"❌ Missing: {imp}")
                return False
        
        # Check for test classes
        test_classes = [
            'TestSecureStorageFixtures',
            'TestSecureStorageInitialization',
            'TestSecureStorageKeyDerivation',
            'TestSecureStorageAPIKeyManagement',
            'TestSecureStorageSecurityProperties'
        ]
        
        for test_class in test_classes:
            if f"class {test_class}" in content:
                print(f"✅ Found test class: {test_class}")
            else:
                print(f"❌ Missing test class: {test_class}")
                return False
        
        # Count test methods
        test_methods = content.count('def test_')
        print(f"✅ Found {test_methods} test methods")
        
        if test_methods < 50:
            print("⚠️  Expected at least 50 test methods")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading test file: {e}")
        return False

def validate_configuration():
    """Validate test configuration files."""
    print("\n🔍 Validating Configuration Files...")
    
    config_files = {
        'pytest.ini': 'Pytest configuration',
        'test_requirements.txt': 'Test dependencies',
        'run_tests.py': 'Test runner script'
    }
    
    all_exist = True
    for file_name, description in config_files.items():
        if Path(file_name).exists():
            print(f"✅ {description}: {file_name}")
        else:
            print(f"❌ Missing {description}: {file_name}")
            all_exist = False
    
    return all_exist

def run_basic_test():
    """Run a basic test to verify functionality."""
    print("\n🔍 Running Basic Functionality Test...")
    
    try:
        # Import and test basic functionality
        spec = importlib.util.spec_from_file_location("secure_core", "secure_core.py")
        secure_core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(secure_core)
        
        if not secure_core.CRYPTO_AVAILABLE:
            print("⚠️  Cryptography not available - skipping crypto tests")
            return True
        
        # Test basic SecureStorage functionality
        storage = secure_core.SecureStorage()
        
        # Test random bytes generation
        random_bytes = storage._secure_random_bytes(32)
        if len(random_bytes) == 32:
            print("✅ _secure_random_bytes() works")
        else:
            print("❌ _secure_random_bytes() failed")
            return False
        
        # Test key derivation
        password = "test_password"
        salt = b'A' * 32
        key = storage._derive_key(password, salt)
        if len(key) == 32:
            print("✅ _derive_key() works")
        else:
            print("❌ _derive_key() failed")
            return False
        
        # Test deterministic key derivation
        key2 = storage._derive_key(password, salt)
        if key == key2:
            print("✅ Key derivation is deterministic")
        else:
            print("❌ Key derivation is not deterministic")
            return False
        
        # Test storage info
        info = storage.get_storage_info()
        required_keys = ['directory', 'encryption', 'key_derivation']
        for key in required_keys:
            if key in info:
                print(f"✅ Storage info contains {key}")
            else:
                print(f"❌ Storage info missing {key}")
                return False
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main validation function."""
    print("🧪 TauTranslatorOmega Test Suite Validation")
    print("=" * 50)
    
    validations = [
        ("Test Structure", validate_test_structure),
        ("Imports", validate_imports),
        ("Test File", validate_test_file),
        ("Configuration", validate_configuration),
        ("Basic Functionality", run_basic_test)
    ]
    
    results = {}
    for name, validation_func in validations:
        try:
            results[name] = validation_func()
        except Exception as e:
            print(f"❌ {name} validation failed with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\nNext steps:")
        print("1. Install test dependencies: pip install -r test_requirements.txt")
        print("2. Run tests: python3 run_tests.py --mode unit")
        print("3. View coverage: open htmlcov/index.html")
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("\nPlease fix the issues above before running tests.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
