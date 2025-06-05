#!/usr/bin/env python3
"""
Local Models Service for TauTranslator
=====================================

Comprehensive local model integration supporting:
- Ollama (recommended for local deployment)
- Transformers (HuggingFace models)
- GGML/GGUF models
- Custom fine-tuned models

Features:
- Model auto-discovery and management
- Performance optimization
- Resource monitoring
- Fallback strategies

Author: DarkLightX/Dana Edwards
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
import subprocess
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import time
import psutil
import platform

# Try importing model libraries
AVAILABLE_LIBRARIES = {}

try:
    import requests
    AVAILABLE_LIBRARIES['requests'] = True
except ImportError:
    AVAILABLE_LIBRARIES['requests'] = False

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    AVAILABLE_LIBRARIES['transformers'] = True
except ImportError:
    AVAILABLE_LIBRARIES['transformers'] = False

try:
    import llama_cpp
    AVAILABLE_LIBRARIES['llama_cpp'] = True
except ImportError:
    AVAILABLE_LIBRARIES['llama_cpp'] = False

logger = logging.getLogger(__name__)


@dataclass
class LocalModelConfig:
    """Configuration for local model service."""
    model_type: str = "ollama"  # "ollama", "transformers", "ggml"
    model_name: str = "llama2"
    max_tokens: int = 1000
    temperature: float = 0.3
    device: str = "auto"  # "cpu", "cuda", "mps", "auto"
    load_in_8bit: bool = False
    load_in_4bit: bool = False
    trust_remote_code: bool = False
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    timeout_seconds: int = 60


@dataclass
class ModelInfo:
    """Information about an available model."""
    name: str
    type: str  # "ollama", "transformers", "ggml"
    size: str
    status: str  # "available", "downloading", "loaded", "error"
    memory_usage: Optional[int] = None
    performance_score: Optional[float] = None
    last_used: Optional[str] = None


@dataclass
class GenerationRequest:
    """Request for text generation."""
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 500
    temperature: float = 0.3
    top_p: float = 0.9
    stop_sequences: Optional[List[str]] = None
    stream: bool = False


@dataclass
class GenerationResult:
    """Result from text generation."""
    success: bool
    generated_text: str
    model_used: str
    generation_time: float
    tokens_generated: int
    tokens_per_second: float
    memory_usage: Optional[int] = None
    error_message: Optional[str] = None


class SystemResourceMonitor:
    """Monitor system resources for model optimization."""
    
    @staticmethod
    def get_available_memory() -> int:
        """Get available system memory in MB."""
        return psutil.virtual_memory().available // (1024 * 1024)
    
    @staticmethod
    def get_cpu_count() -> int:
        """Get number of CPU cores."""
        return psutil.cpu_count()
    
    @staticmethod
    def has_gpu() -> bool:
        """Check if GPU is available."""
        if AVAILABLE_LIBRARIES['transformers']:
            return torch.cuda.is_available()
        return False
    
    @staticmethod
    def get_optimal_device() -> str:
        """Determine optimal device for model execution."""
        if AVAILABLE_LIBRARIES['transformers']:
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
        return "cpu"


class OllamaService:
    """Ollama local model service integration."""
    
    def __init__(self, config: LocalModelConfig):
        self.config = config
        self.base_url = f"http://{config.ollama_host}:{config.ollama_port}"
        self.available_models = []
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def is_running(self) -> bool:
        """Check if Ollama service is running."""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except:
            return False
    
    async def list_models(self) -> List[ModelInfo]:
        """List available Ollama models."""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = []
                    for model in data.get('models', []):
                        models.append(ModelInfo(
                            name=model['name'],
                            type="ollama",
                            size=self._format_size(model.get('size', 0)),
                            status="available",
                            last_used=model.get('modified_at')
                        ))
                    return models
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
        
        return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull/download a model from Ollama registry."""
        try:
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate text using Ollama model."""
        start_time = time.time()
        
        payload = {
            "model": self.config.model_name,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
                "top_p": request.top_p
            }
        }
        
        if request.system_prompt:
            payload["system"] = request.system_prompt
        
        if request.stop_sequences:
            payload["options"]["stop"] = request.stop_sequences
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                generation_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    generated_text = data.get("response", "")
                    
                    return GenerationResult(
                        success=True,
                        generated_text=generated_text,
                        model_used=self.config.model_name,
                        generation_time=generation_time,
                        tokens_generated=len(generated_text.split()),
                        tokens_per_second=len(generated_text.split()) / generation_time if generation_time > 0 else 0
                    )
                else:
                    error_data = await response.json()
                    return GenerationResult(
                        success=False,
                        generated_text="",
                        model_used=self.config.model_name,
                        generation_time=generation_time,
                        tokens_generated=0,
                        tokens_per_second=0,
                        error_message=error_data.get("error", f"HTTP {response.status}")
                    )
        
        except Exception as e:
            generation_time = time.time() - start_time
            return GenerationResult(
                success=False,
                generated_text="",
                model_used=self.config.model_name,
                generation_time=generation_time,
                tokens_generated=0,
                tokens_per_second=0,
                error_message=str(e)
            )
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"


class TransformersService:
    """HuggingFace Transformers service integration."""
    
    def __init__(self, config: LocalModelConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = SystemResourceMonitor.get_optimal_device()
    
    async def load_model(self) -> bool:
        """Load the specified model."""
        if not AVAILABLE_LIBRARIES['transformers']:
            logger.error("Transformers library not available")
            return False
        
        try:
            logger.info(f"Loading model: {self.config.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                trust_remote_code=self.config.trust_remote_code
            )
            
            # Configure model loading options
            model_kwargs = {
                "trust_remote_code": self.config.trust_remote_code
            }
            
            if self.device == "cuda" and torch.cuda.is_available():
                model_kwargs["device_map"] = "auto"
                if self.config.load_in_8bit:
                    model_kwargs["load_in_8bit"] = True
                elif self.config.load_in_4bit:
                    model_kwargs["load_in_4bit"] = True
                else:
                    model_kwargs["torch_dtype"] = torch.float16
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name,
                **model_kwargs
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto" if self.device == "cuda" else None
            )
            
            logger.info(f"Successfully loaded {self.config.model_name} on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {self.config.model_name}: {e}")
            return False
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate text using Transformers model."""
        if not self.pipeline:
            if not await self.load_model():
                return GenerationResult(
                    success=False,
                    generated_text="",
                    model_used=self.config.model_name,
                    generation_time=0,
                    tokens_generated=0,
                    tokens_per_second=0,
                    error_message="Model not loaded"
                )
        
        start_time = time.time()
        
        try:
            # Prepare prompt
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
            
            # Generate
            results = self.pipeline(
                full_prompt,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            generation_time = time.time() - start_time
            
            # Extract generated text
            generated_text = results[0]["generated_text"]
            if generated_text.startswith(full_prompt):
                generated_text = generated_text[len(full_prompt):].strip()
            
            # Calculate tokens
            tokens_generated = len(self.tokenizer.encode(generated_text))
            
            return GenerationResult(
                success=True,
                generated_text=generated_text,
                model_used=self.config.model_name,
                generation_time=generation_time,
                tokens_generated=tokens_generated,
                tokens_per_second=tokens_generated / generation_time if generation_time > 0 else 0,
                memory_usage=SystemResourceMonitor.get_available_memory()
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            return GenerationResult(
                success=False,
                generated_text="",
                model_used=self.config.model_name,
                generation_time=generation_time,
                tokens_generated=0,
                tokens_per_second=0,
                error_message=str(e)
            )


class LocalModelsService:
    """Main local models service coordinator."""
    
    def __init__(self, config: Optional[LocalModelConfig] = None):
        """Initialize local models service."""
        self.config = config or LocalModelConfig(
            model_type="ollama",
            model_name="codellama:34b"  # CodeLlama 34B for high-RAM macOS
        )
        self.ollama_service = None
        self.transformers_service = None
        self.active_service = None
        self.resource_monitor = SystemResourceMonitor()
        
        # Performance tracking
        self.generation_stats = {
            'total_requests': 0,
            'successful_generations': 0,
            'total_generation_time': 0.0,
            'average_tokens_per_second': 0.0
        }
    
    async def initialize(self) -> bool:
        """Initialize the service and select best available option."""
        logger.info("Initializing Local Models Service...")
        
        # Try Ollama first (recommended)
        if self.config.model_type in ["ollama", "auto"]:
            success = await self._initialize_ollama()
            if success:
                self.active_service = "ollama"
                logger.info("Using Ollama service")
                return True
        
        # Fall back to Transformers
        if self.config.model_type in ["transformers", "auto"]:
            success = await self._initialize_transformers()
            if success:
                self.active_service = "transformers"
                logger.info("Using Transformers service")
                return True
        
        logger.warning("No local model service available")
        return False
    
    async def _initialize_ollama(self) -> bool:
        """Initialize Ollama service."""
        try:
            self.ollama_service = OllamaService(self.config)
            
            async with self.ollama_service as service:
                if await service.is_running():
                    # Check if model is available
                    models = await service.list_models()
                    model_names = [m.name for m in models]
                    
                    if self.config.model_name in model_names:
                        logger.info(f"Ollama model {self.config.model_name} is available")
                        return True
                    else:
                        # Try to pull the model
                        logger.info(f"Pulling Ollama model: {self.config.model_name}")
                        if await service.pull_model(self.config.model_name):
                            return True
                        else:
                            # High-performance models for systems with ample RAM
                            high_ram_models = [
                                "llama3.1:70b",  # Best overall performance
                                "codellama:34b",  # Code-specialized
                                "llama3.1:8b",   # Good balance
                                "gemma2:9b",     # Tau-optimized
                                "codegemma:7b",  # Code-focused
                                "phi3:mini"      # Fallback
                            ]
                            
                            for default_model in high_ram_models:
                                if default_model in model_names:
                                    self.config.model_name = default_model
                                    logger.info(f"Using available high-performance model: {default_model}")
                                    return True
                
        except Exception as e:
            logger.error(f"Ollama initialization failed: {e}")
        
        return False
    
    async def _initialize_transformers(self) -> bool:
        """Initialize Transformers service."""
        if not AVAILABLE_LIBRARIES['transformers']:
            return False
        
        try:
            self.transformers_service = TransformersService(self.config)
            
            # Try to load a small model for testing
            original_model = self.config.model_name
            small_models = [
                "microsoft/DialoGPT-small",
                "gpt2",
                "distilgpt2"
            ]
            
            for model_name in [original_model] + small_models:
                self.config.model_name = model_name
                self.transformers_service.config.model_name = model_name
                
                if await self.transformers_service.load_model():
                    logger.info(f"Loaded Transformers model: {model_name}")
                    return True
            
        except Exception as e:
            logger.error(f"Transformers initialization failed: {e}")
        
        return False
    
    async def generate_tau_code(self, requirements: str) -> GenerationResult:
        """Generate Tau code from requirements using local models."""
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
        
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=800,
            temperature=0.3,
            stop_sequences=["Requirements:", "Note:", "Explanation:"]
        )
        
        return await self.generate(request)
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate text using the active local model service."""
        self.generation_stats['total_requests'] += 1
        
        if not self.active_service:
            if not await self.initialize():
                return GenerationResult(
                    success=False,
                    generated_text="",
                    model_used="none",
                    generation_time=0,
                    tokens_generated=0,
                    tokens_per_second=0,
                    error_message="No local model service available"
                )
        
        try:
            if self.active_service == "ollama":
                async with self.ollama_service as service:
                    result = await service.generate(request)
            elif self.active_service == "transformers":
                result = await self.transformers_service.generate(request)
            else:
                raise ValueError(f"Unknown service: {self.active_service}")
            
            # Update statistics
            if result.success:
                self.generation_stats['successful_generations'] += 1
                self.generation_stats['total_generation_time'] += result.generation_time
                self.generation_stats['average_tokens_per_second'] = (
                    (self.generation_stats['average_tokens_per_second'] * 
                     (self.generation_stats['successful_generations'] - 1) + 
                     result.tokens_per_second) / self.generation_stats['successful_generations']
                )
            
            return result
            
        except Exception as e:
            return GenerationResult(
                success=False,
                generated_text="",
                model_used=self.config.model_name,
                generation_time=0,
                tokens_generated=0,
                tokens_per_second=0,
                error_message=str(e)
            )
    
    async def list_available_models(self) -> List[ModelInfo]:
        """List all available local models."""
        models = []
        
        # Ollama models
        if self.ollama_service:
            try:
                async with self.ollama_service as service:
                    if await service.is_running():
                        ollama_models = await service.list_models()
                        models.extend(ollama_models)
            except:
                pass
        
        # Add common Transformers models
        if AVAILABLE_LIBRARIES['transformers']:
            common_models = [
                ("microsoft/DialoGPT-small", "Small conversational model"),
                ("gpt2", "GPT-2 base model"),
                ("distilgpt2", "Distilled GPT-2"),
                ("microsoft/phi-2", "Phi-2 reasoning model"),
                ("google/flan-t5-small", "FLAN-T5 small")
            ]
            
            for model_name, description in common_models:
                models.append(ModelInfo(
                    name=model_name,
                    type="transformers",
                    size="Small",
                    status="available"
                ))
        
        return models
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the local models service."""
        return {
            'active_service': self.active_service,
            'model_name': self.config.model_name,
            'device': self.resource_monitor.get_optimal_device(),
            'available_memory_mb': self.resource_monitor.get_available_memory(),
            'cpu_cores': self.resource_monitor.get_cpu_count(),
            'has_gpu': self.resource_monitor.has_gpu(),
            'libraries_available': AVAILABLE_LIBRARIES,
            'statistics': self.generation_stats
        }


# Testing and example usage
async def test_local_models():
    """Test local models service."""
    print("Testing Local Models Service...")
    print(f"Available libraries: {AVAILABLE_LIBRARIES}")
    
    # System info
    monitor = SystemResourceMonitor()
    print(f"Optimal device: {monitor.get_optimal_device()}")
    print(f"Available memory: {monitor.get_available_memory()}MB")
    print(f"CPU cores: {monitor.get_cpu_count()}")
    print(f"Has GPU: {monitor.has_gpu()}")
    
    # Test configurations
    configs = [
        LocalModelConfig(model_type="ollama", model_name="llama2"),
        LocalModelConfig(model_type="transformers", model_name="distilgpt2")
    ]
    
    for config in configs:
        print(f"\n--- Testing {config.model_type} with {config.model_name} ---")
        
        service = LocalModelsService(config)
        success = await service.initialize()
        
        if success:
            print(f"✅ Service initialized successfully")
            
            # Test generation
            test_requirements = "Monitor temperature sensors and trigger alarm if temperature exceeds 80 degrees."
            
            result = await service.generate_tau_code(test_requirements)
            
            print(f"Generation success: {result.success}")
            if result.success:
                print(f"Generation time: {result.generation_time:.2f}s")
                print(f"Tokens/second: {result.tokens_per_second:.1f}")
                print(f"Generated Tau code:")
                print("-" * 40)
                print(result.generated_text)
                print("-" * 40)
            else:
                print(f"Error: {result.error_message}")
            
            # Show service info
            info = service.get_service_info()
            print(f"Service info: {json.dumps(info, indent=2)}")
            
        else:
            print(f"❌ Failed to initialize {config.model_type} service")
    
    print("\nLocal models testing complete!")


if __name__ == "__main__":
    asyncio.run(test_local_models())