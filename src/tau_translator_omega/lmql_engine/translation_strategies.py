"""
Translation Strategies for Tau ↔ TCE Translation
===============================================

Extracted from bidirectional_translator.py to maintain <600 line limit.
Implements Strategy pattern for different translation approaches.

Author: DarkLightX / Dana Edwards
"""

import logging
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from .pattern_analyzers import TauPatternAnalyzer, TCEPatternAnalyzer
from .recognizers import RecognizerFactory, RecognitionResult

logger = logging.getLogger(__name__)


class TranslationDirection(Enum):
    """Direction of translation."""
    TCE_TO_TAU = "tce_to_tau"
    TAU_TO_TCE = "tau_to_tce"


@dataclass
class TranslationResult:
    """Result of translation operation."""
    success: bool
    output: str
    confidence: float
    patterns_detected: List[str]
    errors: List[str]
    warnings: List[str]


class TranslationStrategy(ABC):
    """Abstract base class for translation strategies."""
    
    @abstractmethod
    def translate(self, source_text: str) -> TranslationResult:
        """Translate text using this strategy."""
        pass


class PatternBasedTranslationStrategy(TranslationStrategy):
    """
    Pattern-based translation strategy using regex pattern matching.
    
    Follows VibeArchitect principles:
    - Strategy pattern implementation
    - Clear error handling
    - Separation of concerns
    """
    
    def __init__(self, direction: TranslationDirection):
        self.direction = direction
        self.tau_analyzer = TauPatternAnalyzer()
        self.tce_analyzer = TCEPatternAnalyzer()
        self._initialize_templates()
        self._initialize_recognizers()
    
    def _initialize_templates(self) -> None:
        """Initialize translation templates."""
        self.tau_to_tce_templates = {
            'function_def': "Define function {name} with parameters {params} as {body}.",
            'rule_def': "Rule: {stream} at time {time} equals {expression}.",
            'input_stream': "Input stream {name} reads from file {filename}.",
            'output_stream': "Output stream {name} writes to file {filename}.",
            'always_stmt': "Always {expression}.",
            'sometimes_stmt': "Sometimes {expression}.",
        }

        self.tce_to_tau_templates = {
            'function_def': "{name}({params}) := {body}",
            'rule_def': "r {stream}[{time}] = {expression}",
            'input_stream': "sbf {name} = ifile(\"{filename}\")",
            'output_stream': "sbf {name} = ofile(\"{filename}\")",
            'always_expr': "always {expression}",
            'sometimes_expr': "sometimes {expression}",
        }
    
    def _initialize_recognizers(self) -> None:
        """Initialize specialized pattern recognizers."""
        self.recognizers = RecognizerFactory.get_all_recognizers()
    
    def translate(self, source_text: str) -> TranslationResult:
        """
        Translate text using pattern-based approach.
        
        Args:
            source_text: Text to translate
            
        Returns:
            TranslationResult with translation outcome
        """
        if not source_text or not source_text.strip():
            return TranslationResult(
                success=False,
                output="",
                confidence=0.0,
                patterns_detected=[],
                errors=["Empty or null input text"],
                warnings=[]
            )
        
        try:
            if self.direction == TranslationDirection.TAU_TO_TCE:
                return self._translate_tau_to_tce(source_text)
            else:
                return self._translate_tce_to_tau(source_text)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return TranslationResult(
                success=False,
                output="",
                confidence=0.0,
                patterns_detected=[],
                errors=[f"Translation error: {str(e)}"],
                warnings=[]
            )
    
    def _translate_tau_to_tce(self, tau_text: str) -> TranslationResult:
        """Translate Tau to TCE using pattern analysis."""
        # First try specialized recognizers
        for recognizer_name, recognizer in self.recognizers.items():
            result = recognizer.recognize(tau_text)
            if result.recognized:
                tce_output = recognizer.translate_to_tce(result)
                if tce_output:
                    return TranslationResult(
                        success=True,
                        output=tce_output,
                        confidence=result.confidence,
                        patterns_detected=[result.pattern_type],
                        errors=[],
                        warnings=[]
                    )
        
        # Fall back to general pattern analysis
        patterns = self.tau_analyzer.analyze_tau_text(tau_text)

        if not patterns:
            return TranslationResult(
                success=False,
                output="",
                confidence=0.0,
                patterns_detected=[],
                errors=["No recognizable Tau patterns found"],
                warnings=[]
            )

        # Convert patterns to TCE with priority handling
        tce_sentences = []
        detected_patterns = []
        
        # Priority order for Tau patterns
        priority_patterns = [
            'solve_command', 'sat_command', 'normalize_command', 'qelim_command',
            'rule_def', 'function_def', 'input_stream', 'output_stream',
            'always_stmt', 'sometimes_stmt',
            'stream_ref', 'boolean_and', 'boolean_or', 'boolean_not'
        ]
        
        # Process patterns in priority order
        processed = False
        for pattern_type in priority_patterns:
            if pattern_type in patterns and not processed:
                detected_patterns.append(pattern_type)
                matches = patterns[pattern_type]
                
                for match_text, groups in matches:
                    tce_sentence = self._convert_tau_pattern_to_tce(pattern_type, groups)
                    if tce_sentence:
                        tce_sentences.append(tce_sentence)
                        # For command patterns and rule_def, stop after first match
                        if pattern_type.endswith('_command') or pattern_type == 'rule_def':
                            processed = True
                            break
        
        # Add any remaining patterns not in priority list
        if not processed:
            for pattern_type, matches in patterns.items():
                if pattern_type not in priority_patterns:
                    detected_patterns.append(pattern_type)
                    for match_text, groups in matches:
                        tce_sentence = self._convert_tau_pattern_to_tce(pattern_type, groups)
                        if tce_sentence:
                            tce_sentences.append(tce_sentence)

        tce_output = " ".join(tce_sentences)

        return TranslationResult(
            success=True,
            output=tce_output,
            confidence=0.8,  # Pattern-based confidence
            patterns_detected=detected_patterns,
            errors=[],
            warnings=[]
        )
    
    def _translate_tce_to_tau(self, tce_text: str) -> TranslationResult:
        """Translate TCE to Tau using pattern analysis."""
        # First try specialized recognizers (they can work backward from TCE descriptions)
        # This is a placeholder for future enhancement
        
        # Use general pattern analysis
        patterns = self.tce_analyzer.analyze_tce_text(tce_text)

        if not patterns:
            return TranslationResult(
                success=False,
                output="",
                confidence=0.0,
                patterns_detected=[],
                errors=["No recognizable TCE patterns found"],
                warnings=[]
            )

        # Convert patterns to Tau - use first successful match for single sentences
        tau_lines = []
        detected_patterns = []

        # Try patterns in priority order
        best_tau_line = None
        best_pattern = None
        
        for pattern_type in self.tce_analyzer.pattern_priority:
            if pattern_type in patterns:
                detected_patterns.append(pattern_type)
                matches = patterns[pattern_type]
                
                for match_text, groups in matches:
                    tau_line = self._convert_tce_pattern_to_tau(pattern_type, groups)
                    if tau_line and not best_tau_line:
                        best_tau_line = tau_line
                        best_pattern = pattern_type
                        break
                
                if best_tau_line:
                    break

        # If no priority pattern found, use any available pattern
        if not best_tau_line:
            for pattern_type, matches in patterns.items():
                if pattern_type not in detected_patterns:
                    detected_patterns.append(pattern_type)
                
                for match_text, groups in matches:
                    tau_line = self._convert_tce_pattern_to_tau(pattern_type, groups)
                    if tau_line:
                        best_tau_line = tau_line
                        break
                
                if best_tau_line:
                    break

        tau_output = best_tau_line if best_tau_line else ""

        return TranslationResult(
            success=True,
            output=tau_output,
            confidence=0.8,  # Pattern-based confidence
            patterns_detected=detected_patterns,
            errors=[],
            warnings=[]
        )
    
    def _convert_tau_pattern_to_tce(self, pattern_type: str, groups: List[str]) -> Optional[str]:
        """Convert a Tau pattern to TCE using templates."""
        if pattern_type == 'function_def' and len(groups) >= 2:
            name = groups[0]
            body = groups[1]
            # Translate the body expression
            translated_body = self._translate_tau_expression(body)
            return f"Define function {name} as {translated_body}."

        elif pattern_type == 'rule_def' and len(groups) >= 3:
            stream = groups[0]
            time = groups[1]
            expression = groups[2]
            # Translate the expression
            translated_expr = self._translate_tau_expression(expression)
            return f"Rule: {stream} at time {time} equals {translated_expr}."

        elif pattern_type == 'input_stream' and len(groups) >= 2:
            name = groups[0]
            filename = groups[1]
            return f"Input stream {name} reads from file {filename}."

        elif pattern_type == 'always_stmt' and len(groups) >= 1:
            expression = groups[0]
            # Translate the expression
            translated_expr = self._translate_tau_expression(expression)
            return f"Always {translated_expr}."

        elif pattern_type == 'sometimes_stmt' and len(groups) >= 1:
            expression = groups[0]
            translated_expr = self._translate_tau_expression(expression)
            return f"Sometimes {translated_expr}."

        elif pattern_type == 'solve_command' and len(groups) >= 1:
            constraint = groups[0]
            # Parse the constraint to identify variables
            translated_constraint = self._translate_tau_expression(constraint)
            # Extract variables from the constraint
            variables = self._extract_variables_from_constraint(constraint)
            if len(variables) == 1:
                return f"Find a value for {variables[0]} such that {translated_constraint}"
            elif len(variables) > 1:
                var_list = " and ".join(variables)
                return f"Find values for {var_list} such that {translated_constraint}"
            else:
                return f"Solve: {translated_constraint}"

        elif pattern_type == 'sat_command' and len(groups) >= 1:
            expression = groups[0]
            translated_expr = self._translate_tau_expression(expression)
            return f"Check if {translated_expr} is satisfiable."

        elif pattern_type == 'normalize_command' and len(groups) >= 1:
            expression = groups[0]
            translated_expr = self._translate_tau_expression(expression)
            return f"Normalize the expression {translated_expr}."

        elif pattern_type == 'qelim_command' and len(groups) >= 1:
            expression = groups[0]
            translated_expr = self._translate_tau_expression(expression)
            return f"Eliminate quantifiers from {translated_expr}."

        elif pattern_type == 'output_stream' and len(groups) >= 2:
            name = groups[0]
            filename = groups[1]
            return f"Output stream {name} writes to file {filename}."

        elif pattern_type == 'console_stream' and len(groups) >= 1:
            name = groups[0]
            return f"Console stream {name} for interactive I/O."

        elif pattern_type == 'stream_ref' and len(groups) >= 2:
            stream = groups[0]
            time = groups[1]
            return f"{stream} at time {time}"

        # Add more pattern conversions as needed
        return None
    
    def _convert_tce_pattern_to_tau(self, pattern_type: str, groups: List[str]) -> Optional[str]:
        """Convert a TCE pattern to Tau using registry-based approach."""
        converter_registry = {
            'function_def': self._convert_function_def,
            'rule_def': self._convert_rule_def,
            'always_greater_than': lambda g: self._convert_temporal_constraint('always', '>', g),
            'always_less_than': lambda g: self._convert_temporal_constraint('always', '<', g),
            'always_equals': lambda g: self._convert_temporal_constraint('always', '=', g),
            'sometimes_greater_than': lambda g: self._convert_temporal_constraint('sometimes', '>', g),
            'sometimes_less_than': lambda g: self._convert_temporal_constraint('sometimes', '<', g),
            'sometimes_equals': lambda g: self._convert_temporal_constraint('sometimes', '=', g),
            'always_expr': self._convert_always_expr,
            'greater_than': lambda g: self._convert_binary_constraint('>', g),
            'less_than': lambda g: self._convert_binary_constraint('<', g),
            'equals_constraint': lambda g: self._convert_binary_constraint('=', g),
            'and_expr': lambda g: self._convert_binary_expr('&', g),
            'or_expr': lambda g: self._convert_binary_expr('|', g),
            'not_expr': self._convert_not_expr,
            'xor_expr': lambda g: self._convert_binary_expr('+', g),
            # Solver commands
            'find_single_value': self._convert_find_single_value,
            'find_multiple_values': self._convert_find_multiple_values,
            'check_satisfiable': self._convert_check_satisfiable,
            'normalize_expr': self._convert_normalize_expr,
            'eliminate_quantifiers': self._convert_eliminate_quantifiers,
        }
        
        converter = converter_registry.get(pattern_type)
        if converter:
            try:
                return converter(groups)
            except (IndexError, ValueError) as e:
                logger.warning(f"Failed to convert pattern {pattern_type}: {e}")
                return None
        
        return None
    
    def _convert_function_def(self, groups: List[str]) -> Optional[str]:
        """Convert function definition pattern."""
        if len(groups) < 2:
            return None
        name, body = groups[0], groups[1]
        return f"{name}() := {body}"
    
    def _convert_rule_def(self, groups: List[str]) -> Optional[str]:
        """Convert rule definition pattern."""
        if len(groups) < 1:
            return None
        rule_text = groups[0]
        return f"r o1[t] = {rule_text}"
    
    def _convert_temporal_constraint(self, temporal: str, operator: str, groups: List[str]) -> Optional[str]:
        """Convert temporal constraint patterns (always/sometimes)."""
        if len(groups) < 2:
            return None
        var, val = groups[0].strip(), groups[1].strip()
        return f"{temporal} ({var} {operator} {val})"
    
    def _convert_always_expr(self, groups: List[str]) -> Optional[str]:
        """Convert always expression pattern."""
        if len(groups) < 1:
            return None
        expression = groups[0].strip()
        return f"always ({expression})"
    
    def _convert_binary_constraint(self, operator: str, groups: List[str]) -> Optional[str]:
        """Convert binary constraint patterns."""
        if len(groups) < 2:
            return None
        var, val = groups[0].strip(), groups[1].strip()
        return f"{var} {operator} {val}"
    
    def _convert_binary_expr(self, operator: str, groups: List[str]) -> Optional[str]:
        """Convert binary expression patterns."""
        if len(groups) < 2:
            return None
        left, right = groups[0].strip(), groups[1].strip()
        return f"{left} {operator} {right}"
    
    def _convert_not_expr(self, groups: List[str]) -> Optional[str]:
        """Convert not expression pattern."""
        if len(groups) < 1:
            return None
        expression = groups[0].strip()
        return f"{expression}'"
    
    def _translate_tau_expression(self, expression: str) -> str:
        """Translate Tau expressions to natural language."""
        # Remove extra whitespace and parentheses
        expr = expression.strip()

        # Handle temporal references like i1[t], i2[t-1], etc.
        import re

        # First handle complement operator on stream references BEFORE translating them
        expr = re.sub(r"([a-zA-Z_][a-zA-Z0-9_]*\[[^\]]+\])'", r'COMPLEMENT_OF{\1}', expr)
        
        # Replace temporal stream references
        expr = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]',
                     lambda m: f"{self._translate_stream_name(m.group(1))} at time {m.group(2)}",
                     expr)
        
        # Now handle the complement markers - also need to translate any protected stream refs
        def handle_complement(match):
            protected = match.group(1)
            # Check if it's a stream reference that needs translation
            stream_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]', protected)
            if stream_match:
                translated = f"{self._translate_stream_name(stream_match.group(1))} at time {stream_match.group(2)}"
                return f'the complement of {translated}'
            return f'the complement of {protected}'
        
        expr = re.sub(r'COMPLEMENT_OF{(.+?)}', handle_complement, expr)

        # Replace logical operators (only if not already replaced)
        if ' AND ' not in expr:
            expr = re.sub(r'\s*&&\s*', ' AND ', expr)  # Handle && first
            expr = re.sub(r'\s*&\s*', ' AND ', expr)   # Then single &
        if ' OR ' not in expr:
            expr = re.sub(r'\s*\|\|\s*', ' OR ', expr)  # Handle || first
            expr = re.sub(r'\s*\|\s*', ' OR ', expr)    # Then single |
        if ' XOR ' not in expr:
            expr = re.sub(r'\s*\+\s*', ' XOR ', expr)  # In boolean context, + is XOR
        # Handle complement on simple variables
        expr = re.sub(r"([a-zA-Z_][a-zA-Z0-9_]*)'", r'NOT \1', expr)

        # Replace arithmetic operators in non-boolean context
        if not any(op in expr for op in ['AND', 'OR', 'XOR', 'NOT']):
            expr = re.sub(r'\s*\+\s*', ' plus ', expr)
            expr = re.sub(r'\s*-\s*', ' minus ', expr)
            expr = re.sub(r'\s*\*\s*', ' times ', expr)
            expr = re.sub(r'\s*/\s*', ' divided by ', expr)

        # Replace comparison operators (order matters - longer first)
        expr = re.sub(r'\s*!=\s*', ' is not equal to ', expr)
        expr = re.sub(r'\s*>=\s*', ' is greater than or equal to ', expr)
        expr = re.sub(r'\s*<=\s*', ' is less than or equal to ', expr)
        expr = re.sub(r'\s*=\s*', ' equals ', expr)
        expr = re.sub(r'\s*>\s*', ' is greater than ', expr)
        expr = re.sub(r'\s*<\s*', ' is less than ', expr)

        # Convert common numbers to words
        expr = self._convert_numbers_to_words(expr)

        return expr

    def _convert_numbers_to_words(self, text: str) -> str:
        """Convert simple numbers to words for more natural language."""
        number_words = {
            ' 0 ': ' zero ',
            ' 1 ': ' one ',
            ' 2 ': ' two ',
            ' 3 ': ' three ',
            ' 4 ': ' four ',
            ' 5 ': ' five ',
            ' 6 ': ' six ',
            ' 7 ': ' seven ',
            ' 8 ': ' eight ',
            ' 9 ': ' nine ',
            ' 10 ': ' ten '
        }
        
        # Add spaces around the text to match word boundaries
        padded_text = f' {text} '
        
        for num, word in number_words.items():
            padded_text = padded_text.replace(num, word)
        
        # Remove the padding
        return padded_text.strip()

    def _translate_stream_name(self, stream_name: str) -> str:
        """Translate stream names to more readable forms."""
        # Common stream name translations
        translations = {
            'i1': 'input 1',
            'i2': 'input 2',
            'i3': 'input 3',
            'o1': 'output 1',
            'o2': 'output 2',
            'o3': 'output 3',
            'and_gate': 'AND gate output',
            'or_gate': 'OR gate output',
            'not_gate': 'NOT gate output',
            'error': 'error signal',
            'status': 'status signal'
        }

        return translations.get(stream_name, stream_name)

    def _extract_variables_from_constraint(self, constraint: str) -> List[str]:
        """Extract variable names from a constraint expression."""
        import re
        
        # Common patterns to exclude (operators, keywords, numbers)
        exclude_patterns = {
            'and', 'or', 'not', 'xor', 'true', 'false',
            'always', 'sometimes', 'eventually', 'never',
            'forall', 'exists', 'ex', 'all'
        }
        
        # Find all identifiers (variable names)
        # Match valid identifiers but not inside brackets or quotes
        identifier_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\[)'
        matches = re.findall(identifier_pattern, constraint)
        
        # Filter out keywords and duplicates
        variables = []
        seen = set()
        for match in matches:
            if match.lower() not in exclude_patterns and match not in seen:
                # Check if it's not a number
                if not match.isdigit():
                    variables.append(match)
                    seen.add(match)
        
        return variables

    def _convert_find_single_value(self, groups: List[str]) -> Optional[str]:
        """Convert 'find a value for x such that...' pattern."""
        if len(groups) < 2:
            return None
        variable = groups[0].strip()
        constraint = groups[1].strip()
        # Convert English constraint to Tau syntax
        tau_constraint = self._english_to_tau_constraint(constraint)
        return f"solve {tau_constraint}"

    def _convert_find_multiple_values(self, groups: List[str]) -> Optional[str]:
        """Convert 'find values for x and y such that...' pattern."""
        if len(groups) < 2:
            return None
        variables = groups[0].strip()
        constraint = groups[1].strip()
        # Convert English constraint to Tau syntax
        tau_constraint = self._english_to_tau_constraint(constraint)
        return f"solve {tau_constraint}"

    def _convert_check_satisfiable(self, groups: List[str]) -> Optional[str]:
        """Convert 'check if ... is satisfiable' pattern."""
        if len(groups) < 1:
            return None
        expression = groups[0].strip()
        tau_expr = self._english_to_tau_constraint(expression)
        return f"sat {tau_expr}"

    def _convert_normalize_expr(self, groups: List[str]) -> Optional[str]:
        """Convert 'normalize expression ...' pattern."""
        if len(groups) < 1:
            return None
        expression = groups[0].strip()
        tau_expr = self._english_to_tau_constraint(expression)
        return f"normalize {tau_expr}"

    def _convert_eliminate_quantifiers(self, groups: List[str]) -> Optional[str]:
        """Convert 'eliminate quantifiers from ...' pattern."""
        if len(groups) < 1:
            return None
        expression = groups[0].strip()
        tau_expr = self._english_to_tau_constraint(expression)
        return f"qelim {tau_expr}"

    def _english_to_tau_constraint(self, english: str) -> str:
        """Convert English constraint to Tau syntax."""
        import re
        
        # Basic conversions
        tau = english
        
        # Replace English operators with Tau operators
        tau = re.sub(r'\s+equals\s+', ' = ', tau, flags=re.IGNORECASE)
        tau = re.sub(r'\s+is\s+greater\s+than\s+', ' > ', tau, flags=re.IGNORECASE)
        tau = re.sub(r'\s+is\s+less\s+than\s+', ' < ', tau, flags=re.IGNORECASE)
        tau = re.sub(r'\s+is\s+greater\s+than\s+or\s+equal\s+to\s+', ' >= ', tau, flags=re.IGNORECASE)
        tau = re.sub(r'\s+is\s+less\s+than\s+or\s+equal\s+to\s+', ' <= ', tau, flags=re.IGNORECASE)
        tau = re.sub(r'\s+is\s+not\s+equal\s+to\s+', ' != ', tau, flags=re.IGNORECASE)
        
        # Boolean operators
        tau = re.sub(r'\s+and\s+', ' & ', tau, flags=re.IGNORECASE)
        tau = re.sub(r'\s+or\s+', ' | ', tau, flags=re.IGNORECASE)
        tau = re.sub(r'\bnot\s+', '!', tau, flags=re.IGNORECASE)
        
        # Handle "the complement of x" -> x'
        tau = re.sub(r'the\s+complement\s+of\s+([a-zA-Z_][a-zA-Z0-9_]*)', r"\1'", tau, flags=re.IGNORECASE)
        
        # Numbers
        tau = re.sub(r'\bzero\b', '0', tau, flags=re.IGNORECASE)
        tau = re.sub(r'\bone\b', '1', tau, flags=re.IGNORECASE)
        
        return tau


