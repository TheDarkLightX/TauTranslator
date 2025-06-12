"""
Parser Pipeline following Intentional Disclosure Principle
Copyright: DarkLightX/Dana Edwards

Orchestrates: Natural Language → ILR → TCE → Tau Code
Each method clearly discloses its purpose and side effects.
"""

from typing import List
from returns.result import Result, Success, Failure
import logging

from ..core.domain_types import (
    NaturalLanguageInput, TCEStatement, TauProgram,
    TranslationDirection, TranslationResult
)
from ..domain.nlp_translation_service import NLPTranslationService
from ..domain.text_to_ilr_service import TextToILRService  
from ..domain.ilr_to_tce_transformer import ILRToTCETransformer
from .base import TranslationEngine

# Import from infrastructure layer
from ..infrastructure.tau_code_generator import TauCodeGenerator
from ..infrastructure.tce_parser_adapter import TCEParserAdapter

logger = logging.getLogger(__name__)


class ParserPipelineOrchestrator(TranslationEngine):
    """Orchestrates multi-stage parsing pipeline following IDP."""
    
    def __init__(self):
        super().__init__("parser_pipeline", "Multi-stage Parser Pipeline")
        # Core services (pure logic)
        self._nlp_service = NLPTranslationService()
        self._text_to_ilr_converter = TextToILRService()
        self._ilr_to_tce_transformer = ILRToTCETransformer()
        
        # Infrastructure adapters (I/O operations)
        self._tce_parser_adapter = TCEParserAdapter()
        self._tau_code_generator = TauCodeGenerator()
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if pipeline supports translation direction."""
        return (self._is_valid_input(text) and 
                self._is_supported_direction(direction))
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Return list of supported translation directions."""
        return [
            TranslationDirection.NL_TO_TAU,
            TranslationDirection.NL_TO_TCE,
            TranslationDirection.TCE_TO_TAU,
            TranslationDirection.TCE_TO_NL
        ]
    
    def translate(self, text: str, direction: TranslationDirection) -> TranslationResult:
        """Orchestrate translation based on direction."""
        try:
            if direction == TranslationDirection.NL_TO_TAU:
                return self._translate_natural_language_to_tau_code(text)
            elif direction == TranslationDirection.NL_TO_TCE:
                return self._translate_natural_language_to_tce(text)
            elif direction == TranslationDirection.TCE_TO_TAU:
                return self._translate_tce_to_tau_code(text)
            elif direction == TranslationDirection.TCE_TO_NL:
                return self._translate_tce_to_natural_language(text)
            else:
                return self._create_unsupported_direction_error(direction, text)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return self._create_translation_error(str(e), text, direction)
    
    # High-level orchestrator methods (Rule 2: max 10 lines, no implementation details)
    
    def _translate_natural_language_to_tau_code(self, text: str) -> TranslationResult:
        """Orchestrate: Natural Language → ILR → TCE → Tau."""
        tce_result = self._translate_natural_language_to_tce(text)
        if not tce_result.success:
            return tce_result
        
        return self._translate_tce_to_tau_code(tce_result.translated_text)
    
    def _translate_natural_language_to_tce(self, text: str) -> TranslationResult:
        """Orchestrate: Natural Language → ILR → TCE."""
        normalized_text = self._normalize_input_text(text)
        ilr_result = self._convert_text_to_ilr_representation(normalized_text)
        
        if isinstance(ilr_result, Failure):
            return self._create_ilr_conversion_error(ilr_result, text)
        
        tce_result = self._transform_ilr_to_tce_statements(ilr_result.value)
        if isinstance(tce_result, Failure):
            return self._create_tce_transformation_error(tce_result, text)
        
        tce_text = self._format_tce_statements_as_text(tce_result.value)
        return self._create_successful_tce_result(tce_text, text)
    
    def _translate_tce_to_tau_code(self, tce_text: str) -> TranslationResult:
        """Orchestrate: TCE → AST → Tau Code."""
        ast_result = self._parse_tce_to_ast_via_infrastructure(tce_text)
        if isinstance(ast_result, Failure):
            return self._create_parsing_error(ast_result, tce_text)
        
        tau_result = self._generate_tau_code_from_ast_via_infrastructure(ast_result.value)
        if isinstance(tau_result, Failure):
            return self._create_generation_error(tau_result, tce_text)
        
        return self._create_successful_tau_result(tau_result.value, tce_text)
    
    def _translate_tce_to_natural_language(self, tce_text: str) -> TranslationResult:
        """Orchestrate: TCE → Natural Language."""
        normalized_tce = self._normalize_tce_text(tce_text)
        nl_result = self._convert_tce_to_natural_language_via_service(normalized_tce)
        
        if nl_result.success:
            return self._create_successful_nl_result(nl_result.output_text, tce_text)
        else:
            return self._create_nl_conversion_error(nl_result, tce_text)
    
    # Implementation methods (Rule 2: each does one thing)
    
    def _is_valid_input(self, text: str) -> bool:
        """Validate input text is non-empty."""
        return bool(text and text.strip())
    
    def _is_supported_direction(self, direction: TranslationDirection) -> bool:
        """Check if direction is in supported list."""
        return direction in self.get_supported_directions()
    
    def _normalize_input_text(self, text: str) -> str:
        """Clean and normalize natural language input."""
        normalized = text.strip()
        if not normalized.endswith('.'):
            normalized += '.'
        return normalized
    
    def _normalize_tce_text(self, text: str) -> str:
        """Clean and normalize TCE input."""
        return text.strip()
    
    def _convert_text_to_ilr_representation(self, text: str) -> Result:
        """Convert normalized text to ILR using core service."""
        return self._text_to_ilr_converter.convert_text_to_ilr(text)
    
    def _transform_ilr_to_tce_statements(self, ilr_node) -> Result:
        """Transform ILR to TCE statements using core service."""
        return self._ilr_to_tce_transformer.transform_ilr_to_tce_async(ilr_node)
    
    def _format_tce_statements_as_text(self, statements: List[TCEStatement]) -> str:
        """Format TCE statements into text representation."""
        lines = []
        for stmt in statements:
            line = self._format_single_tce_statement(stmt)
            lines.append(line)
        return " ".join(lines)
    
    def _format_single_tce_statement(self, stmt: TCEStatement) -> str:
        """Format a single TCE statement."""
        line = stmt.pattern
        for key, value in stmt.bindings.items():
            placeholder = f"{{{key}}}"
            if placeholder in line:
                line = line.replace(placeholder, value)
        return line + "."
    
    def _parse_tce_to_ast_via_infrastructure(self, tce_text: str) -> Result:
        """Parse TCE to AST using infrastructure adapter."""
        return self._tce_parser_adapter.parse_tce_text_to_ast(tce_text)
    
    def _generate_tau_code_from_ast_via_infrastructure(self, ast) -> Result:
        """Generate Tau code from AST using infrastructure adapter."""
        return self._tau_code_generator.generate_tau_code_from_ast(ast)
    
    def _convert_tce_to_natural_language_via_service(self, tce_text: str):
        """Convert TCE to natural language using core service."""
        from ..domain.nlp_types import TCEText
        return self._nlp_service.translate_tce_to_nl(TCEText(tce_text))
    
    # Result creation methods (Rule 1: names reveal purpose)
    
    def _create_successful_tce_result(self, tce_text: str, original: str) -> TranslationResult:
        """Create successful TCE translation result."""
        return TranslationResult(
            success=True,
            translated_text=tce_text,
            original_text=original,
            translation_method=self.name,
            direction=TranslationDirection.NL_TO_TCE,
            confidence=0.85,
            metadata={"pipeline": "nl->ilr->tce"}
        )
    
    def _create_successful_tau_result(self, tau_code: str, original: str) -> TranslationResult:
        """Create successful Tau translation result."""
        return TranslationResult(
            success=True,
            translated_text=tau_code,
            original_text=original,
            translation_method=self.name,
            direction=TranslationDirection.TCE_TO_TAU,
            confidence=0.95,
            metadata={"pipeline": "tce->ast->tau"}
        )
    
    def _create_successful_nl_result(self, nl_text: str, original: str) -> TranslationResult:
        """Create successful natural language result."""
        return TranslationResult(
            success=True,
            translated_text=nl_text,
            original_text=original,
            translation_method=self.name,
            direction=TranslationDirection.TCE_TO_NL,
            confidence=0.80,
            metadata={"pipeline": "tce->nl"}
        )
    
    def _create_translation_error(self, error: str, text: str, direction: TranslationDirection) -> TranslationResult:
        """Create error result with details."""
        return TranslationResult(
            success=False,
            translated_text="",
            original_text=text,
            translation_method=self.name,
            direction=direction,
            confidence=0.0,
            error_message=error
        )
    
    def _create_ilr_conversion_error(self, result: Failure, text: str) -> TranslationResult:
        """Create ILR conversion error result."""
        return self._create_translation_error(
            f"ILR conversion failed: {result.failure()}",
            text,
            TranslationDirection.NL_TO_TCE
        )
    
    def _create_tce_transformation_error(self, result: Failure, text: str) -> TranslationResult:
        """Create TCE transformation error result."""
        return self._create_translation_error(
            f"TCE transformation failed: {result.failure()}",
            text,
            TranslationDirection.NL_TO_TCE
        )
    
    def _create_parsing_error(self, result: Failure, text: str) -> TranslationResult:
        """Create parsing error result."""
        return self._create_translation_error(
            f"TCE parsing failed: {result.failure()}",
            text,
            TranslationDirection.TCE_TO_TAU
        )
    
    def _create_generation_error(self, result: Failure, text: str) -> TranslationResult:
        """Create code generation error result."""
        return self._create_translation_error(
            f"Tau generation failed: {result.failure()}",
            text,
            TranslationDirection.TCE_TO_TAU
        )
    
    def _create_nl_conversion_error(self, result, text: str) -> TranslationResult:
        """Create natural language conversion error result."""
        return self._create_translation_error(
            result.error_message or "TCE to NL conversion failed",
            text,
            TranslationDirection.TCE_TO_NL
        )
    
    def _create_unsupported_direction_error(self, direction: TranslationDirection, text: str) -> TranslationResult:
        """Create unsupported direction error result."""
        return self._create_translation_error(
            f"Unsupported translation direction: {direction}",
            text,
            direction
        )