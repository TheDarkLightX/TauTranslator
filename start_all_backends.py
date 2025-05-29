#!/usr/bin/env python3
"""
Complete Backend Startup Script
===============================

Starts all FastAPI backend services for TauTranslatorOmega PWA integration.
"""

import sys
import subprocess
import os
import time
import signal
from pathlib import Path
from threading import Thread

def check_port_available(port):
    """Check if a port is available."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False

def start_service_in_thread(service_name, command, port):
    """Start a service in a separate thread."""
    print(f"🚀 Starting {service_name} on port {port}...")
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"[{service_name}] {line.strip()}")
        
        process.wait()
        
    except Exception as e:
        print(f"❌ Error starting {service_name}: {e}")

def main():
    """Main startup function."""
    print("🎯 TauTranslatorOmega Complete Backend Startup")
    print("=" * 50)
    
    # Check if ports are available
    services = [
        ("Main Translation Backend", 8000),
        ("LLM Configuration Service", 45311)
    ]
    
    for service_name, port in services:
        if not check_port_available(port):
            print(f"❌ Port {port} is already in use ({service_name})")
            print(f"   Please stop the service running on port {port} or use a different port")
            return 1
    
    print("✅ All required ports are available")
    
    # Define service commands
    commands = {
        "Main Backend": [
            sys.executable, "-m", "uvicorn",
            "backend_server:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ],
        "LLM Config": [
            sys.executable, "-m", "uvicorn",
            "src.tau_translator_omega.llm_config_service.main:llm_app",
            "--host", "127.0.0.1",
            "--port", "45311",
            "--reload",
            "--log-level", "info"
        ]
    }
    
    print("\n🚀 Starting All Backend Services...")
    print("=" * 40)
    
    # Start services in separate threads
    threads = []
    processes = []
    
    try:
        for service_name, command in commands.items():
            print(f"Starting {service_name}...")
            
            # Start process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            processes.append((service_name, process))
            
            # Give it a moment to start
            time.sleep(2)
        
        print("\n✅ All services started!")
        print("\n📖 Service Information:")
        print("=" * 30)
        print("🔐 Main Translation Backend:")
        print("   URL: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
        print("   Health: http://localhost:8000/health")
        print("\n🔧 LLM Configuration Service:")
        print("   URL: http://localhost:45311")
        print("   Docs: http://localhost:45311/docs")
        print("   Health: http://localhost:45311/api/llm-config/health")
        print("\n🌐 PWA Frontend:")
        print("   Start with: cd pwa && npm run dev")
        print("   URL: http://localhost:3000")
        print("\n🔄 Press Ctrl+C to stop all services")
        
        # Wait for user interrupt
        try:
            while True:
                # Check if any process has died
                for service_name, process in processes:
                    if process.poll() is not None:
                        print(f"\n❌ {service_name} has stopped unexpectedly")
                        return 1
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️  Stopping all services...")
            
            # Terminate all processes
            for service_name, process in processes:
                print(f"Stopping {service_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"Force killing {service_name}...")
                    process.kill()
            
            print("✅ All services stopped")
            return 0
    
    except Exception as e:
        print(f"❌ Error managing services: {e}")
        
        # Clean up any running processes
        for service_name, process in processes:
            try:
                process.terminate()
            except:
                pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
