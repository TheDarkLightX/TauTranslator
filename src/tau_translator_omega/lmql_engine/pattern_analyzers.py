"""
Pattern Analyzers for Tau ↔ TCE Translation
==========================================

Extracted from bidirectional_translator.py to maintain <600 line limit.
Implements pattern recognition for both Tau and TCE languages.

Author: DarkLightX / Dana Edwards
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PatternAnalyzer(ABC):
    """Abstract base class for pattern analyzers following Strategy pattern."""
    
    @abstractmethod
    def analyze_text(self, text: str) -> Dict[str, List[Tuple[str, List[str]]]]:
        """Analyze text and extract patterns."""
        pass


class TauPatternAnalyzer(PatternAnalyzer):
    """
    Analyzes Tau Language text patterns without using IDNI parser.
    Uses regex and heuristics for pattern recognition.
    
    Follows VibeArchitect principles:
    - Single Responsibility: Only Tau pattern analysis
    - Immutable patterns dictionary
    - Clear error handling
    """
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize Tau language patterns with validation."""
        patterns = {
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
        
        # Validate patterns at initialization
        self._validate_patterns(patterns)
        return patterns
    
    def _validate_patterns(self, patterns: Dict[str, str]) -> None:
        """Validate regex patterns for syntax errors."""
        for name, pattern in patterns.items():
            try:
                re.compile(pattern)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{name}': {pattern} - {e}")
                raise ValueError(f"Invalid regex pattern '{name}': {e}")
    
    @property
    def patterns(self) -> Dict[str, str]:
        """Read-only access to patterns."""
        return self._patterns.copy()
    
    def analyze_text(self, tau_text: str) -> Dict[str, List[Tuple[str, List[str]]]]:
        """
        Analyze Tau text and extract patterns.
        
        Args:
            tau_text: Raw Tau language text
            
        Returns:
            Dictionary mapping pattern types to list of (match, groups) tuples
            
        Raises:
            ValueError: If tau_text is None or empty
        """
        if not tau_text or not tau_text.strip():
            raise ValueError("tau_text cannot be None or empty")
        
        results = {}
        
        # Split into lines for analysis
        lines = [line.strip() for line in tau_text.split('\n') if line.strip()]
        
        for pattern_name, pattern_regex in self._patterns.items():
            matches = []
            
            for line in lines:
                try:
                    match = re.search(pattern_regex, line)
                    if match:
                        matches.append((match.group(0), list(match.groups())))
                except re.error as e:
                    logger.warning(f"Pattern matching error for {pattern_name}: {e}")
                    continue
            
            if matches:
                results[pattern_name] = matches
        
        return results

    def analyze_tau_text(self, tau_text: str) -> Dict[str, List[Tuple[str, List[str]]]]:
        """Legacy method name for backward compatibility."""
        return self.analyze_text(tau_text)


class TCEPatternAnalyzer(PatternAnalyzer):
    """
    Analyzes TCE (Tau Controlled English) patterns.
    
    Follows VibeArchitect principles:
    - Single Responsibility: Only TCE pattern analysis
    - Clear pattern priority ordering
    - Comprehensive error handling
    """
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
        self._pattern_priority = self._initialize_priority()
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize TCE patterns with validation."""
        patterns = {
            # Function definitions
            'function_def': r'define\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+.*as\s+(.+)',
            
            # Rules
            'rule_def': r'rule:?\s*(.+)',
            
            # Stream declarations
            'input_stream': r'input\s+stream\s+([a-zA-Z0-9_]+).*from\s+(.+)',
            'output_stream': r'output\s+stream\s+([a-zA-Z0-9_]+).*to\s+(.+)',
            
            # Constraint expressions (more specific patterns first)
            'always_greater_than': r'(.+)\s+is\s+always\s+greater\s+than\s+(.+)',
            'always_less_than': r'(.+)\s+is\s+always\s+less\s+than\s+(.+)', 
            'always_equals': r'(.+)\s+is\s+always\s+equals?\s+(.+)',
            'sometimes_greater_than': r'(.+)\s+is\s+sometimes\s+greater\s+than\s+(.+)',
            'sometimes_less_than': r'(.+)\s+is\s+sometimes\s+less\s+than\s+(.+)',
            'sometimes_equals': r'(.+)\s+is\s+sometimes\s+equals?\s+(.+)',
            'greater_than': r'(.+)\s+(?:is\s+)?greater\s+than\s+(.+)',
            'less_than': r'(.+)\s+(?:is\s+)?less\s+than\s+(.+)',
            'equals_constraint': r'(.+)\s+(?:is\s+)?equals?\s+(.+)',
            
            # Temporal expressions (more general)
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
            
            # Solver commands
            'find_single_value': r'find\s+a\s+value\s+for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+such\s+that\s+(.+)',
            'find_multiple_values': r'find\s+values\s+for\s+(.+?)\s+such\s+that\s+(.+)',
            'check_satisfiable': r'check\s+if\s+(.+)\s+is\s+satisfiable',
            'normalize_expr': r'normalize\s+(?:the\s+)?expression\s+(.+)',
            'eliminate_quantifiers': r'eliminate\s+quantifiers\s+from\s+(.+)',
        }
        
        # Validate patterns
        self._validate_patterns(patterns)
        return patterns
    
    def _initialize_priority(self) -> List[str]:
        """Initialize pattern matching priority order."""
        return [
            # Solver commands have high priority
            'find_single_value', 'find_multiple_values',
            'check_satisfiable', 'normalize_expr', 'eliminate_quantifiers',
            # Temporal constraints
            'always_greater_than', 'always_less_than', 'always_equals',
            'sometimes_greater_than', 'sometimes_less_than', 'sometimes_equals',
            # Simple constraints
            'greater_than', 'less_than', 'equals_constraint',
            # Temporal expressions
            'always_expr', 'sometimes_expr',
            # Boolean operations
            'and_expr', 'or_expr', 'not_expr', 'xor_expr',
            # Definitions
            'function_def', 'rule_def'
        ]
    
    def _validate_patterns(self, patterns: Dict[str, str]) -> None:
        """Validate regex patterns for syntax errors."""
        for name, pattern in patterns.items():
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{name}': {pattern} - {e}")
                raise ValueError(f"Invalid regex pattern '{name}': {e}")
    
    @property
    def patterns(self) -> Dict[str, str]:
        """Read-only access to patterns."""
        return self._patterns.copy()
    
    @property
    def pattern_priority(self) -> List[str]:
        """Read-only access to pattern priority."""
        return self._pattern_priority.copy()
    
    def analyze_text(self, tce_text: str) -> Dict[str, List[Tuple[str, List[str]]]]:
        """
        Analyze TCE text and extract patterns.
        
        Args:
            tce_text: Raw TCE text
            
        Returns:
            Dictionary mapping pattern types to list of (match, groups) tuples
            
        Raises:
            ValueError: If tce_text is None or empty
        """
        if not tce_text or not tce_text.strip():
            raise ValueError("tce_text cannot be None or empty")
        
        results = {}
        
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]', tce_text) if s.strip()]
        
        for pattern_name, pattern_regex in self._patterns.items():
            matches = []
            
            for sentence in sentences:
                try:
                    match = re.search(pattern_regex, sentence, re.IGNORECASE)
                    if match:
                        matches.append((match.group(0), list(match.groups())))
                except re.error as e:
                    logger.warning(f"Pattern matching error for {pattern_name}: {e}")
                    continue
            
            if matches:
                results[pattern_name] = matches
        
        return results

    def analyze_tce_text(self, tce_text: str) -> Dict[str, List[Tuple[str, List[str]]]]:
        """Legacy method name for backward compatibility."""
        return self.analyze_text(tce_text)

    def get_best_match(self, tce_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the best pattern match based on priority.
        
        Args:
            tce_text: Raw TCE text
            
        Returns:
            Tuple of (pattern_type, best_match) or (None, None) if no match
        """
        patterns = self.analyze_text(tce_text)
        
        # Try patterns in priority order
        for pattern_type in self._pattern_priority:
            if pattern_type in patterns and patterns[pattern_type]:
                match_text, groups = patterns[pattern_type][0]
                return pattern_type, match_text
        
        # If no priority pattern found, use any available pattern
        for pattern_type, matches in patterns.items():
            if matches:
                match_text, groups = matches[0]
                return pattern_type, match_text
        
        return None, None


class PatternAnalyzerFactory:
    """Factory for creating pattern analyzers following Factory pattern."""
    
    @staticmethod
    def create_tau_analyzer() -> TauPatternAnalyzer:
        """Create a Tau pattern analyzer."""
        return TauPatternAnalyzer()
    
    @staticmethod
    def create_tce_analyzer() -> TCEPatternAnalyzer:
        """Create a TCE pattern analyzer."""
        return TCEPatternAnalyzer()
    
    @staticmethod
    def create_analyzer(analyzer_type: str) -> PatternAnalyzer:
        """
        Create pattern analyzer by type.
        
        Args:
            analyzer_type: 'tau' or 'tce'
            
        Returns:
            Appropriate pattern analyzer
            
        Raises:
            ValueError: If analyzer_type is not supported
        """
        if analyzer_type.lower() == 'tau':
            return TauPatternAnalyzer()
        elif analyzer_type.lower() == 'tce':
            return TCEPatternAnalyzer()
        else:
            raise ValueError(f"Unsupported analyzer type: {analyzer_type}")