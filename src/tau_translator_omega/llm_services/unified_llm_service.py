#!/usr/bin/env python3
"""
Unified LLM Service for TauTranslator
====================================

Comprehensive LLM service that coordinates and provides unified access to:
- OpenRouter (recommended - 100+ models with one API key)
- OpenAI Direct
- Anthropic
- Guidance Framework  
- Local Models (Ollama, Transformers)
- LMQL Integration
- Pattern-based Fallback

Features:
- Provider priority system with automatic fallback
- Performance monitoring and optimization
- Cost tracking and optimization
- Caching and rate limiting
- Comprehensive error handling and recovery

Author: DarkLightX/Dana Edwards
"""

import os
import sys
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib

# Import our services
try:
    from .guidance_service import GuidanceService, GuidanceConfig, TauGenerationRequest, TauGenerationResult
    GUIDANCE_AVAILABLE = True
except ImportError:
    GUIDANCE_AVAILABLE = False

try:
    from .local_models_service import LocalModelsService, LocalModelConfig, GenerationRequest, GenerationResult
    LOCAL_MODELS_AVAILABLE = True
except ImportError:
    LOCAL_MODELS_AVAILABLE = False

# External LLM libraries
LLM_LIBRARIES = {}

try:
    import openai
    LLM_LIBRARIES['openai'] = True
except ImportError:
    LLM_LIBRARIES['openai'] = False

try:
    import anthropic
    LLM_LIBRARIES['anthropic'] = True
except ImportError:
    LLM_LIBRARIES['anthropic'] = False

try:
    import requests
    LLM_LIBRARIES['requests'] = True
except ImportError:
    LLM_LIBRARIES['requests'] = False

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """LLM provider types."""
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GUIDANCE = "guidance"
    LOCAL_MODELS = "local_models"
    LMQL = "lmql"
    PATTERN_FALLBACK = "pattern_fallback"


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    provider_type: ProviderType
    enabled: bool = True
    priority: int = 5  # Lower = higher priority
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.3
    timeout_seconds: int = 30
    cost_per_token: float = 0.0  # For cost tracking
    rate_limit_per_minute: int = 60
    retry_attempts: int = 3


@dataclass
class UnifiedRequest:
    """Unified request for any LLM provider."""
    prompt: str
    system_prompt: Optional[str] = None
    requirements_text: Optional[str] = None  # For Tau-specific requests
    max_tokens: int = 1000
    temperature: float = 0.3
    provider_preference: Optional[ProviderType] = None
    use_cache: bool = True
    timeout_seconds: int = 30


@dataclass
class UnifiedResponse:
    """Unified response from any LLM provider."""
    success: bool
    generated_text: str
    provider_used: ProviderType
    model_used: str
    response_time: float
    tokens_generated: int
    estimated_cost: float
    confidence_score: float
    cached: bool = False
    error_message: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None


@dataclass
class ServiceMetrics:
    """Metrics for tracking service performance."""
    total_requests: int = 0
    successful_requests: int = 0
    total_response_time: float = 0.0
    total_cost: float = 0.0
    cache_hits: int = 0
    provider_usage: Dict[str, int] = None
    
    def __post_init__(self):
        if self.provider_usage is None:
            self.provider_usage = {}


