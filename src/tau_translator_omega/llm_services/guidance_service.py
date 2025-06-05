#!/usr/bin/env python3
"""
Guidance Framework Integration for TauTranslator
===============================================

Comprehensive implementation of Microsoft's Guidance framework for
structured Tau language generation with constraint satisfaction.

Features:
- Structured Tau code generation
- Grammar-aware validation
- Multi-step reasoning
- Error recovery and refinement
- Performance optimization

Author: DarkLightX/Dana Edwards
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import time
import re

try:
    import guidance
    from guidance import models, gen, select, capture, system, user, assistant
    GUIDANCE_AVAILABLE = True
except ImportError:
    GUIDANCE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class GuidanceConfig:
    """Configuration for Guidance service."""
    model_type: str = "transformers"  # "openai", "transformers", "local"
    model_name: str = "microsoft/phi-2"
    max_tokens: int = 1000
    temperature: float = 0.3
    cache_enabled: bool = True
    timeout_seconds: int = 30
    retry_attempts: int = 3


@dataclass
class TauGenerationRequest:
    """Request for Tau code generation."""
    requirements_text: str
    context: Optional[Dict[str, Any]] = None
    validation_level: str = "strict"  # "strict", "moderate", "permissive"
    expected_patterns: Optional[List[str]] = None
    max_refinement_iterations: int = 3


@dataclass
class TauGenerationResult:
    """Result from Tau code generation."""
    success: bool
    tau_code: str
    confidence_score: float
    validation_results: Dict[str, Any]
    generation_time: float
    refinement_iterations: int
    intermediate_steps: List[Dict[str, Any]]
    error_message: Optional[str] = None


class TauGrammarValidator:
    """Validates generated Tau code against grammar rules."""
    
    def __init__(self):
        self.tau_patterns = {
            'stream_declaration': r'sbf\s+\w+\s*=\s*(ifile|ofile|console)',
            'rule_definition': r'r\s+\w+\[.*?\]\s*=',
            'function_definition': r'\w+\s*\([^)]*\)\s*:=',
            'temporal_property': r'(always|sometimes|never|eventually)\s+',
            'constraint': r'\w+\[t\]\s*(>|<|>=|<=|=|!=)\s*\d+',
            'logical_operator': r'(&&|\|\||->|<->|!)',
            'quantifier': r'(forall|exists)\s+\w+',
            'stream_reference': r'\w+\[t\]',
            'balanced_parens': r'\([^()]*\)'
        }
    
    def validate(self, tau_code: str, validation_level: str = "strict") -> Dict[str, Any]:
        """
        Validate Tau code against grammar patterns.
        
        Args:
            tau_code: Generated Tau code to validate
            validation_level: "strict", "moderate", or "permissive"
            
        Returns:
            Validation results with score and feedback
        """
        result = {
            'valid': True,
            'confidence_score': 0.0,
            'errors': [],
            'warnings': [],
            'patterns_found': [],
            'missing_patterns': [],
            'suggestions': []
        }
        
        if not tau_code.strip():
            result['valid'] = False
            result['errors'].append("Empty Tau code")
            return result
        
        # Check for required patterns
        pattern_scores = {}
        for pattern_name, pattern_regex in self.tau_patterns.items():
            matches = re.findall(pattern_regex, tau_code, re.IGNORECASE)
            if matches:
                pattern_scores[pattern_name] = len(matches) / max(1, tau_code.count('\n') + 1)
                result['patterns_found'].append(pattern_name)
            else:
                pattern_scores[pattern_name] = 0.0
                result['missing_patterns'].append(pattern_name)
        
        # Calculate confidence score
        essential_patterns = ['rule_definition', 'constraint', 'logical_operator']
        optional_patterns = ['stream_declaration', 'temporal_property', 'quantifier']
        
        essential_score = sum(
            pattern_scores.get(p, 0) for p in essential_patterns
        ) / len(essential_patterns)
        
        optional_score = sum(
            pattern_scores.get(p, 0) for p in optional_patterns
        ) / len(optional_patterns)
        
        result['confidence_score'] = (essential_score * 0.7) + (optional_score * 0.3)
        
        # Syntax validation
        self._validate_syntax(tau_code, result, validation_level)
        
        # Generate suggestions
        self._generate_suggestions(result)
        
        return result
    
    def _validate_syntax(self, tau_code: str, result: Dict[str, Any], level: str):
        """Validate syntax based on validation level."""
        lines = tau_code.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check balanced parentheses
            if line.count('(') != line.count(')'):
                error = f"Line {i}: Unbalanced parentheses"
                if level == "strict":
                    result['errors'].append(error)
                    result['valid'] = False
                else:
                    result['warnings'].append(error)
            
            # Check balanced brackets
            if line.count('[') != line.count(']'):
                error = f"Line {i}: Unbalanced brackets"
                if level == "strict":
                    result['errors'].append(error)
                    result['valid'] = False
                else:
                    result['warnings'].append(error)
            
            # Check for undefined variables (basic check)
            if ':=' in line and level in ["strict", "moderate"]:
                parts = line.split(':=')
                if len(parts) == 2:
                    variables = re.findall(r'\b\w+\b', parts[1])
                    for var in variables:
                        if not any(f'{var}[' in prev_line for prev_line in tau_code[:tau_code.find(line)].split('\n')):
                            if var not in ['t', 'true', 'false'] and not var.isdigit():
                                result['warnings'].append(f"Possible undefined variable: {var}")
    
    def _generate_suggestions(self, result: Dict[str, Any]):
        """Generate improvement suggestions."""
        missing = result['missing_patterns']
        
        if 'stream_declaration' in missing:
            result['suggestions'].append("Consider adding stream declarations (sbf name = source)")
        
        if 'temporal_property' in missing:
            result['suggestions'].append("Add temporal properties (always, sometimes, eventually)")
        
        if 'rule_definition' in missing:
            result['suggestions'].append("Define rules (r name[t] = expression)")
        
        if 'constraint' in missing:
            result['suggestions'].append("Add constraints with comparison operators")


class GuidanceService:
    """Main Guidance service for Tau code generation."""
    
    def __init__(self, config: Optional[GuidanceConfig] = None):
        """Initialize Guidance service with configuration."""
        if not GUIDANCE_AVAILABLE:
            raise ImportError("Guidance framework not available. Install with: pip install guidance")
        
        self.config = config or GuidanceConfig()
        self.model = None
        self.validator = TauGrammarValidator()
        self.generation_stats = {
            'total_requests': 0,
            'successful_generations': 0,
            'average_generation_time': 0.0,
            'cache_hits': 0
        }
        
        # Initialize model
        self._initialize_model()
        
        logger.info(f"GuidanceService initialized with {self.config.model_type} model")
    
    def _initialize_model(self):
        """Initialize the Guidance model based on configuration."""
        try:
            if self.config.model_type == "openai":
                # Check for OpenAI API key
                if not os.getenv('OPENAI_API_KEY'):
                    logger.warning("OpenAI API key not found, falling back to local model")
                    self._initialize_local_model()
                else:
                    self.model = models.OpenAI(
                        model=self.config.model_name or "gpt-3.5-turbo",
                        api_key=os.getenv('OPENAI_API_KEY')
                    )
                    logger.info(f"Initialized OpenAI model: {self.config.model_name}")
            
            elif self.config.model_type == "transformers":
                self._initialize_transformers_model()
            
            else:
                self._initialize_local_model()
                
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            logger.info("Falling back to mock model for testing")
            self.model = None
    
    def _initialize_transformers_model(self):
        """Initialize transformers-based model."""
        try:
            self.model = models.Transformers(
                model=self.config.model_name,
                device_map="auto",
                torch_dtype="auto"
            )
            logger.info(f"Initialized Transformers model: {self.config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Transformers model: {e}")
            self._initialize_local_model()
    
    def _initialize_local_model(self):
        """Initialize local/mock model for testing."""
        try:
            # Try to use a small local model
            self.model = models.Transformers("microsoft/DialoGPT-small")
            logger.info("Initialized local DialoGPT model")
        except:
            logger.warning("No local model available, using mock responses")
            self.model = None
    
    async def generate_tau_code(self, request: TauGenerationRequest) -> TauGenerationResult:
        """
        Generate Tau code from natural language requirements.
        
        Args:
            request: Generation request with requirements and options
            
        Returns:
            Generation result with Tau code and validation
        """
        start_time = time.time()
        self.generation_stats['total_requests'] += 1
        
        intermediate_steps = []
        
        try:
            # Step 1: Initial analysis
            analysis_step = await self._analyze_requirements(request.requirements_text)
            intermediate_steps.append({
                'step': 'analysis',
                'result': analysis_step,
                'timestamp': time.time() - start_time
            })
            
            # Step 2: Generate initial Tau code
            initial_generation = await self._generate_initial_tau(request, analysis_step)
            intermediate_steps.append({
                'step': 'initial_generation',
                'result': initial_generation,
                'timestamp': time.time() - start_time
            })
            
            # Step 3: Validation and refinement
            final_result = await self._refine_tau_code(
                initial_generation, 
                request, 
                intermediate_steps,
                start_time
            )
            
            generation_time = time.time() - start_time
            self.generation_stats['average_generation_time'] = (
                (self.generation_stats['average_generation_time'] * (self.generation_stats['total_requests'] - 1) + 
                 generation_time) / self.generation_stats['total_requests']
            )
            
            if final_result.success:
                self.generation_stats['successful_generations'] += 1
            
            return final_result
            
        except Exception as e:
            logger.error(f"Tau generation failed: {e}")
            return TauGenerationResult(
                success=False,
                tau_code="",
                confidence_score=0.0,
                validation_results={},
                generation_time=time.time() - start_time,
                refinement_iterations=0,
                intermediate_steps=intermediate_steps,
                error_message=str(e)
            )
    
    async def _analyze_requirements(self, requirements_text: str) -> Dict[str, Any]:
        """Analyze requirements to identify key components."""
        if not self.model:
            # Mock analysis for testing
            return {
                'entities': ['system', 'sensor', 'alarm'],
                'constraints': ['temperature > 80', 'pressure < 100'],
                'temporal_aspects': ['always', 'within 1 second'],
                'actions': ['trigger alarm', 'log data']
            }
        
        try:
            with guidance.system():
                analysis_prompt = guidance('''
                You are a requirements analysis expert. Analyze the following requirements and extract key components:

                Requirements: {{requirements}}

                Extract the following:
                1. Key entities/variables:
                {{#geneach 'entities' num_iterations=5}}
                - {{gen 'this' pattern='[a-zA-Z_][a-zA-Z0-9_]*' max_tokens=10}}
                {{/geneach}}

                2. Constraints/conditions:
                {{#geneach 'constraints' num_iterations=3}}
                - {{gen 'this' max_tokens=20}}
                {{/geneach}}

                3. Temporal aspects:
                {{#geneach 'temporal' num_iterations=3}}
                - {{gen 'this' max_tokens=15}}
                {{/geneach}}

                4. Actions/behaviors:
                {{#geneach 'actions' num_iterations=3}}
                - {{gen 'this' max_tokens=20}}
                {{/geneach}}
                ''')
            
            result = analysis_prompt(requirements=requirements_text)
            
            return {
                'entities': [item.strip() for item in result.get('entities', []) if item.strip()],
                'constraints': [item.strip() for item in result.get('constraints', []) if item.strip()],
                'temporal_aspects': [item.strip() for item in result.get('temporal', []) if item.strip()],
                'actions': [item.strip() for item in result.get('actions', []) if item.strip()]
            }
            
        except Exception as e:
            logger.error(f"Requirements analysis failed: {e}")
            # Return basic analysis
            return {
                'entities': re.findall(r'\b[a-zA-Z_]\w*\b', requirements_text)[:5],
                'constraints': [],
                'temporal_aspects': [],
                'actions': []
            }
    
    async def _generate_initial_tau(self, request: TauGenerationRequest, analysis: Dict[str, Any]) -> str:
        """Generate initial Tau code based on analysis."""
        if not self.model:
            # Mock generation for testing
            entities = analysis.get('entities', ['sensor', 'alarm'])
            return f"""# Generated Tau specification
