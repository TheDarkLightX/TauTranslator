"""
LLM Translation Service
=======================

Handles LLM-assisted translation for complex natural language inputs.
Provides multiple interpretations, explanations, and interactive clarification.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

from ..core.result_enhanced import Result, Success, Failure
from ..core.error_types import AppError, Errors
from ..core.functional_utils import safe_result
from .intent_analysis_service import IntentAnalysis, DomainContext

# Import LLM components
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent.parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from tau_translator_omega.llm_services.unified_llm_service import (
        UnifiedLLMService, UnifiedRequest, ProviderType
    )
    from tau_translator_omega.llm_sysprompts.tau_language_comprehensive_prompt import (
        get_tau_prompt, VALIDATION_EXAMPLES
    )
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logging.warning("LLM components not available")

logger = logging.getLogger(__name__)


@dataclass
class TranslationOption:
    """A single translation option with metadata."""
    tau_expression: str
    tce_expression: Optional[str]
    explanation: str
    confidence: float
    warnings: List[str]
    domain_context: Optional[DomainContext]


@dataclass
class LLMTranslationResult:
    """Result of LLM-assisted translation."""
    success: bool
    options: List[TranslationOption]
    primary_option: Optional[TranslationOption]
    clarification_needed: bool
    clarification_prompts: List[str]
    metadata: Dict[str, any]


@dataclass
class TauLLMConfig:
    """Configuration for Tau-aware LLM translation."""
    
    # LLM Connection Settings
    provider: str = "openai"  # "openai", "anthropic", "local", "ollama"
    api_key: Optional[str] = None
    model_name: str = "gpt-4"
    local_model_path: Optional[str] = None
    ollama_endpoint: str = "http://localhost:11434"
    
    # Tau Language Settings
    tau_prompt_path: str = "src/tau_translator_omega/llm_sysprompts/tau_language_comprehensive_prompt.py"
    include_examples: bool = True
    max_examples: int = 5
    
    # Knowledge Base Settings
    use_knowledge_base: bool = True
    knowledge_base_path: str = "data/tau_knowledge"
    learn_from_interactions: bool = True
    min_confidence_to_learn: float = 0.8
    
    # Translation Settings
    temperature: float = 0.3
    max_tokens: int = 2000
    num_options: int = 3
    include_explanations: bool = True
    
    # Interactive Mode Settings
    interactive_mode: bool = True
    clarification_threshold: float = 0.6
    max_clarification_rounds: int = 3
    
    @classmethod
    def from_env(cls) -> "TauLLMConfig":
        """Load configuration from environment variables (≤10 lines)."""
        return cls(
            provider=os.getenv("TAU_LLM_PROVIDER", "openai"),
            api_key=os.getenv("TAU_LLM_API_KEY"),
            model_name=os.getenv("TAU_LLM_MODEL", "gpt-4"),
            local_model_path=os.getenv("TAU_LOCAL_MODEL_PATH"),
            ollama_endpoint=os.getenv("TAU_OLLAMA_ENDPOINT", "http://localhost:11434"),
            use_knowledge_base=os.getenv("TAU_USE_KB", "true").lower() == "true",
            interactive_mode=os.getenv("TAU_INTERACTIVE", "true").lower() == "true"
        )
    
    def validate(self) -> Result[bool, str]:
        """Validate configuration (≤10 lines)."""
        if self.provider in ["openai", "anthropic"] and not self.api_key:
            return Failure(f"API key required for {self.provider}")
        
        if self.provider == "local" and not self.local_model_path:
            return Failure("Local model path required for local provider")
        
        # Don't fail on missing prompt file - we have a default
        # if not os.path.exists(self.tau_prompt_path):
        #     return Failure(f"Tau prompt file not found: {self.tau_prompt_path}")
            
        return Success(True)

class LLMTranslationService:
    """
    Service for LLM-assisted translation of complex natural language.
    
    Provides multiple interpretations, explanations, and supports
    interactive clarification similar to Claude Code.
    Now includes memory and learning capabilities.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize with LLM service and configuration."""
        self.config = config or {}
        self.llm_service = None
        self.max_options = self.config.get('max_options', 3)
        self.temperature = self.config.get('temperature', 0.3)
        self.provider = self._get_provider()
        
        # Initialize memory service
        from .translation_memory_service import TranslationMemoryService
        memory_config = self.config.get('memory_config', {})
        self.memory_service = TranslationMemoryService(memory_config)
        
        if LLM_AVAILABLE:
            self.llm_service = UnifiedLLMService()
    
    def translate_with_llm(
        self,
        text: str,
        intent_analysis: IntentAnalysis,
        user_id: Optional[str] = None
    ) -> Result[LLMTranslationResult, AppError]:
        """
        Translate using LLM with multiple options and explanations.
        Now includes memory search and learning.
        
        Args:
            text: Natural language input
            intent_analysis: Results from intent analysis
            user_id: Optional user ID for personalized memories
            
        Returns:
            LLMTranslationResult with options and metadata
        """
        if not LLM_AVAILABLE or not self.llm_service:
            return Failure(Errors.internal("LLM service not available"))
        
        # Search memory for similar translations
        memory_result = self.memory_service.search_memories(
            text,
            memory_types=None,  # Search all types
            user_id=user_id,
            limit=5
        )
        
        return (
            self._prepare_context_with_memory(text, intent_analysis, memory_result, user_id)
            .bind(self._generate_translations)
            .bind(self._analyze_options)
            .bind(self._check_clarification_needed)
            .bind(lambda data: self._create_and_remember_result(data, text, user_id))
        )
    
    def clarify_translation(
        self,
        original_text: str,
        clarification: str,
        previous_result: LLMTranslationResult,
        user_id: Optional[str] = None
    ) -> Result[LLMTranslationResult, AppError]:
        """Handle user clarification and regenerate translations."""
        enhanced_prompt = self._create_clarification_prompt(
            original_text,
            clarification,
            previous_result
        )
        
        result = self._generate_with_prompt(enhanced_prompt)
        
        # Save clarification to memory if successful
        if isinstance(result, Success):
            llm_result = result.unwrap()
            if llm_result.success and llm_result.primary_option:
                self.memory_service.remember_clarification(
                    original_text=original_text,
                    clarification=clarification,
                    final_translation=llm_result.primary_option.tau_expression,
                    user_id=user_id
                )
        
        return result
    
    def _get_provider(self) -> ProviderType:
        """Get configured LLM provider."""
        provider_name = self.config.get('provider', 'openai')
        provider_map = {
            'openai': ProviderType.OPENAI,
            'anthropic': ProviderType.ANTHROPIC,
            'openrouter': ProviderType.OPENROUTER,
            'local': ProviderType.LOCAL_MODELS
        }
        return provider_map.get(provider_name, ProviderType.OPENAI)
    
    def _prepare_context(
        self,
        text: str,
        intent_analysis: IntentAnalysis
    ) -> Result[Dict, AppError]:
        """Prepare context for LLM translation."""
        # Get appropriate prompt based on intent
        base_prompt = get_tau_prompt('nl_to_tau')
        
        # Add domain-specific context
        domain_context = self._get_domain_context(intent_analysis.domain_contexts)
        
        # Create enhanced prompt
        context = {
            'text': text,
            'base_prompt': base_prompt,
            'domain_context': domain_context,
            'intent_analysis': intent_analysis,
            'examples': self._get_relevant_examples(intent_analysis)
        }
        
        return Success(context)
    
    def _prepare_context_with_memory(
        self,
        text: str,
        intent_analysis: IntentAnalysis,
        memory_result: Result,
        user_id: Optional[str]
    ) -> Result[Dict, AppError]:
        """Prepare context with memory information."""
        # Get base context
        base_context_result = self._prepare_context(text, intent_analysis)
        
        if isinstance(base_context_result, Failure):
            return base_context_result
        
        context = base_context_result.unwrap()
        
        # Add memory context if available
        if isinstance(memory_result, Success):
            memories = memory_result.unwrap()
            
            # Add exact match if found
            if memories.exact_match:
                context['exact_match'] = {
                    'source': memories.exact_match.source_text,
                    'target': memories.exact_match.target_text,
                    'confidence': memories.exact_match.confidence
                }
            
            # Add similar translations
            if memories.similar_matches:
                context['similar_translations'] = [
                    {
                        'source': mem.source_text,
                        'target': mem.target_text,
                        'confidence': mem.confidence,
                        'type': mem.memory_type.value
                    }
                    for mem in memories.similar_matches[:3]
                ]
            
            # Add user preferences if available
            if user_id:
                prefs_result = self.memory_service.get_user_preferences(user_id)
                if isinstance(prefs_result, Success):
                    context['user_preferences'] = prefs_result.unwrap()
        
        return Success(context)
    
    def _generate_translations(
        self,
        context: Dict
    ) -> Result[List[Dict], AppError]:
        """Generate multiple translation options using LLM."""
        prompt = self._build_translation_prompt(context)
        
        # Run async LLM generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            options = []
            
            # Generate multiple options with different temperatures
            temperatures = [0.1, 0.3, 0.5] if self.max_options >= 3 else [0.2]
            
            for temp in temperatures[:self.max_options]:
                result = loop.run_until_complete(
                    self._generate_single_option(prompt, temp)
                )
                if result:
                    options.append(result)
            
            return Success(options) if options else Failure(
                Errors.internal("Failed to generate translations")
            )
            
        finally:
            loop.close()
    
    async def _generate_single_option(
        self,
        prompt: str,
        temperature: float
    ) -> Optional[Dict]:
        """Generate a single translation option."""
        request = UnifiedRequest(
            prompt=prompt,
            system_prompt=get_tau_prompt('general'),
            max_tokens=800,
            temperature=temperature,
            provider_preference=self.provider
        )
        
        response = await self.llm_service.generate(request)
        
        if response.success:
            return self._parse_llm_response(response.generated_text)
        return None
    
    def _build_translation_prompt(self, context: Dict) -> str:
        """Build comprehensive translation prompt with memory context."""
        text = context['text']
        intent = context['intent_analysis']
        
        # Build memory context section
        memory_section = ""
        
        if context.get('exact_match'):
            match = context['exact_match']
            memory_section += f"\n\nPrevious exact translation found:\nInput: \"{match['source']}\"\nTau: {match['target']}\nConfidence: {match['confidence']:.2f}"
        
        if context.get('similar_translations'):
            memory_section += "\n\nSimilar translations from memory:"
            for trans in context['similar_translations']:
                memory_section += f"\n- \"{trans['source']}\" → {trans['target']} (confidence: {trans['confidence']:.2f})"
        
        if context.get('user_preferences'):
            prefs = context['user_preferences']
            if prefs:
                memory_section += f"\n\nUser preferences: {', '.join(f'{k}: {v}' for k, v in prefs.items())}"
        
        prompt = f"""{context['base_prompt']}

