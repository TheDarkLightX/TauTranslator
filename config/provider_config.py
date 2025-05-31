#!/usr/bin/env python3
"""
Provider Configuration
======================

Configuration for AI providers with OpenRouter emphasis.
"""

class ProviderConfig:
    """Configuration for AI providers."""
    
    def __init__(self):
        self.providers = {
            "openrouter": {
                "name": "OpenRouter",
                "description": "Access 100+ AI models with one API key (Recommended)",
                "url": "https://openrouter.ai/keys",
                "models": [
                    "openai/gpt-4-turbo",
                    "meta-llama/llama-3.1-8b-instruct", 
                    "google/gemini-pro-1.5",
                    "meta-llama/llama-3.1-70b-instruct",
                    "mistralai/mistral-large"
                ],
                "example": "sk-or-v1-...",
                "priority": 1,
                "recommended": True,
                "benefits": [
                    "100+ models with one key",
                    "Often 50-80% cheaper than direct APIs",
                    "No multiple subscriptions needed",
                    "Latest models automatically available"
                ]
            },
            "openai": {
                "name": "OpenAI Direct",
                "description": "Direct OpenAI API access",
                "url": "https://platform.openai.com/api-keys",
                "models": ["gpt-4-turbo", "gpt-3.5-turbo", "gpt-4"],
                "example": "sk-...",
                "priority": 2,
                "benefits": [
                    "Direct access to OpenAI models",
                    "Guaranteed availability",
                    "Official support"
                ]
            },
            "google": {
                "name": "Google AI Direct",
                "description": "Direct Google AI API access",
                "url": "https://aistudio.google.com/app/apikey",
                "models": ["gemini-pro", "gemini-1.5-flash"],
                "example": "AIza...",
                "priority": 3,
                "benefits": [
                    "Direct access to Google models",
                    "Advanced reasoning capabilities",
                    "Long context windows"
                ]
            }
        }
    
    def get_provider(self, provider_id: str) -> dict:
        """Get provider configuration."""
        return self.providers.get(provider_id, {})
    
    def get_all_providers(self) -> dict:
        """Get all provider configurations."""
        return self.providers
    
    def get_sorted_providers(self) -> list:
        """Get providers sorted by priority."""
        return sorted(
            self.providers.items(),
            key=lambda x: x[1].get('priority', 999)
        )
    
    def validate_key_format(self, provider_id: str, api_key: str) -> bool:
        """Validate API key format for provider."""
        if provider_id == "openrouter":
            return api_key.startswith("sk-or-v1-") and len(api_key) > 20
        elif provider_id == "openai":
            return (api_key.startswith("sk-") and 
                   not api_key.startswith("sk-ant-") and 
                   len(api_key) > 20)
        elif provider_id == "anthropic":
            return api_key.startswith("sk-ant-") and len(api_key) > 20
        elif provider_id == "google":
            return api_key.startswith("AIza") and len(api_key) > 20
        
        return len(api_key) > 10  # Basic check for others
    
    def get_validation_error(self, provider_id: str, api_key: str) -> str:
        """Get validation error message."""
        provider = self.get_provider(provider_id)
        expected = provider.get("example", "valid API key")
        
        if not api_key:
            return "API key cannot be empty"
        
        if not self.validate_key_format(provider_id, api_key):
            return f"Invalid format. Expected: {expected}"
        
        return ""  # No error

# Global instance
provider_config = ProviderConfig()
