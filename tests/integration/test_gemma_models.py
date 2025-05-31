#!/usr/bin/env python3
"""
Test Gemma Model Loading and Integration
========================================

Tests loading various Gemma models for Tau translation.
"""

import os
import sys
import time
import psutil
import logging
from pathlib import Path
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GemmaModelTester:
    """Test Gemma model loading and performance."""
    
    def __init__(self):
        self.models_to_test = [
            "google/gemma-2b",
            "google/gemma-7b",
            "google/gemma-2b-it",  # Instruction-tuned version
            "google/gemma-7b-it"   # Instruction-tuned version
        ]
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
    def get_system_info(self):
        """Get current system resource usage."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            'gpu_available': torch.cuda.is_available(),
            'gpu_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }
    
    def test_model_loading(self, model_id: str):
        """Test loading a specific Gemma model."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing model: {model_id}")
        logger.info(f"{'='*60}")
        
        # Check system resources before loading
        sys_info_before = self.get_system_info()
        logger.info(f"System before loading: CPU {sys_info_before['cpu_percent']:.1f}%, "
                   f"Memory {sys_info_before['memory_percent']:.1f}%, "
                   f"Available {sys_info_before['memory_available_gb']:.1f}GB")
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Start timing
            start_time = time.time()
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Determine appropriate dtype based on model size and memory
            if "7b" in model_id and sys_info_before['memory_available_gb'] < 16:
                logger.warning("Limited memory for 7B model, using 8-bit quantization")
                load_in_8bit = True
                torch_dtype = torch.float16
            else:
                load_in_8bit = False
                torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
            
            # Load model
            logger.info(f"Loading model with dtype={torch_dtype}, load_in_8bit={load_in_8bit}...")
            
            model_kwargs = {
                "torch_dtype": torch_dtype,
                "device_map": "auto",
                "low_cpu_mem_usage": True,
            }
            
            if load_in_8bit:
                model_kwargs["load_in_8bit"] = True
            
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                **model_kwargs
            )
            
            load_time = time.time() - start_time
            logger.info(f"✓ Model loaded successfully in {load_time:.1f} seconds")
            
            # Check system resources after loading
            sys_info_after = self.get_system_info()
            logger.info(f"System after loading: CPU {sys_info_after['cpu_percent']:.1f}%, "
                       f"Memory {sys_info_after['memory_percent']:.1f}%, "
                       f"Available {sys_info_after['memory_available_gb']:.1f}GB")
            
            # Test the model with a simple Tau translation task
            test_result = self.test_translation(model, tokenizer, model_id)
            
            # Clean up
            del model
            del tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return {
                'success': True,
                'model_id': model_id,
                'load_time': load_time,
                'test_result': test_result,
                'memory_used_gb': (sys_info_before['memory_available_gb'] - 
                                 sys_info_after['memory_available_gb'])
            }
            
        except Exception as e:
            logger.error(f"✗ Failed to load {model_id}: {str(e)}")
            return {
                'success': False,
                'model_id': model_id,
                'error': str(e)
            }
    
    def test_translation(self, model, tokenizer, model_id: str):
        """Test the model with a Tau translation task."""
        logger.info("\nTesting translation capability...")
        
        # Prepare test prompt
        test_prompt = """Convert this requirement to Tau specification:

Requirement: The system must always ensure temperature stays between 20 and 80 degrees.

Tau specification:
"""
        
        try:
            # Tokenize
            inputs = tokenizer(test_prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generation_time = time.time() - start_time
            
            # Decode
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            tau_part = response.split("Tau specification:")[-1].strip()
            
            logger.info(f"Generated in {generation_time:.1f}s:")
            logger.info(f"Response: {tau_part[:200]}...")
            
            # Check if it looks like valid Tau
            looks_valid = any(keyword in tau_part.lower() for keyword in ['always', 'temperature', '[t]', '>=', '<='])
            
            return {
                'generation_time': generation_time,
                'response_preview': tau_part[:200],
                'looks_valid': looks_valid
            }
            
        except Exception as e:
            logger.error(f"Translation test failed: {e}")
            return {
                'error': str(e)
            }
    
    def run_all_tests(self):
        """Run tests on all Gemma models."""
        results = []
        
        logger.info("Starting Gemma model tests...")
        logger.info(f"System info: {self.get_system_info()}")
        
        for model_id in self.models_to_test:
            # Skip 7B models if memory is limited
            sys_info = self.get_system_info()
            if "7b" in model_id and sys_info['memory_available_gb'] < 8:
                logger.warning(f"Skipping {model_id} - insufficient memory")
                results.append({
                    'success': False,
                    'model_id': model_id,
                    'error': 'Insufficient memory'
                })
                continue
            
            result = self.test_model_loading(model_id)
            results.append(result)
            
            # Brief pause between models
            time.sleep(2)
        
        return results
    
    def print_summary(self, results):
        """Print summary of test results."""
        logger.info("\n" + "="*60)
        logger.info("GEMMA MODEL TEST SUMMARY")
        logger.info("="*60)
        
        for result in results:
            if result['success']:
                logger.info(f"\n✓ {result['model_id']}")
                logger.info(f"  - Load time: {result['load_time']:.1f}s")
                logger.info(f"  - Memory used: {result.get('memory_used_gb', 0):.1f}GB")
                if 'test_result' in result and result['test_result']:
                    logger.info(f"  - Generation time: {result['test_result'].get('generation_time', 'N/A'):.1f}s")
                    logger.info(f"  - Translation valid: {result['test_result'].get('looks_valid', False)}")
            else:
                logger.info(f"\n✗ {result['model_id']}")
                logger.info(f"  - Error: {result['error']}")
        
        # Recommendations
        logger.info("\n" + "="*60)
        logger.info("RECOMMENDATIONS")
        logger.info("="*60)
        
        successful_models = [r['model_id'] for r in results if r['success']]
        
        if successful_models:
            # Recommend based on performance
            if "google/gemma-2b-it" in successful_models:
                logger.info("Recommended: google/gemma-2b-it (instruction-tuned, efficient)")
            elif "google/gemma-2b" in successful_models:
                logger.info("Recommended: google/gemma-2b (base model, efficient)")
            
            logger.info("\nTo use in production:")
            logger.info("1. Update advanced_llm_translator.py to use recommended model")
            logger.info("2. Consider quantization for larger models")
            logger.info("3. Use instruction-tuned versions for better task following")
        else:
            logger.info("No models loaded successfully. Consider:")
            logger.info("1. Using cloud APIs (OpenAI, Anthropic)")
            logger.info("2. Reducing model size requirements")
            logger.info("3. Upgrading system memory")


def main():
    """Run Gemma model tests."""
    # Check if transformers is available
    try:
        import transformers
        logger.info(f"Transformers version: {transformers.__version__}")
    except ImportError:
        logger.error("Transformers not installed. Install with: pip install transformers torch")
        return
    
    # Run tests
    tester = GemmaModelTester()
    results = tester.run_all_tests()
    tester.print_summary(results)


if __name__ == "__main__":
    main()