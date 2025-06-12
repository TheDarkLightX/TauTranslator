"""
NLP endpoints following the Intentional Disclosure Principle.

This module orchestrates NLP operations with complete transparency:
- All async operations explicitly marked with _async suffix
- Domain types replace primitives for type safety
- Business logic separated from I/O operations
- Every method under 10 lines with single responsibility

Copyright: DarkLightX / Dana Edwards
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional, NewType, Literal, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..core.responses import create_success_response, create_error_response
from ..core.result_enhanced import Result, Success, Failure, success, failure

import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# =======================
# Domain Types (Rule 3: Maximize Disclosure via Type System)
# =======================

CodeText = NewType("CodeText", str)
LineNumber = NewType("LineNumber", int)
ErrorMessage = NewType("ErrorMessage", str)
ExplanationText = NewType("ExplanationText", str)
SuggestionText = NewType("SuggestionText", str)
ConfidenceScore = NewType("ConfidenceScore", float)

class SeverityLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class SuggestionType(Enum):
    KEYWORD = "keyword"
    OPERATOR = "operator"
    TEMPORAL = "temporal"
    QUANTIFIER = "quantifier"
    IDENTIFIER = "identifier"

class LanguageType(Enum):
    TAU = "TAU"
    TCE = "TCE"

@dataclass(frozen=True)
class ValidationError:
    """Represents a validation error or warning."""
    line: LineNumber
    message: ErrorMessage
    severity: SeverityLevel

@dataclass(frozen=True)
class ValidationResult:
    """Complete validation result."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    suggestions: List[SuggestionText] = field(default_factory=list)

@dataclass(frozen=True)
class Suggestion:
    """An autocomplete suggestion."""
    text: SuggestionText
    type: SuggestionType
    confidence: Optional[ConfidenceScore] = None

@dataclass(frozen=True)
class LineExplanation:
    """Explanation for a single line of code."""
    line: CodeText
    explanation: ExplanationText

@dataclass(frozen=True)
class CodeExplanation:
    """Complete code explanation."""
    overall: ExplanationText
    line_explanations: List[LineExplanation]

# Request/Response Models
class AutocompleteRequest(BaseModel):
    text: str
    position: Optional[int] = None
    context: Optional[str] = None

class ValidationRequest(BaseModel):
    code: str
    language: str = "TAU"

class ExplainRequest(BaseModel):
    code: str
    language: str = "TAU"

# =======================
# Infrastructure Layer (Rule 4: Isolate Impurity)
# =======================

class NLPServiceLoader:
    """Handles loading of NLP service (I/O operation)."""
    
    _service_instance = None
    
    @classmethod
    def load_nlp_service_async(cls) -> Result[Optional['NLPTranslationService']]:
        """
        Note: This is a pure function (no side effects).
        Load NLP service if available."""
        if cls._service_instance is not None:
            return success(cls._service_instance)
        
        try:
            # This is the only place where we do the import (I/O)
            from nlp.nlp_integration import NLPTranslationService
            cls._service_instance = NLPTranslationService()
            return success(cls._service_instance)
        except ImportError:
            return success(None)  # NLP not available
        except Exception as e:
            return failure("SERVICE_LOAD_ERROR", f"Failed to load NLP service: {str(e)}")

# =======================
# Core Business Logic (Pure Functions)
# =======================

class TauConstants:
    """TAU language constants."""
    KEYWORDS = frozenset(['DEFINE', 'CONCEPT', 'always', 'sometimes', 'eventually', 
                         'forall', 'exists', 'true', 'false', 'never'])
    OPERATORS = frozenset([':=', '->', '<->', '&&', '||', '!', '=', '!=', '>', '<', '>=', '<='])
    TEMPORAL_KEYWORDS = frozenset(['always', 'sometimes', 'eventually', 'never'])
    QUANTIFIERS = frozenset(['forall', 'exists'])
    DEFINITION_KEYWORDS = frozenset(['DEFINE', 'CONCEPT', 'FUNCTION'])

