#!/usr/bin/env python3
"""
TauTranslator Setup Script

Installs TauTranslator and creates system-wide launcher.

Copyright: DarkLightX/Dana Edwards
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from setuptools import setup, find_packages


# Project metadata
PROJECT_NAME = "tau-translator"
VERSION = "1.0.0"
DESCRIPTION = "Educational tool for learning formal specification languages (TAU/TCE)"
AUTHOR = "DarkLightX/Dana Edwards"
PYTHON_REQUIRES = ">=3.8"

# Dependencies
INSTALL_REQUIRES = [
    "PyQt6>=6.0.0",
    "requests>=2.25.0",
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
    "aiofiles>=0.8.0",
]

EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=6.0',
        'pytest-asyncio',
        'black',
        'flake8',
        'mypy',
    ],
    'nlp': [
        'spacy>=3.0',
        'transformers>=4.0',
    ]
}


def create_desktop_entry():
    """Create desktop entry for Linux systems."""
    if platform.system() != 'Linux':
        return
    
    desktop_entry = """[Desktop Entry]
Version=1.0
Type=Application
Name=Tau Translator
Comment=Educational tool for formal specification languages
Exec=tau-translator desktop
Icon=tau-translator
Terminal=false
Categories=Development;Education;
StartupNotify=true
"""
    
    # Create desktop entry
    desktop_dir = Path.home() / '.local' / 'share' / 'applications'
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = desktop_dir / 'tau-translator.desktop'
    desktop_file.write_text(desktop_entry)
    
    print(f"✅ Created desktop entry: {desktop_file}")


def create_macos_app():
    """Create macOS application bundle."""
    if platform.system() != 'Darwin':
        return
    
    # This would create a .app bundle for macOS
    # For now, just create a launcher script
    script_content = """#!/bin/bash
cd "$(dirname "$0")"
python3 -m tau_translator desktop
"""
    
    app_dir = Path('/usr/local/bin')
    if app_dir.exists():
        launcher = app_dir / 'tau-translator'
        try:
            launcher.write_text(script_content)
            launcher.chmod(0o755)
            print(f"✅ Created macOS launcher: {launcher}")
        except PermissionError:
            print("⚠️  Could not create global launcher (permission denied)")


def create_windows_shortcuts():
    """Create Windows shortcuts."""
    if platform.system() != 'Windows':
        return
    
    # Create batch file launcher
    batch_content = """@echo off
python -m tau_translator %*
"""
    
    # Try to add to PATH or create in Scripts
    scripts_dir = Path(sys.prefix) / 'Scripts'
    if scripts_dir.exists():
        batch_file = scripts_dir / 'tau-translator.bat'
        batch_file.write_text(batch_content)
        print(f"✅ Created Windows launcher: {batch_file}")


def post_install():
    """Run post-installation tasks."""
    print("\n🎉 TauTranslator Installation Complete!")
    print("=" * 50)
    
    # Create platform-specific shortcuts
    if platform.system() == 'Linux':
        create_desktop_entry()
    elif platform.system() == 'Darwin':
        create_macos_app()
    elif platform.system() == 'Windows':
        create_windows_shortcuts()
    
    print("\n📚 Quick Start:")
    print("  - Run 'tau-translator' to launch the application")
    print("  - Run 'tau-translator --help' for options")
    print("  - Run 'tau-translator desktop' for the GUI")
    print("  - Run 'tau-translator web' for the web interface")
    
    print("\n🎯 Features:")
    print("  - Educational system with progress tracking")
    print("  - Intelligent autocomplete for TAU/TCE")
    print("  - Multiple interfaces: PyQt6, React, CLI")
    print("  - Achievement system and skill monitoring")
    
    print("\n📖 Documentation:")
    print("  - README.md - General overview")
    print("  - README_UNIFIED.md - Unified edition guide")
    print("  - docs/ - Detailed documentation")
    
    print("\n✨ Enjoy learning formal specification languages!")


# Custom install command
from setuptools.command.install import install

class PostInstallCommand(install):
    """Custom installation command."""
    
    def run(self):
        install.run(self)
        post_install()


if __name__ == '__main__':
    # Read long description from README
    readme_path = Path(__file__).parent / 'README.md'
    long_description = readme_path.read_text() if readme_path.exists() else DESCRIPTION
    
    setup(
        name=PROJECT_NAME,
        version=VERSION,
        author=AUTHOR,
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/DarkLightX/TauTranslator',
        
        # Package configuration
        packages=find_packages(exclude=['tests', 'tests.*', 'venv', 'venv.*']),


        
        # Include non-Python files
        include_package_data=True,
        package_data={
            '': ['*.json', '*.yaml', '*.lark', '*.md'],
            'tau_translator': ['ui/*.py', 'pwa/*'],
        },
        
        # Scripts
        entry_points={
            'console_scripts': [
                'tau-translator=tau_translator:main',
            ],
        },
        
        # Dependencies
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        
        # Metadata
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Education',
            'Intended Audience :: Developers',
            'Topic :: Education',
            'Topic :: Software Development :: Interpreters',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
        ],
        
        # Custom commands
        cmdclass={
            'install': PostInstallCommand,
        },
    )