#!/usr/bin/env python3
"""
Advanced LLM-based Translator with Multiple Framework Support
============================================================

Supports LMQL, Guidance, Gemma3, and other LLMs for high-quality
requirements-to-Tau translation with iterative refinement.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from pathlib import Path
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing various LLM frameworks
AVAILABLE_FRAMEWORKS = {}

# LMQL
try:
    import lmql
    AVAILABLE_FRAMEWORKS['lmql'] = True
    logger.info("LMQL framework available")
except ImportError:
    AVAILABLE_FRAMEWORKS['lmql'] = False
    logger.warning("LMQL not available")

# Guidance
try:
    import guidance
    AVAILABLE_FRAMEWORKS['guidance'] = True
    logger.info("Guidance framework available")
except ImportError:
    AVAILABLE_FRAMEWORKS['guidance'] = False
    logger.warning("Guidance not available")

# Transformers (for Gemma3 and other models)
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch
    AVAILABLE_FRAMEWORKS['transformers'] = True
    logger.info("Transformers framework available")
except ImportError:
    AVAILABLE_FRAMEWORKS['transformers'] = False
    logger.warning("Transformers not available")

# OpenAI
try:
    import openai
    AVAILABLE_FRAMEWORKS['openai'] = True
    logger.info("OpenAI framework available")
except ImportError:
    AVAILABLE_FRAMEWORKS['openai'] = False
    logger.warning("OpenAI not available")

# Anthropic
try:
    import anthropic
    AVAILABLE_FRAMEWORKS['anthropic'] = True
    logger.info("Anthropic framework available")
except ImportError:
    AVAILABLE_FRAMEWORKS['anthropic'] = False
    logger.warning("Anthropic not available")


@dataclass
class TranslationContext:
    """Context for iterative translation refinement."""
    original_text: str
    current_translation: str
    iteration: int = 0
    feedback_history: List[Dict[str, str]] = None
    confidence_scores: List[float] = None
    
    def __post_init__(self):
        if self.feedback_history is None:
            self.feedback_history = []
        if self.confidence_scores is None:
            self.confidence_scores = []


class AdvancedLLMTranslator:
    """
    Advanced translator supporting multiple LLM frameworks with
    iterative refinement capabilities.
    """
    
    def __init__(self, preferred_framework: str = "auto", model_name: str = None):
        """
        Initialize the translator with preferred framework.
        
        Args:
            preferred_framework: One of 'lmql', 'guidance', 'transformers', 'openai', 'anthropic', 'auto'
            model_name: Specific model to use (e.g., 'google/gemma-2b', 'gpt-4', 'claude-3')
        """
        self.preferred_framework = preferred_framework
        self.model_name = model_name
        self.framework = None
        self.model = None
        self.tokenizer = None
        
        # Initialize the selected framework
        self._initialize_framework()
        
        # Tau language patterns for validation
        self.tau_patterns = {
            'stream_declaration': r'sbf\s+\w+\s*=\s*(ifile|ofile|console)',
            'rule_definition': r'r\s+\w+\[.*?\]\s*=',
            'function_definition': r'\w+\s*\([^)]*\)\s*:=',
            'temporal_property': r'(always|sometimes|never)\s+',
            'constraint': r'\w+\[t\]\s*(>|<|>=|<=|=)\s*\d+'
        }
    
    def _initialize_framework(self):
        """Initialize the selected LLM framework."""
        if self.preferred_framework == "auto":
            # Auto-select best available framework
            if AVAILABLE_FRAMEWORKS.get('lmql'):
                self.framework = 'lmql'
            elif AVAILABLE_FRAMEWORKS.get('guidance'):
                self.framework = 'guidance'
            elif AVAILABLE_FRAMEWORKS.get('openai'):
                self.framework = 'openai'
            elif AVAILABLE_FRAMEWORKS.get('anthropic'):
                self.framework = 'anthropic'
            elif AVAILABLE_FRAMEWORKS.get('transformers'):
                self.framework = 'transformers'
            else:
                logger.warning("No LLM framework available, using pattern-based fallback")
                self.framework = 'pattern'
        else:
            if AVAILABLE_FRAMEWORKS.get(self.preferred_framework):
                self.framework = self.preferred_framework
            else:
                logger.warning(f"{self.preferred_framework} not available, using fallback")
                self.framework = 'pattern'
        
        # Load model based on framework
        if self.framework == 'transformers':
            self._load_transformers_model()
        elif self.framework == 'guidance':
            self._load_guidance_model()
        
        logger.info(f"Using {self.framework} framework for translation")
    
    def _load_transformers_model(self):
        """Load a transformer model (e.g., Gemma3)."""
        if not AVAILABLE_FRAMEWORKS['transformers']:
            return
        
        try:
            if self.model_name:
                model_id = self.model_name
            else:
                # Default to Gemma 2B for efficiency
                model_id = "google/gemma-2b"
            
            logger.info(f"Loading model: {model_id}")
            
            # Check if model is already downloaded
            cache_dir = Path.home() / ".cache" / "huggingface"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
            
            logger.info(f"Successfully loaded {model_id}")
            
        except Exception as e:
            logger.error(f"Failed to load transformer model: {e}")
            self.framework = 'pattern'  # Fallback
    
    def _load_guidance_model(self):
        """Initialize Guidance with appropriate model."""
        if not AVAILABLE_FRAMEWORKS['guidance']:
            return
        
        try:
            if self.model_name and 'gpt' in self.model_name:
                self.model = guidance.models.OpenAI(self.model_name)
            else:
                # Use local model if available
                self.model = guidance.models.Transformers("microsoft/phi-2")
            
            logger.info("Guidance model initialized")
            
        except Exception as e:
            logger.error(f"Failed to load Guidance model: {e}")
            self.framework = 'pattern'
    
    async def translate_requirements_to_tau(self, 
                                          requirements_text: str,
                                          max_iterations: int = 3,
                                          interactive: bool = False) -> TranslationContext:
        """
        Translate natural language requirements to Tau specification.
        
        Args:
            requirements_text: Natural language requirements
            max_iterations: Maximum refinement iterations
            interactive: Whether to request user feedback
            
        Returns:
            TranslationContext with final translation
        """
        context = TranslationContext(
            original_text=requirements_text,
            current_translation=""
        )
        
        # Initial translation
        context.current_translation = await self._translate_initial(requirements_text)
        context.iteration = 1
        
        # Iterative refinement
        while context.iteration < max_iterations:
            # Validate current translation
            validation_result = self._validate_tau_syntax(context.current_translation)
            
            if validation_result['valid'] and validation_result['confidence'] > 0.8:
                break
            
            # Get feedback (from user or auto-generated)
            if interactive:
                feedback = await self._get_user_feedback(context)
            else:
                feedback = self._generate_auto_feedback(validation_result)
            
            context.feedback_history.append({
                'iteration': context.iteration,
                'feedback': feedback,
                'validation': validation_result
            })
            
            # Refine translation based on feedback
            context.current_translation = await self._refine_translation(context, feedback)
            context.iteration += 1
        
        return context
    
    async def _translate_initial(self, requirements_text: str) -> str:
        """Perform initial translation based on selected framework."""
        if self.framework == 'lmql':
            return await self._translate_with_lmql(requirements_text)
        elif self.framework == 'guidance':
            return await self._translate_with_guidance(requirements_text)
        elif self.framework == 'openai':
            return await self._translate_with_openai(requirements_text)
        elif self.framework == 'anthropic':
            return await self._translate_with_anthropic(requirements_text)
        elif self.framework == 'transformers':
            return await self._translate_with_transformers(requirements_text)
        else:
            return self._translate_with_patterns(requirements_text)
    
    async def _translate_with_lmql(self, text: str) -> str:
        """Translate using LMQL constraints."""
        if not AVAILABLE_FRAMEWORKS['lmql']:
            return self._translate_with_patterns(text)
        
        try:
            # LMQL query for structured Tau generation
            query = '''
            argmax
                """Convert these requirements to Tau specification:
                {text}
                
                Tau Specification:
                [TAU]"""
            from
                "openai/gpt-3.5-turbo"
            where
                len(TAU) < 1000 and
                TAU matches r"(sbf|r |always|sometimes|:=)"
            '''
            
            result = await lmql.run(query, text=text)
            return result.variables['TAU']
            
        except Exception as e:
            logger.error(f"LMQL translation failed: {e}")
            return self._translate_with_patterns(text)
    
    async def _translate_with_guidance(self, text: str) -> str:
        """Translate using Guidance framework."""
        if not AVAILABLE_FRAMEWORKS['guidance'] or not self.model:
            return self._translate_with_patterns(text)
        
        try:
            # Guidance program for Tau generation
            program = guidance('''
            You are a Tau specification expert. Convert these requirements to Tau:
            
            Requirements: {{requirements}}
            
            First, identify the key entities and constraints:
            {{#assistant~}}
            {{entities}}
            {{/assistant}}
            
            Now generate the Tau specification:
            ```tau
            {{#assistant~}}
            {{tau_spec}}
            {{/assistant}}
            ```
            ''')
            
            result = program(requirements=text)
            return result['tau_spec']
            
        except Exception as e:
            logger.error(f"Guidance translation failed: {e}")
            return self._translate_with_patterns(text)
    
    async def _translate_with_openai(self, text: str) -> str:
        """Translate using OpenAI API."""
        if not AVAILABLE_FRAMEWORKS['openai']:
            return self._translate_with_patterns(text)
        
        try:
            client = openai.OpenAI()
            
            response = client.chat.completions.create(
                model=self.model_name or "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in Tau formal specification language. Convert natural language requirements to valid Tau code."},
                    {"role": "user", "content": f"Convert these requirements to Tau specification:\n\n{text}"}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI translation failed: {e}")
            return self._translate_with_patterns(text)
    
    async def _translate_with_anthropic(self, text: str) -> str:
        """Translate using Anthropic API."""
        if not AVAILABLE_FRAMEWORKS['anthropic']:
            return self._translate_with_patterns(text)
        
        try:
            client = anthropic.Anthropic()
            
            response = client.messages.create(
                model=self.model_name or "claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": f"You are an expert in Tau formal specification language. Convert these natural language requirements to valid Tau code:\n\n{text}"
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic translation failed: {e}")
            return self._translate_with_patterns(text)
    
    async def _translate_with_transformers(self, text: str) -> str:
        """Translate using local transformer model."""
        if not AVAILABLE_FRAMEWORKS['transformers'] or not self.model:
            return self._translate_with_patterns(text)
        
        try:
            prompt = f"""Convert these natural language requirements to Tau specification:

