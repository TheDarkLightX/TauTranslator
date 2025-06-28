# Copyright (c) DarkLightX / Dana Edwards

"""
Configuration for external translation providers.

This module defines the available AI providers that the application can use for translation services.
It allows for a centralized place to manage provider details like names and supported models.
"""

from typing import Dict, Any

class ProviderConfig:
    """Manages the configuration for various translation providers."""

    def __init__(self):
        self._providers: Dict[str, Dict[str, Any]] = {
            'openai': {
                'name': 'OpenAI',
                'models': ['gpt-4-turbo', 'gpt-3.5-turbo'],
                'api_endpoint': 'https://api.openai.com/v1/chat/completions'
            },
            'anthropic': {
                'name': 'Anthropic',
                'models': ['claude-3-sonnet-20240229', 'claude-3-opus-20240229'],
                'api_endpoint': 'https://api.anthropic.com/v1/messages'
            },
            'huggingface_codegen': {
                'name': 'HuggingFace CodeGen',
                'models': ['Salesforce/codegen-350M-multi'],
                'api_endpoint': 'https://api-inference.huggingface.co/models/Salesforce/codegen-350M-multi'
            }
        }

    def get_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """Returns a dictionary of all configured providers."""
        return self._providers

    def get_provider(self, provider_id: str) -> Dict[str, Any]:
        """Returns the configuration for a specific provider."""
        return self._providers.get(provider_id)

# Singleton instance to be used throughout the application
provider_config = ProviderConfig()
