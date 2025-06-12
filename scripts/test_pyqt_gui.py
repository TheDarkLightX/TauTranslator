#!/usr/bin/env python3
"""
PyQt GUI Test Runner
===================

Interactive test script for the Tau Translator PyQt GUI.
Tests basic functionality and provides a way to manually test the interface.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent  # Go up one level from scripts
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'ui'))

def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking PyQt GUI Dependencies...")
    print("=" * 50)
    
    dependencies = {
        'PyQt6': None,
        'PyQt5': None,
        'Backend': None,
        'Translator': None
    }
    
    # Check PyQt6 first
    try:
        import PyQt6.QtWidgets
        dependencies['PyQt6'] = True
        print("✅ PyQt6 is available")
    except ImportError:
        dependencies['PyQt6'] = False
        print("❌ PyQt6 not installed")
        
        # Try PyQt5 as fallback
        try:
            import PyQt5.QtWidgets
            dependencies['PyQt5'] = True
            print("✅ PyQt5 is available (fallback)")
        except ImportError:
            dependencies['PyQt5'] = False
            print("❌ PyQt5 not installed")
    
    # Check backend
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            dependencies['Backend'] = True
            print("✅ Backend is running")
        else:
            dependencies['Backend'] = False
            print("⚠️  Backend returned status:", response.status_code)
    except:
        dependencies['Backend'] = False
        print("⚠️  Backend not accessible (GUI will work in offline mode)")
    
    # Check translator
    try:
        from tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
        dependencies['Translator'] = True
        print("✅ Translator module available")
    except ImportError:
        dependencies['Translator'] = False
        print("⚠️  Translator module not found (mock mode will be used)")
    
    return dependencies


def run_pyqt_gui():
    """Run the PyQt GUI application."""
    print("\n🚀 Launching Tau Translator PyQt GUI...")
    print("=" * 50)
    
    try:
        # Try to import the PyQt GUI
        gui_path = project_root / 'ui' / 'tau_translator_desktop_qt.py'
        if gui_path.exists():
            # PyQt6 version
            try:
                from ui.tau_translator_desktop_qt import TauTranslatorQt, QApplication
                print("Using PyQt6 version")
            except ImportError:
                # Try PyQt5 fallback
                print("PyQt6 import failed, trying modified import...")
                # We'll need to modify imports for PyQt5
                return run_pyqt5_fallback()
        else:
            print(f"❌ GUI file not found: {gui_path}")
            return False
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Tau Translator")
        app.setOrganizationName("TauTranslator")
        
        # Create and show main window
        window = TauTranslatorQt()
        window.show()
        
        print("✅ GUI launched successfully!")
        print("\n📝 Test Instructions:")
        print("1. Try translating between Natural Language and Tau")
        print("2. Test the swap button")
        print("3. Try different themes (Ctrl+T)")
        print("4. Test file operations (New, Open, Save)")
        print("5. Check syntax highlighting for Tau code")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_pyqt5_fallback():
    """Run with PyQt5 compatibility mode."""
    print("\n🔄 Attempting PyQt5 compatibility mode...")
    
    # Create a modified version that works with PyQt5
    try:
        # Read the original file
        gui_path = project_root / 'ui' / 'tau_translator_desktop_qt.py'
        with open(gui_path, 'r') as f:
            content = f.read()
        
        # Replace PyQt6 imports with PyQt5
        content = content.replace('from PyQt6.QtWidgets', 'from PyQt5.QtWidgets')
        content = content.replace('from PyQt6.QtCore', 'from PyQt5.QtCore')
        content = content.replace('from PyQt6.QtGui', 'from PyQt5.QtGui')
        content = content.replace('QFont.Weight.Bold', 'QFont.Bold')
        content = content.replace('Qt.ToolButtonStyle.ToolButtonTextUnderIcon', 'Qt.ToolButtonTextUnderIcon')
        content = content.replace('Qt.AlignmentFlag.AlignCenter', 'Qt.AlignCenter')
        content = content.replace('Qt.MouseButton.LeftButton', 'Qt.LeftButton')
        content = content.replace('Qt.KeyboardModifier.ControlModifier', 'Qt.ControlModifier')
        
        # Write temporary file
        temp_file = project_root / 'ui' / 'tau_translator_desktop_qt_py5.py'
        with open(temp_file, 'w') as f:
            f.write(content)
        
        # Import and run
        from ui.tau_translator_desktop_qt_py5 import TauTranslatorQt
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = TauTranslatorQt()
        window.show()
        
        print("✅ PyQt5 compatibility mode activated!")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ PyQt5 fallback failed: {e}")
        return False


def run_tests():
    """Run automated tests if available."""
    print("\n🧪 Running PyQt GUI Tests...")
    print("=" * 50)
    
    try:
        import pytest
        test_file = project_root / 'tests' / 'ui' / 'test_tau_translator_qt_autocomplete.py'
        if test_file.exists():
            print(f"Running tests from {test_file}")
            pytest.main(['-v', str(test_file)])
        else:
            print("⚠️  Test file not found:", test_file)
    except ImportError:
        print("⚠️  pytest not installed, skipping automated tests")


def main():
    """Main entry point."""
    print("🎯 Tau Translator PyQt GUI Test Runner")
    print("=" * 50)
    
    # Check dependencies
    deps = check_dependencies()
    
    # Check if we can run
    if not deps['PyQt6'] and not deps['PyQt5']:
        print("\n❌ Cannot run GUI: No PyQt installation found")
        print("Install with: pip install PyQt6 or pip install PyQt5")
        return 1
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Run PyQt GUI")
    print("2. Run automated tests")
    print("3. Run both")
    print("Q. Quit")
    
    choice = input("\nSelect option (1/2/3/Q): ").strip().upper()
    
    if choice == '1':
        run_pyqt_gui()
    elif choice == '2':
        run_tests()
    elif choice == '3':
        run_tests()
        input("\nPress Enter to continue to GUI...")
        run_pyqt_gui()
    elif choice == 'Q':
        print("Exiting...")
        return 0
    else:
        print("Invalid choice")
        return 1


if __name__ == '__main__':
    sys.exit(main())