Requirements:
{text}

Tau Specification:
```tau
"""
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=500,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the Tau code from response
            if "```tau" in response:
                tau_code = response.split("```tau")[1].split("```")[0].strip()
                return tau_code
            else:
                # Extract everything after "Tau Specification:"
                parts = response.split("Tau Specification:")
                if len(parts) > 1:
                    return parts[1].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Transformer translation failed: {e}")
            return self._translate_with_patterns(text)
    
    def _translate_with_patterns(self, text: str) -> str:
        """Fallback pattern-based translation."""
        logger.info("Using pattern-based translation (fallback)")
        
        # Import the NLP engine
        from nlp_requirements_engine import NLPRequirementsEngine
        
        engine = NLPRequirementsEngine(use_spacy=False, use_transformers=False)
        requirements = engine.extract_requirements(text)
        spec = engine.requirements_to_tau(requirements)
        
        return engine.generate_tau_code(spec)
    
    def _validate_tau_syntax(self, tau_code: str) -> Dict[str, Any]:
        """Validate Tau syntax and structure."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'confidence': 0.0,
            'patterns_found': []
        }
        
        if not tau_code.strip():
            result['valid'] = False
            result['errors'].append("Empty specification")
            return result
        
        # Check for required patterns
        pattern_scores = {}
        for pattern_name, pattern in self.tau_patterns.items():
            import re
            if re.search(pattern, tau_code):
                pattern_scores[pattern_name] = 1.0
                result['patterns_found'].append(pattern_name)
            else:
                pattern_scores[pattern_name] = 0.0
        
        # Calculate confidence based on patterns found
        if pattern_scores:
            result['confidence'] = sum(pattern_scores.values()) / len(pattern_scores)
        
        # Basic syntax checks
        lines = tau_code.strip().split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check for basic syntax errors
            if line.count('(') != line.count(')'):
                result['errors'].append(f"Line {i}: Unmatched parentheses")
                result['valid'] = False
            
            if line.count('[') != line.count(']'):
                result['errors'].append(f"Line {i}: Unmatched brackets")
                result['valid'] = False
        
        return result
    
    def _generate_auto_feedback(self, validation_result: Dict[str, Any]) -> str:
        """Generate automatic feedback based on validation."""
        feedback_parts = []
        
        if validation_result['errors']:
            feedback_parts.append("Fix these syntax errors:")
            feedback_parts.extend(f"- {error}" for error in validation_result['errors'])
        
        missing_patterns = []
        for pattern in self.tau_patterns:
            if pattern not in validation_result['patterns_found']:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            feedback_parts.append("\nConsider adding:")
            if 'stream_declaration' in missing_patterns:
                feedback_parts.append("- Stream declarations (sbf name = ifile/ofile)")
            if 'temporal_property' in missing_patterns:
                feedback_parts.append("- Temporal properties (always/sometimes)")
            if 'rule_definition' in missing_patterns:
                feedback_parts.append("- Rules (r name[t] = expression)")
        
        return '\n'.join(feedback_parts)
    
    async def _get_user_feedback(self, context: TranslationContext) -> str:
        """Get interactive user feedback."""
        print("\n" + "=" * 60)
        print("Current Tau Translation:")
        print("-" * 60)
        print(context.current_translation)
        print("-" * 60)
        
        validation = self._validate_tau_syntax(context.current_translation)
        print(f"\nValidation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
        print(f"Confidence: {validation['confidence']:.2f}")
        
        if validation['errors']:
            print("\nErrors:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        feedback = input("\nProvide feedback (or press Enter to accept): ").strip()
        return feedback or "Looks good"
    
    async def _refine_translation(self, context: TranslationContext, feedback: str) -> str:
        """Refine translation based on feedback."""
        refinement_prompt = f"""
        Original requirements:
        {context.original_text}
        
        Current Tau translation:
        {context.current_translation}
        
        Feedback:
        {feedback}
        
        Please refine the Tau specification based on the feedback.
        """
        
        # Use the same framework for refinement
        if self.framework == 'lmql':
            return await self._refine_with_lmql(refinement_prompt)
        elif self.framework == 'guidance':
            return await self._refine_with_guidance(refinement_prompt)
        elif self.framework in ['openai', 'anthropic', 'transformers']:
            # These use similar prompting
            return await self._translate_initial(refinement_prompt)
        else:
            # Pattern-based refinement
            return self._pattern_based_refinement(context, feedback)
    
    async def _refine_with_lmql(self, prompt: str) -> str:
        """Refine using LMQL."""
        try:
            query = '''
            argmax
                """{prompt}
                
                Refined Tau Specification:
                [REFINED_TAU]"""
            from
                "openai/gpt-3.5-turbo"
            where
                len(REFINED_TAU) < 1000
            '''
            
            result = await lmql.run(query, prompt=prompt)
            return result.variables['REFINED_TAU']
            
        except Exception as e:
            logger.error(f"LMQL refinement failed: {e}")
            return self.current_translation
    
    async def _refine_with_guidance(self, prompt: str) -> str:
        """Refine using Guidance."""
        try:
            program = guidance('''
            {{prompt}}
            
            Analyzing the feedback and current translation:
            {{#assistant~}}
            {{analysis}}
            {{/assistant}}
            
            Refined Tau specification:
            ```tau
            {{#assistant~}}
            {{refined_tau}}
            {{/assistant}}
            ```
            ''')
            
            result = program(prompt=prompt)
            return result['refined_tau']
            
        except Exception as e:
            logger.error(f"Guidance refinement failed: {e}")
            return self.current_translation
    
    def _pattern_based_refinement(self, context: TranslationContext, feedback: str) -> str:
        """Simple pattern-based refinement."""
        refined = context.current_translation
        
        # Add missing patterns based on feedback
        if "stream" in feedback.lower() and "sbf" not in refined:
            refined = "sbf input_stream = ifile(\"data.txt\")\n\n" + refined
        
        if "temporal" in feedback.lower() and "always" not in refined:
            lines = refined.strip().split('\n')
            if lines:
                refined += f"\n\nalways {lines[0].split('=')[0].strip()}"
        
        return refined


# Example usage function
async def example_usage():
    """Demonstrate the advanced translator."""
    translator = AdvancedLLMTranslator(preferred_framework="auto")
    
    requirements = """
    Create a safety monitoring system for industrial equipment.
    The system must continuously monitor temperature and pressure sensors.
    Temperature must stay between 20 and 80 degrees Celsius.
    Pressure must not exceed 100 PSI.
    If either limit is exceeded, activate the emergency shutdown.
    Log all sensor readings to a file every second.
    The emergency shutdown must engage within 100 milliseconds.
    """
    
    print("Translating requirements to Tau specification...")
    context = await translator.translate_requirements_to_tau(
        requirements,
        max_iterations=3,
        interactive=False
    )
    
    print("\nFinal Tau Specification:")
    print("=" * 60)
    print(context.current_translation)
    print("=" * 60)
    
    validation = translator._validate_tau_syntax(context.current_translation)
    print(f"\nValidation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
    print(f"Confidence: {validation['confidence']:.2f}")
    print(f"Patterns found: {', '.join(validation['patterns_found'])}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())