#!/usr/bin/env python3
"""
Simple Test Backend
==================

Minimal FastAPI backend to test if the basic setup works.
"""

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    app = FastAPI(title="Test Backend")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "message": "Simple test backend is working",
            "secureStorageAvailable": False,
            "cryptoAvailable": False,
            "configuredProviders": []
        }
    
    @app.post("/auth")
    async def test_auth(request: dict):
        return {
            "authenticated": True,
            "sessionToken": "test_token_123",
            "message": "Test authentication successful"
        }
    
    @app.post("/api/translate")
    async def test_translate(request: dict):
        source_text = request.get("sourceText", "")
        return {
            "translatedText": f"[TEST BACKEND] Mock translation of: {source_text}",
            "provider": "test_backend",
            "model": "mock",
            "processingTime": 0.1
        }

def main():
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available. Install with:")
        print("   pip install fastapi uvicorn")
        return 1
    
    print("🧪 Starting Simple Test Backend on port 8000...")
    print("📖 Endpoints:")
    print("   GET  /health - Health check")
    print("   POST /auth - Test authentication")
    print("   POST /api/translate - Test translation")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
