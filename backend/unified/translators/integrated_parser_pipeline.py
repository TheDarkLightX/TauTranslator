"""
Integrated Parser Pipeline
Copyright: DarkLightX/Dana Edwards

Connects: Natural Language → ILR → TCE → Tau Code
Following craftsmanship principles with methods ≤10 lines.
"""

from typing import Optional, List
from returns.result import Result, Success, Failure
import logging

from ..core.domain_types import SourceText, TargetText
from ..domain.nlp_types import NaturalLanguageText, TCEText
from ..domain.nlp_translation_service import NLPTranslationService
from ..domain.text_to_ilr_service import TextToILRService
from ..domain.ilr_to_tce_transformer import ILRToTCETransformer
from ..domain.tce_types import TCEStatement
from .base import TranslationEngine, TranslationResult, TranslationDirection

# Import TCE to Tau translator from core engine
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser


logger = logging.getLogger(__name__)


class IntegratedParserPipeline(TranslationEngine):
    """Full pipeline: Natural Language → ILR → TCE → Tau."""
    
    def __init__(self):
        super().__init__("integrated_parser", "Integrated Parser Pipeline")
        self._nlp_service = NLPTranslationService()
        self._ilr_generator = TextToILRService()
        self._ilr_to_tce = ILRToTCETransformer()
        self._tce_parser = CNLParser()
        self._tau_generator = TCETauTranslator()
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the translation."""
        return (self.validate_input(text) and 
                direction in self.get_supported_directions())
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get supported translation directions."""
        return [
            TranslationDirection.NL_TO_TAU,
            TranslationDirection.NL_TO_TCE,
            TranslationDirection.TCE_TO_TAU,
            TranslationDirection.TCE_TO_NL
        ]
    
    def translate(self, text: str, direction: TranslationDirection) -> TranslationResult:
        """Translate using the full pipeline."""
        try:
            if direction == TranslationDirection.NL_TO_TAU:
                return self._translate_nl_to_tau(text)
            elif direction == TranslationDirection.NL_TO_TCE:
                return self._translate_nl_to_tce(text)
            elif direction == TranslationDirection.TCE_TO_TAU:
                return self._translate_tce_to_tau(text)
            elif direction == TranslationDirection.TCE_TO_NL:
                return self._translate_tce_to_nl(text)
            else:
                return self._create_error_result(f"Unsupported direction: {direction}", text, direction)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return self._create_error_result(str(e), text, direction)
    
    def _translate_nl_to_tau(self, text: str) -> TranslationResult:
        """Natural Language → ILR → TCE → Tau."""
        # Step 1: NL to TCE
        tce_result = self._translate_nl_to_tce(text)
        if not tce_result.success:
            return tce_result
        
        # Step 2: TCE to Tau
        return self._translate_tce_to_tau(tce_result.translated_text)
    
    def _translate_nl_to_tce(self, text: str) -> TranslationResult:
        """Natural Language → ILR → TCE."""
        # Step 1: Use NLP service for initial translation
        nl_text = NaturalLanguageText(text)
        nlp_result = self._nlp_service.translate_nl_to_tce(nl_text)
        
        if not nlp_result.success:
            return self._create_translation_result(nlp_result)
        
        # Step 2: Generate ILR from the NLP result
        ilr_result = self._generate_ilr(nlp_result.output_text or "")
        if isinstance(ilr_result, Failure):
            return self._create_error_result(ilr_result.failure())
        
        # Step 3: Transform ILR to TCE
        tce_result = self._transform_ilr_to_tce(ilr_result.unwrap())
        if isinstance(tce_result, Failure):
            return self._create_error_result(tce_result.failure())
        
        # Convert TCE statements to text
        tce_text = self._format_tce_statements(tce_result.unwrap())
        return TranslationResult(
            success=True,
            translated_text=tce_text,
            original_text=text,
            translation_method=self.name,
            direction=TranslationDirection.NL_TO_TCE,
            confidence=0.85,
            metadata={"pipeline": "nl->ilr->tce"}
        )
    
    def _translate_tce_to_tau(self, tce_text: str) -> TranslationResult:
        """TCE → Tau using CNL parser and translator."""
        try:
            # Parse TCE to AST
            ast = self._tce_parser.parse(tce_text)
            if not ast:
                return self._create_error_result("Failed to parse TCE")
            
            # Translate AST to Tau
            tau_result = self._tau_generator.translate(ast)
            
            return TranslationResult(
                success=True,
                translated_text=tau_result.tau_code,
                original_text=tce_text,
                translation_method=self.name,
                direction=TranslationDirection.TCE_TO_TAU,
                confidence=0.95,
                metadata={
                    "warnings": tau_result.warnings,
                    "pipeline": "tce->tau"
                }
            )
        except Exception as e:
            return self._create_error_result(f"TCE to Tau failed: {str(e)}")
    
    def _translate_tce_to_nl(self, tce_text: str) -> TranslationResult:
        """TCE → Natural Language using NLP service."""
        try:
            # Use NLP service to translate TCE to natural language
            tce_input = TCEText(tce_text)
            result = self._nlp_service.translate_tce_to_nl(tce_input)
            
            if result.success:
                return TranslationResult(
                    success=True,
                    translated_text=result.output_text or "",
                    original_text=tce_text,
                    translation_method=self.name,
                    direction=TranslationDirection.TCE_TO_NL,
                    confidence=result.confidence,
                    metadata={"pipeline": "tce->nl"}
                )
            else:
                return self._create_error_result(result.error_message or "TCE to NL translation failed", tce_text, TranslationDirection.TCE_TO_NL)
        except Exception as e:
            return self._create_error_result(f"TCE to NL failed: {str(e)}", tce_text, TranslationDirection.TCE_TO_NL)
    
    def _generate_ilr(self, nlp_translation: str) -> Result:
        """Generate ILR from NLP translation."""
        return self._ilr_generator.convert_text_to_ilr(nlp_translation)
    
    def _transform_ilr_to_tce(self, ilr_node) -> Result:
        """Transform ILR to TCE statements."""
        return self._ilr_to_tce.transform_ilr_to_tce_async(ilr_node)
    
    def _format_tce_statements(self, statements: list[TCEStatement]) -> str:
        """Format TCE statements as text."""
        lines = []
        for stmt in statements:
            # Use the pattern with bindings filled in
            line = stmt.pattern
            for key, value in stmt.bindings.items():
                placeholder = f"{{{key}}}"
                if placeholder in line:
                    line = line.replace(placeholder, value)
            lines.append(line + ".")
        return " ".join(lines)
    
    def _create_translation_result(self, nlp_result) -> TranslationResult:
        """Create TranslationResult from NLP result."""
        return TranslationResult(
            success=nlp_result.success,
            translated_text=nlp_result.output_text or "",
            original_text="",  # Will be set by caller
            translation_method=self.name,
            direction=TranslationDirection.NL_TO_TCE,
            confidence=nlp_result.confidence,
            metadata={"pattern_used": str(nlp_result.pattern_used) if nlp_result.pattern_used else None}
        )
    
    def _create_error_result(self, error: str, text: str = "", direction: TranslationDirection = TranslationDirection.NL_TO_TAU) -> TranslationResult:
        """Create error result."""
        return TranslationResult(
            success=False,
            translated_text="",
            original_text=text,
            translation_method=self.name,
            direction=direction,
            confidence=0.0,
            error_message=error
        )