sbf input_stream = ifile("sensor_data.txt")
sbf output_stream = ofile("alarm_log.txt")

# Rules for {', '.join(entities[:3])}
r monitor[t] = {entities[0] if entities else 'sensor'}[t] > 80
r trigger_alarm[t] = monitor[t] && !alarm[t-1]

# Temporal properties
always (trigger_alarm[t] -> alarm[t])
"""
        
        try:
            with guidance.system():
                tau_prompt = guidance('''
                You are a Tau language expert. Convert these requirements to valid Tau specification.

                Requirements: {{requirements}}
                
                Analysis:
                - Entities: {{entities}}
                - Constraints: {{constraints}}
                - Temporal aspects: {{temporal}}
                - Actions: {{actions}}

                Generate a complete Tau specification:

                ```tau
                {{#assistant~}}
                {{gen 'tau_code' max_tokens=800 temperature=0.3}}
                {{/assistant}}
                ```
                ''')
            
            result = tau_prompt(
                requirements=request.requirements_text,
                entities=', '.join(analysis.get('entities', [])),
                constraints='; '.join(analysis.get('constraints', [])),
                temporal='; '.join(analysis.get('temporal_aspects', [])),
                actions='; '.join(analysis.get('actions', []))
            )
            
            tau_code = result.get('tau_code', '').strip()
            
            # Clean up the generated code
            tau_code = self._clean_tau_code(tau_code)
            
            return tau_code
            
        except Exception as e:
            logger.error(f"Initial Tau generation failed: {e}")
            # Return template-based generation
            return self._generate_template_tau(analysis)
    
    def _clean_tau_code(self, tau_code: str) -> str:
        """Clean and format generated Tau code."""
        lines = []
        for line in tau_code.split('\n'):
            line = line.strip()
            
            # Remove markdown code blocks
            if line.startswith('```'):
                continue
            
            # Skip empty lines at start/end
            if line or lines:
                lines.append(line)
        
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        
        return '\n'.join(lines)
    
    def _generate_template_tau(self, analysis: Dict[str, Any]) -> str:
        """Generate template-based Tau code as fallback."""
        entities = analysis.get('entities', ['sensor'])
        
        tau_code = f"""# Tau specification generated from requirements
