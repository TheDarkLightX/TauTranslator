#!/usr/bin/env python3
"""
Run TAU Translator GUI
=====================

Simple launcher for the TAU Translator GUI.
Tries different versions in order of stability.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import subprocess
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent
    
    print("🎯 TAU Translator GUI Launcher")
    print("=" * 40)
    
    # List of GUI options in order of preference
    gui_options = [
        {
            "name": "Original PyQt GUI",
            "path": project_root / "ui" / "tau_translator_desktop_qt.py",
            "description": "Full-featured stable version"
        },
        {
            "name": "Simple PyQt Test",
            "path": project_root / "scripts" / "test_pyqt_simple.py",
            "description": "Minimal test window"
        },
        {
            "name": "AutoComplete GUI",
            "path": project_root / "ui" / "tau_translator_desktop_qt_autocomplete.py",
            "description": "Enhanced with autocomplete (experimental)"
        }
    ]
    
    # Check which are available
    available = []
    for option in gui_options:
        if option["path"].exists():
            available.append(option)
            print(f"✅ Found: {option['name']}")
        else:
            print(f"❌ Missing: {option['name']}")
    
    if not available:
        print("\n❌ No GUI files found!")
        return 1
    
    print("\nOptions:")
    for i, option in enumerate(available, 1):
        print(f"{i}. {option['name']} - {option['description']}")
    
    if len(available) == 1:
        choice = 1
        print(f"\nOnly one option available, launching {available[0]['name']}...")
    else:
        try:
            choice = int(input(f"\nSelect GUI to run (1-{len(available)}): "))
            if choice < 1 or choice > len(available):
                print("Invalid choice, using option 1")
                choice = 1
        except (ValueError, KeyboardInterrupt):
            print("\nUsing option 1")
            choice = 1
    
    selected = available[choice - 1]
    print(f"\n🚀 Launching {selected['name']}...")
    
    try:
        subprocess.run([sys.executable, str(selected["path"])], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ GUI exited with error code: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n✅ GUI closed by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())