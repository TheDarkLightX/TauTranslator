#!/usr/bin/env python3
"""
Start NLP Demo
=============

Launches the integrated NLP system with web interface for demonstration.

Author: DarklightX (Dana Edwards)
"""

import subprocess
import time
import webbrowser
import sys
import os
import signal
from pathlib import Path

# Track processes for cleanup
processes = []

def cleanup():
    """Clean up all started processes."""
    print("\n🛑 Shutting down services...")
    for proc in processes:
        try:
            if proc.poll() is None:  # Still running
                proc.terminate()
                proc.wait(timeout=5)
        except:
            pass
    print("✅ All services stopped")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    cleanup()
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def start_service(name, command, cwd=None):
    """Start a service and track it."""
    print(f"🚀 Starting {name}...")
    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(proc)
        time.sleep(2)  # Give service time to start
        
        # Check if still running
        if proc.poll() is None:
            print(f"✅ {name} started successfully")
            return True
        else:
            print(f"❌ {name} failed to start")
            return False
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return False

def main():
    """Main startup sequence."""
    print("🎯 TauTranslator NLP Demo Launcher")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    
    # 1. Start integrated NLP backend
    if start_service(
        "Integrated NLP Backend",
        "python3 backend/integrated_nlp_backend.py --port 8000",
        cwd=project_root
    ):
        print("   📍 Backend: http://localhost:8000/health")
    
    # 2. Start the working backend (for fallback)
    if start_service(
        "Working Backend (Fallback)",
        "python3 deprecated/working_backend.py",
        cwd=project_root
    ):
        print("   📍 Fallback: http://localhost:8003")
    
    # 3. Start PWA web interface
    pwa_dir = project_root / "pwa"
    if pwa_dir.exists():
        if start_service(
            "PWA Web Interface", 
            "npm run dev",
            cwd=pwa_dir
        ):
            print("   📍 Web UI: http://localhost:3000")
            time.sleep(3)  # Give Next.js time to compile
            
            # Open browser
            print("\n🌐 Opening web browser...")
            webbrowser.open("http://localhost:3000")
    
    print("\n✅ All services started!")
    print("\n📝 Quick Test Instructions:")
    print("1. Go to http://localhost:3000 in your browser")
    print("2. Enter 'Always x is true' in the left panel")
    print("3. Select 'Plain English' → 'Tau Language Code'")
    print("4. Click 'Translate'")
    print("5. You should see: 'always (x is true)' with confidence score")
    
    print("\n💡 Features to Try:")
    print("- Translation: Type natural language and translate to Tau")
    print("- Confidence: See NLP confidence scores")
    print("- Patterns: Various temporal and boolean expressions")
    
    print("\n🛑 Press Ctrl+C to stop all services")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    main()