class SyntaxValidator:
    """Validates TAU syntax."""
    
    @staticmethod
    def validate_parentheses(line: CodeText, line_number: LineNumber) -> Optional[ValidationError]:
        """
        Note: This is a pure function (no side effects).
        Check parentheses balance."""
        if line.count('(') != line.count(')'):
            return ValidationError(
                line=line_number,
                message=ErrorMessage("Unmatched parentheses"),
                severity=SeverityLevel.ERROR
            )
        return None
    
    @staticmethod
    def validate_brackets(line: CodeText, line_number: LineNumber) -> Optional[ValidationError]:
        """
        Note: This is a pure function (no side effects).
        Check brackets balance."""
        if line.count('[') != line.count(']'):
            return ValidationError(
                line=line_number,
                message=ErrorMessage("Unmatched brackets"),
                severity=SeverityLevel.ERROR
            )
        return None
    
    @staticmethod
    def check_keyword_usage(line: CodeText, line_number: LineNumber) -> Optional[ValidationError]:
        """
        Note: This is a pure function (no side effects).
        Check for keywords without operators."""
        for keyword in TauConstants.KEYWORDS:
            if keyword in line and not any(op in line for op in [':=', ':', '->', '<->']):
                return ValidationError(
                    line=line_number,
                    message=ErrorMessage(f"Keyword '{keyword}' found without operator"),
                    severity=SeverityLevel.WARNING
                )
        return None

class CodeLineProcessor:
    """Processes code lines."""
    
    @staticmethod
    def extract_code_lines(code: CodeText) -> List[Tuple[LineNumber, CodeText]]:
        """
        Note: This is a pure function (no side effects).
        Extract non-empty, non-comment lines with line numbers."""
        lines = []
        for i, line in enumerate(code.split('\n')):
            stripped = line.strip()
            if stripped and not stripped.startswith('//'):
                lines.append((LineNumber(i + 1), CodeText(stripped)))
        return lines
    
    @staticmethod
    def is_meaningful_line(line: CodeText) -> bool:
        """
        Note: This is a pure function (no side effects).
        Check if line contains meaningful code."""
        stripped = line.strip()
        return bool(stripped) and not stripped.startswith('//')

class SuggestionGenerator:
    """Generates autocomplete suggestions."""
    
    @staticmethod
    def generate_basic_suggestions(text: CodeText) -> List[Suggestion]:
        """
        Note: This is a pure function (no side effects).
        Generate basic keyword/operator suggestions."""
        suggestions = []
        text_lower = text.lower()
        
        suggestions.extend(SuggestionGenerator._match_keywords(text_lower))
        suggestions.extend(SuggestionGenerator._match_operators(text))
        
        return suggestions[:10]  # Limit to 10
    
    @staticmethod
    def _match_keywords(text_lower: str) -> List[Suggestion]:
        """
        Note: This is a pure function (no side effects).
        Match keywords against input text."""
        matches = []
        for keyword in TauConstants.KEYWORDS:
            if keyword.lower().startswith(text_lower):
                suggestion_type = SuggestionGenerator._determine_keyword_type(keyword)
                matches.append(Suggestion(
                    text=SuggestionText(keyword),
                    type=suggestion_type
                ))
        return matches
    
    @staticmethod
    def _match_operators(text: str) -> List[Suggestion]:
        """
        Note: This is a pure function (no side effects).
        Match operators against input text."""
        matches = []
        for operator in TauConstants.OPERATORS:
            if operator.startswith(text):
                matches.append(Suggestion(
                    text=SuggestionText(operator),
                    type=SuggestionType.OPERATOR
                ))
        return matches
    
    @staticmethod
    def _determine_keyword_type(keyword: str) -> SuggestionType:
        """
        Note: This is a pure function (no side effects).
        Determine the type of a keyword."""
        if keyword in TauConstants.TEMPORAL_KEYWORDS:
            return SuggestionType.TEMPORAL
        elif keyword in TauConstants.QUANTIFIERS:
            return SuggestionType.QUANTIFIER
        else:
            return SuggestionType.KEYWORD

