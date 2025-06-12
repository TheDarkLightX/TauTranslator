#!/usr/bin/env python3
"""
Master Demo Runner for TauTranslator
===================================

Lists and runs all available demos for the TauTranslator project.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import subprocess
from pathlib import Path

# Demo scripts information
DEMOS = [
    {
        "name": "PyQt GUI with AutoComplete",
        "script": "demo_pyqt_autocomplete.py",
        "description": "Desktop GUI with real-time autocomplete for TAU/CNL",
        "requirements": ["PyQt6 or PyQt5"]
    },
    {
        "name": "NLP GUI Demo",
        "script": "demos/nlp_gui_demo.py",
        "description": "NLP translation features with GUI",
        "requirements": ["tkinter", "NLP models"]
    },
    {
        "name": "Dictionary Loading Demo",
        "script": "../examples/demo_dictionary_loading.py",
        "description": "Shows how to load custom dictionaries",
        "requirements": []
    },
    {
        "name": "NLP Features Demo",
        "script": "../examples/demo_nlp_features.py",
        "description": "Demonstrates NLP translation capabilities",
        "requirements": ["NLP integration"]
    },
    {
        "name": "Memory Optimization Demo",
        "script": "../examples/demo_memory_optimization.py",
        "description": "Shows memory-efficient translation",
        "requirements": []
    },
    {
        "name": "SIMD Processing Demo",
        "script": "../examples/demo_simd_processing.py",
        "description": "Demonstrates SIMD performance optimizations",
        "requirements": ["numpy"]
    },
    {
        "name": "UI Features Demo",
        "script": "../examples/demo_ui_features.py",
        "description": "Shows various UI components",
        "requirements": ["tkinter or PyQt"]
    },
    {
        "name": "LMQL Translator Demo",
        "script": "../examples/demo_lmql_translator.py",
        "description": "LMQL-based translation demo",
        "requirements": ["lmql"]
    }
]

def print_header():
    """Print demo runner header."""
    print("=" * 60)
    print("🎯 TauTranslator Demo Runner")
    print("=" * 60)
    print()

def list_demos():
    """List all available demos."""
    print("📋 Available Demos:\n")
    for i, demo in enumerate(DEMOS, 1):
        print(f"{i}. {demo['name']}")
        print(f"   📄 {demo['description']}")
        if demo['requirements']:
            print(f"   📦 Requirements: {', '.join(demo['requirements'])}")
        print()

def run_demo(demo_info):
    """Run a specific demo."""
    script_path = Path(__file__).parent / demo_info['script']
    
    if not script_path.exists():
        print(f"❌ Demo script not found: {script_path}")
        return False
    
    print(f"\n🚀 Running: {demo_info['name']}")
    print(f"📄 Script: {script_path}")
    print("-" * 60)
    
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\n⚠️  Demo exited with error")
        return False
    except KeyboardInterrupt:
        print(f"\n✅ Demo closed by user")
        return True
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        return False

def main():
    """Main demo runner."""
    print_header()
    
    while True:
        list_demos()
        print("Options:")
        print("  1-{} : Run specific demo".format(len(DEMOS)))
        print("  A    : Run all demos in sequence")
        print("  Q    : Quit")
        print()
        
        choice = input("Select option: ").strip().upper()
        
        if choice == 'Q':
            print("👋 Goodbye!")
            break
        elif choice == 'A':
            print("\n🎬 Running all demos...\n")
            for i, demo in enumerate(DEMOS, 1):
                print(f"\n[{i}/{len(DEMOS)}] {demo['name']}")
                if not run_demo(demo):
                    if input("\nContinue with next demo? (Y/n): ").strip().lower() == 'n':
                        break
                else:
                    input("\nPress Enter for next demo...")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(DEMOS):
                    run_demo(DEMOS[idx])
                    input("\nPress Enter to continue...")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a number or A/Q")
        
        print("\n" + "=" * 60 + "\n")

if __name__ == '__main__':
    main()