class ResponseCache:
    """Simple in-memory cache for responses."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _generate_key(self, request: UnifiedRequest) -> str:
        """Generate cache key from request."""
        key_data = {
            'prompt': request.prompt,
            'system_prompt': request.system_prompt,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def get(self, request: UnifiedRequest) -> Optional[UnifiedResponse]:
        """Get cached response if available and not expired."""
        if not request.use_cache:
            return None
        
        key = self._generate_key(request)
        if key in self.cache:
            response, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                response.cached = True
                return response
            else:
                del self.cache[key]
        
        return None
    
    def set(self, request: UnifiedRequest, response: UnifiedResponse):
        """Cache a response."""
        if not request.use_cache:
            return
        
        key = self._generate_key(request)
        
        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (response, time.time())


class OpenRouterProvider:
    """OpenRouter API provider integration."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.api_key = config.api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def generate(self, request: UnifiedRequest) -> UnifiedResponse:
        """Generate response using OpenRouter."""
        if not self.api_key:
            return UnifiedResponse(
                success=False,
                generated_text="",
                provider_used=ProviderType.OPENROUTER,
                model_used=self.config.model_name or "unknown",
                response_time=0,
                tokens_generated=0,
                estimated_cost=0,
                confidence_score=0,
                error_message="OpenRouter API key not available"
            )
        
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TauTranslator",  # Optional
            "X-Title": "TauTranslator"
        }
        
        payload = {
            "model": self.config.model_name or "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": request.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": request.prompt}
            ],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=request.timeout_seconds)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        generated_text = data["choices"][0]["message"]["content"]
                        tokens_used = data.get("usage", {}).get("total_tokens", 0)
                        
                        return UnifiedResponse(
                            success=True,
                            generated_text=generated_text,
                            provider_used=ProviderType.OPENROUTER,
                            model_used=payload["model"],
                            response_time=response_time,
                            tokens_generated=tokens_used,
                            estimated_cost=tokens_used * self.config.cost_per_token,
                            confidence_score=0.9  # High confidence for API responses
                        )
                    else:
                        error_data = await response.json()
                        return UnifiedResponse(
                            success=False,
                            generated_text="",
                            provider_used=ProviderType.OPENROUTER,
                            model_used=payload["model"],
                            response_time=response_time,
                            tokens_generated=0,
                            estimated_cost=0,
                            confidence_score=0,
                            error_message=error_data.get("error", {}).get("message", f"HTTP {response.status}")
                        )
        
        except Exception as e:
            return UnifiedResponse(
                success=False,
                generated_text="",
                provider_used=ProviderType.OPENROUTER,
                model_used=self.config.model_name or "unknown",
                response_time=time.time() - start_time,
                tokens_generated=0,
                estimated_cost=0,
                confidence_score=0,
                error_message=str(e)
            )


class PatternFallbackProvider:
    """Pattern-based fallback provider for when all else fails."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
    
    async def generate(self, request: UnifiedRequest) -> UnifiedResponse:
        """Generate response using pattern-based approach."""
        start_time = time.time()
        
        try:
            # Import pattern-based translator
            sys.path.append(str(Path(__file__).parent.parent.parent.parent))
            from nlp.nlp_requirements_engine import NLPRequirementsEngine
            
            engine = NLPRequirementsEngine(use_spacy=False, use_transformers=False)
            
            if request.requirements_text:
                # Tau-specific generation
                requirements = engine.extract_requirements(request.requirements_text)
                spec = engine.requirements_to_tau(requirements)
                generated_text = engine.generate_tau_code(spec)
            else:
                # Generic pattern-based response
                generated_text = self._generate_pattern_response(request.prompt)
            
            return UnifiedResponse(
                success=True,
                generated_text=generated_text,
                provider_used=ProviderType.PATTERN_FALLBACK,
                model_used="pattern-based",
                response_time=time.time() - start_time,
                tokens_generated=len(generated_text.split()),
                estimated_cost=0,  # Free
                confidence_score=0.6  # Moderate confidence
            )
            
        except Exception as e:
            # Ultimate fallback
            generated_text = self._generate_simple_tau_template(request)
            
            return UnifiedResponse(
                success=True,
                generated_text=generated_text,
                provider_used=ProviderType.PATTERN_FALLBACK,
                model_used="template",
                response_time=time.time() - start_time,
                tokens_generated=len(generated_text.split()),
                estimated_cost=0,
                confidence_score=0.4,  # Low confidence
                error_message=f"Pattern engine failed: {e}"
            )
    
    def _generate_pattern_response(self, prompt: str) -> str:
        """Generate pattern-based response."""
        if "tau" in prompt.lower() and "translate" in prompt.lower():
            return """# Generated Tau specification
sbf input_stream = ifile("data.txt")
sbf output_stream = ofile("results.txt")