# Entities: {', '.join(entities)}

# Stream declarations
sbf input_stream = ifile("data.txt")
sbf output_stream = ofile("results.txt")

"""
        
        # Add rules for entities
        for i, entity in enumerate(entities[:3]):
            tau_code += f"# Rule for {entity}\n"
            tau_code += f"r {entity}_rule[t] = {entity}[t] > 0\n\n"
        
        # Add temporal property
        if entities:
            tau_code += f"# Temporal properties\n"
            tau_code += f"always ({entities[0]}_rule[t] -> output[t])\n"
        
        return tau_code
    
    async def _refine_tau_code(self, initial_tau: str, request: TauGenerationRequest, 
                              intermediate_steps: List[Dict], start_time: float) -> TauGenerationResult:
        """Refine Tau code through validation and iteration."""
        current_tau = initial_tau
        refinement_iterations = 0
        
        for iteration in range(request.max_refinement_iterations):
            # Validate current Tau code
            validation_results = self.validator.validate(
                current_tau, 
                request.validation_level
            )
            
            intermediate_steps.append({
                'step': f'validation_{iteration}',
                'result': validation_results,
                'tau_code': current_tau,
                'timestamp': time.time() - start_time
            })
            
            # Check if validation passes
            if validation_results['valid'] and validation_results['confidence_score'] > 0.7:
                return TauGenerationResult(
                    success=True,
                    tau_code=current_tau,
                    confidence_score=validation_results['confidence_score'],
                    validation_results=validation_results,
                    generation_time=time.time() - start_time,
                    refinement_iterations=refinement_iterations,
                    intermediate_steps=intermediate_steps
                )
            
            # Generate refinement if needed
            if iteration < request.max_refinement_iterations - 1:
                refined_tau = await self._generate_refinement(
                    current_tau, 
                    validation_results, 
                    request.requirements_text
                )
                
                if refined_tau and refined_tau != current_tau:
                    current_tau = refined_tau
                    refinement_iterations += 1
                    
                    intermediate_steps.append({
                        'step': f'refinement_{iteration}',
                        'result': {'refined_tau': refined_tau},
                        'timestamp': time.time() - start_time
                    })
                else:
                    break
        
        # Final validation
        final_validation = self.validator.validate(current_tau, request.validation_level)
        
        return TauGenerationResult(
            success=final_validation['valid'],
            tau_code=current_tau,
            confidence_score=final_validation['confidence_score'],
            validation_results=final_validation,
            generation_time=time.time() - start_time,
            refinement_iterations=refinement_iterations,
            intermediate_steps=intermediate_steps
        )
    
    async def _generate_refinement(self, current_tau: str, validation_results: Dict[str, Any], 
                                  original_requirements: str) -> str:
        """Generate refined Tau code based on validation feedback."""
        if not self.model:
            # Simple rule-based refinement for testing
            return self._rule_based_refinement(current_tau, validation_results)
        
        try:
            feedback = []
            if validation_results['errors']:
                feedback.extend(validation_results['errors'])
            if validation_results['warnings']:
                feedback.extend(validation_results['warnings'])
            if validation_results['suggestions']:
                feedback.extend(validation_results['suggestions'])
            
            with guidance.system():
                refinement_prompt = guidance('''
                You are a Tau language expert. Improve the following Tau code based on validation feedback.

                Original requirements: {{requirements}}

                Current Tau code:
                ```tau
                {{current_tau}}
                ```

                Validation feedback:
                {{feedback}}

                Generate improved Tau code that addresses the feedback:

                ```tau
                {{#assistant~}}
                {{gen 'refined_tau' max_tokens=800 temperature=0.2}}
                {{/assistant}}
                ```
                ''')
            
            result = refinement_prompt(
                requirements=original_requirements,
                current_tau=current_tau,
                feedback='\n'.join(feedback)
            )
            
            refined_tau = result.get('refined_tau', '').strip()
            return self._clean_tau_code(refined_tau)
            
        except Exception as e:
            logger.error(f"Refinement generation failed: {e}")
            return self._rule_based_refinement(current_tau, validation_results)
    
    def _rule_based_refinement(self, current_tau: str, validation_results: Dict[str, Any]) -> str:
        """Apply rule-based refinements as fallback."""
        refined_tau = current_tau
        missing_patterns = validation_results.get('missing_patterns', [])
        
        # Add missing stream declarations
        if 'stream_declaration' in missing_patterns and 'sbf' not in refined_tau:
            stream_decl = "sbf input_stream = ifile(\"data.txt\")\nsbf output_stream = ofile(\"results.txt\")\n\n"
            refined_tau = stream_decl + refined_tau
        
        # Add temporal properties if missing
        if 'temporal_property' in missing_patterns and not re.search(r'(always|sometimes|eventually)', refined_tau):
            lines = refined_tau.strip().split('\n')
            rule_lines = [line for line in lines if line.strip().startswith('r ')]
            if rule_lines:
                rule_name = rule_lines[0].split('[')[0].replace('r ', '').strip()
                refined_tau += f"\n\n# Temporal property\nalways ({rule_name}[t] -> output[t])"
        
        return refined_tau
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service performance statistics."""
        return {
            'total_requests': self.generation_stats['total_requests'],
            'successful_generations': self.generation_stats['successful_generations'],
            'success_rate': (
                self.generation_stats['successful_generations'] / 
                max(1, self.generation_stats['total_requests'])
            ),
            'average_generation_time': self.generation_stats['average_generation_time'],
            'cache_hits': self.generation_stats['cache_hits'],
            'model_type': self.config.model_type,
            'model_name': self.config.model_name
        }