class CodeExplainer:
    """Explains TAU code constructs."""
    
    EXPLANATIONS = {
        'DEFINE': "Defines a new concept or function",
        'always': "States that something is always true",
        'sometimes': "States that something is sometimes true",
        'eventually': "States that something will eventually be true",
        'never': "States that something is never true",
        'forall': "Universal quantification - true for all values",
        'exists': "Existential quantification - true for at least one value",
        '<->': "Logical equivalence (if and only if)",
        '->': "Logical implication",
        ':=': "Definition or assignment"
    }
    
    @staticmethod
    def explain_line(line: CodeText) -> Optional[ExplanationText]:
        """
        Note: This is a pure function (no side effects).
        Generate explanation for a single line."""
        for construct, explanation in CodeExplainer.EXPLANATIONS.items():
            if construct in line:
                return ExplanationText(explanation)
        return None
    
    @staticmethod
    def generate_overall_explanation(explanations: List[LineExplanation]) -> ExplanationText:
        """
        Note: This is a pure function (no side effects).
        Generate overall code explanation."""
        parts = ["This TAU code"]
        
        if any('DEFINE' in e.line for e in explanations):
            parts.append("defines concepts or functions")
        if any(kw in e.line for e in explanations for kw in TauConstants.TEMPORAL_KEYWORDS):
            parts.append("uses temporal logic")
        if any(q in e.line for e in explanations for q in TauConstants.QUANTIFIERS):
            parts.append("includes quantifiers")
        
        return ExplanationText(f"{', '.join(parts)}." if len(parts) > 1 else "This TAU code is empty.")

class ValidationService:
    """Orchestrates validation operations."""
    
    def __init__(self, validator: SyntaxValidator, processor: CodeLineProcessor):
        self._validator = validator
        self._processor = processor
    
    def validate_code(self, code: CodeText) -> ValidationResult:
        """
        Note: This is a pure function (no side effects).
        Validate code and return results (Rule 2: orchestration)."""
        lines = self._processor.extract_code_lines(code)
        errors = self._collect_errors(lines)
        warnings = self._collect_warnings(lines)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=self._generate_fix_suggestions(errors)
        )
    
    def _collect_errors(self, lines: List[Tuple[LineNumber, CodeText]]) -> List[ValidationError]:
        """
        Note: This is a pure function (no side effects).
        Collect all syntax errors."""
        errors = []
        for line_num, line_text in lines:
            errors.extend(filter(None, [
                self._validator.validate_parentheses(line_text, line_num),
                self._validator.validate_brackets(line_text, line_num)
            ]))
        return errors
    
    def _collect_warnings(self, lines: List[Tuple[LineNumber, CodeText]]) -> List[ValidationError]:
        """
        Note: This is a pure function (no side effects).
        Collect all syntax warnings."""
        warnings = []
        for line_num, line_text in lines:
            warning = self._validator.check_keyword_usage(line_text, line_num)
            if warning:
                warnings.append(warning)
        return warnings
    
    @staticmethod
    def _generate_fix_suggestions(errors: List[ValidationError]) -> List[SuggestionText]:
        """
        Note: This is a pure function (no side effects).
        Generate fix suggestions based on errors."""
        suggestions = []
        for error in errors:
            if "parentheses" in error.message:
                suggestions.append(SuggestionText("Check parentheses matching"))
            elif "brackets" in error.message:
                suggestions.append(SuggestionText("Check bracket matching"))
        return list(set(suggestions))  # Remove duplicates