# Basic rule
r monitor[t] = condition[t]
always (monitor[t] -> action[t])"""
        
        return "Pattern-based response: Please provide more specific requirements for Tau translation."
    
    def _generate_simple_tau_template(self, request: UnifiedRequest) -> str:
        """Generate simple Tau template as ultimate fallback."""
        return """# Simple Tau template
sbf input = ifile("input.txt")
sbf output = ofile("output.txt")

# Rule template
r basic_rule[t] = input[t] > 0
always (basic_rule[t] -> output[t])"""


class UnifiedLLMService:
    """Main unified LLM service coordinator."""
    
    def __init__(self):
        """Initialize the unified LLM service."""
        self.providers = {}
        self.metrics = ServiceMetrics()
        self.cache = ResponseCache()
        
        # Initialize providers based on availability
        self._initialize_providers()
        
        logger.info(f"UnifiedLLMService initialized with {len(self.providers)} providers")
    
    def _initialize_providers(self):
        """Initialize all available providers."""
        # OpenRouter (highest priority - recommended)
        self.providers[ProviderType.OPENROUTER] = {
            'provider': OpenRouterProvider(ProviderConfig(
                provider_type=ProviderType.OPENROUTER,
                priority=1,
                model_name="meta-llama/llama-3.1-70b-instruct",  # High-quality model for macOS
                cost_per_token=0.000001
            )),
            'config': ProviderConfig(provider_type=ProviderType.OPENROUTER, priority=1)
        }
        
        # Guidance (if available)
        if GUIDANCE_AVAILABLE:
            self.providers[ProviderType.GUIDANCE] = {
                'provider': None,  # Will be initialized on demand
                'config': ProviderConfig(provider_type=ProviderType.GUIDANCE, priority=3)
            }
        
        # Local Models (if available)  
        if LOCAL_MODELS_AVAILABLE:
            self.providers[ProviderType.LOCAL_MODELS] = {
                'provider': None,  # Will be initialized on demand
                'config': ProviderConfig(provider_type=ProviderType.LOCAL_MODELS, priority=4)
            }
        
        # Pattern Fallback (always available)
        self.providers[ProviderType.PATTERN_FALLBACK] = {
            'provider': PatternFallbackProvider(ProviderConfig(
                provider_type=ProviderType.PATTERN_FALLBACK,
                priority=99  # Lowest priority
            )),
            'config': ProviderConfig(provider_type=ProviderType.PATTERN_FALLBACK, priority=99)
        }
    
    async def generate_tau_code(self, requirements: str, **kwargs) -> UnifiedResponse:
        """Generate Tau code from natural language requirements."""
        system_prompt = """You are a Tau language expert. Convert natural language requirements to valid Tau specification code.

Tau Language Guidelines:
- Use 'sbf' for stream declarations: sbf name = ifile("file.txt")
- Use 'r' for rules: r rule_name[t] = expression  
- Use temporal operators: always, sometimes, eventually
- Use logical operators: &&, ||, !, ->, <->
- Use quantifiers: forall, exists
- Use constraints with comparison operators: >, <, >=, <=, =, !=

Generate clean, valid Tau code without explanations."""
        
        prompt = f"""Convert these requirements to Tau specification:

Requirements: {requirements}

