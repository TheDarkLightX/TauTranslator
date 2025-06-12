#!/usr/bin/env python3
"""
Demo Script for PyQt AutoComplete GUI
====================================

Quick demo to test the PyQt GUI with autocomplete functionality.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import subprocess
from pathlib import Path

def check_pyqt():
    """Check which PyQt version is available."""
    try:
        import PyQt6
        return "PyQt6"
    except ImportError:
        try:
            import PyQt5
            return "PyQt5"
        except ImportError:
            return None

def main():
    print("🎯 Tau Translator PyQt AutoComplete Demo")
    print("=" * 50)
    
    # Check PyQt availability
    pyqt_version = check_pyqt()
    
    if not pyqt_version:
        print("❌ No PyQt installation found!")
        print("\nTo install PyQt, run one of:")
        print("  pip install PyQt6")
        print("  pip install PyQt5")
        return 1
    
    print(f"✅ Found {pyqt_version}")
    
    print("\n📝 Demo Features:")
    print("1. AutoComplete for TAU and CNL languages")
    print("2. Syntax highlighting for TAU")
    print("3. Language swapping")
    print("4. Mock translation")
    
    print("\n🚀 Launching GUI...")
    
    # Run the autocomplete version
    project_root = Path(__file__).parent.parent
    gui_file = project_root / "ui" / "tau_translator_desktop_qt_autocomplete.py"
    
    if gui_file.exists():
        if pyqt_version == "PyQt5":
            print("⚠️  Note: The GUI uses PyQt6. PyQt5 compatibility may require modifications.")
        
        try:
            subprocess.run([sys.executable, str(gui_file)], check=True)
        except KeyboardInterrupt:
            print("\n✅ GUI closed")
        except Exception as e:
            print(f"❌ Error: {e}")
            
            # Try the regular version
            print("\n🔄 Trying regular PyQt GUI...")
            regular_gui = project_root / "ui" / "tau_translator_desktop_qt.py"
            if regular_gui.exists():
                try:
                    subprocess.run([sys.executable, str(regular_gui)], check=True)
                except Exception as e2:
                    print(f"❌ Regular GUI also failed: {e2}")
    else:
        print(f"❌ GUI file not found: {gui_file}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())