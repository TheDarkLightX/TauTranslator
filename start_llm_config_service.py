#!/usr/bin/env python3
"""
LLM Configuration Service Startup Script
========================================

Starts the FastAPI LLM Configuration Service on port 45311.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking LLM Configuration Service Dependencies...")
    
    required_packages = [
        ('fastapi', 'FastAPI framework'),
        ('uvicorn', 'ASGI server'),
        ('psutil', 'System resource monitoring'),
        ('huggingface_hub', 'Hugging Face model downloads')
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
        print("  pip install fastapi uvicorn psutil huggingface_hub")
        return False
    
    print("✅ All dependencies available")
    return True

def check_llm_service_files():
    """Check if LLM service files exist."""
    print("\n🔍 Checking LLM Configuration Service Files...")
    
    required_files = [
        'src/tau_translator_omega/llm_config_service/main.py',
        'src/tau_translator_omega/llm_config_service/models.py',
        'src/tau_translator_omega/llm_config_service/crud.py',
        'src/tau_translator_omega/llm_config_service/model_management.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All LLM service files available")
    return True

def start_llm_service():
    """Start the LLM Configuration Service."""
    print("\n🚀 Starting LLM Configuration Service...")
    print("=" * 50)
    
    try:
        # Run uvicorn directly
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.tau_translator_omega.llm_config_service.main:llm_app",
            "--host", "127.0.0.1",
            "--port", "45311",
            "--reload",
            "--log-level", "info"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start LLM service: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Service stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return 1

def show_usage_info():
    """Show usage information."""
    print("\n📖 LLM Configuration Service Information")
    print("=" * 45)
    print("🌐 Server URL: http://localhost:45311")
    print("📚 API Documentation: http://localhost:45311/docs")
    print("🔧 Alternative docs: http://localhost:45311/redoc")
    print("❤️  Health check: http://localhost:45311/api/llm-config/health")
    print("\n🔑 API Endpoints:")
    print("  GET  /api/system/resources - System resources")
    print("  GET  /api/gemma-models - Gemma model status")
    print("  POST /api/gemma-models/download - Download models")
    print("  GET  /api/llm-services - LLM service configurations")
    print("  POST /api/llm-services - Create LLM service")
    print("  POST /api/guidance/load-model - Load model with Guidance")
    print("  POST /api/lmql/run-query - Run LMQL query")
    print("\n🔄 To stop the server: Press Ctrl+C")

def main():
    """Main startup function."""
    print("🎯 LLM Configuration Service Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check service files
    if not check_llm_service_files():
        return 1
    
    # Show usage info
    show_usage_info()
    
    # Start the service
    return start_llm_service()

if __name__ == "__main__":
    sys.exit(main())