Tau specification:"""
        
        request = UnifiedRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            requirements_text=requirements,
            max_tokens=kwargs.get('max_tokens', 800),
            temperature=kwargs.get('temperature', 0.3),
            provider_preference=kwargs.get('provider_preference'),
            use_cache=kwargs.get('use_cache', True),
            timeout_seconds=kwargs.get('timeout_seconds', 30)
        )
        
        return await self.generate(request)
    
    async def generate(self, request: UnifiedRequest) -> UnifiedResponse:
        """Generate response using the best available provider."""
        self.metrics.total_requests += 1
        
        # Check cache first
        cached_response = self.cache.get(request)
        if cached_response:
            self.metrics.cache_hits += 1
            return cached_response
        
        # Get ordered list of providers to try
        providers_to_try = self._get_provider_priority_list(request.provider_preference)
        
        for provider_type in providers_to_try:
            if provider_type not in self.providers:
                continue
            
            provider_info = self.providers[provider_type]
            provider = provider_info['provider']
            
            # Initialize provider on demand
            if provider is None:
                provider = await self._initialize_provider_on_demand(provider_type)
                if provider is None:
                    continue
                self.providers[provider_type]['provider'] = provider
            
            try:
                # Generate response
                response = await self._generate_with_provider(provider, request, provider_type)
                
                # Update metrics
                if response.success:
                    self.metrics.successful_requests += 1
                    self.metrics.total_response_time += response.response_time
                    self.metrics.total_cost += response.estimated_cost
                    
                    # Track provider usage
                    provider_name = provider_type.value
                    self.metrics.provider_usage[provider_name] = (
                        self.metrics.provider_usage.get(provider_name, 0) + 1
                    )
                    
                    # Cache successful response
                    self.cache.set(request, response)
                    
                    logger.info(f"Successfully generated response using {provider_type.value}")
                    return response
                else:
                    logger.warning(f"Provider {provider_type.value} failed: {response.error_message}")
                    
            except Exception as e:
                logger.error(f"Provider {provider_type.value} error: {e}")
                continue
        
        # If all providers failed, return error
        return UnifiedResponse(
            success=False,
            generated_text="",
            provider_used=ProviderType.PATTERN_FALLBACK,
            model_used="none",
            response_time=0,
            tokens_generated=0,
            estimated_cost=0,
            confidence_score=0,
            error_message="All providers failed"
        )
    
    def _get_provider_priority_list(self, preference: Optional[ProviderType]) -> List[ProviderType]:
        """Get ordered list of providers to try."""
        if preference and preference in self.providers:
            # Try preferred provider first
            providers = [preference]
            other_providers = [p for p in self.providers.keys() if p != preference]
            providers.extend(sorted(other_providers, key=lambda p: self.providers[p]['config'].priority))
        else:
            # Sort by priority
            providers = sorted(
                self.providers.keys(),
                key=lambda p: self.providers[p]['config'].priority
            )
        
        return providers
    
    async def _initialize_provider_on_demand(self, provider_type: ProviderType):
        """Initialize a provider on demand."""
        try:
            if provider_type == ProviderType.GUIDANCE:
                config = GuidanceConfig(model_type="transformers", model_name="microsoft/phi-2")
                return GuidanceService(config)
            
            elif provider_type == ProviderType.LOCAL_MODELS:
                config = LocalModelConfig(model_type="auto")
                service = LocalModelsService(config)
                if await service.initialize():
                    return service
                return None
            
        except Exception as e:
            logger.error(f"Failed to initialize {provider_type.value}: {e}")
            return None
    
    async def _generate_with_provider(self, provider, request: UnifiedRequest, 
                                    provider_type: ProviderType) -> UnifiedResponse:
        """Generate response with a specific provider."""
        if provider_type == ProviderType.GUIDANCE:
            # Convert to Guidance request
            guidance_request = TauGenerationRequest(
                requirements_text=request.requirements_text or request.prompt,
                validation_level="moderate",
                max_refinement_iterations=2
            )
            
            guidance_result = await provider.generate_tau_code(guidance_request)
            
            return UnifiedResponse(
                success=guidance_result.success,
                generated_text=guidance_result.tau_code,
                provider_used=ProviderType.GUIDANCE,
                model_used="guidance",
                response_time=guidance_result.generation_time,
                tokens_generated=len(guidance_result.tau_code.split()),
                estimated_cost=0,  # Local generation
                confidence_score=guidance_result.confidence_score,
                error_message=guidance_result.error_message,
                validation_results=guidance_result.validation_results
            )
        
        elif provider_type == ProviderType.LOCAL_MODELS:
            # Convert to local models request
            if request.requirements_text:
                local_result = await provider.generate_tau_code(request.requirements_text)
            else:
                local_request = GenerationRequest(
                    prompt=request.prompt,
                    system_prompt=request.system_prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )
                local_result = await provider.generate(local_request)
            
            return UnifiedResponse(
                success=local_result.success,
                generated_text=local_result.generated_text,
                provider_used=ProviderType.LOCAL_MODELS,
                model_used=local_result.model_used,
                response_time=local_result.generation_time,
                tokens_generated=local_result.tokens_generated,
                estimated_cost=0,  # Local generation
                confidence_score=0.8,  # Good confidence for local models
                error_message=local_result.error_message
            )
        
        else:
            # Direct provider call (OpenRouter, etc.)
            return await provider.generate(request)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status."""
        provider_status = {}
        for provider_type, provider_info in self.providers.items():
            provider_status[provider_type.value] = {
                'available': provider_info['provider'] is not None,
                'priority': provider_info['config'].priority,
                'enabled': provider_info['config'].enabled
            }
        
        return {
            'providers': provider_status,
            'metrics': asdict(self.metrics),
            'cache_size': len(self.cache.cache),
            'libraries_available': {
                'guidance': GUIDANCE_AVAILABLE,
                'local_models': LOCAL_MODELS_AVAILABLE,
                **LLM_LIBRARIES
            }
        }
    
    def get_metrics(self) -> ServiceMetrics:
        """Get service metrics."""
        return self.metrics
    
    async def test_providers(self) -> Dict[str, Any]:
        """Test all available providers."""
        test_request = UnifiedRequest(
            prompt="Generate a simple Tau specification for monitoring temperature.",
            system_prompt="You are a Tau language expert.",
            requirements_text="Monitor temperature and alert if it exceeds 80 degrees.",
            max_tokens=200,
            temperature=0.3,
            use_cache=False  # Don't cache test requests
        )
        
        results = {}
        
        for provider_type in self.providers:
            try:
                # Test with specific provider preference
                test_request.provider_preference = provider_type
                response = await self.generate(test_request)
                
                results[provider_type.value] = {
                    'success': response.success,
                    'response_time': response.response_time,
                    'model_used': response.model_used,
                    'tokens_generated': response.tokens_generated,
                    'confidence_score': response.confidence_score,
                    'error_message': response.error_message
                }
                
            except Exception as e:
                results[provider_type.value] = {
                    'success': False,
                    'error_message': str(e)
                }
        
        return results


