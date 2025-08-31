# Copyright (c) DarkLightX / Dana Edwards

"""
Core translation service for TauTranslator.
Encapsulates translation engines, parsing, and interaction with AI providers.
"""

import logging
import asyncio
from typing import Dict, Optional

import httpx
from returns.result import Result, Success, Failure

# Project-specific imports
from backend.services.auth_service import AuthService
from backend.api_models import TranslationRequest, TranslationResponse
from backend.config.provider_config import provider_config

# Placeholder for translation engine imports
try:
    from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
    from tau_translator_omega.core_engine.translators.tce_tau_translator import TCETauTranslator
    from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
    from tau_translator_omega.gemma3 import translator as gemma3_translator
    TRANSLATION_ENGINES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Could not import one or more translation engines: {e}. Internal translation will be disabled.")
    LMQLBidirectionalTranslator, TCETauTranslator, CNLParser, gemma3_translator = None, None, None, None
    TRANSLATION_ENGINES_AVAILABLE = False

logger = logging.getLogger(__name__)

# --- Custom Error Types ---

class TranslationServiceError(Exception):
    """Base class for translation service errors."""
    pass

class ProviderError(TranslationServiceError):
    """Error related to an external AI provider."""
    pass

class EngineError(TranslationServiceError):
    """Error related to an internal translation engine."""
    pass

# --- Service Class ---

class TranslationService:
    """
    Manages all translation logic, including internal engines and external providers.
    """
    def __init__(self, auth_service: AuthService):
        if not isinstance(auth_service, AuthService) or not auth_service.storage:
            raise ValueError("TranslationService requires an initialized AuthService with active storage.")
        self.auth_service = auth_service
        self.storage = auth_service.storage
        
        # Initialize internal engines
        self.lmql_translator, self.tce_tau_translator, self.cnl_parser, self.gemma3_available = self._initialize_translation_engines()

    # --- Orchestrator Method ---

    async def translate_text_with_service(self, request: TranslationRequest) -> Result[TranslationResponse, TranslationServiceError]:
        """Orchestrates the translation process based on the request."""
        logger.info(f"Executing translation: {request.source_lang} -> {request.target_lang} via provider '{request.provider}'")

        if request.provider and request.provider != 'default':
            # Use a specific AI provider
            api_key_result = self._get_api_key_for_provider_from_storage(request.provider)
            if isinstance(api_key_result, Failure):
                return api_key_result # Propagate error
            
            translation_result = await self._translate_with_ai_provider_async(
                request, request.provider, api_key_result.unwrap()
            )
        else:
            # Use internal engines
            translation_result = await self._translate_with_internal_engines_async(request)

        # If all attempts fail, return a final error
        if isinstance(translation_result, Failure):
            logger.error(f"All translation attempts failed for the request. Error: {translation_result.failure()}")
        
        return translation_result

    # --- Implementation Details: Engine Initialization ---

    def _initialize_translation_engines(self) -> tuple:
        """Initializes and returns available translation engines."""
        if not TRANSLATION_ENGINES_AVAILABLE:
            return None, None, None, False
        
        try:
            lmql = LMQLBidirectionalTranslator()
            tce = TCETauTranslator()
            cnl = CNLParser(debug=False)
            gemma3 = gemma3_translator.check_gemma3_availability()
            logger.info("Internal translation engines initialized successfully.")
            return lmql, tce, cnl, gemma3
        except Exception as e:
            logger.exception(f"Error during translation engine initialization: {e}")
            return None, None, None, False

    # --- Implementation Details: Translation Logic ---

    def _get_api_key_for_provider_from_storage(self, provider_id: str) -> Result[str, ProviderError]:
        """Retrieves a provider's API key from secure storage."""
        api_key = self.storage.get_api_key(provider_id)
        if not api_key:
            return Failure(ProviderError(f"API key for provider '{provider_id}' not configured."))
        return Success(api_key)

    async def _translate_with_internal_engines_async(self, request: TranslationRequest) -> Result[TranslationResponse, EngineError]:
        """Translates text using the best available internal engine."""
        if not TRANSLATION_ENGINES_AVAILABLE:
            return Failure(EngineError("Internal translation engines are not available."))
        
        # Simple routing logic
        try:
            if request.source_lang == 'TCE' and request.target_lang == 'TAU' and self.tce_tau_translator:
                translated_text = self.tce_tau_translator.translate(request.text)
            elif request.source_lang == 'PLAIN_ENGLISH' and request.target_lang == 'CNL' and self.cnl_parser:
                translated_text = self.cnl_parser.parse_to_cnl(request.text)
            elif self.lmql_translator:
                translated_text = await self.lmql_translator.translate(request.text, request.source_lang, request.target_lang)
            else:
                return Failure(EngineError("No suitable internal engine found for the requested translation."))
            
            return Success(TranslationResponse(translated_text=translated_text, provider="internal_engine"))
        except Exception as e:
            logger.exception(f"An internal engine failed during translation: {e}")
            return Failure(EngineError(f"Internal engine error: {e}"))

    async def _translate_with_ai_provider_async(self, request: TranslationRequest, provider: str, api_key: str) -> Result[TranslationResponse, ProviderError]:
        """Translates text using a specified external AI provider."""
        system_prompt = "You are an expert translator for technical and formal languages. Translate accurately, preserving intent."
        user_prompt = f"Translate from {request.source_lang} to {request.target_lang}:\n\n{request.text}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                if provider == 'openai':
                    response_text = await self._call_openai_api_async(client, api_key, system_prompt, user_prompt)
                elif provider == 'anthropic':
                    response_text = await self._call_anthropic_api_async(client, api_key, system_prompt, user_prompt)
                else:
                    return Failure(ProviderError(f"Unsupported AI provider: {provider}"))
            
            return Success(TranslationResponse(translated_text=response_text, provider=provider))
        except Exception as e:
            logger.exception(f"AI provider '{provider}' failed: {e}")
            return Failure(ProviderError(f"Error with provider {provider}: {e}"))

    # --- Implementation Details: External API Calls ---

    async def _call_openai_api_async(self, client: httpx.AsyncClient, key: str, system_prompt: str, user_prompt: str) -> str:
        """Calls the OpenAI Chat Completions API."""
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "gpt-4-turbo",
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0.2, "max_tokens": 1024
            }
        )
        response.raise_for_status() # Raise exception for 4xx/5xx responses
        return response.json()['choices'][0]['message']['content'].strip()

    async def _call_anthropic_api_async(self, client: httpx.AsyncClient, key: str, system_prompt: str, user_prompt: str) -> str:
        """Calls the Anthropic Messages API."""
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            json={
                "model": "claude-3-sonnet-20240229",
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
                "temperature": 0.2, "max_tokens": 1024
            }
        )
        response.raise_for_status()
        return response.json()['content'][0]['text'].strip()