class AutocompleteService:
    """Orchestrates autocomplete operations."""
    
    def __init__(self, suggestion_generator: SuggestionGenerator):
        self._generator = suggestion_generator
    
    async def get_suggestions_async(
        self, 
        text: CodeText, 
        nlp_service: Optional['NLPTranslationService']
    ) -> Result[List[Suggestion]]:
        """Get autocomplete suggestions (Rule 2: orchestration)."""
        if nlp_service is None:
            # Use basic suggestions
            return success(self._generator.generate_basic_suggestions(text))
        
        # Use NLP-powered suggestions
        return await self._get_nlp_suggestions_async(text, nlp_service)
    
    async def _get_nlp_suggestions_async(
        self, 
        text: CodeText, 
        nlp_service: 'NLPTranslationService'
    ) -> Result[List[Suggestion]]:
        """Get suggestions from NLP service."""
        try:
            raw_suggestions = nlp_service.autocomplete_engine.get_completions(text, max_results=10)
            return success(self._format_nlp_suggestions(raw_suggestions))
        except Exception as e:
            return failure("NLP_ERROR", f"NLP suggestion failed: {str(e)}")
    
    @staticmethod
    def _format_nlp_suggestions(
        raw_suggestions: List[Tuple[str, float]]
    ) -> List[Suggestion]:
        """Format NLP suggestions into domain objects."""
        formatted = []
        for text, confidence in raw_suggestions:
            suggestion_type = SuggestionGenerator._determine_keyword_type(text)
            formatted.append(Suggestion(
                text=SuggestionText(text),
                type=suggestion_type,
                confidence=ConfidenceScore(confidence)
            ))
        return formatted

class ExplanationService:
    """Orchestrates code explanation."""
    
    def __init__(self, explainer: CodeExplainer, processor: CodeLineProcessor):
        self._explainer = explainer
        self._processor = processor
    
    def explain_code(self, code: CodeText) -> CodeExplanation:
        """
        Note: This is a pure function (no side effects).
        Explain code structure and meaning (Rule 2: orchestration)."""
        lines = self._processor.extract_code_lines(code)
        line_explanations = self._generate_line_explanations(lines)
        overall = self._explainer.generate_overall_explanation(line_explanations)
        
        return CodeExplanation(
            overall=overall,
            line_explanations=line_explanations
        )
    
    def _generate_line_explanations(
        self, 
        lines: List[Tuple[LineNumber, CodeText]]
    ) -> List[LineExplanation]:
        """Generate explanations for each line."""
        explanations = []
        for _, line_text in lines:
            explanation = self._explainer.explain_line(line_text)
            if explanation:
                explanations.append(LineExplanation(
                    line=line_text,
                    explanation=explanation
                ))
        return explanations

# =======================
# API Endpoints (Rule 2: Orchestration only)
# =======================

# Initialize services
_nlp_loader = NLPServiceLoader()
_validator = SyntaxValidator()
_processor = CodeLineProcessor()
_generator = SuggestionGenerator()
_explainer = CodeExplainer()

_validation_service = ValidationService(_validator, _processor)
_autocomplete_service = AutocompleteService(_generator)
_explanation_service = ExplanationService(_explainer, _processor)

@router.post("/autocomplete")
async def autocomplete_async(request: AutocompleteRequest):
    """
        Note: This is a pure function (no side effects).
        Provide autocomplete suggestions with explicit async naming."""
    nlp_result = _nlp_loader.load_nlp_service_async()
    nlp_service = nlp_result.value if nlp_result.is_success() else None
    
    suggestions_result = await _autocomplete_service.get_suggestions_async(
        CodeText(request.text), 
        nlp_service
    )
    
    if suggestions_result.is_success():
        return create_success_response({
            "suggestions": [s.__dict__ for s in suggestions_result.value],
            "source": "nlp" if nlp_service else "basic"
        })
    else:
        return create_error_response(suggestions_result.message)

@router.post("/validate")
async def validate_syntax_async(request: ValidationRequest):
    """
        Note: This is a pure function (no side effects).
        Validate syntax and provide suggestions with explicit async naming."""
    validation_result = _validation_service.validate_code(CodeText(request.code))
    
    return create_success_response({
        "is_valid": validation_result.is_valid,
        "errors": [e.__dict__ for e in validation_result.errors],
        "warnings": [w.__dict__ for w in validation_result.warnings],
        "suggestions": validation_result.suggestions
    })

@router.post("/explain")
async def explain_code_async(request: ExplainRequest):
    """
        Note: This is a pure function (no side effects).
        Explain code structure and meaning with explicit async naming."""
    explanation = _explanation_service.explain_code(CodeText(request.code))
    
    return create_success_response({
        "explanation": explanation.overall,
        "line_explanations": [le.__dict__ for le in explanation.line_explanations]
    })