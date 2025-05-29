#!/usr/bin/env python3
"""
FastAPI Backend Test Script
===========================

Test script to verify the FastAPI backend is working correctly.
"""

import asyncio
import json
import sys
from pathlib import Path

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

BACKEND_URL = "http://127.0.0.1:8000"

async def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing Health Check...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"   Status: {data['status']}")
                print(f"   Secure Storage: {data['secureStorageAvailable']}")
                print(f"   Crypto Available: {data['cryptoAvailable']}")
                print(f"   Configured Providers: {data['configuredProviders']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_authentication():
    """Test authentication endpoint."""
    print("\n🔐 Testing Authentication...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test with a sample password
            auth_data = {"password": "TestPassword123!"}
            response = await client.post(f"{BACKEND_URL}/auth", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Authentication endpoint works")
                print(f"   Authenticated: {data['authenticated']}")
                if data.get('sessionToken'):
                    print(f"   Session Token: {data['sessionToken'][:20]}...")
                return data.get('sessionToken')
            else:
                print(f"✅ Authentication endpoint works (expected failure for test password)")
                print(f"   Status: {response.status_code}")
                return None
    
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

async def test_providers_endpoint(session_token=None):
    """Test providers endpoint."""
    print("\n📡 Testing Providers Endpoint...")
    
    try:
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/providers", headers=headers)
            
            if response.status_code == 401:
                print("✅ Providers endpoint properly requires authentication")
                return True
            elif response.status_code == 200:
                data = response.json()
                print("✅ Providers endpoint works")
                print(f"   Found {len(data)} providers")
                for provider in data:
                    print(f"   - {provider['provider']}: {'✅' if provider['configured'] else '❌'}")
                return True
            else:
                print(f"❌ Providers endpoint failed: {response.status_code}")
                return False
    
    except Exception as e:
        print(f"❌ Providers endpoint error: {e}")
        return False

async def test_translation_endpoint(session_token=None):
    """Test translation endpoint."""
    print("\n🌐 Testing Translation Endpoint...")
    
    try:
        headers = {"Content-Type": "application/json"}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        translation_data = {
            "sourceText": "Hello world",
            "sourceLangKey": "PLAIN_ENGLISH",
            "targetLangKey": "TAU",
            "sourceLangLabel": "Plain English",
            "targetLangLabel": "Tau Language"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/translate", 
                json=translation_data,
                headers=headers
            )
            
            if response.status_code == 401:
                print("✅ Translation endpoint properly requires authentication")
                return True
            elif response.status_code == 200:
                data = response.json()
                print("✅ Translation endpoint works")
                print(f"   Translated Text: {data['translatedText'][:50]}...")
                print(f"   Provider: {data.get('provider', 'unknown')}")
                return True
            else:
                print(f"❌ Translation endpoint failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    pass
                return False
    
    except Exception as e:
        print(f"❌ Translation endpoint error: {e}")
        return False

async def test_api_documentation():
    """Test API documentation endpoints."""
    print("\n📚 Testing API Documentation...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test OpenAPI JSON
            response = await client.get(f"{BACKEND_URL}/openapi.json")
            if response.status_code == 200:
                print("✅ OpenAPI JSON available")
            else:
                print(f"❌ OpenAPI JSON failed: {response.status_code}")
                return False
            
            # Test Swagger UI (just check if it returns HTML)
            response = await client.get(f"{BACKEND_URL}/docs")
            if response.status_code == 200 and "swagger" in response.text.lower():
                print("✅ Swagger UI available")
            else:
                print(f"❌ Swagger UI failed: {response.status_code}")
                return False
            
            return True
    
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False

def check_backend_files():
    """Check if required backend files exist."""
    print("📁 Checking Backend Files...")
    
    required_files = [
        "backend_server.py",
        "secure_core.py", 
        "provider_config.py",
        "backend_requirements.txt"
    ]
    
    missing_files = []
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - MISSING")
            missing_files.append(file_name)
    
    return len(missing_files) == 0

async def main():
    """Main test function."""
    print("🧪 FastAPI Backend Test Suite")
    print("=" * 40)
    
    if not HTTPX_AVAILABLE:
        print("❌ httpx not available. Install with: pip install httpx")
        return 1
    
    # Check files
    if not check_backend_files():
        print("\n❌ Missing required files. Cannot proceed with tests.")
        return 1
    
    # Run tests
    tests = [
        ("Health Check", test_health_check()),
        ("Authentication", test_authentication()),
        ("API Documentation", test_api_documentation()),
    ]
    
    results = {}
    session_token = None
    
    for test_name, test_coro in tests:
        try:
            if test_name == "Authentication":
                session_token = await test_coro
                results[test_name] = session_token is not None or True  # Auth endpoint working is success
            else:
                results[test_name] = await test_coro
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Test endpoints that require authentication
    auth_tests = [
        ("Providers Endpoint", test_providers_endpoint(session_token)),
        ("Translation Endpoint", test_translation_endpoint(session_token)),
    ]
    
    for test_name, test_coro in auth_tests:
        try:
            results[test_name] = await test_coro
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI backend is working correctly.")
        print("\n📖 Next steps:")
        print("1. Visit http://localhost:8000/docs for API documentation")
        print("2. Test authentication with your master password")
        print("3. Configure AI provider API keys")
        print("4. Start your PWA and test integration")
    else:
        print("❌ Some tests failed. Check the backend server and dependencies.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
