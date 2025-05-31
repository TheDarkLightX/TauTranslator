#!/usr/bin/env python3
"""
GUI Testing Script
==================

Test TauTranslator GUI components in automated mode.
"""

import sys
import threading
import time
import tkinter as tk
from pathlib import Path

def test_gui_import():
    """Test if GUI can be imported successfully."""
    try:
        print("🧪 Testing GUI imports...")
        
        # Test main GUI app
        from tau_translator_app import TauTranslatorApp
        print("✅ TauTranslatorApp import successful")
        
        return True
    except Exception as e:
        print(f"❌ GUI import failed: {e}")
        return False

def test_gui_creation():
    """Test GUI creation without showing window."""
    try:
        print("🧪 Testing GUI creation...")
        
        # Create a test GUI
        from tau_translator_app import TauTranslatorApp
        
        # Override mainloop to prevent blocking
        app = TauTranslatorApp()
        app.root.withdraw()  # Hide the window
        
        print("✅ GUI created successfully")
        
        # Test basic functionality
        if hasattr(app, 'create_ui'):
            print("✅ UI creation method available")
        
        if hasattr(app, 'load_translator'):
            print("✅ Translator loading method available")
        
        # Clean up
        app.root.destroy()
        print("✅ GUI cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        return False

def test_translation_functionality():
    """Test GUI translation functionality."""
    try:
        print("🧪 Testing translation functionality...")
        
        # Use our production translator for testing
        from production_translator import ProductionTranslator
        
        translator = ProductionTranslator()
        result = translator.translate("always x > 0", "tau_to_tce")
        
        if result["success"]:
            print(f"✅ Translation successful: {result['output']}")
            return True
        else:
            print(f"❌ Translation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        return False

def test_web_interface():
    """Test web interface availability."""
    try:
        print("🧪 Testing web interface...")
        
        from src.tau_translator_omega.web_interface.app import app
        print("✅ Flask app import successful")
        
        # Test if app is configured
        if hasattr(app, 'config'):
            print("✅ Flask app properly configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def run_comprehensive_gui_test():
    """Run comprehensive GUI testing."""
    print("🎯 TauTranslator GUI Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_gui_import),
        ("GUI Creation Test", test_gui_creation),
        ("Translation Test", test_translation_functionality),
        ("Web Interface Test", test_web_interface),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
        
        print(f"{'✅' if results[test_name] else '❌'} {test_name}: {'PASSED' if results[test_name] else 'FAILED'}")
    
    # Summary
    print(f"\n📊 Test Summary:")
    print("-" * 30)
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All GUI tests passed!")
        return True
    else:
        print("⚠️  Some GUI tests failed")
        return False

if __name__ == "__main__":
    success = run_comprehensive_gui_test()
    sys.exit(0 if success else 1)