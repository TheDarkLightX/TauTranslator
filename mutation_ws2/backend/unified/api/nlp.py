from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, NewType

from returns.result import Result, Success, Failure

from backend.unified.core.domain_types import AppError
from backend.unified.core.semantic_validator import ValidationError
from backend.unified.core.error_handling import ErrorType

# --- Type Definitions ---
CodeText = NewType('CodeText', str)
LineNumber = NewType('LineNumber', int)
ErrorMessage = NewType('ErrorMessage', str)
ExplanationText = NewType('ExplanationText', str)
SuggestionText = NewType('SuggestionText', str)
ConfidenceScore = NewType('ConfidenceScore', float)


class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SuggestionType(Enum):
    REFACTOR = "refactor"
    PERFORMANCE = "performance"
    CLARITY = "clarity"
    TEMPORAL = "temporal"
    QUANTIFIER = "quantifier"
    KEYWORD = "keyword"
    OPERATOR = "operator"


@dataclass(frozen=True)
class Suggestion:
    suggestion_type: SuggestionType
    text: SuggestionText
    confidence: ConfidenceScore


@dataclass(frozen=True)
class LineExplanation:
    line: CodeText
    explanation: ExplanationText


class TauConstants:
    KEYWORDS = {"DEFINE", "always", "never", "sometimes", "exists", "forall"}
    OPERATORS = {":=", "->", "<->", "&", "|", "!"}


# --- Stateless Service Classes ---

class CodeLineProcessor:
    """Handles processing of raw code text into lines."""

    @staticmethod
    def extract_code_lines(code: CodeText) -> List[Tuple[LineNumber, CodeText]]:
        """Extracts meaningful, non-empty, non-comment lines."""
        lines = []
        for i, line_text in enumerate(code.splitlines(), 1):
            if CodeLineProcessor.is_meaningful_line(CodeText(line_text)):
                lines.append((LineNumber(i), CodeText(line_text)))
        return lines

    @staticmethod
    def is_meaningful_line(line: CodeText) -> bool:
        """A line is meaningful if it's not empty and not a comment."""
        stripped_line = line.strip()
        return bool(stripped_line) and not stripped_line.startswith("//")


class SyntaxValidator:
    """Performs basic syntax validation checks."""

    @staticmethod
    def validate_parentheses(line: CodeText, line_number: LineNumber) -> Optional[ValidationError]:
        if line.count('(') != line.count(')'):
            return ValidationError(message=ErrorMessage("Unmatched parentheses"), error_type=ErrorType.SYNTAX_ERROR, suggestion='Check parentheses balance.', confidence=0.9)
        return None

    @staticmethod
    def validate_brackets(line: CodeText, line_number: LineNumber) -> Optional[ValidationError]:
        if line.count('[') != line.count(']'):
            return ValidationError(message=ErrorMessage("Unmatched brackets"), error_type=ErrorType.SYNTAX_ERROR, suggestion='Check bracket balance.', confidence=0.9)
        return None

    @staticmethod
    def check_keyword_usage(line: CodeText, line_number: LineNumber) -> Optional[ValidationError]:
        for keyword in TauConstants.KEYWORDS:
            if keyword in line and not any(op in line for op in TauConstants.OPERATORS):
                return ValidationError(
                    message=ErrorMessage(f"Keyword '{keyword}' found without a corresponding operator."),
                    error_type=ErrorType.SYNTAX_WARNING,
                    suggestion=f'Consider adding an operator like `:=` or `->` to the line with {keyword}.',
                    confidence=0.7
                )
        return None


class ValidationService:
    """Orchestrates validation using various specialized validators."""

    def __init__(self, syntax_validator: SyntaxValidator, code_line_processor: CodeLineProcessor):
        self.syntax_validator = syntax_validator
        self.code_line_processor = code_line_processor

    def validate_code(self, code: CodeText) -> Result[None, List[ValidationError]]:
        errors = []
        lines = self.code_line_processor.extract_code_lines(code)
        for line_num, line_text in lines:
            results = [
                self.syntax_validator.validate_parentheses(line_text, line_num),
                self.syntax_validator.validate_brackets(line_text, line_num),
                self.syntax_validator.check_keyword_usage(line_text, line_num),
            ]
            errors.extend(res for res in results if res)

        if errors:
            return Failure(errors)
        return Success(None)


