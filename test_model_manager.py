#!/usr/bin/env python3
"""
Test Model Manager
==================

Simple test to verify model manager functionality and debug issues.
"""

import sys
from pathlib import Path

def test_basic_imports():
    """Test basic Python imports."""
    print("🧪 Testing Basic Imports")
    print("-" * 30)
    
    try:
        import tkinter as tk
        print("✅ tkinter: Available")
    except ImportError as e:
        print(f"❌ tkinter: {e}")
        return False
    
    try:
        import json
        print("✅ json: Available")
    except ImportError as e:
        print(f"❌ json: {e}")
        return False
    
    try:
        import threading
        print("✅ threading: Available")
    except ImportError as e:
        print(f"❌ threading: {e}")
        return False
    
    try:
        import subprocess
        print("✅ subprocess: Available")
    except ImportError as e:
        print(f"❌ subprocess: {e}")
        return False
    
    return True

def test_model_manager_import():
    """Test model manager import."""
    print("\n🧪 Testing Model Manager Import")
    print("-" * 30)
    
    try:
        from model_manager import ModelManager
        print("✅ ModelManager: Import successful")
        return True
    except ImportError as e:
        print(f"❌ ModelManager: Import failed - {e}")
        return False
    except Exception as e:
        print(f"❌ ModelManager: Unexpected error - {e}")
        return False

def test_model_manager_creation():
    """Test model manager creation."""
    print("\n🧪 Testing Model Manager Creation")
    print("-" * 30)
    
    try:
        from model_manager import ModelManager
        
        def status_callback(message):
            print(f"Status: {message}")
        
        manager = ModelManager(status_callback=status_callback)
        print("✅ ModelManager: Created successfully")
        
        # Test dependency checking
        print("\n📦 Checking Dependencies:")
        deps = manager.check_dependencies()
        for package, installed in deps.items():
            status = "✅ Installed" if installed else "❌ Missing"
            print(f"  {package}: {status}")
        
        # Test model status
        print("\n🤖 Model Status:")
        status = manager.get_model_status()
        print(f"  Current model: {status['current']}")
        print(f"  Available models: {len(status['available'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ ModelManager creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependency_installation():
    """Test dependency installation (dry run)."""
    print("\n🧪 Testing Dependency Installation (Dry Run)")
    print("-" * 30)
    
    try:
        from model_manager import ModelManager
        
        manager = ModelManager()
        
        # Check what would be installed
        packages = ['torch', 'transformers', 'huggingface-hub', 'accelerate']
        
        print("Packages that would be installed:")
        for package in packages:
            try:
                __import__(package)
                print(f"  ✅ {package}: Already installed")
            except ImportError:
                print(f"  📦 {package}: Would be installed")
        
        return True
        
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        return False

def test_ui_creation():
    """Test UI creation."""
    print("\n🧪 Testing UI Creation")
    print("-" * 30)
    
    try:
        import tkinter as tk
        from model_manager import ModelManager, ModelManagerDialog
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create manager
        manager = ModelManager()
        
        # Try to create dialog (but don't show it)
        print("Creating ModelManagerDialog...")
        dialog = ModelManagerDialog(root, manager)
        dialog.dialog.withdraw()  # Hide the dialog
        
        print("✅ UI Creation: Successful")
        
        # Clean up
        dialog.dialog.destroy()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ UI Creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔧 Model Manager Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Model Manager Import", test_model_manager_import),
        ("Model Manager Creation", test_model_manager_creation),
        ("Dependency Installation", test_dependency_installation),
        ("UI Creation", test_ui_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Model Manager should work.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip3 install requests")
        print("- Check file permissions")
        print("- Ensure tkinter is available")

if __name__ == "__main__":
    main()
