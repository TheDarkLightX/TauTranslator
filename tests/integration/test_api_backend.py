#!/usr/bin/env python3
"""
Test API Backend for TauTranslator
=================================

Simple FastAPI backend for testing PWA integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

app = FastAPI(title="TauTranslator API", version="1.0.0")

# Enable CORS for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str = None
    direction: str = "tau_to_tce"
    sourceText: str = None
    sourceLangKey: str = None
    targetLangKey: str = None

class TranslationResponse(BaseModel):
    success: bool
    output: str
    confidence: float
    errors: Optional[list] = None
    warnings: Optional[list] = None

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "TauTranslator API"}

@app.post("/translate")
async def translate(request: TranslationRequest):
    """Translate between languages using PWA format."""
    try:
        # Handle PWA format
        text = request.sourceText or request.text
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Determine direction from PWA lang keys
        if request.sourceLangKey == "PLAIN_ENGLISH" and request.targetLangKey in ["TAU", "ILR", "CNL"]:
            direction = "tce_to_tau"
        elif request.sourceLangKey in ["TAU", "ILR", "CNL"] and request.targetLangKey == "PLAIN_ENGLISH":
            direction = "tau_to_tce"
        else:
            direction = request.direction
        
        # Import our production translator
        from production_translator import ProductionTranslator
        
        translator = ProductionTranslator()
        result = translator.translate(text, direction)
        
        # Return PWA-compatible format
        return {
            "translatedText": result["output"],
            "provider": "production_translator",
            "model": "pattern_based",
            "processingTime": 0.1,
            "secure": True
        }
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth")
async def authenticate(request: dict):
    """Mock authentication endpoint."""
    password = request.get("password", "")
    if not password:
        raise HTTPException(status_code=400, detail="Password required")
    
    # Mock authentication - accept any password
    return {
        "authenticated": True,
        "sessionToken": f"mock-token-{len(password)}",
        "message": "Authentication successful"
    }

@app.get("/examples")
async def get_examples():
    """Get example translations."""
    return {
        "examples": [
            {
                "tau": "always temperature > 20",
                "tce": "Always temperature greater than 20",
                "domain": "temperature_control"
            },
            {
                "tau": "r output[t] = input[t] & enable[t]",
                "tce": "Rule: output at time t equals input at time t AND enable at time t",
                "domain": "logic_gates"
            },
            {
                "tau": "sometimes pressure < 100",
                "tce": "Sometimes pressure less than 100",
                "domain": "pressure_monitoring"
            }
        ]
    }

@app.get("/status")
async def get_status():
    """Get system status."""
    try:
        from production_translator import ProductionTranslator
        translator = ProductionTranslator()
        
        # Test translation
        test_result = translator.translate("always x > 0", "tau_to_tce")
        
        return {
            "translator_available": True,
            "translation_test": test_result["success"],
            "version": "1.0.0",
            "framework": "pattern-based"
        }
    except Exception as e:
        return {
            "translator_available": False,
            "error": str(e),
            "version": "1.0.0"
        }

if __name__ == "__main__":
    print("🚀 Starting TauTranslator Test API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=False
    )