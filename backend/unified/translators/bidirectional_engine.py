"""
Bidirectional Translation Engine
Canonical implementation using existing CNL/TCE parser infrastructure

Copyright: DarkLightX/Dana Edwards
"""

from typing import Optional, Dict, Any, List
import logging
import sys
from pathlib import Path

# Add src to path to access existing parsers
src_path = Path(__file__).parent.parent.parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from .base import (
    TranslationEngine, TranslationDirection, TranslationResult,
    ConfigurableEngine
)
from backend.unified.domain.nlp_translation_service import NLPTranslationService
from backend.unified.domain.ilr_generation_service import ILRGenerationService
from backend.unified.domain.ilr_tau_translation_service import TauTranslationService
from backend.unified.domain.tau_to_english_translator import TauToEnglishService
from backend.unified.domain.tce_types import TCEExpression
from backend.unified.core.domain_types import SourceText

# Import existing CNL/TCE parser
try:
    from tau_translator_omega.core_engine.cnl_parser.parser import TceTransformer, Lark
    from tau_translator_omega.core_engine.cnl_parser.parser import GRAMMAR_FILE_PATH
    CNL_PARSER_AVAILABLE = True
except ImportError:
    CNL_PARSER_AVAILABLE = False
    print("Warning: CNL parser not available")


