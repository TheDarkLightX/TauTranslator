"""
Natural Language to TCE Translator
Copyright: DarkLightX/Dana Edwards

Converts plain English to TCE (Tau Controlled English) using TDD approach.
"""

from typing import Dict, List, Tuple, Optional
import re


class NaturalLanguageToTCETranslator:
    """Translates natural language to TCE following craftsmanship principles."""
    
    def __init__(self):
        self._initialize_patterns()
        self._initialize_mappings()
    
    def translate_to_tce(self, text: str) -> str:
        """Main translation method: Natural Language → TCE."""
        normalized = self._normalize_input(text)
        converted = self._apply_conversions(normalized)
        formatted = self._format_as_tce(converted)
        return formatted
    
    def _initialize_patterns(self) -> None:
        """Initialize regex patterns for parsing."""
        self._patterns = {
            'for_all': re.compile(r'for (?:all|every) (\w+)(?:,|\s+)(.+)'),
            'exists': re.compile(r'(?:there )?exists? (\w+) such that (.+)'),
            'if_then': re.compile(r'if (.+?) then (.+)'),
            'comparison': re.compile(r'(\w+) is (greater than|less than|at least|at most|equal to) (.+)'),
            'temporal': re.compile(r'(always|sometimes|eventually) (.+)'),
            'must_have': re.compile(r'all (\w+) must have (.+)'),
        }
    
    def _initialize_mappings(self) -> None:
        """Initialize word/phrase mappings."""
        self._word_mappings = {
            # Comparisons
            'equals': '=',
            'is equal to': '=',
            'is greater than': '>',
            'is less than': '<',
            'is at least': '>=',
            'is at most': '<=',
            'greater than': '>',
            'less than': '<',
            'at least': '>=',
            'at most': '<=',
            
            # Mathematical
            'plus': '+',
            'minus': '-',
            'times': '*',
            'divided by': '/',
            
            # Boolean
            'and': 'and',
            'or': 'or',
            'not': 'not',
            
            # Quantifiers
            'for every': 'for all',
            'must have': 'have',
            
            # Stream processing
            'rule': 'rule',
            'result': 'rule',  # "result o1 at time t" -> "rule o1 at time t"
            
            # XOR and advanced operators
            'xor': 'xor',
            'implies': 'implies',
            'if and only if': 'if and only if',
            
            # Function definitions
            'is defined as': '= defined as',
            'complement': 'complement',
        }
    
    def _normalize_input(self, text: str) -> str:
        """Normalize input text."""
        normalized = text.strip()
        # Remove trailing punctuation for processing
        if normalized.endswith('.'):
            normalized = normalized[:-1]
        return normalized
    
    def _apply_conversions(self, text: str) -> str:
        """Apply pattern-based conversions."""
        # Handle quantifiers first
        text = self._convert_quantifiers(text)
        
        # Handle conditionals
        text = self._convert_conditionals(text)
        
        # Handle temporal operators
        text = self._convert_temporal(text)
        
        # Handle comparisons
        text = self._convert_comparisons(text)
        
        # Apply word mappings
        text = self._apply_word_mappings(text)
        
        return text
    
    def _convert_quantifiers(self, text: str) -> str:
        """Convert quantifier expressions."""
        # Handle "all X must have Y" pattern
        must_have_match = self._patterns['must_have'].match(text)
        if must_have_match:
            subject = must_have_match.group(1)
            property = must_have_match.group(2)
            return f"for all {subject}, {subject} have {property}"
        
        # Handle "for all/every X, Y" pattern
        for_all_match = self._patterns['for_all'].match(text)
        if for_all_match:
            variable = for_all_match.group(1)
            predicate = for_all_match.group(2).strip()
            return f"for all {variable}, {predicate}"
        
        # Handle "exists X such that Y" pattern
        exists_match = self._patterns['exists'].match(text)
        if exists_match:
            variable = exists_match.group(1)
            condition = exists_match.group(2)
            return f"exists {variable} such that {condition}"
        
        return text
    
    def _convert_conditionals(self, text: str) -> str:
        """Convert conditional expressions."""
        if_then_match = self._patterns['if_then'].match(text)
        if if_then_match:
            condition = if_then_match.group(1)
            consequence = if_then_match.group(2)
            
            # Process condition and consequence
            condition = self._process_clause(condition)
            consequence = self._process_clause(consequence)
            
            return f"if {condition} then {consequence}"
        
        return text
    
    def _convert_temporal(self, text: str) -> str:
        """Convert temporal expressions."""
        temporal_match = self._patterns['temporal'].match(text)
        if temporal_match:
            operator = temporal_match.group(1)
            predicate = temporal_match.group(2)
            return f"{operator} {predicate}"
        
        return text
    
    def _convert_comparisons(self, text: str) -> str:
        """Convert comparison expressions."""
        # Look for comparison patterns
        comparison_match = self._patterns['comparison'].search(text)
        if comparison_match:
            subject = comparison_match.group(1)
            comparison = comparison_match.group(2)
            value = comparison_match.group(3)
            
            # Map comparison to operator
            op = self._word_mappings.get(comparison, comparison)
            
            # Replace in text
            old_text = comparison_match.group(0)
            new_text = f"{subject} {op} {value}"
            text = text.replace(old_text, new_text)
        
        return text
    
    def _process_clause(self, clause: str) -> str:
        """Process a clause (condition or consequence)."""
        # Handle assignments with "is"
        if " is " in clause:
            parts = clause.split(" is ", 1)
            if len(parts) == 2:
                subject = parts[0].strip()
                value = parts[1].strip()
                
                # Check if value is a comparison
                for comp_word, comp_op in [
                    ('greater than', '>'),
                    ('less than', '<'),
                    ('at least', '>='),
                    ('at most', '<='),
                ]:
                    if value.startswith(comp_word):
                        rest = value[len(comp_word):].strip()
                        return f"{subject} {comp_op} {rest}"
                
                # Otherwise it's an assignment
                return f"{subject} = {value}"
        
        return clause
    
    def _apply_word_mappings(self, text: str) -> str:
        """Apply simple word/phrase replacements."""
        result = text
        
        # Apply mappings in order (longer phrases first)
        sorted_mappings = sorted(
            self._word_mappings.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        for old, new in sorted_mappings:
            # Use word boundaries for single words
            if ' ' not in old:
                pattern = r'\b' + re.escape(old) + r'\b'
                result = re.sub(pattern, new, result)
            else:
                result = result.replace(old, new)
        
        # Handle "is" separately with context awareness
        result = self._convert_is_contextually(result)
        
        return result
    
    def _convert_is_contextually(self, text: str) -> str:
        """Convert 'is' to '=' only in assignment contexts."""
        # Don't convert "is" when it's part of a predicate or property
        # Pattern: X is Y where Y is a number or simple value
        pattern = r'\b(\w+)\s+is\s+(\d+|\w+)\b'
        
        def replace_is(match):
            subject = match.group(1)
            value = match.group(2)
            # Check if value looks like a number or simple assignment
            if value.isdigit() or value in ['true', 'false', 'on', 'off', 'yes', 'no']:
                return f"{subject} = {value}"
            # Check if it's not a predicate word
            elif value not in ['prime', 'even', 'odd', 'positive', 'negative', 'valid', 'invalid', 
                               'secure', 'open', 'closed', 'active', 'inactive', 'ready', 'busy']:
                return f"{subject} = {value}"
            else:
                return match.group(0)  # Keep original
        
        return re.sub(pattern, replace_is, text)
    
    def _format_as_tce(self, text: str) -> str:
        """Format text as proper TCE."""
        # The TCE grammar does not use sentence-terminating periods.
        # This was a source of parsing errors.
        # We also strip any lingering whitespace.
        return text.strip()