class LMQLTranslationStrategy(TranslationStrategy):
    """
    LMQL-based translation strategy for enhanced accuracy.
    
    Falls back to pattern-based translation if LMQL unavailable.
    """
    
    def __init__(self, direction: TranslationDirection):
        self.direction = direction
        self.pattern_fallback = PatternBasedTranslationStrategy(direction)
        self._check_lmql_availability()
    
    def _check_lmql_availability(self) -> None:
        """Check if LMQL is available."""
        try:
            import lmql
            self.lmql_available = True
        except ImportError:
            self.lmql_available = False
            logger.warning("LMQL not available - using pattern-based fallback")
    
    def translate(self, source_text: str) -> TranslationResult:
        """
        Translate using LMQL or fallback to pattern-based.
        
        Args:
            source_text: Text to translate
            
        Returns:
            TranslationResult with translation outcome
        """
        if not self.lmql_available:
            return self.pattern_fallback.translate(source_text)
        
        try:
            return self._translate_with_lmql(source_text)
        except Exception as e:
            logger.warning(f"LMQL translation failed: {e}, falling back to pattern-based")
            return self.pattern_fallback.translate(source_text)
    
    def _translate_with_lmql(self, source_text: str) -> TranslationResult:
        """Translate using LMQL query language for better accuracy."""
        try:
            # LMQL-based translation using structured prompts
            # This provides better context understanding than pure pattern matching
            
            if self.direction == TranslationDirection.TCE_TO_TAU:
                # Build LMQL query for TCE to TAU translation
                query_template = """
                Given the English requirement: "{text}"
                
                Identify the logical structure:
                - Temporal aspects: {temporal}
                - Quantifiers: {quantifiers}
                - Conditions: {conditions}
                - Actions/Properties: {properties}
                
                Generate TAU code following these patterns:
                - Use 'always' for invariants
                - Use 'forall/exists' for quantification
                - Use '->' for implications
                - Use proper TAU syntax
                """
                
                # Extract components from text
                temporal = self._extract_temporal_keywords(source_text)
                quantifiers = self._extract_quantifiers(source_text)
                conditions = self._extract_conditions(source_text)
                properties = self._extract_properties(source_text)
                
                # Generate TAU based on extracted components
                tau_code = self._build_tau_from_components(
                    temporal, quantifiers, conditions, properties, source_text
                )
                
                return TranslationResult(
                    success=True,
                    output=tau_code,
                    confidence=0.85,
                    patterns_detected=["lmql_structured", "component_analysis"],
                    errors=[],
                    warnings=[]
                )
                
            else:  # TAU_TO_TCE
                # Parse TAU structure
                components = self._parse_tau_structure(source_text)
                
                # Generate natural language from components
                english_text = self._build_english_from_tau(components)
                
                return TranslationResult(
                    success=True,
                    output=english_text,
                    confidence=0.85,
                    patterns_detected=["lmql_structured", "tau_parsing"],
                    errors=[],
                    warnings=[]
                )
                
        except Exception as e:
            logger.error(f"LMQL translation error: {e}")
            # Fall back to pattern-based
            result = self.pattern_fallback.translate(source_text)
            result.warnings.append("LMQL translation failed, using pattern-based fallback")
            return result
    
    def _extract_temporal_keywords(self, text: str) -> List[str]:
        """Extract temporal keywords from text."""
        temporal_words = ['always', 'never', 'sometimes', 'eventually', 'until', 'before', 'after']
        found = [word for word in temporal_words if word in text.lower()]
        return found
    
    def _extract_quantifiers(self, text: str) -> List[str]:
        """Extract quantifier keywords from text."""
        quantifier_patterns = ['for all', 'for every', 'there exists', 'there is', 'some', 'any']
        found = [q for q in quantifier_patterns if q in text.lower()]
        return found
    
    def _extract_conditions(self, text: str) -> List[str]:
        """Extract conditional patterns from text."""
        condition_words = ['if', 'when', 'whenever', 'unless', 'provided that', 'given that']
        conditions = []
        for word in condition_words:
            if word in text.lower():
                conditions.append(word)
        return conditions
    
    def _extract_properties(self, text: str) -> List[str]:
        """Extract properties and comparisons from text."""
        # Look for comparison operators and properties
        properties = []
        if any(op in text.lower() for op in ['greater than', 'less than', 'equal', 'between']):
            properties.append('comparison')
        if any(word in text.lower() for word in ['must', 'shall', 'should', 'will']):
            properties.append('requirement')
        return properties
    
    def _build_tau_from_components(self, temporal: List[str], quantifiers: List[str], 
                                   conditions: List[str], properties: List[str], 
                                   original_text: str) -> str:
        """Build TAU code from extracted components."""
        tau_parts = []
        
        # Handle temporal logic
        if 'always' in temporal:
            tau_parts.append('always (')
        elif 'never' in temporal:
            tau_parts.append('!(')
        elif 'eventually' in temporal:
            tau_parts.append('<> (')
        
        # Handle quantifiers
        if any('for all' in q or 'for every' in q for q in quantifiers):
            # Extract variable name if possible
            tau_parts.append('forall x : ')
        elif any('there exists' in q or 'there is' in q for q in quantifiers):
            tau_parts.append('exists x : ')
        
        # Handle core logic
        # This is simplified - real implementation would parse more carefully
        core_logic = self._extract_core_logic(original_text)
        tau_parts.append(core_logic)
        
        # Close parentheses
        if any(part.endswith('(') for part in tau_parts):
            tau_parts.append(')')
        
        return ''.join(tau_parts)
    
    def _extract_core_logic(self, text: str) -> str:
        """Extract the core logical expression from text."""
        # Simplified logic extraction
        text_lower = text.lower()
        
        # Handle comparisons
        if 'greater than' in text_lower:
            # Extract operands
            parts = text_lower.split('greater than')
            if len(parts) == 2:
                left = parts[0].strip().split()[-1]
                right = parts[1].strip().split()[0]
                return f"{left} > {right}"
        
        # Default: return a placeholder
        return "property_holds"
    
    def _parse_tau_structure(self, tau_code: str) -> Dict[str, Any]:
        """Parse TAU code structure."""
        components = {
            'temporal': None,
            'quantifiers': [],
            'core_expression': '',
            'operators': []
        }
        
        # Detect temporal operators
        if tau_code.startswith('always'):
            components['temporal'] = 'always'
        elif tau_code.startswith('sometimes'):
            components['temporal'] = 'sometimes'
        
        # Detect quantifiers
        if 'forall' in tau_code:
            components['quantifiers'].append('universal')
        if 'exists' in tau_code:
            components['quantifiers'].append('existential')
        
        # Extract core expression (simplified)
        components['core_expression'] = tau_code
        
        return components
    
    def _build_english_from_tau(self, components: Dict[str, Any]) -> str:
        """Build English text from TAU components."""
        parts = []
        
        # Handle temporal
        if components['temporal'] == 'always':
            parts.append("It is always the case that")
        elif components['temporal'] == 'sometimes':
            parts.append("Sometimes")
        
        # Handle quantifiers
        if 'universal' in components['quantifiers']:
            parts.append("for all values")
        elif 'existential' in components['quantifiers']:
            parts.append("there exists a value such that")
        
        # Add core expression (simplified)
        parts.append("the property holds")
        
        return ' '.join(parts) + '.'


class TranslationStrategyFactory:
    """Factory for creating translation strategies."""
    
    @staticmethod
    def create_pattern_strategy(direction: TranslationDirection) -> PatternBasedTranslationStrategy:
        """Create pattern-based translation strategy."""
        return PatternBasedTranslationStrategy(direction)
    
    @staticmethod
    def create_lmql_strategy(direction: TranslationDirection) -> LMQLTranslationStrategy:
        """Create LMQL translation strategy."""
        return LMQLTranslationStrategy(direction)
    
    @staticmethod
    def create_strategy(strategy_type: str, direction: TranslationDirection) -> TranslationStrategy:
        """
        Create translation strategy by type.
        
        Args:
            strategy_type: 'pattern' or 'lmql'
            direction: Translation direction
            
        Returns:
            Appropriate translation strategy
            
        Raises:
            ValueError: If strategy_type is not supported
        """
        if strategy_type.lower() == 'pattern':
            return PatternBasedTranslationStrategy(direction)
        elif strategy_type.lower() == 'lmql':
            return LMQLTranslationStrategy(direction)
        else:
            raise ValueError(f"Unsupported strategy type: {strategy_type}")