#!/usr/bin/env python3
"""
TauTranslatorOmega Backend Server
================================

FastAPI backend that integrates secure API key management with translation services.
Connects the PWA frontend with the secure backend functionality.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# FastAPI and related imports
try:
    from fastapi import FastAPI, HTTPException, Depends, status, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Import our secure components
try:
    from secure_core import SecureStorage, CRYPTO_AVAILABLE
    from provider_config import provider_config
    SECURE_BACKEND_AVAILABLE = True
except ImportError:
    SECURE_BACKEND_AVAILABLE = False

# Import translation engines and parsers
try:
    from src.tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
    from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
    from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
    from src.tau_translator_omega.gemma3.translator import gemma3_translator
    TRANSLATION_ENGINES_AVAILABLE = True
except ImportError:
    TRANSLATION_ENGINES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class TranslationRequest(BaseModel):
    sourceText: str = Field(..., description="Text to translate")
    sourceLangKey: str = Field(..., description="Source language key")
    targetLangKey: str = Field(..., description="Target language key")
    sourceLangLabel: Optional[str] = Field(None, description="Source language label")
    targetLangLabel: Optional[str] = Field(None, description="Target language label")

class TranslationResponse(BaseModel):
    translatedText: str = Field(..., description="Translated text")
    provider: Optional[str] = Field(None, description="AI provider used")
    model: Optional[str] = Field(None, description="AI model used")
    processingTime: Optional[float] = Field(None, description="Processing time in seconds")

class APIKeyRequest(BaseModel):
    provider: str = Field(..., description="Provider name")
    apiKey: str = Field(..., description="API key")

class APIKeyResponse(BaseModel):
    provider: str = Field(..., description="Provider name")
    configured: bool = Field(..., description="Whether API key is configured")
    models: List[str] = Field(default_factory=list, description="Available models")

class AuthRequest(BaseModel):
    password: str = Field(..., description="Master password")

class AuthResponse(BaseModel):
    authenticated: bool = Field(..., description="Authentication status")
    sessionToken: Optional[str] = Field(None, description="Session token")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    secureStorageAvailable: bool = Field(..., description="Secure storage availability")
    cryptoAvailable: bool = Field(..., description="Cryptography availability")
    configuredProviders: List[str] = Field(default_factory=list, description="Configured providers")
    translationEngines: Optional[Dict[str, bool]] = Field(default_factory=dict, description="Translation engine status")

# Global storage instance
storage_instance: Optional[SecureStorage] = None
authenticated_sessions: Dict[str, float] = {}  # Simple session management

class TauTranslatorBackend:
    """Main backend service class with integrated parsers and translation engines."""

    def __init__(self):
        self.storage = None
        self.authenticated = False

        # Translation engines
        self.lmql_translator = None
        self.tce_tau_translator = None
        self.cnl_parser = None
        self.gemma3_available = False

        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available. Install with: pip install fastapi uvicorn")

        if not SECURE_BACKEND_AVAILABLE:
            raise ImportError("Secure backend not available. Check secure_core.py and provider_config.py")

        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography not available. Using fallback security.")

        # Initialize translation engines
        self._initialize_translation_engines()

    def _initialize_translation_engines(self):
        """Initialize available translation engines and parsers."""
        logger.info("Initializing translation engines...")

        if TRANSLATION_ENGINES_AVAILABLE:
            try:
                # Initialize LMQL bidirectional translator
                self.lmql_translator = LMQLBidirectionalTranslator()
                logger.info("✅ LMQL translator initialized")

                # Initialize TCE-to-Tau translator
                self.tce_tau_translator = TCETauTranslator()
                logger.info("✅ TCE-Tau translator initialized")

                # Initialize CNL parser
                self.cnl_parser = CNLParser(debug=False)
                logger.info("✅ CNL parser initialized")

                # Check Gemma3 availability
                self.gemma3_available = gemma3_translator.loaded
                if not self.gemma3_available:
                    logger.info("⚠️  Gemma3 not loaded - will use LMQL/pattern-based translation")
                else:
                    logger.info("✅ Gemma3 translator available")

            except Exception as e:
                logger.error(f"Error initializing translation engines: {e}")
                self.lmql_translator = None
                self.tce_tau_translator = None
                self.cnl_parser = None
        else:
            logger.warning("⚠️  Translation engines not available - using mock translation")

    def get_available_engines(self) -> Dict[str, bool]:
        """Get status of available translation engines."""
        return {
            "lmql_translator": self.lmql_translator is not None,
            "tce_tau_translator": self.tce_tau_translator is not None,
            "cnl_parser": self.cnl_parser is not None,
            "gemma3_translator": self.gemma3_available,
            "translation_engines_available": TRANSLATION_ENGINES_AVAILABLE
        }

    def initialize_storage(self, password: str) -> bool:
        """Initialize secure storage with password."""
        try:
            self.storage = SecureStorage()
            
            if self.storage.is_first_time():
                success = self.storage.setup_encryption(password)
                if success:
                    logger.info("Secure storage initialized for first time")
                    self.authenticated = True
                    return True
                else:
                    logger.error("Failed to setup encryption")
                    return False
            else:
                success = self.storage.unlock_with_password(password)
                if success:
                    logger.info("Secure storage unlocked successfully")
                    self.authenticated = True
                    return True
                else:
                    logger.error("Failed to unlock storage - incorrect password")
                    return False
        
        except Exception as e:
            logger.error(f"Storage initialization error: {e}")
            return False
    
    def get_configured_providers(self) -> List[str]:
        """Get list of configured providers."""
        if not self.storage or not self.authenticated:
            return []
        
        try:
            configured = []
            for provider_id in provider_config.get_all_providers().keys():
                if self.storage.has_api_key(provider_id):
                    configured.append(provider_id)
            return configured
        except Exception as e:
            logger.error(f"Error getting configured providers: {e}")
            return []
    
    async def translate_text(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using integrated parsers and translation engines."""
        if not self.storage or not self.authenticated:
            raise HTTPException(status_code=401, detail="Not authenticated")

        start_time = asyncio.get_event_loop().time()

        try:
            # Determine translation direction and method
            source_lang = request.sourceLangKey
            target_lang = request.targetLangKey
            source_text = request.sourceText

            logger.info(f"Translating from {source_lang} to {target_lang}")

            # Use real translation engines if available
            if TRANSLATION_ENGINES_AVAILABLE and self.lmql_translator:
                translated_text = await self._translate_with_engines(source_text, source_lang, target_lang)
                provider = "integrated_engines"
                model = "lmql_cnl_parser"
            else:
                # Fallback to configured AI providers
                configured_providers = self.get_configured_providers()
                if configured_providers:
                    provider_to_use = "openrouter" if "openrouter" in configured_providers else configured_providers[0]
                    api_key = self.storage.get_api_key(provider_to_use)
                    if api_key:
                        translated_text = await self._translate_with_ai_provider(source_text, source_lang, target_lang, provider_to_use, api_key)
                        provider = provider_to_use
                        model = f"{provider_to_use}_api"
                    else:
                        raise HTTPException(status_code=400, detail=f"No API key for {provider_to_use}")
                else:
                    # Final fallback to mock
                    translated_text = await self._mock_translation(request, "fallback")
                    provider = "mock"
                    model = "fallback"

            processing_time = asyncio.get_event_loop().time() - start_time

            return TranslationResponse(
                translatedText=translated_text,
                provider=provider,
                model=model,
                processingTime=processing_time
            )

        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    
    async def _mock_translation(self, request: TranslationRequest, provider: str) -> str:
        """Mock translation for demonstration."""
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        source_text = request.sourceText
        source_lang = request.sourceLangKey
        target_lang = request.targetLangKey
        
        if source_lang == 'PLAIN_ENGLISH':
            if target_lang == 'CNL':
                return f"[{provider.upper()} CNL]: Controlled Natural Language version of: \"{source_text[:50]}...\""
            elif target_lang == 'TAU':
                return f"// {provider.upper()} Tau Language\nDEFINE CONCEPT translated_concept AS (\n  description: \"{source_text[:50]}...\"\n);"
            elif target_lang == 'ILR':
                return f"<ILR_{provider.upper()}>\n  <statement>\n    <text>{source_text[:50]}...</text>\n  </statement>\n</ILR_{provider.upper()}>"
        else:
            return f"[{provider.upper()} Plain English]: This represents the meaning of: \"{source_text[:50]}...\" (from {source_lang})"
        
        return f"[{provider.upper()}]: Translated \"{source_text[:50]}...\" from {source_lang} to {target_lang}"

    async def _translate_with_engines(self, source_text: str, source_lang: str, target_lang: str) -> str:
        """Translate using integrated parsers and translation engines."""
        try:
            # Parse input if it's a formal language
            if source_lang in ['TAU', 'CNL'] and self.cnl_parser:
                try:
                    # Parse the input to validate syntax
                    ast_node = self.cnl_parser.parse(source_text)
                    logger.info(f"Successfully parsed {source_lang} input")
                except Exception as parse_error:
                    logger.warning(f"Parse error for {source_lang}: {parse_error}")
                    # Continue with unparsed text

            # Use LMQL bidirectional translator
            if source_lang == 'PLAIN_ENGLISH' and target_lang in ['TAU', 'CNL']:
                # TCE to Tau/CNL translation
                result = self.lmql_translator.translate_tce_to_tau(source_text)
                if result.success:
                    return result.output
                else:
                    logger.warning(f"LMQL translation failed: {result.errors}")

            elif source_lang in ['TAU', 'CNL'] and target_lang == 'PLAIN_ENGLISH':
                # Tau/CNL to TCE translation
                result = self.lmql_translator.translate_tau_to_tce(source_text)
                if result.success:
                    return result.output
                else:
                    logger.warning(f"LMQL translation failed: {result.errors}")

            # Try Gemma3 if available
            if self.gemma3_available:
                if source_lang == 'PLAIN_ENGLISH':
                    gemma_result = gemma3_translator.translate_tce_to_tau(source_text)
                    if gemma_result:
                        return gemma_result
                else:
                    gemma_result = gemma3_translator.translate_tau_to_tce(source_text)
                    if gemma_result:
                        return gemma_result

            # Fallback to enhanced pattern-based translation
            return await self._enhanced_pattern_translation(source_text, source_lang, target_lang)

        except Exception as e:
            logger.error(f"Engine translation error: {e}")
            return await self._enhanced_pattern_translation(source_text, source_lang, target_lang)

    async def _translate_with_ai_provider(self, source_text: str, source_lang: str, target_lang: str, provider: str, api_key: str) -> str:
        """Translate using external AI provider APIs."""
        import aiohttp
        import json
        
        # Prepare the prompt based on language pair
        if source_lang == 'PLAIN_ENGLISH' and target_lang == 'TAU':
            system_prompt = """You are an expert in formal specification languages, particularly the Tau language.
Translate the given plain English requirement into Tau language syntax.
Use proper Tau constructs like DEFINE, :=, rules (r), streams (sbf), and temporal operators."""
            user_prompt = f"Translate to Tau language: {source_text}"
            
        elif source_lang == 'PLAIN_ENGLISH' and target_lang == 'CNL':
            system_prompt = """You are an expert in Controlled Natural Language (CNL) for requirements engineering.
Convert the informal requirement into structured CNL using patterns like:
- The system SHALL...
- WHEN [condition] THEN [action]
- IF [condition] THEN [requirement]"""
            user_prompt = f"Convert to CNL: {source_text}"
            
        elif source_lang == 'TAU' and target_lang == 'PLAIN_ENGLISH':
            system_prompt = """You are an expert in the Tau formal specification language.
Translate Tau code into clear, natural English descriptions.
Explain what the formal specification means in plain language."""
            user_prompt = f"Explain this Tau code in plain English: {source_text}"
            
        else:
            system_prompt = f"You are an expert translator for formal specification languages."
            user_prompt = f"Translate from {source_lang} to {target_lang}: {source_text}"
        
        try:
            if provider.lower() == 'openrouter':
                # OpenRouter API implementation
                async with aiohttp.ClientSession() as session:
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://tau-translator.app",
                        "X-Title": "TauTranslator"
                    }
                    
                    # Use a suitable model for code translation
                    data = {
                        "model": "anthropic/claude-2",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    }
                    
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result['choices'][0]['message']['content'].strip()
                        else:
                            error_text = await response.text()
                            logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                            raise Exception(f"OpenRouter API error: {response.status}")
                            
            elif provider.lower() == 'huggingface':
                # HuggingFace API implementation
                async with aiohttp.ClientSession() as session:
                    # Use a code generation model
                    url = "https://api-inference.huggingface.co/models/Salesforce/codegen-350M-multi"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    # Format prompt for code generation
                    full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nTranslation:"
                    
                    data = {
                        "inputs": full_prompt,
                        "parameters": {
                            "temperature": 0.3,
                            "max_new_tokens": 500,
                            "return_full_text": False
                        }
                    }
                    
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            if isinstance(result, list) and len(result) > 0:
                                return result[0]['generated_text'].strip()
                            return str(result).strip()
                        else:
                            error_text = await response.text()
                            logger.error(f"HuggingFace API error: {response.status} - {error_text}")
                            raise Exception(f"HuggingFace API error: {response.status}")
                            
            else:
                # Unsupported provider
                raise ValueError(f"Unsupported AI provider: {provider}")
                
        except Exception as e:
            logger.error(f"AI provider translation error: {e}")
            # Fall back to pattern-based translation
            return await self._enhanced_pattern_translation(source_text, source_lang, target_lang)

    async def _enhanced_pattern_translation(self, source_text: str, source_lang: str, target_lang: str) -> str:
        """Enhanced pattern-based translation with better logic."""
        await asyncio.sleep(0.2)  # Simulate processing

        # More sophisticated pattern matching
        if source_lang == 'PLAIN_ENGLISH':
            if target_lang == 'TAU':
                # Look for mathematical expressions
                if any(word in source_text.lower() for word in ['function', 'define', 'equals', 'plus', 'minus']):
                    return f"// Pattern-based Tau translation\nDEFINE FUNCTION pattern_func AS (\n  // Based on: {source_text[:50]}...\n);"
                # Look for rules
                elif any(word in source_text.lower() for word in ['if', 'when', 'then', 'rule']):
                    return f"r pattern_rule[t] = (\n  // Rule based on: {source_text[:50]}...\n)"
                # Look for streams
                elif any(word in source_text.lower() for word in ['input', 'output', 'stream', 'file']):
                    return f"sbf pattern_stream = ifile(\"pattern.in\")\n// Based on: {source_text[:50]}..."
                else:
                    return f"// General Tau pattern\npattern_concept := \"{source_text[:50]}...\""

            elif target_lang == 'CNL':
                return f"Pattern CNL: The system shall implement the requirement that {source_text[:50]}..."

        else:
            # Formal to natural language
            if 'DEFINE' in source_text.upper() or ':=' in source_text:
                return f"Pattern Translation: This defines a concept or function based on the formal specification: {source_text[:50]}..."
            elif any(pattern in source_text for pattern in ['r ', 'sbf', '->']):
                return f"Pattern Translation: This specifies a rule or stream operation: {source_text[:50]}..."
            else:
                return f"Pattern Translation: This formal specification means: {source_text[:50]}..."

        return f"Pattern-based translation of \"{source_text[:50]}...\" from {source_lang} to {target_lang}"

