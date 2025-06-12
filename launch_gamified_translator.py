#!/usr/bin/env python3
"""
Launch script for Tau Translator Gamified Educational Edition

This script ensures all dependencies are available and launches
the complete gamified application.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check and install required dependencies."""
    required_packages = [
        'PyQt6',
        'requests',
        'aiofiles',
        'asyncio'
    ]
    
    print("Checking dependencies...")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is missing. Installing...")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ])
                print(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                print(f"Please install manually: pip install {package}")
                return False
    
    return True


def launch_application():
    """Launch the gamified translator."""
    # Get the UI script path
    ui_path = Path(__file__).parent / 'ui' / 'tau_translator_gamified_complete.py'
    
    if not ui_path.exists():
        print(f"❌ Could not find application at: {ui_path}")
        return False
    
    print("\n🚀 Launching Tau Translator - Educational Gamified Edition...")
    print("=" * 60)
    print("Features:")
    print("- 🎮 Gamification: Earn XP, unlock achievements, complete challenges")
    print("- 📚 Educational: Learn TAU/TCE with intelligent autocomplete")
    print("- 🏆 Progress Tracking: Monitor your learning journey")
    print("- ⚡ Real-time Feedback: See your progress as you learn")
    print("=" * 60)
    print()
    
    try:
        # Launch the application
        subprocess.run([sys.executable, str(ui_path)])
        return True
    except KeyboardInterrupt:
        print("\n👋 Thanks for using Tau Translator!")
        return True
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        return False


def main():
    """Main entry point."""
    print("Tau Translator - Educational Gamified Edition")
    print("=" * 45)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        print("Please install missing dependencies and try again")
        sys.exit(1)
    
    # Launch application
    if not launch_application():
        sys.exit(1)


if __name__ == '__main__':
    main()