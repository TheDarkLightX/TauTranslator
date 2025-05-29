#!/usr/bin/env python3
"""
TauTranslatorOmega Backend Startup Script
=========================================

Easy startup script for the FastAPI backend with dependency checking.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking FastAPI Backend Dependencies...")
    
    required_packages = [
        ('fastapi', 'FastAPI framework'),
        ('uvicorn', 'ASGI server'),
        ('pydantic', 'Data validation'),
        ('cryptography', 'Encryption (optional but recommended)')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with:")
        print("  pip install -r backend_requirements.txt")
        print("  OR")
        print("  sudo apt install python3-fastapi python3-uvicorn python3-cryptography")
        return False
    
    print("✅ All dependencies available")
    return True

def check_secure_components():
    """Check if secure components are available."""
    print("\n🔍 Checking Secure Components...")
    
    components = [
        ('secure_core.py', 'Secure storage implementation'),
        ('provider_config.py', 'Provider configuration'),
        ('fallback_secure_manager.py', 'Fallback security (optional)')
    ]
    
    missing_components = []
    
    for component, description in components:
        if Path(component).exists():
            print(f"✅ {component} - {description}")
        else:
            print(f"❌ {component} - {description} - MISSING")
            missing_components.append(component)
    
    if missing_components:
        print(f"\n⚠️  Missing components: {', '.join(missing_components)}")
        print("These files should be in the same directory as this script.")
        return False
    
    print("✅ All secure components available")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("\n🚀 Starting TauTranslatorOmega FastAPI Backend...")
    print("=" * 50)
    
    try:
        # Import and run the backend
        from backend_server import main
        return main()
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure backend_server.py is in the current directory")
        return 1
    
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return 1

def show_usage_info():
    """Show usage information."""
    print("\n📖 FastAPI Backend Usage Information")
    print("=" * 40)
    print("🌐 Server URL: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Alternative docs: http://localhost:8000/redoc")
    print("❤️  Health check: http://localhost:8000/health")
    print("\n🔑 API Endpoints:")
    print("  POST /auth - Authenticate with master password")
    print("  POST /api/translate - Translate text")
    print("  GET  /api/providers - List AI providers")
    print("  POST /api/providers/{id}/key - Set API key")
    print("  DELETE /api/providers/{id}/key - Remove API key")
    print("\n🔄 To stop the server: Press Ctrl+C")

def main():
    """Main startup function."""
    print("🎯 TauTranslatorOmega FastAPI Backend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check secure components
    if not check_secure_components():
        return 1
    
    # Show usage info
    show_usage_info()
    
    # Start the backend
    return start_backend()

if __name__ == "__main__":
    sys.exit(main())
