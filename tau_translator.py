#!/usr/bin/env python3
"""
TauTranslator - Unified Launcher

This is the main entry point for TauTranslator that provides access to all
available interfaces and ensures proper setup.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import Optional, List, Dict
import json


class TauTranslatorLauncher:
    """Unified launcher for TauTranslator applications."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config_file = self.root_dir / '.tau_translator_config.json'
        self.config = self._load_config()
        
        # Define canonical implementations
        self.APPLICATIONS = {
            'desktop': {
                'name': 'Desktop GUI (PyQt6)',
                'description': 'Full-featured PyQt6 desktop application with educational autocomplete',
                'path': 'ui/tau_translator_qt_educational_complete.py',
                'requires': ['PyQt6', 'requests'],
                'default': True
            },
            'web': {
                'name': 'Web Interface (React/Next.js)',
                'description': 'Progressive Web App - requires backend server',
                'path': 'pwa',
                'command': 'npm run dev',
                'requires': ['node', 'npm'],
                'needs_backend': True
            },
            'simple': {
                'name': 'Simple Desktop GUI (PyQt6)',
                'description': 'Lightweight PyQt6 interface with basic features',
                'path': 'ui/tau_translator_desktop_qt.py',
                'requires': ['PyQt6']
            },
            'cli': {
                'name': 'Command Line Interface',
                'description': 'Terminal-based translation tool',
                'path': 'backend/unified/english_to_tau_translator.py',
                'requires': []
            },
            'api': {
                'name': 'API Server (FastAPI)',
                'description': 'Backend REST API server with Swagger docs',
                'path': 'backend/unified/server.py',
                'requires': ['fastapi', 'uvicorn']
            }
        }
    
    def _load_config(self) -> Dict:
        """Load saved configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_config(self):
        """Save configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_python_version(self) -> bool:
        """Check if Python version is sufficient."""
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            print(f"   Current version: {sys.version}")
            return False
        return True
    
    def check_dependency(self, package: str) -> bool:
        """Check if a Python package is installed."""
        if package in ['node', 'npm']:
            # Check system commands
            try:
                subprocess.run([package, '--version'], 
                             capture_output=True, check=True)
                return True
            except:
                return False
        else:
            # Check Python packages
            try:
                __import__(package)
                return True
            except ImportError:
                return False
    
    def install_dependencies(self, packages: List[str]) -> bool:
        """Install missing Python dependencies."""
        python_packages = [p for p in packages if p not in ['node', 'npm']]
        
        if not python_packages:
            return True
        
        print(f"\n📦 Installing dependencies: {', '.join(python_packages)}")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'] + python_packages
            )
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("   Please install manually:")
            print(f"   pip install {' '.join(python_packages)}")
            return False
    
    def check_backend_running(self) -> bool:
        """Check if backend API server is running."""
        try:
            import requests
            response = requests.get('http://localhost:8000/health', timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def start_backend(self) -> Optional[subprocess.Popen]:
        """Start the backend API server."""
        print("\n🚀 Starting backend server...")
        
        server_path = self.root_dir / self.APPLICATIONS['api']['path']
        if not server_path.exists():
            print(f"❌ Backend server not found at {server_path}")
            return None
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(server_path)],
                cwd=server_path.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for server to start
            import time
            time.sleep(3)
            
            if self.check_backend_running():
                print("✅ Backend server started successfully")
                return process
            else:
                print("⚠️  Backend server started but not responding")
                return process
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return None
    
    def launch_application(self, app_type: str) -> bool:
        """Launch the specified application."""
        if app_type not in self.APPLICATIONS:
            print(f"❌ Unknown application type: {app_type}")
            return False
        
        app = self.APPLICATIONS[app_type]
        print(f"\n🚀 Launching {app['name']}...")
        print(f"   {app['description']}")
        
        # Check dependencies
        missing_deps = []
        for dep in app.get('requires', []):
            if not self.check_dependency(dep):
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
            
            if all(dep not in ['node', 'npm'] for dep in missing_deps):
                # Can install Python packages
                if not self.install_dependencies(missing_deps):
                    return False
            else:
                # System dependencies
                print("\n❌ Please install system dependencies:")
                if 'node' in missing_deps or 'npm' in missing_deps:
                    print("   - Node.js: https://nodejs.org/")
                return False
        
        # Check if backend is needed
        backend_process = None
        if app.get('needs_backend') and not self.check_backend_running():
            print("\n⚠️  This application requires the backend server")
            response = input("Start backend server? (y/n): ")
            if response.lower() == 'y':
                backend_process = self.start_backend()
                if not backend_process:
                    return False
            else:
                print("❌ Cannot proceed without backend server")
                return False
        
        # Launch the application
        try:
            if app_type == 'web':
                # Special handling for web app
                pwa_dir = self.root_dir / app['path']
                print(f"\n📂 Changing to PWA directory: {pwa_dir}")
                
                # Check if node_modules exists
                if not (pwa_dir / 'node_modules').exists():
                    print("📦 Installing npm dependencies...")
                    subprocess.run(['npm', 'install'], cwd=pwa_dir, check=True)
                
                # Start the dev server
                print("\n🌐 Starting web server at http://localhost:3000")
                subprocess.run(['npm', 'run', 'dev'], cwd=pwa_dir)
                
            else:
                # Python applications
                app_path = self.root_dir / app['path']
                if not app_path.exists():
                    print(f"❌ Application not found at {app_path}")
                    return False
                
                subprocess.run([sys.executable, str(app_path)])
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using TauTranslator!")
            return True
        except Exception as e:
            print(f"\n❌ Failed to launch application: {e}")
            return False
        finally:
            # Clean up backend process if we started it
            if backend_process:
                print("\n🛑 Stopping backend server...")
                backend_process.terminate()
    
    def show_menu(self):
        """Show interactive menu."""
        print("\n" + "=" * 60)
        print("TauTranslator - Choose Your Interface")
        print("=" * 60)
        
        for key, app in self.APPLICATIONS.items():
            default = " (default)" if app.get('default') else ""
            print(f"\n[{key}] {app['name']}{default}")
            print(f"    {app['description']}")
        
        print("\n[q] Quit")
        print("=" * 60)
        
        # Get saved preference
        default_choice = self.config.get('default_app', 'desktop')
        
        choice = input(f"\nEnter your choice [{default_choice}]: ").strip().lower()
        
        if not choice:
            choice = default_choice
        
        if choice == 'q':
            return None
        
        if choice in self.APPLICATIONS:
            # Save preference
            save_default = input("Save as default? (y/n): ").strip().lower()
            if save_default == 'y':
                self.config['default_app'] = choice
                self._save_config()
        
        return choice
    
    def run_first_time_setup(self):
        """Run first-time setup wizard."""
        print("\n🎉 Welcome to TauTranslator!")
        print("This appears to be your first time running the application.")
        print("\nLet's set up your environment...")
        
        # Install core dependencies
        core_deps = ['PyQt6', 'requests', 'fastapi', 'uvicorn']
        print(f"\n📦 Installing core dependencies...")
        
        if self.install_dependencies(core_deps):
            print("\n✅ Setup complete!")
            self.config['setup_complete'] = True
            self._save_config()
        else:
            print("\n⚠️  Setup incomplete. Some features may not work.")
    
    def run(self, app_type: Optional[str] = None):
        """Main entry point."""
        print("TauTranslator - Unified Launcher")
        print("================================")
        
        # Check Python version
        if not self.check_python_version():
            return 1
        
        # First time setup
        if not self.config.get('setup_complete'):
            self.run_first_time_setup()
        
        # Launch specific app or show menu
        if app_type:
            # Direct launch
            if app_type not in self.APPLICATIONS:
                print(f"❌ Unknown application: {app_type}")
                print(f"   Available: {', '.join(self.APPLICATIONS.keys())}")
                return 1
            
            success = self.launch_application(app_type)
            return 0 if success else 1
        else:
            # Interactive menu
            while True:
                choice = self.show_menu()
                if choice is None:
                    break
                
                if choice in self.APPLICATIONS:
                    self.launch_application(choice)
                    break
                else:
                    print(f"\n❌ Invalid choice: {choice}")
        
        return 0