# Example usage and testing
async def test_guidance_service():
    """Test the Guidance service with sample requirements."""
    print("Testing Guidance Service...")
    
    # Test configuration
    config = GuidanceConfig(
        model_type="transformers",
        model_name="microsoft/phi-2",
        max_tokens=500,
        temperature=0.3
    )
    
    try:
        service = GuidanceService(config)
        
        # Test requirements
        test_requirements = [
            "Create a monitoring system for temperature sensors. If temperature exceeds 80 degrees, trigger an alarm.",
            "Implement a safety system that monitors pressure and temperature. Always ensure pressure is below 100 PSI.",
            "Design a data logging system that records sensor readings every second and alerts on anomalies."
        ]
        
        for i, requirements in enumerate(test_requirements, 1):
            print(f"\n--- Test Case {i} ---")
            print(f"Requirements: {requirements}")
            
            request = TauGenerationRequest(
                requirements_text=requirements,
                validation_level="moderate",
                max_refinement_iterations=2
            )
            
            result = await service.generate_tau_code(request)
            
            print(f"Success: {result.success}")
            print(f"Confidence: {result.confidence_score:.2f}")
            print(f"Generation time: {result.generation_time:.2f}s")
            print(f"Refinement iterations: {result.refinement_iterations}")
            
            if result.success:
                print("Generated Tau code:")
                print("-" * 40)
                print(result.tau_code)
                print("-" * 40)
            else:
                print(f"Error: {result.error_message}")
            
            # Show validation results
            validation = result.validation_results
            if validation:
                print(f"Validation - Valid: {validation.get('valid', False)}")
                print(f"Patterns found: {', '.join(validation.get('patterns_found', []))}")
                if validation.get('suggestions'):
                    print(f"Suggestions: {'; '.join(validation.get('suggestions', []))}")
        
        # Show service stats
        print(f"\n--- Service Statistics ---")
        stats = service.get_service_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
            
    except ImportError as e:
        print(f"Guidance not available: {e}")
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_guidance_service())