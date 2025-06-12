"""
Enhanced NLP Translation Service
Integrates the complex English parser with existing translation infrastructure.

Provides seamless English→TCE→TAU translation with support for:
- Complex relative clauses
- Coreference resolution
- Nested quantifiers
- Property chaining

Copyright: DarkLightX/Dana Edwards
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import re

from .nlp_translation_service import NLPTranslationService
from .complex_english_parser import ComplexEnglishParser, parse_complex_english
from .tce_types import TCEExpression
from ..core.domain_types import SourceText
from ..core.result_enhanced import Result, Success, Failure

@dataclass
class ParsedStructure:
    """Represents a parsed linguistic structure."""
    tau_formula: str
    tce_expression: str
    entities: List[Dict[str, Any]]
    confidence: float

class EnhancedNLPTranslationService(NLPTranslationService):
    """Enhanced NLP service with complex English parsing capabilities."""
    
    def __init__(self):
        super().__init__()
        self.complex_parser = ComplexEnglishParser()
        
    def translate_to_tce(self, source: SourceText) -> Result[TCEExpression]:
        """Translate English to TCE with enhanced parsing."""
        text = source.text.strip()
        
        # Try complex parsing first for sentences with certain indicators
        if self._should_use_complex_parser(text):
            result = self._translate_with_complex_parser(text)
            if result.is_success():
                return result
        
        # Fall back to pattern-based translation
        return super().translate_to_tce(source)
    
    def translate_to_tau(self, source: SourceText) -> Result[str]:
        """Direct English to TAU translation using complex parser."""
        text = source.text.strip()
        
        try:
            # Use complex parser for direct TAU generation
            tau_formula = parse_complex_english(text)
            return Success(tau_formula)
        except Exception as e:
            # Fall back to TCE pipeline
            tce_result = self.translate_to_tce(source)
            if tce_result.is_error():
                return Failure(f"Complex parsing failed: {e}, TCE fallback failed: {tce_result.error}")
            
            # Convert TCE to TAU
            from .ilr_tau_translation_service import create_ilr_tau_translation_service
            tau_service = create_ilr_tau_translation_service()
            tau_result = tau_service.translate_tce_to_tau(tce_result.unwrap().expression)
            return tau_result
    
    def _should_use_complex_parser(self, text: str) -> bool:
        """Determine if text needs complex parsing."""
        text_lower = text.lower()
        
        # Indicators of complexity
        complex_indicators = [
            'who', 'which', 'that',  # Relative clauses
            'the ', 'the person', 'the car',  # Definite references (coreference)
            'if .* then',  # Conditionals
            'owns', 'has', 'have',  # Relations
            'every .* who', 'all .* who',  # Quantified relative clauses
            ', if', 'and if',  # Complex conditional structures
        ]
        
        # Check for complexity indicators
        complexity_score = 0
        for indicator in complex_indicators:
            if re.search(indicator, text_lower):
                complexity_score += 1
        
        # Use complex parser if score > 2 or has relative clauses
        return complexity_score >= 2 or any(rel in text_lower for rel in ['who', 'which', 'that'])
    
    def _translate_with_complex_parser(self, text: str) -> Result[TCEExpression]:
        """Use complex parser to generate TCE."""
        try:
            # Parse to logical form
            logical_form = self.complex_parser.parse(text)
            tau_formula = logical_form.to_tau()
            
            # Convert TAU formula to TCE-like expression
            tce_text = self._tau_to_tce_approximation(tau_formula)
            
            return Success(TCEExpression(expression=tce_text))
            
        except Exception as e:
            return Failure(f"Complex parsing failed: {str(e)}")
    
    def _tau_to_tce_approximation(self, tau_formula: str) -> str:
        """Convert TAU formula to TCE-like syntax (approximation)."""
        # This is a simplified conversion - in production would be more sophisticated
        tce = tau_formula
        
        # Basic conversions
        conversions = [
            ('∀', 'forall'),
            ('∃', 'exists'),
            ('→', 'implies'),
            ('∧', 'and'),
            ('∨', 'or'),
            ('¬', 'not'),
            (': (', ': '),  # Simplify scoping
        ]
        
        for old, new in conversions:
            tce = tce.replace(old, new)
        
        # Handle quantifier syntax
        tce = re.sub(r'forall(\w+):', r'forall \1:', tce)
        tce = re.sub(r'exists(\w+):', r'exists \1 such that', tce)
        
        return tce
    
    def analyze_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze the linguistic complexity of input text."""
        features = {
            'has_quantifiers': bool(re.search(r'\b(all|every|some|no|each)\b', text.lower())),
            'has_relative_clauses': bool(re.search(r'\b(who|which|that)\b', text.lower())),
            'has_conditionals': bool(re.search(r'\b(if|then|when|unless)\b', text.lower())),
            'has_coreference': bool(re.search(r'\b(the|this|that|it|they)\b', text.lower())),
            'has_modals': bool(re.search(r'\b(must|should|will|can|may)\b', text.lower())),
            'sentence_length': len(text.split()),
            'complexity_score': 0
        }
        
        # Calculate complexity score
        features['complexity_score'] = sum([
            features['has_quantifiers'] * 1,
            features['has_relative_clauses'] * 3,
            features['has_conditionals'] * 2,
            features['has_coreference'] * 2,
            features['has_modals'] * 1,
            (features['sentence_length'] > 15) * 2
        ])
        
        # Determine complexity level
        score = features['complexity_score']
        if score >= 7:
            features['complexity_level'] = 'very_complex'
        elif score >= 5:
            features['complexity_level'] = 'complex'
        elif score >= 3:
            features['complexity_level'] = 'intermediate'
        elif score >= 1:
            features['complexity_level'] = 'basic'
        else:
            features['complexity_level'] = 'simple'
        
        return features

# Factory function
def create_enhanced_nlp_service() -> EnhancedNLPTranslationService:
    """Create an instance of the enhanced NLP service."""
    return EnhancedNLPTranslationService()