class BidirectionalTranslationEngine(ConfigurableEngine):
    """
    Engine that supports bidirectional translation between:
    - English ↔ TCE ↔ TAU
    Uses existing CNL/TCE parser infrastructure
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="BidirectionalEngine",
            description="Bidirectional translation using existing parsers",
            config=config or {}
        )
        
        # Initialize services
        self.nlp_service = NLPTranslationService()
        self.ilr_service = ILRGenerationService()
        self.tau_service = TauTranslationService()
        self.tau_to_english_service = TauToEnglishService()
        
        # Initialize TCE parser if available
        self.tce_parser = None
        if CNL_PARSER_AVAILABLE:
            try:
                with open(GRAMMAR_FILE_PATH, 'r') as f:
                    grammar = f.read()
                self.tce_parser = Lark(grammar, start='start', parser='lalr')
                self.tce_transformer = TceTransformer()
            except Exception as e:
                print(f"Failed to initialize TCE parser: {e}")
        
        self.logger = logging.getLogger(__name__)
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get all supported translation directions."""
        return [
            TranslationDirection.TO_TAU,        # English → TAU
            TranslationDirection.TO_TCE,        # English → TCE
            TranslationDirection.TO_ENGLISH,    # TAU/TCE → English
            TranslationDirection.NL_TO_TAU,     # Natural Language → TAU
            TranslationDirection.NL_TO_TCE,     # Natural Language → TCE
            TranslationDirection.TCE_TO_TAU,    # TCE → TAU
            TranslationDirection.TCE_TO_NL,     # TCE → Natural Language
            TranslationDirection.BIDIRECTIONAL  # Automatic detection
        ]
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the translation."""
        if direction == TranslationDirection.BIDIRECTIONAL:
            return True  # We handle automatic detection
        
        return direction in self.get_supported_directions()
    
    async def translate_async(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform the translation asynchronously."""
        # This is a simple async wrapper. For a truly non-blocking implementation,
        # the underlying services would need to be async as well.
        return self.translate(text, direction, **kwargs)

    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform the translation."""
        start_time = kwargs.get('start_time')
        
        try:
            # Handle bidirectional mode
            if direction == TranslationDirection.BIDIRECTIONAL:
                detected_direction = self._detect_direction(text)
                if detected_direction:
                    direction = detected_direction
                else:
                    return self._create_result(
                        success=False,
                        translated_text="",
                        original_text=text,
                        direction=direction,
                        error_message="Could not detect language direction",
                        start_time=start_time
                    )
            
            # Route to appropriate translation method
            if direction == TranslationDirection.TO_TAU:
                return self._translate_to_tau(text, start_time)
            elif direction == TranslationDirection.TO_TCE:
                return self._translate_to_tce(text, start_time)
            elif direction == TranslationDirection.TO_ENGLISH:
                return self._translate_to_english(text, start_time)
            elif direction == TranslationDirection.NL_TO_TAU:
                return self._translate_nl_to_tau(text, start_time)
            elif direction == TranslationDirection.NL_TO_TCE:
                return self._translate_nl_to_tce(text, start_time)
            elif direction == TranslationDirection.TCE_TO_TAU:
                return self._translate_tce_to_tau(text, start_time)
            elif direction == TranslationDirection.TCE_TO_NL:
                return self._translate_tce_to_nl(text, start_time)
            else:
                return self._create_result(
                    success=False,
                    translated_text="",
                    original_text=text,
                    direction=direction,
                    error_message=f"Unsupported direction: {direction.value}",
                    start_time=start_time
                )
        
        except Exception as e:
            self.logger.error(f"Translation error: {str(e)}")
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message=str(e),
                start_time=start_time
            )
    
    def _detect_direction(self, text: str) -> Optional[TranslationDirection]:
        """Enhanced language detection with better pattern recognition."""
        return self._classify_language_advanced(text)
    
    def _classify_language_advanced(self, text: str) -> Optional[TranslationDirection]:
        """Advanced language classification (≤10 lines)."""
        scores = self._calculate_language_scores(text)
        
        if self._try_parse_as_tce(text):
            return TranslationDirection.TCE_TO_TAU
        
        if scores['tau'] > scores['tce'] and scores['tau'] > scores['english']:
            return TranslationDirection.TO_ENGLISH
        elif scores['tce'] > scores['english']:
            return TranslationDirection.TCE_TO_TAU
        else:
            return TranslationDirection.TO_TAU
    
    def _calculate_language_scores(self, text: str) -> Dict[str, int]:
        """Calculate language confidence scores (≤10 lines)."""
        text_lower = text.lower()
        
        tau_indicators = ['∀', '∃', '→', '&', '|', '^', ':=', 'always', 'sometimes', 'eventually']
        tce_indicators = ['for all', 'there exists', 'such that', 'if.*then', 'define.*as']
        english_indicators = ['the', 'is', 'are', 'will', 'should', 'must', 'can', 'a ', 'an ']
        
        tau_score = sum(2 if indicator in text_lower else 0 for indicator in tau_indicators)
        tce_score = sum(1 if indicator in text_lower else 0 for indicator in tce_indicators)
        english_score = sum(1 if indicator in text_lower else 0 for indicator in english_indicators)
        
        return {'tau': tau_score, 'tce': tce_score, 'english': english_score}
    
    def _try_parse_as_tce(self, text: str) -> bool:
        """Try parsing text as TCE (≤10 lines)."""
        if not self.tce_parser:
            return False
        
        try:
            # Add sentence terminator if missing
            test_text = text if text.endswith('.') else text + '.'
            self.tce_parser.parse(test_text)
            return True
        except:
            return False
    
    def _translate_to_tau(self, text: str, start_time: float) -> TranslationResult:
        """Translate English to TAU."""
        # English → TCE → ILR → TAU
        tce_result = self.nlp_service.translate_to_tce(SourceText(text))
        
        if tce_result.is_error():
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=TranslationDirection.TO_TAU,
                error_message=f"TCE translation failed: {tce_result.error}",
                start_time=start_time
            )
        
        # TCE → ILR
        ilr_result = self.ilr_service.generate_ilr(tce_result.value)
        
        if ilr_result.is_error():
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=TranslationDirection.TO_TAU,
                error_message=f"ILR generation failed: {ilr_result.error}",
                start_time=start_time
            )
        
        # ILR → TAU
        tau_result = self.tau_service.translate_to_tau(ilr_result.value)
        
        if tau_result.is_error():
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=TranslationDirection.TO_TAU,
                error_message=f"TAU translation failed: {tau_result.error}",
                start_time=start_time
            )
        
        return self._create_result(
            success=True,
            translated_text=str(tau_result.value),
            original_text=text,
            direction=TranslationDirection.TO_TAU,
            confidence=0.9,
            metadata={
                "pipeline": "English → TCE → ILR → TAU",
                "intermediate_tce": str(tce_result.value),
                "intermediate_ilr": str(ilr_result.value)
            },
            start_time=start_time
        )
    
    def _translate_to_tce(self, text: str, start_time: float) -> TranslationResult:
        """Translate English to TCE."""
        result = self.nlp_service.translate_to_tce(SourceText(text))
        
        if result.is_error():
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=TranslationDirection.TO_TCE,
                error_message=f"TCE translation failed: {result.error}",
                start_time=start_time
            )
        
        return self._create_result(
            success=True,
            translated_text=str(result.value),
            original_text=text,
            direction=TranslationDirection.TO_TCE,
            confidence=0.95,
            metadata={"pipeline": "English → TCE"},
            start_time=start_time
        )
    
    def _translate_to_english(self, text: str, start_time: float) -> TranslationResult:
        """Translate TAU/TCE to English."""
        # First try TAU → English using our new async service
        import asyncio
        try:
            tau_result = asyncio.run(self.tau_to_english_service.translate_expression_async(text))
            
            if isinstance(tau_result, type(tau_result)) and hasattr(tau_result, 'is_success') and tau_result.is_success():
                return self._create_result(
                    success=True,
                    translated_text=tau_result.value,
                    original_text=text,
                    direction=TranslationDirection.TO_ENGLISH,
                    confidence=0.9,
                    metadata={"pipeline": "TAU → English (enhanced)"},
                    start_time=start_time
                )
        except Exception as e:
            self.logger.debug(f"TAU to English translation failed: {e}")
        
        # If TAU parsing fails, try parsing as TCE
        if self.tce_parser:
            try:
                tree = self.tce_parser.parse(text)
                ast = self.tce_transformer.transform(tree)
                
                # Convert TCE AST to English
                # For now, use a simple conversion
                english = self._tce_ast_to_english(ast)
                
                return self._create_result(
                    success=True,
                    translated_text=english,
                    original_text=text,
                    direction=TranslationDirection.TO_ENGLISH,
                    confidence=0.85,
                    metadata={"pipeline": "TCE → English (via AST)"},
                    start_time=start_time
                )
            except Exception as e:
                self.logger.debug(f"TCE parsing failed: {e}")
        
        # Both parsers failed
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TO_ENGLISH,
            error_message=f"Could not parse as TAU or TCE. TAU error: {tau_result.error}",
            start_time=start_time
        )
    
    def _translate_nl_to_tau(self, text: str, start_time: float) -> TranslationResult:
        """Natural Language to TAU (same as English to TAU)."""
        return self._translate_to_tau(text, start_time)
    
    def _translate_nl_to_tce(self, text: str, start_time: float) -> TranslationResult:
        """Natural Language to TCE (same as English to TCE)."""
        return self._translate_to_tce(text, start_time)
    
    def _translate_tce_to_tau(self, text: str, start_time: float) -> TranslationResult:
        """Translate TCE to TAU."""
        # Parse TCE first if parser available
        if self.tce_parser:
            try:
                tree = self.tce_parser.parse(text)
                # Successfully parsed, now use standard pipeline
            except Exception as e:
                return self._create_result(
                    success=False,
                    translated_text="",
                    original_text=text,
                    direction=TranslationDirection.TCE_TO_TAU,
                    error_message=f"TCE parsing failed: {str(e)}",
                    start_time=start_time
                )
        
        # Use standard pipeline: TCE → ILR → TAU
        tce_expr = TCEExpression(expression=text)
        
        # TCE → ILR
        ilr_result = self.ilr_service.generate_ilr(tce_expr)
        
        if ilr_result.is_error():
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=TranslationDirection.TCE_TO_TAU,
                error_message=f"ILR generation failed: {ilr_result.error}",
                start_time=start_time
            )
        
        # ILR → TAU
        tau_result = self.tau_service.translate_to_tau(ilr_result.value)
        
        if tau_result.is_error():
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=TranslationDirection.TCE_TO_TAU,
                error_message=f"TAU translation failed: {tau_result.error}",
                start_time=start_time
            )
        
        return self._create_result(
            success=True,
            translated_text=str(tau_result.value),
            original_text=text,
            direction=TranslationDirection.TCE_TO_TAU,
            confidence=0.95,
            metadata={
                "pipeline": "TCE → ILR → TAU",
                "intermediate_ilr": str(ilr_result.value)
            },
            start_time=start_time
        )
    
    def _translate_tce_to_nl(self, text: str, start_time: float) -> TranslationResult:
        """Translate TCE to Natural Language."""
        if self.tce_parser:
            try:
                tree = self.tce_parser.parse(text)
                ast = self.tce_transformer.transform(tree)
                
                # Convert TCE AST to English
                english = self._tce_ast_to_english(ast)
                
                return self._create_result(
                    success=True,
                    translated_text=english,
                    original_text=text,
                    direction=TranslationDirection.TCE_TO_NL,
                    confidence=0.9,
                    metadata={"pipeline": "TCE → English (via existing parser)"},
                    start_time=start_time
                )
            except Exception as e:
                return self._create_result(
                    success=False,
                    translated_text="",
                    original_text=text,
                    direction=TranslationDirection.TCE_TO_NL,
                    error_message=f"TCE parsing failed: {str(e)}",
                    start_time=start_time
                )
        
        # Fallback to simple transformation
        result = text
        replacements = {
            'define predicate': 'We define a predicate',
            'define function': 'We define a function',
            'forall': 'for all',
            'exists': 'there exists',
            'such that': 'where'
        }
        
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return self._create_result(
            success=True,
            translated_text=result,
            original_text=text,
            direction=TranslationDirection.TCE_TO_NL,
            confidence=0.6,
            metadata={"pipeline": "TCE → English (rule-based fallback)"},
            start_time=start_time
        )
    
    def _tce_ast_to_english(self, ast) -> str:
        """Convert TCE AST to English text."""
        # This is a simplified conversion - would need more work for full implementation
        if hasattr(ast, '__iter__'):
            parts = []
            for node in ast:
                parts.append(self._node_to_english(node))
            return " ".join(parts)
        else:
            return self._node_to_english(ast)
    
    def _node_to_english(self, node) -> str:
        """Convert a single AST node to English."""
        # Import AST node types
        try:
            from tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
                FactNode, RuleNode, DefinitionNode, PredicateCallNode,
                QuantifierBlockNode, ComparisonNode, ArithmeticBinaryOpNode
            )
            
            if isinstance(node, FactNode):
                return f"{self._node_to_english(node.expr)}."
            elif isinstance(node, RuleNode):
                cond = self._node_to_english(node.condition) if node.condition else ""
                pred = self._node_to_english(node.predicate_call)
                return f"If {cond} then {pred}."
            elif isinstance(node, DefinitionNode):
                pred_def = self._node_to_english(node.predicate_def)
                expr = self._node_to_english(node.expr)
                return f"We define {pred_def} as {expr}."
            elif isinstance(node, PredicateCallNode):
                args = ", ".join(self._node_to_english(arg) for arg in node.args)
                return f"{node.name}({args})"
            elif isinstance(node, QuantifierBlockNode):
                vars = ", ".join(node.variables)
                expr = self._node_to_english(node.expr) if node.expr else ""
                if node.quantifier == "forall":
                    return f"for all {vars}, {expr}"
                else:
                    return f"there exists {vars} such that {expr}"
            elif isinstance(node, ComparisonNode):
                left = self._node_to_english(node.left)
                right = self._node_to_english(node.right)
                op_map = {
                    '=': 'equals',
                    '>': 'is greater than',
                    '<': 'is less than',
                    '>=': 'is at least',
                    '<=': 'is at most'
                }
                op = op_map.get(node.operator, node.operator)
                return f"{left} {op} {right}"
            else:
                # Default string representation
                return str(node)
        except:
            # Fallback if AST nodes not available
            return str(node)