User Input: "{text}"

Context Analysis:
- Complexity: {intent.complexity_score:.2f}
- Domains: {', '.join(d.value for d in intent.domain_contexts)}
- Key Patterns: {', '.join(intent.key_patterns)}

{context['domain_context']}
{memory_section}

Please provide:
1. A Tau expression that captures the user's intent
2. The intermediate TCE expression (if applicable)
3. A clear explanation of your interpretation
4. Any assumptions made
5. Alternative interpretations if the input is ambiguous

Format your response as:
TAU: <expression>
TCE: <expression or "N/A">
EXPLANATION: <explanation>
ASSUMPTIONS: <list assumptions or "None">
ALTERNATIVES: <alternative interpretations or "None">
CONFIDENCE: <0.0-1.0>
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse structured response from LLM."""
        lines = response.strip().split('\n')
        result = {
            'tau': '',
            'tce': None,
            'explanation': '',
            'assumptions': [],
            'alternatives': [],
            'confidence': 0.7
        }
        
        current_field = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TAU:'):
                result['tau'] = line[4:].strip()
                current_field = 'tau'
            elif line.startswith('TCE:'):
                tce = line[4:].strip()
                result['tce'] = None if tce == 'N/A' else tce
                current_field = 'tce'
            elif line.startswith('EXPLANATION:'):
                result['explanation'] = line[12:].strip()
                current_field = 'explanation'
            elif line.startswith('ASSUMPTIONS:'):
                assumptions = line[12:].strip()
                if assumptions != 'None':
                    result['assumptions'] = [
                        a.strip() for a in assumptions.split(',')
                    ]
                current_field = 'assumptions'
            elif line.startswith('ALTERNATIVES:'):
                alts = line[13:].strip()
                if alts != 'None':
                    result['alternatives'] = [
                        a.strip() for a in alts.split(';')
                    ]
                current_field = 'alternatives'
            elif line.startswith('CONFIDENCE:'):
                try:
                    result['confidence'] = float(line[11:].strip())
                except ValueError:
                    result['confidence'] = 0.5
            elif current_field == 'explanation' and line:
                result['explanation'] += ' ' + line
        
        return result
    
    def _analyze_options(
        self,
        options: List[Dict]
    ) -> Result[List[TranslationOption], AppError]:
        """Analyze and rank translation options."""
        translation_options = []
        
        for opt in options:
            warnings = []
            
            # Check for common issues
            if not opt.get('tau'):
                warnings.append("Empty Tau expression generated")
                continue
            
            if opt.get('assumptions'):
                warnings.append(f"Assumptions made: {', '.join(opt['assumptions'])}")
            
            # Create TranslationOption
            translation_options.append(TranslationOption(
                tau_expression=opt['tau'],
                tce_expression=opt.get('tce'),
                explanation=opt.get('explanation', 'No explanation provided'),
                confidence=opt.get('confidence', 0.5),
                warnings=warnings,
                domain_context=None  # Could be enhanced
            ))
        
        # Sort by confidence
        translation_options.sort(key=lambda x: x.confidence, reverse=True)
        
        return Success(translation_options)
    
    def _check_clarification_needed(
        self,
        options: List[TranslationOption]
    ) -> Result[Tuple[List[TranslationOption], bool, List[str]], AppError]:
        """Check if clarification is needed from user."""
        clarification_needed = False
        clarification_prompts = []
        
        if not options:
            clarification_needed = True
            clarification_prompts.append(
                "Could you please rephrase your requirement more specifically?"
            )
        elif len(options) > 1:
            # Check confidence spread
            confidences = [opt.confidence for opt in options]
            if max(confidences) - min(confidences) < 0.2:
                clarification_needed = True
                clarification_prompts.append(
                    "Your input could be interpreted in multiple ways. Could you clarify:"
                )
                
                # Generate specific clarification questions
                for i, opt in enumerate(options[:2]):
                    clarification_prompts.append(
                        f"Option {i+1}: Did you mean '{opt.explanation}'?"
                    )
        
        # Check for low confidence
        if options and options[0].confidence < 0.6:
            clarification_needed = True
            clarification_prompts.append(
                "I'm not fully confident in my interpretation. Could you provide more context?"
            )
        
        return Success((options, clarification_needed, clarification_prompts))
    
    def _create_result(
        self,
        data: Tuple[List[TranslationOption], bool, List[str]]
    ) -> Result[LLMTranslationResult, AppError]:
        """Create final LLM translation result."""
        options, clarification_needed, clarification_prompts = data
        
        result = LLMTranslationResult(
            success=len(options) > 0,
            options=options,
            primary_option=options[0] if options else None,
            clarification_needed=clarification_needed,
            clarification_prompts=clarification_prompts,
            metadata={
                'provider': self.provider.value,
                'temperature': self.temperature,
                'options_generated': len(options)
            }
        )
        
        return Success(result)
    
    def _create_and_remember_result(
        self,
        data: Tuple[List[TranslationOption], bool, List[str]],
        original_text: str,
        user_id: Optional[str]
    ) -> Result[LLMTranslationResult, AppError]:
        """Create result and save to memory if successful."""
        # Create the result
        result = self._create_result(data)
        
        if isinstance(result, Success):
            llm_result = result.unwrap()
            
            # Save successful primary translation to memory
            if llm_result.success and llm_result.primary_option:
                option = llm_result.primary_option
                
                # Save the translation
                self.memory_service.remember_translation(
                    source=original_text,
                    target=option.tau_expression,
                    confidence=option.confidence,
                    metadata={
                        'tce': option.tce_expression,
                        'explanation': option.explanation,
                        'domains': [d.value for d in data[0][0].domain_context.domain_contexts]
                            if hasattr(data[0][0], 'domain_context') else []
                    },
                    user_id=user_id
                )
                
                # Also save TCE if available
                if option.tce_expression:
                    self.memory_service.remember_translation(
                        source=original_text,
                        target=option.tce_expression,
                        confidence=option.confidence * 0.9,  # Slightly lower for intermediate
                        metadata={
                            'translation_type': 'tce_intermediate',
                            'tau_target': option.tau_expression
                        },
                        user_id=user_id
                    )
        
        return result
    
    def _get_domain_context(self, domains: List[DomainContext]) -> str:
        """Get domain-specific context for prompt."""
        context_parts = []
        
        domain_hints = {
            DomainContext.TEMPORAL: "Use temporal operators (always/[], sometimes/<>)",
            DomainContext.QUANTIFIED: "Use quantifiers (all x, ex x)",
            DomainContext.CONDITIONAL: "Use implication (->)",
            DomainContext.ACCESS_CONTROL: "Express permissions and constraints",
            DomainContext.MATHEMATICAL: "Use comparisons (=, <, >, <=, >=)"
        }
        
        for domain in domains:
            if domain in domain_hints:
                context_parts.append(domain_hints[domain])
        
        return "Domain hints: " + "; ".join(context_parts) if context_parts else ""
    
    def _get_relevant_examples(self, intent: IntentAnalysis) -> List[Dict]:
        """Get examples relevant to the detected domains."""
        relevant = []
        
        for example in VALIDATION_EXAMPLES:
            # Simple relevance check - could be enhanced
            if any(domain.value in example['explanation'].lower() 
                   for domain in intent.domain_contexts):
                relevant.append(example)
        
        return relevant[:3]  # Limit examples
    
    def _create_clarification_prompt(
        self,
        original_text: str,
        clarification: str,
        previous_result: LLMTranslationResult
    ) -> str:
        """Create prompt incorporating user clarification."""
        previous_options = "\n".join(
            f"- {opt.tau_expression} ({opt.explanation})"
            for opt in previous_result.options[:3]
        )
        
        return f"""Original request: "{original_text}"