class SuggestionGenerator:
    """Generates suggestions for code improvements."""

    @staticmethod
    def generate_basic_suggestions(code: CodeText) -> List[Suggestion]:
        prefix = str(code).strip().lower()
        suggestions = []

        if not prefix:
            all_keywords = (Suggestion(
                suggestion_type=SuggestionGenerator._determine_keyword_type(kw) or SuggestionType.KEYWORD,
                text=SuggestionText(kw),
                confidence=ConfidenceScore(0.7)
            ) for kw in TauConstants.KEYWORDS)
            suggestions.extend(kw for kw in all_keywords if kw.suggestion_type)

            all_operators = (Suggestion(
                suggestion_type=SuggestionType.OPERATOR,
                text=SuggestionText(op),
                confidence=ConfidenceScore(0.7)
            ) for op in TauConstants.OPERATORS)
            suggestions.extend(all_operators)
            return suggestions

        for keyword in TauConstants.KEYWORDS:
            if keyword.lower().startswith(prefix):
                suggestion_type = SuggestionGenerator._determine_keyword_type(keyword)
                if suggestion_type:
                    suggestions.append(Suggestion(
                        suggestion_type=suggestion_type,
                        text=SuggestionText(keyword),
                        confidence=ConfidenceScore(0.9)
                    ))

        for operator in TauConstants.OPERATORS:
            if operator.startswith(prefix):
                suggestions.append(Suggestion(
                    suggestion_type=SuggestionType.OPERATOR,
                    text=SuggestionText(operator),
                    confidence=ConfidenceScore(0.9)
                ))

        if "!=" in code:
            suggestions.append(Suggestion(
                suggestion_type=SuggestionType.CLARITY,
                text=SuggestionText("Consider using `not (a = b)` instead of `a != b`"),
                confidence=ConfidenceScore(0.95)
            ))

        return suggestions

    @staticmethod
    def _determine_keyword_type(keyword: str) -> Optional[SuggestionType]:
        temporal_keywords = {"always", "never", "sometimes"}
        quantifier_keywords = {"forall", "exists"}

        if keyword in temporal_keywords:
            return SuggestionType.TEMPORAL
        if keyword in quantifier_keywords:
            return SuggestionType.QUANTIFIER
        if keyword.upper() == "DEFINE" or keyword in ["true", "false"]:
            return SuggestionType.KEYWORD

        return None


class NLPServiceLoader:
    """Handles loading of NLP service (I/O operation)."""

    _service_instance: Optional['NLPTranslationService'] = None

    @classmethod
    def load_nlp_service_async(cls) -> Result[Optional['NLPTranslationService'], AppError]:
        """Load NLP service if available."""
        if cls._service_instance is not None:
            return Success(cls._service_instance)

        try:
            # This is a lazy import to avoid circular dependencies and loading costs
            from nlp.nlp_integration import NLPTranslationService
            cls._service_instance = NLPTranslationService()
            return Success(cls._service_instance)
        except ImportError:
            # This is a valid state; the NLP service is optional.
            return Success(None)
        except Exception as e:
            # This indicates a real problem with the optional service.
            return Failure(AppError(error_code="SERVICE_LOAD_ERROR", message=f"Failed to load NLP service: {str(e)}"))


# --- Main Service Classes ---

class CodeExplainer:
    """Explains code snippets using a rule-based approach."""

    def explain(self, code: CodeText) -> Result[ExplanationText, AppError]:
        """Orchestrates the explanation of a full code snippet."""
        code_str = str(code).strip()
        if not code_str:
            return Success(ExplanationText("The code is empty."))

        lines = code_str.splitlines()
        line_explanations: List[LineExplanation] = []

        for line_content in lines:
            line_text = CodeText(line_content)
            explanation = self._explain_line(line_text)
            if explanation:
                line_explanations.append(explanation)

        if not line_explanations:
            return Success(ExplanationText("Could not generate any specific explanations for the code."))

        overall_explanation = self._generate_overall_explanation(line_explanations)
        return Success(overall_explanation)

    def _explain_line(self, line: CodeText) -> Optional[LineExplanation]:
        """Explains a single line of code based on keyword matching."""
        line_str = str(line).strip()
        explanation_text = None

        if line_str.startswith("DEFINE"):
            explanation_text = ExplanationText("Defines a new constant, function, or predicate.")
        elif line_str.startswith("always"):
            explanation_text = ExplanationText("Asserts a temporal property that must always hold.")
        elif line_str.startswith("never"):
            explanation_text = ExplanationText("Asserts a temporal property that must never hold.")
        elif line_str.startswith("forall"):
            explanation_text = ExplanationText("Makes a universal quantification (for all).")
        elif "->" in line_str:
            explanation_text = ExplanationText("Represents a logical implication.")

        if explanation_text:
            return LineExplanation(line=line, explanation=explanation_text)

        return None

    def _generate_overall_explanation(self, explanations: List[LineExplanation]) -> ExplanationText:
        """Generates a summary from a list of line explanations."""
        if not explanations:
            return ExplanationText("No specific explanations could be generated.")

        summary_parts = ["This code appears to contain the following elements:"]
        for expl in explanations:
            summary_parts.append(f"- A line with `{str(expl.line)[:20]}...` which {str(expl.explanation).lower()}")

        return ExplanationText("\n".join(summary_parts))


class AutocompleteService:
    """Provides autocomplete suggestions."""

    def __init__(self, nlp_service_loader: Optional[NLPServiceLoader] = None):
        self.nlp_service_loader = nlp_service_loader

    def get_suggestions(self, partial_code: CodeText) -> Result[List[Suggestion], AppError]:
        suggestions = SuggestionGenerator.generate_basic_suggestions(partial_code)
        return Success(suggestions)


class ExplanationService:
    """Provides explanations for code."""

    def __init__(self, code_explainer: CodeExplainer, nlp_service_loader: Optional[NLPServiceLoader] = None):
        self.code_explainer = code_explainer
        self.nlp_service_loader = nlp_service_loader

    def explain_code(self, code: CodeText) -> Result[ExplanationText, AppError]:
        """Generates a human-readable explanation of a Tau code snippet."""
        return self.code_explainer.explain(code)

    def get_suggestions(self, partial_code: CodeText) -> Result[List[Suggestion], AppError]:
        return Success(SuggestionGenerator.generate_basic_suggestions(partial_code))