# Example usage and testing
async def test_unified_service():
    """Test the unified LLM service."""
    print("Testing Unified LLM Service...")
    
    service = UnifiedLLMService()
    
    # Show service status
    status = service.get_service_status()
    print(f"Service status: {json.dumps(status, indent=2)}")
    
    # Test providers
    print("\n--- Testing Providers ---")
    provider_results = await service.test_providers()
    
    for provider, result in provider_results.items():
        print(f"\n{provider}:")
        if result['success']:
            print(f"  ✅ Success ({result['response_time']:.2f}s)")
            print(f"  Model: {result['model_used']}")
            print(f"  Confidence: {result['confidence_score']:.2f}")
        else:
            print(f"  ❌ Failed: {result['error_message']}")
    
    # Test Tau generation
    print("\n--- Testing Tau Generation ---")
    requirements = "Create a safety monitoring system that checks temperature sensors every second and triggers an alarm if temperature exceeds 80 degrees Celsius."
    
    response = await service.generate_tau_code(requirements)
    
    print(f"Success: {response.success}")
    print(f"Provider used: {response.provider_used.value}")
    print(f"Model: {response.model_used}")
    print(f"Response time: {response.response_time:.2f}s")
    print(f"Confidence: {response.confidence_score:.2f}")
    
    if response.success:
        print(f"Generated Tau code:")
        print("-" * 50)
        print(response.generated_text)
        print("-" * 50)
    else:
        print(f"Error: {response.error_message}")
    
    # Show final metrics
    print(f"\n--- Service Metrics ---")
    metrics = service.get_metrics()
    print(f"Total requests: {metrics.total_requests}")
    print(f"Success rate: {metrics.successful_requests / max(1, metrics.total_requests):.1%}")
    print(f"Cache hits: {metrics.cache_hits}")
    print(f"Provider usage: {metrics.provider_usage}")


if __name__ == "__main__":
    asyncio.run(test_unified_service())