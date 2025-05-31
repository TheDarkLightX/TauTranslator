#!/usr/bin/env python3
"""
Backend Status Checker
======================

Quick script to check if the FastAPI backends are running.
"""

import requests
import sys

def check_port(port, service_name):
    """Check if a service is running on a specific port."""
    try:
        response = requests.get(f'http://127.0.0.1:{port}/health', timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} (Port {port}): ONLINE")
            try:
                data = response.json()
                print(f"   Status: {data.get('status', 'unknown')}")
                if 'translationEngines' in data:
                    engines = data['translationEngines']
                    print(f"   Translation Engines: {sum(engines.values())}/{len(engines)} available")
            except:
                pass
            return True
        else:
            print(f"❌ {service_name} (Port {port}): ERROR (HTTP {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {service_name} (Port {port}): OFFLINE")
        return False
    except Exception as e:
        print(f"❌ {service_name} (Port {port}): ERROR - {e}")
        return False

def check_pwa_proxy():
    """Check if PWA proxy is working."""
    try:
        response = requests.get('http://127.0.0.1:3000/health', timeout=5)
        if response.status_code == 200:
            print("✅ PWA Proxy (Port 3000): WORKING")
            return True
        else:
            print(f"❌ PWA Proxy (Port 3000): ERROR (HTTP {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ PWA Proxy (Port 3000): OFFLINE")
        return False
    except Exception as e:
        print(f"❌ PWA Proxy (Port 3000): ERROR - {e}")
        return False

def main():
    """Main status check function."""
    print("🔍 TauTranslatorOmega Backend Status Check")
    print("=" * 45)
    
    # Check individual backends
    main_backend = check_port(8000, "Main Translation Backend")
    llm_service = check_port(45311, "LLM Configuration Service")
    
    print("\n🌐 PWA Integration Check")
    print("-" * 25)
    pwa_proxy = check_pwa_proxy()
    
    print("\n📊 Summary")
    print("-" * 10)
    
    if main_backend and llm_service and pwa_proxy:
        print("🎉 All services are running correctly!")
        print("✅ Your PWA should work with full backend integration")
    elif main_backend or llm_service:
        print("⚠️  Some services are running")
        if not main_backend:
            print("❌ Main backend needed for authentication and translation")
        if not llm_service:
            print("❌ LLM service needed for model management")
        if not pwa_proxy:
            print("❌ PWA not accessible - check if 'npm run dev' is running")
    else:
        print("❌ No backends are running")
        print("\n🚀 To start all backends:")
        print("   cd ~/TauTranslator")
        print("   python3 start_all_backends.py")
        print("\n🌐 To start PWA:")
        print("   cd ~/TauTranslator/pwa")
        print("   npm run dev")
    
    print("\n🔧 Troubleshooting")
    print("-" * 15)
    print("• Check if ports 8000, 45311, 3000 are free:")
    print("  netstat -tlnp | grep -E ':(8000|45311|3000)'")
    print("• Check for Python/Node.js processes:")
    print("  ps aux | grep -E '(python|node|uvicorn)'")
    print("• Kill stuck processes if needed:")
    print("  pkill -f uvicorn")
    print("  pkill -f 'npm run dev'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Status check interrupted")
        sys.exit(1)
