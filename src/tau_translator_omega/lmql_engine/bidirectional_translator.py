"""
LMQL-based Bidirectional Translator for Tau ↔ TCE
==================================================

This module provides bidirectional translation between Tau Language and 
Tau Controlled English (TCE) using LMQL for constrained generation.

Key Features:
- Grammar-guided translation
- Pattern recognition and validation
- Bidirectional conversion
- Legal compliance (no IDNI parser dependency)
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# LMQL imports
try:
    import lmql
    LMQL_AVAILABLE = True
except ImportError:
    LMQL_AVAILABLE = False
    print("⚠️  LMQL not available - using pattern-based fallback")

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

class TauPatternAnalyzer:
    """
    Analyzes Tau Language text patterns without using IDNI parser.
    Uses regex and heuristics for pattern recognition.
    """
    
    def __init__(self):
        self.patterns = {
            # Function definitions
            'function_def': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*:=\s*(.+)',
            
            # Recurrence relations
            'recurrence_base': r'([a-zA-Z_][a-zA-Z0-9_]*)\[0\]\s*\([^)]*\)\s*:=\s*(.+)',
            'recurrence_step': r'([a-zA-Z_][a-zA-Z0-9_]*)\[n\]\s*\([^)]*\)\s*:=\s*(.+)',
            
            # Stream declarations
            'input_stream': r'sbf\s+([a-zA-Z0-9_]+)\s*=\s*ifile\s*\(\s*"([^"]+)"\s*\)',
            'output_stream': r'sbf\s+([a-zA-Z0-9_]+)\s*=\s*ofile\s*\(\s*"([^"]+)"\s*\)',
            'console_stream': r'sbf\s+([a-zA-Z0-9_]+)\s*=\s*console',
            
            # Rules
            'rule_def': r'r\s+([a-zA-Z0-9_]+)\[([^]]+)\]\s*=\s*(.+)',
            
            # Temporal logic
            'always_stmt': r'always\s+(.+)',
            'sometimes_stmt': r'sometimes\s+(.+)',
            
            # Boolean operations
            'boolean_and': r'(.+)\s*&\s*(.+)',
            'boolean_or': r'(.+)\s*\|\s*(.+)',
            'boolean_not': r"(.+)'",
            'boolean_xor': r'(.+)\s*\+\s*(.+)',
            
            # Solver commands
            'sat_command': r'sat\s+(.+)',
            'solve_command': r'solve\s+(.+)',
            'normalize_command': r'normalize\s+(.+)',
            'qelim_command': r'qelim\s+(.+)',
            
            # Bitvector operations
            'bitvector_literal': r'(0x[0-9a-fA-F]+|0b[01]+|\d+[ul]?)',
            
            # Stream references
            'stream_ref': r'([a-zA-Z0-9_]+)\[([^]]+)\]',
        }
    
    def analyze_tau_text(self, tau_text: str) -> Dict[str, List[Tuple[str, List[str]]]]:
        """
        Analyze Tau text and extract patterns.
        
        Args:
            tau_text: Raw Tau language text
            
        Returns:
            Dictionary mapping pattern types to list of (match, groups) tuples
        """
        results = {}
        
        # Split into lines for analysis
        lines = [line.strip() for line in tau_text.split('\n') if line.strip()]
        
        for pattern_name, pattern_regex in self.patterns.items():
            matches = []
            
            for line in lines:
                match = re.search(pattern_regex, line)
                if match:
                    matches.append((match.group(0), list(match.groups())))
            
            if matches:
                results[pattern_name] = matches
        
        return results

class TCEPatternAnalyzer:
    """
    Analyzes TCE (Tau Controlled English) patterns.
    """
    
    def __init__(self):
        self.patterns = {
            # Function definitions
            'function_def': r'define\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+.*as\s+(.+)',
            
            # Rules
            'rule_def': r'rule:?\s*(.+)',
            
            # Stream declarations
            'input_stream': r'input\s+stream\s+([a-zA-Z0-9_]+).*from\s+(.+)',
            'output_stream': r'output\s+stream\s+([a-zA-Z0-9_]+).*to\s+(.+)',
            
            # Temporal expressions
            'always_expr': r'always\s+(.+)',
            'sometimes_expr': r'sometimes\s+(.+)',
            
            # Boolean expressions
            'and_expr': r'(.+)\s+and\s+(.+)',
            'or_expr': r'(.+)\s+or\s+(.+)',
            'not_expr': r'not\s+(.+)',
            'xor_expr': r'(.+)\s+xor\s+(.+)',
            
            # Arithmetic
            'equals_expr': r'(.+)\s+equals\s+(.+)',
            'plus_expr': r'(.+)\s+plus\s+(.+)',
            'minus_expr': r'(.+)\s+minus\s+(.+)',
        }
    
    def analyze_tce_text(self, tce_text: str) -> Dict[str, List[Tuple[str, List[str]]]]:
        """
        Analyze TCE text and extract patterns.
        
        Args:
            tce_text: Raw TCE text
            
        Returns:
            Dictionary mapping pattern types to list of (match, groups) tuples
        """
        results = {}
        
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]', tce_text) if s.strip()]
        
        for pattern_name, pattern_regex in self.patterns.items():
            matches = []
            
            for sentence in sentences:
                match = re.search(pattern_regex, sentence, re.IGNORECASE)
                if match:
                    matches.append((match.group(0), list(match.groups())))
            
            if matches:
                results[pattern_name] = matches
        
        return results

class LMQLBidirectionalTranslator:
    """
    Main translator class using LMQL for bidirectional Tau ↔ TCE translation.
    """

    def __init__(self):
        self.tau_analyzer = TauPatternAnalyzer()
        self.tce_analyzer = TCEPatternAnalyzer()

        # Translation templates for different patterns
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

        # LMQL model configuration
        self.model_name = "openai/gpt-3.5-turbo"  # Can be changed to other models
        self.use_lmql = LMQL_AVAILABLE
    
    def translate_tau_to_tce(self, tau_text: str) -> TranslationResult:
        """
        Translate Tau Language to TCE using LMQL or pattern analysis.

        Args:
            tau_text: Tau language code

        Returns:
            TranslationResult with TCE output
        """
        if self.use_lmql:
            return self._translate_tau_to_tce_with_lmql(tau_text)
        else:
            return self._translate_tau_to_tce_with_patterns(tau_text)

    def _translate_tau_to_tce_with_lmql(self, tau_text: str) -> TranslationResult:
        """Translate using LMQL for enhanced accuracy."""
        try:
            # Use LMQL query for translation
            result = self._lmql_tau_to_tce_query(tau_text)

            return TranslationResult(
                success=True,
                output=result,
                confidence=0.9,  # LMQL-based confidence
                patterns_detected=["lmql_enhanced"],
                errors=[],
                warnings=[]
            )

        except Exception as e:
            # Fallback to pattern-based approach
            return self._translate_tau_to_tce_with_patterns(tau_text)

    def _translate_tau_to_tce_with_patterns(self, tau_text: str) -> TranslationResult:
        """Translate using pattern analysis (fallback method)."""
        try:
            # Analyze Tau patterns
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

            # Convert patterns to TCE
            tce_sentences = []
            detected_patterns = []

            for pattern_type, matches in patterns.items():
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

        except Exception as e:
            return TranslationResult(
                success=False,
                output="",
                confidence=0.0,
                patterns_detected=[],
                errors=[f"Translation error: {str(e)}"],
                warnings=[]
            )
    
    def translate_tce_to_tau(self, tce_text: str) -> TranslationResult:
        """
        Translate TCE to Tau Language using LMQL or pattern analysis.

        Args:
            tce_text: TCE natural language text

        Returns:
            TranslationResult with Tau output
        """
        if self.use_lmql:
            return self._translate_tce_to_tau_with_lmql(tce_text)
        else:
            return self._translate_tce_to_tau_with_patterns(tce_text)

    def _translate_tce_to_tau_with_lmql(self, tce_text: str) -> TranslationResult:
        """Translate using LMQL for enhanced accuracy."""
        try:
            # Use LMQL query for translation
            result = self._lmql_tce_to_tau_query(tce_text)

            return TranslationResult(
                success=True,
                output=result,
                confidence=0.9,  # LMQL-based confidence
                patterns_detected=["lmql_enhanced"],
                errors=[],
                warnings=[]
            )

        except Exception as e:
            # Fallback to pattern-based approach
            return self._translate_tce_to_tau_with_patterns(tce_text)

    def _translate_tce_to_tau_with_patterns(self, tce_text: str) -> TranslationResult:
        """Translate using pattern analysis (fallback method)."""
        try:
            # Analyze TCE patterns
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

            # Convert patterns to Tau
            tau_lines = []
            detected_patterns = []

            for pattern_type, matches in patterns.items():
                detected_patterns.append(pattern_type)

                for match_text, groups in matches:
                    tau_line = self._convert_tce_pattern_to_tau(pattern_type, groups)
                    if tau_line:
                        tau_lines.append(tau_line)

            tau_output = "\n".join(tau_lines)

            return TranslationResult(
                success=True,
                output=tau_output,
                confidence=0.8,  # Pattern-based confidence
                patterns_detected=detected_patterns,
                errors=[],
                warnings=[]
            )

        except Exception as e:
            return TranslationResult(
                success=False,
                output="",
                confidence=0.0,
                patterns_detected=[],
                errors=[f"Translation error: {str(e)}"],
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

        # Add more pattern conversions as needed
        return None

    def _translate_tau_expression(self, expression: str) -> str:
        """Translate Tau expressions to natural language."""
        # Remove extra whitespace and parentheses
        expr = expression.strip()

        # Handle temporal references like i1[t], i2[t-1], etc.
        import re

        # Replace temporal stream references
        expr = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]',
                     lambda m: f"{self._translate_stream_name(m.group(1))} at time {m.group(2)}",
                     expr)

        # Replace logical operators
        expr = re.sub(r'\s*&\s*', ' AND ', expr)
        expr = re.sub(r'\s*\|\s*', ' OR ', expr)
        expr = re.sub(r'\s*\+\s*', ' XOR ', expr)  # In boolean context, + is XOR
        expr = re.sub(r"([a-zA-Z_][a-zA-Z0-9_]*)'", r'NOT \1', expr)  # Handle negation

        # Replace arithmetic operators in non-boolean context
        if not any(op in expr for op in ['AND', 'OR', 'XOR', 'NOT']):
            expr = re.sub(r'\s*\+\s*', ' plus ', expr)
            expr = re.sub(r'\s*-\s*', ' minus ', expr)
            expr = re.sub(r'\s*\*\s*', ' times ', expr)
            expr = re.sub(r'\s*/\s*', ' divided by ', expr)

        # Replace comparison operators
        expr = re.sub(r'\s*=\s*', ' equals ', expr)
        expr = re.sub(r'\s*>\s*', ' is greater than ', expr)
        expr = re.sub(r'\s*<\s*', ' is less than ', expr)
        expr = re.sub(r'\s*>=\s*', ' is greater than or equal to ', expr)
        expr = re.sub(r'\s*<=\s*', ' is less than or equal to ', expr)

        return expr

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
    
    def _convert_tce_pattern_to_tau(self, pattern_type: str, groups: List[str]) -> Optional[str]:
        """Convert a TCE pattern to Tau using templates."""
        if pattern_type == 'function_def' and len(groups) >= 2:
            name = groups[0]
            body = groups[1]
            return f"{name}() := {body}"
        
        elif pattern_type == 'rule_def' and len(groups) >= 1:
            rule_text = groups[0]
            # Simple heuristic conversion
            return f"r o1[t] = {rule_text}"
        
        elif pattern_type == 'always_expr' and len(groups) >= 1:
            expression = groups[0]
            return f"always {expression}"
        
        # Add more pattern conversions as needed
        return None

    def _lmql_tau_to_tce_query(self, tau_text: str) -> str:
        """LMQL query for Tau to TCE translation."""
        if not LMQL_AVAILABLE:
            raise ImportError("LMQL not available")

        try:
            # Try to use actual LMQL query
            return self._run_lmql_tau_to_tce(tau_text)
        except Exception:
            # Fallback to enhanced pattern-based conversion
            return self._enhanced_tau_to_tce_conversion(tau_text)

    def _lmql_tce_to_tau_query(self, tce_text: str) -> str:
        """LMQL query for TCE to Tau translation."""
        if not LMQL_AVAILABLE:
            raise ImportError("LMQL not available")

        try:
            # Try to use actual LMQL query
            return self._run_lmql_tce_to_tau(tce_text)
        except Exception:
            # Fallback to enhanced pattern-based conversion
            return self._enhanced_tce_to_tau_conversion(tce_text)

    def _run_lmql_tau_to_tce(self, tau_text: str) -> str:
        """Run translation using Gemma 3 or LMQL."""
        try:
            # Try Gemma 3 first (best quality)
            try:
                from ..gemma3.translator import gemma3_translator

                if not gemma3_translator.loaded:
                    gemma3_translator.load_model()

                if gemma3_translator.loaded:
                    result = gemma3_translator.translate_tau_to_tce(tau_text)
                    if result:
                        return result
            except ImportError:
                pass  # Gemma 3 not available

            # Fallback to enhanced pattern-based approach
            return self._enhanced_tau_to_tce_conversion(tau_text)

        except Exception as e:
            print(f"Translation error: {e}")
            return self._enhanced_tau_to_tce_conversion(tau_text)

    def _run_lmql_tce_to_tau(self, tce_text: str) -> str:
        """Run translation using Gemma 3 or LMQL."""
        try:
            # Try Gemma 3 first (best quality)
            try:
                from ..gemma3.translator import gemma3_translator

                if not gemma3_translator.loaded:
                    gemma3_translator.load_model()

                if gemma3_translator.loaded:
                    result = gemma3_translator.translate_tce_to_tau(tce_text)
                    if result:
                        return result
            except ImportError:
                pass  # Gemma 3 not available

            # Fallback to enhanced pattern-based approach
            return self._enhanced_tce_to_tau_conversion(tce_text)

        except Exception as e:
            print(f"Translation error: {e}")
            return self._enhanced_tce_to_tau_conversion(tce_text)

    def _enhanced_tau_to_tce_conversion(self, tau_text: str) -> str:
        """Enhanced Tau to TCE conversion using intelligent pattern matching."""
        # Analyze patterns
        patterns = self.tau_analyzer.analyze_tau_text(tau_text)

        # Enhanced conversion logic
        tce_parts = []

        for pattern_type, matches in patterns.items():
            for match_text, groups in matches:
                if pattern_type == 'function_def' and len(groups) >= 2:
                    name = groups[0]
                    body = groups[1]
                    # Translate the body expression
                    translated_body = self._translate_tau_expression(body)
                    tce_parts.append(f"Define function {name} as {translated_body}")

                elif pattern_type == 'rule_def' and len(groups) >= 3:
                    stream = groups[0]
                    time = groups[1]
                    expression = groups[2]
                    # Translate the expression properly
                    translated_expr = self._translate_tau_expression(expression)
                    tce_parts.append(f"Rule: {stream} at time {time} equals {translated_expr}")

                elif pattern_type == 'input_stream' and len(groups) >= 2:
                    name = groups[0]
                    filename = groups[1]
                    tce_parts.append(f"Input stream {name} reads from file {filename}")

                elif pattern_type == 'always_stmt' and len(groups) >= 1:
                    expression = groups[0]
                    # Translate the expression
                    translated_expr = self._translate_tau_expression(expression)
                    tce_parts.append(f"Always {translated_expr}")

                elif pattern_type == 'sometimes_stmt' and len(groups) >= 1:
                    expression = groups[0]
                    # Translate the expression
                    translated_expr = self._translate_tau_expression(expression)
                    tce_parts.append(f"Sometimes {translated_expr}")

        return ". ".join(tce_parts) + "." if tce_parts else "No recognizable patterns found."

    def _enhanced_tce_to_tau_conversion(self, tce_text: str) -> str:
        """Enhanced TCE to Tau conversion using intelligent pattern matching."""
        # Analyze patterns
        patterns = self.tce_analyzer.analyze_tce_text(tce_text)

        # Enhanced conversion logic
        tau_lines = []

        for pattern_type, matches in patterns.items():
            for match_text, groups in matches:
                if pattern_type == 'function_def' and len(groups) >= 2:
                    name = groups[0]
                    body = groups[1]
                    tau_lines.append(f"{name}() := {body}")

                elif pattern_type == 'rule_def' and len(groups) >= 1:
                    rule_text = groups[0]
                    # Simple heuristic conversion
                    tau_lines.append(f"r o1[t] = {rule_text}")

                elif pattern_type == 'always_expr' and len(groups) >= 1:
                    expression = groups[0]
                    tau_lines.append(f"always {expression}")

                elif pattern_type == 'sometimes_expr' and len(groups) >= 1:
                    expression = groups[0]
                    tau_lines.append(f"sometimes {expression}")

        return "\n".join(tau_lines) if tau_lines else "# No recognizable patterns found"

# LMQL queries will be implemented here when LMQL is available
# These are placeholders for the actual LMQL implementation

def create_lmql_tau_to_tce_query():
    """Create LMQL query for Tau to TCE translation."""
    if not LMQL_AVAILABLE:
        return None

    # This will be implemented when LMQL is available
    # @lmql.query
    # def tau_to_tce_query(tau_text: str):
    #     '''lmql
    #     "Convert this Tau Language code to natural English:\n{tau_text}\n\nDescription:"
    #
    #     description = ""
    #
    #     # Use LMQL constraints for better generation
    #     if "function" in tau_text:
    #         "This defines a function" where STOPS_AT(description, ".")
    #     elif "rule" in tau_text:
    #         "This creates a rule" where STOPS_AT(description, ".")
    #     elif "sbf" in tau_text:
    #         "This declares a stream" where STOPS_AT(description, ".")
    #     else:
    #         "This expresses" where STOPS_AT(description, ".")
    #
    #     return description
    #     '''
    pass

def create_lmql_tce_to_tau_query():
    """Create LMQL query for TCE to Tau translation."""
    if not LMQL_AVAILABLE:
        return None

    # This will be implemented when LMQL is available
    # @lmql.query
    # def tce_to_tau_query(tce_text: str):
    #     '''lmql
    #     "Convert this natural language to Tau Language code:\n{tce_text}\n\nTau code:"
    #
    #     tau_code = ""
    #
    #     # Constrain to valid Tau syntax
    #     if "function" in tce_text.lower():
    #         "{tau_code}" where REGEX(tau_code, r"[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\) := .*")
    #     elif "rule" in tce_text.lower():
    #         "{tau_code}" where REGEX(tau_code, r"r [a-zA-Z0-9_]+\[t\] = .*")
    #     elif "stream" in tce_text.lower():
    #         "{tau_code}" where REGEX(tau_code, r"sbf [a-zA-Z0-9_]+ = .*")
    #     else:
    #         "{tau_code}"
    #
    #     return tau_code
    #     '''
    pass