def main():
    """Command line entry point."""
    parser = argparse.ArgumentParser(
        description='TauTranslator - Formal Specification Language Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available interfaces:
  desktop    - Full-featured PyQt6 desktop application (default)
  web        - React/Next.js Progressive Web App (requires backend)
  simple     - Lightweight PyQt6 desktop GUI
  cli        - Command line interface
  api        - FastAPI REST server only

Examples:
  tau_translator                # Show interactive menu
  tau_translator desktop        # Launch desktop GUI directly
  tau_translator web           # Start web interface
  tau_translator --list        # List all available interfaces
        """
    )
    
    parser.add_argument(
        'interface',
        nargs='?',
        choices=['desktop', 'web', 'simple', 'cli', 'api'],
        help='Interface to launch'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available interfaces'
    )
    
    args = parser.parse_args()
    
    launcher = TauTranslatorLauncher()
    
    if args.list:
        print("\nAvailable TauTranslator Interfaces:")
        print("=" * 50)
        for key, app in launcher.APPLICATIONS.items():
            print(f"\n{key}:")
            print(f"  Name: {app['name']}")
            print(f"  Description: {app['description']}")
            print(f"  Requires: {', '.join(app.get('requires', ['None']))}")
        return 0
    
    return launcher.run(args.interface)


if __name__ == '__main__':
    sys.exit(main())