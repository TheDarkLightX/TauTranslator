#!/usr/bin/env python3
"""
TauTranslatorOmega Launcher
===========================

Simple launcher that checks dependencies and starts the GUI.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def install_basic_dependencies():
    """Install basic dependencies."""
    print("📦 Installing basic dependencies...")
    
    basic_deps = ["tkinter"]  # tkinter is usually built-in
    
    # Check if tkinter is available
    try:
        import tkinter
        print("✅ tkinter available")
    except ImportError:
        print("❌ tkinter not available - please install python3-tk")
        return False
    
    return True

def launch_gui():
    """Launch the GUI application."""
    print("🚀 Launching TauTranslatorOmega...")
    
    try:
        # Try to run the main GUI
        subprocess.run([sys.executable, "tau_translator_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch GUI: {e}")
        return False
    except FileNotFoundError:
        print("❌ tau_translator_app.py not found")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("🌍 TauTranslatorOmega Launcher")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return False
    
    # Check basic dependencies
    if not install_basic_dependencies():
        input("Press Enter to exit...")
        return False
    
    # Launch GUI
    if not launch_gui():
        input("Press Enter to exit...")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