Previous interpretations:
{previous_options}

User clarification: "{clarification}"

Based on this clarification, please provide the correct Tau translation.

TAU: <expression>
EXPLANATION: <clear explanation incorporating the clarification>
CONFIDENCE: <0.0-1.0>"""
    
    def _generate_with_prompt(self, prompt: str) -> Result[LLMTranslationResult, AppError]:
        """Generate translation with a custom prompt."""
        if not self.llm_service:
            return Failure(Errors.internal("LLM service not available"))
        
        # Create simple context for generation
        context = {
            'text': prompt,
            'base_prompt': get_tau_prompt('general'),
            'domain_context': "",
            'intent_analysis': None,
            'examples': []
        }
        
        return (
            Success(context)
            .bind(self._generate_translations)
            .bind(self._analyze_options)
            .bind(lambda opts: Success((opts, False, [])))  # No clarification for clarifications
            .bind(self._create_result)
        )

class EnhancedTauLLMService(LLMTranslationService):
    """
    Enhanced LLM service specifically for Tau language translation.
    Integrates knowledge base, prompt loading, and multiple LLM providers.
    """
    
    def __init__(self, config: Optional[TauLLMConfig] = None):
        """Initialize with Tau-specific configuration (≤10 lines)."""
        self.tau_config = config or TauLLMConfig.from_env()
        
        # Validate configuration
        validation = self.tau_config.validate()
        if isinstance(validation, Failure):
            raise ValueError(f"Invalid configuration: {validation.failure()}")
        
        # Initialize base class with config dict
        super().__init__(self.tau_config.__dict__)
        
        # Initialize Tau-specific components
        self.tau_prompt = self._load_tau_prompt()
        # Import TauKnowledgeBase from the correct location
        if self.tau_config.use_knowledge_base:
            from .translation_memory_service import TauKnowledgeBase
            self.knowledge_base = TauKnowledgeBase()
        else:
            self.knowledge_base = None
        self.llm_provider = self._initialize_llm_provider()
    
    def _load_tau_prompt(self) -> str:
        """Load Tau language prompt from file and grammar (≤10 lines)."""
        try:
            # Import the prompt module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "tau_prompt", 
                self.tau_config.tau_prompt_path
            )
            tau_prompt_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tau_prompt_module)
            
            # Get the comprehensive prompt
            base_prompt = tau_prompt_module.TAU_LANGUAGE_COMPREHENSIVE_PROMPT
            
            # Enhance with actual grammar if available
            enhanced_prompt = self._enhance_prompt_with_grammar(base_prompt)
            return enhanced_prompt
        except Exception as e:
            logger.warning(f"Failed to load Tau prompt: {e}, using default")
            return self._get_default_tau_prompt_with_grammar()
    
    def _initialize_llm_provider(self):
        """Initialize LLM provider based on configuration (≤10 lines)."""
        provider = self.tau_config.provider
        
        if provider == "openai":
            return self._init_openai_provider()
        elif provider == "anthropic":
            return self._init_anthropic_provider()
        elif provider == "ollama":
            return self._init_ollama_provider()
        elif provider == "local":
            return self._init_local_provider()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _init_openai_provider(self):
        """Initialize OpenAI provider (≤10 lines)."""
        try:
            import openai
            openai.api_key = self.tau_config.api_key
            return openai
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def _init_anthropic_provider(self):
        """Initialize Anthropic provider (≤10 lines)."""
        try:
            import anthropic
            return anthropic.Client(api_key=self.tau_config.api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    def _init_ollama_provider(self):
        """Initialize Ollama provider (≤10 lines)."""
        try:
            import requests
            # Test connection
            response = requests.get(f"{self.tau_config.ollama_endpoint}/api/tags")
            if response.status_code != 200:
                raise ConnectionError(f"Cannot connect to Ollama at {self.tau_config.ollama_endpoint}")
            return self.tau_config.ollama_endpoint
        except Exception as e:
            raise ConnectionError(f"Ollama initialization failed: {e}")
    
    def _init_local_provider(self):
        """Initialize local model provider (≤10 lines)."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model = AutoModelForCausalLM.from_pretrained(self.tau_config.local_model_path)
            tokenizer = AutoTokenizer.from_pretrained(self.tau_config.local_model_path)
            return {"model": model, "tokenizer": tokenizer}
        except ImportError:
            raise ImportError("Transformers not installed. Run: pip install transformers")
    
    async def translate_with_tau_context(
        self, 
        text: str, 
        user_context: Optional[str] = None
    ) -> LLMTranslationResult:
        """Translate with full Tau context and knowledge base (≤10 lines)."""
        # Check knowledge base first
        if self.knowledge_base:
            component = self.knowledge_base.find_component(text)
            if component and component["confidence"] >= 0.9:
                return self._create_component_result(component, text)
        
        # Prepare enhanced context
        context = self._prepare_tau_context(text, user_context)
        
        # Get translation options
        # Create a simple intent analysis for now
        from .intent_analysis_service import IntentAnalysis, DomainContext, TranslationPath
        intent_analysis = IntentAnalysis(
            text=text,
            complexity_score=0.7,
            ambiguity_score=0.3,
            domain_contexts=[DomainContext.MATHEMATICAL],
            recommended_path=TranslationPath.LLM_ASSISTED,
            confidence=0.8,
            key_patterns=["specification"],
            warnings=[]
        )
        
        # Call the base translate_with_llm method
        llm_service = LLMTranslationService(self.tau_config.__dict__)
        result_monad = llm_service.translate_with_llm(text, intent_analysis)
        
        # Unwrap the Result monad
        if hasattr(result_monad, 'unwrap'):
            try:
                result = result_monad.unwrap()
            except Exception as e:
                # Return a failure result
                return LLMTranslationResult(
                    success=False,
                    options=[],
                    primary_option=None,
                    clarification_needed=False,
                    clarification_prompts=[],
                    metadata={"error": str(e)}
                )
        else:
            result = result_monad
        
        # Learn from high-confidence results
        if self.tau_config.learn_from_interactions and result.success:
            await self._learn_from_result(text, result)
        
        return result
    
    def _prepare_tau_context(self, text: str, user_context: Optional[str]) -> str:
        """Prepare context with Tau prompt and examples (≤10 lines)."""
        context_parts = [self.tau_prompt]
        
        # Add knowledge base examples
        if self.knowledge_base:
            examples = self.knowledge_base.get_tau_examples(text)
            if examples:
                context_parts.append("\n## Similar Examples:")
                for ex in examples[:self.tau_config.max_examples]:
                    context_parts.append(f"- {ex['description']}: `{ex['tau']}`")
        
        # Add user context
        if user_context:
            context_parts.append(f"\n## User Context:\n{user_context}")
        
        return "\n".join(context_parts)
    
    def _create_component_result(self, component: Dict, original_text: str) -> LLMTranslationResult:
        """Create result from component library match (≤10 lines)."""
        option = TranslationOption(
            tau_expression=component["tau"],
            tce_expression=None,
            explanation=f"Standard component: {component['description']}",
            confidence=component["confidence"],
            warnings=[],
            domain_context=None
        )
        
        return LLMTranslationResult(
            success=True,
            options=[option],
            primary_option=option,
            clarification_needed=False,
            clarification_prompts=[],
            metadata={
                "source": "component_library",
                "component_id": component["id"],
                "original_text": original_text
            }
        )
    
    async def _learn_from_result(self, text: str, result: LLMTranslationResult):
        """Learn from translation result if confidence is high (≤10 lines)."""
        if not result.options or not self.knowledge_base:
            return
        
        best_option = max(result.options, key=lambda x: x.confidence)
        
        if best_option.confidence >= self.tau_config.min_confidence_to_learn:
            # Note: learn_from_translation is not async, so no await needed
            self.knowledge_base.learn_from_translation(
                text,
                best_option.tau_expression,
                best_option.confidence
            )
    
    def _enhance_prompt_with_grammar(self, base_prompt: str) -> str:
        """Enhance prompt with actual Tau grammar (≤10 lines)."""
        grammar_content = self._load_tau_grammar()
        if grammar_content:
            return f"""{base_prompt}

## ACTUAL TAU GRAMMAR SPECIFICATION
The following is the actual Tau parser grammar that defines the exact syntax:

```lark
{grammar_content}
```

Use this grammar to ensure your translations follow the exact Tau syntax rules.
"""
        return base_prompt
    
    def _load_tau_grammar(self) -> Optional[str]:
        """Load the actual Tau grammar file (≤10 lines)."""
        from ..core.tau_grammar_loader import TauGrammarLoader
        
        # Load grammar using centralized loader
        content, path = TauGrammarLoader.load_grammar(preferred='tau_controlled')
        
        if content:
            logger.info(f"Loaded Tau grammar for LLM from {path}")
            # Also extract key rules for quick reference
            self.grammar_rules = TauGrammarLoader.extract_grammar_rules(content)
            
        return content
    
    def _get_default_tau_prompt_with_grammar(self) -> str:
        """Get default prompt with grammar if available (≤10 lines)."""
        base = self._get_default_tau_prompt()
        return self._enhance_prompt_with_grammar(base)
    
    def _get_default_tau_prompt(self) -> str:
        """Get default Tau prompt if file loading fails (≤10 lines)."""
        return """
You are an expert in Tau language, a formal specification language for logical and temporal properties.

Tau Language Quick Reference:
- Boolean Functions (bf): Variables like x, y, z with operators &, |, ', +
- Well-Formed Formulas (wff): Created by comparisons (=, !=, <, >) with operators &&, ||, !, ->, <->
- Quantifiers: all x (...), ex x (...)
- Temporal: always/[], sometimes/<>

Examples:
- 1-bit adder: adder1(a, b, sum, carry) := (sum = a + b) && (carry = a & b).
- Bit constraint: bit(x) := (x = 0) || (x = 1).
- Verification: all x, y (bit(x) && bit(y) -> valid(x, y)).

When translating, provide clear Tau specifications with explanations.
"""
    
    async def interactive_translation_session(
        self, 
        initial_text: str
    ) -> AsyncIterator[Union[LLMTranslationResult, str]]:
        """Start an interactive translation session (≤10 lines)."""
        context = [f"User wants to specify: {initial_text}"]
        clarification_count = 0
        
        while clarification_count < self.tau_config.max_clarification_rounds:
            result = await self.translate_with_tau_context(
                initial_text, 
                "\n".join(context)
            )
            
            yield result
            
            if not result.needs_clarification:
                break
            
            # Wait for user response (yielded as string)
            user_response = yield result.clarification_prompt
            context.append(f"User clarification: {user_response}")
            clarification_count += 1
    
    def generate_tau_with_prompt(self, text: str, custom_prompt: str) -> str:
        """Generate Tau translation with custom prompt (≤10 lines)."""
        full_prompt = f"{self.tau_prompt}\n\n{custom_prompt}\n\nTranslate to Tau: {text}"
        
        if self.tau_config.provider == "openai":
            return self._generate_openai(full_prompt)
        elif self.tau_config.provider == "anthropic":
            return self._generate_anthropic(full_prompt)
        elif self.tau_config.provider == "ollama":
            return self._generate_ollama(full_prompt)
        elif self.tau_config.provider == "local":
            return self._generate_local(full_prompt)
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI (≤10 lines)."""
        response = self.llm_provider.ChatCompletion.create(
            model=self.tau_config.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.tau_config.temperature,
            max_tokens=self.tau_config.max_tokens
        )
        return response.choices[0].message.content
    
    def _generate_anthropic(self, prompt: str) -> str:
        """Generate using Anthropic (≤10 lines)."""
        response = self.llm_provider.completions.create(
            prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
            model=self.tau_config.model_name,
            max_tokens_to_sample=self.tau_config.max_tokens,
            temperature=self.tau_config.temperature
        )
        return response.completion
    
    def _generate_ollama(self, prompt: str) -> str:
        """Generate using Ollama (≤10 lines)."""
        import requests
        
        response = requests.post(
            f"{self.llm_provider}/api/generate",
            json={
                "model": self.tau_config.model_name,
                "prompt": prompt,
                "temperature": self.tau_config.temperature
            }
        )
        
        return response.json()["response"]
    
    def _generate_local(self, prompt: str) -> str:
        """Generate using local model (≤10 lines)."""
        model = self.llm_provider["model"]
        tokenizer = self.llm_provider["tokenizer"]
        
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(
            **inputs,
            max_new_tokens=self.tau_config.max_tokens,
            temperature=self.tau_config.temperature
        )
        
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