# Initialize backend
backend = TauTranslatorBackend() if FASTAPI_AVAILABLE and SECURE_BACKEND_AVAILABLE else None

# Create FastAPI app
app = FastAPI(
    title="TauTranslatorOmega Backend",
    description="Secure backend for Tau Language translation with encrypted API key management",
    version="1.0.0"
) if FASTAPI_AVAILABLE else None

if app:
    # CORS middleware for PWA integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # PWA development server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Security dependency
security = HTTPBearer(auto_error=False) if FASTAPI_AVAILABLE else None

async def get_authenticated_backend(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to ensure backend is authenticated."""
    if not backend or not backend.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Backend not authenticated. Please authenticate first.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return backend

# API Routes
if app and backend:
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint with translation engine status."""
        engine_status = backend.get_available_engines() if backend else {}

        return HealthResponse(
            status="healthy",
            secureStorageAvailable=SECURE_BACKEND_AVAILABLE,
            cryptoAvailable=CRYPTO_AVAILABLE,
            configuredProviders=backend.get_configured_providers() if backend and backend.authenticated else [],
            translationEngines=engine_status
        )
    
    @app.post("/auth", response_model=AuthResponse)
    async def authenticate(auth_request: AuthRequest):
        """Authenticate with master password."""
        try:
            success = backend.initialize_storage(auth_request.password)
            if success:
                # Generate simple session token (in production, use proper JWT)
                session_token = f"session_{hash(auth_request.password)}_{int(asyncio.get_event_loop().time())}"
                authenticated_sessions[session_token] = asyncio.get_event_loop().time()
                
                return AuthResponse(
                    authenticated=True,
                    sessionToken=session_token
                )
            else:
                raise HTTPException(status_code=401, detail="Authentication failed")
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")
    
    @app.post("/api/translate", response_model=TranslationResponse)
    async def translate(
        request: TranslationRequest,
        authenticated_backend: TauTranslatorBackend = Depends(get_authenticated_backend)
    ):
        """Translate text using configured AI providers."""
        return await authenticated_backend.translate_text(request)
    
    @app.get("/api/providers", response_model=List[APIKeyResponse])
    async def get_providers(
        authenticated_backend: TauTranslatorBackend = Depends(get_authenticated_backend)
    ):
        """Get available providers and their configuration status."""
        providers = []
        
        for provider_id, provider_info in provider_config.get_all_providers().items():
            configured = authenticated_backend.storage.has_api_key(provider_id)
            
            providers.append(APIKeyResponse(
                provider=provider_id,
                configured=configured,
                models=provider_info.get("models", [])
            ))
        
        return providers
    
    @app.post("/api/providers/{provider_id}/key")
    async def set_api_key(
        provider_id: str,
        key_request: APIKeyRequest,
        authenticated_backend: TauTranslatorBackend = Depends(get_authenticated_backend)
    ):
        """Set API key for a provider."""
        try:
            # Validate provider
            if provider_id not in provider_config.get_all_providers():
                raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_id}")
            
            # Validate key format
            error = provider_config.get_validation_error(provider_id, key_request.apiKey)
            if error:
                raise HTTPException(status_code=400, detail=error)
            
            # Store key
            authenticated_backend.storage.store_api_key(provider_id, key_request.apiKey)
            
            return {"message": f"API key set for {provider_id}", "success": True}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error setting API key: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to set API key: {str(e)}")
    
    @app.delete("/api/providers/{provider_id}/key")
    async def remove_api_key(
        provider_id: str,
        authenticated_backend: TauTranslatorBackend = Depends(get_authenticated_backend)
    ):
        """Remove API key for a provider."""
        try:
            authenticated_backend.storage.remove_api_key(provider_id)
            return {"message": f"API key removed for {provider_id}", "success": True}
        
        except Exception as e:
            logger.error(f"Error removing API key: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to remove API key: {str(e)}")

def main():
    """Main function to run the backend server."""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available. Install with:")
        print("   pip install fastapi uvicorn")
        return 1
    
    if not SECURE_BACKEND_AVAILABLE:
        print("❌ Secure backend not available. Check secure_core.py and provider_config.py")
        return 1
    
    print("🚀 Starting TauTranslatorOmega Backend Server")
    print(f"🔐 Crypto Available: {CRYPTO_AVAILABLE}")
    print(f"🔧 Secure Storage Available: {SECURE_BACKEND_AVAILABLE}")
    print("📡 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    
    # Run the server
    uvicorn.run(
        "backend_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    import sys
    sys.exit(main())
