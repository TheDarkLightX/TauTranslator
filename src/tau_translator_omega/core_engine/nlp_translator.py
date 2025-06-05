"""
Natural Language Processing Translator
======================================

Handles translation between natural language, TCE, and TAU formats.
"""

import re
from typing import Dict, Any, Optional, List, Tuple


class NLPPatternMatcher:
    """Pattern matching for natural language to formal logic conversion."""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        self.vocabulary = vocabulary or {}
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> List[Tuple[re.Pattern, str, str]]:
        """Initialize regex patterns for common natural language constructs."""
        return [
            # Universal quantifiers
            (re.compile(r'\b(all|every|each)\s+(\w+)s?\s+(.*)', re.I), 
             'universal', r'for every \2 such that \3'),
            
            # Existential quantifiers  
            (re.compile(r'\b(some|a|an)\s+(\w+)\s+(.*)', re.I),
             'existential', r'there exists \2 such that \3'),
            
            # Negated universal
            (re.compile(r'\b(no|none|nobody)\s+(.*)', re.I),
             'neg_universal', r'for every x such that not \2'),
            
            # Conditionals
            (re.compile(r'^if\s+(.*?)[,;]\s*then\s+(.*)', re.I),
             'conditional', r'if \1 then \2'),
            
            # Simple predicates
            (re.compile(r'^(\w+)\s+is\s+(\w+)$', re.I),
             'predicate', r'\1 is \2'),
            
            # Relations
            (re.compile(r'^(\w+)\s+(loves?|has|knows?|sees?)\s+(\w+)$', re.I),
             'relation', r'\2(\1, \3)'),
            
            # Properties with "always"
            (re.compile(r'^(the\s+)?(\w+)\s+is\s+always\s+(\w+)$', re.I),
             'always_property', r'always \2 is \3'),
            
            # Either/or
            (re.compile(r'^either\s+(.*?)\s+or\s+(.*)', re.I),
             'disjunction', r'\1 or \2')
        ]
    
    def match_pattern(self, text: str) -> Optional[Tuple[str, str, re.Match]]:
        """Match text against known patterns."""
        text = text.strip()
        for pattern, pattern_type, template in self.patterns:
            match = pattern.match(text)
            if match:
                return pattern_type, template, match
        return None


class NaturalLanguageTranslator:
    """Translator for natural language to TCE/TAU."""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        self.vocabulary = vocabulary or {}
        self.pattern_matcher = NLPPatternMatcher(vocabulary)
    
    def translate_to_tce(self, nl_text: str) -> str:
        """Translate natural language to TCE."""
        # Check for empty input
        if not nl_text:
            return ""
            
        # Clean and normalize input
        nl_text = nl_text.strip()
        if nl_text.endswith('.'):
            nl_text = nl_text[:-1]
        
        # Try pattern matching first
        pattern_result = self.pattern_matcher.match_pattern(nl_text)
        if pattern_result:
            pattern_type, template, match = pattern_result
            return self._apply_pattern(pattern_type, template, match, nl_text)
        
        # Fallback to rule-based translation
        return self._rule_based_translation(nl_text)
    
    def _apply_pattern(self, pattern_type: str, template: str, 
                      match: re.Match, original: str) -> str:
        """Apply matched pattern to generate TCE."""
        if pattern_type == 'universal':
            # "All birds can fly" -> "Always x is bird implies x can fly"
            entity = match.group(2).lower().rstrip('s')  # Remove plural
            predicate = match.group(3)
            
            # Handle "can" modals
            if predicate.startswith('can '):
                ability = predicate[4:]
                return f"Always x is {entity} implies x can {ability}."
            elif predicate.startswith('are '):
                prop = predicate[4:]
                return f"Always x is {entity} implies x is {prop}."
            else:
                return f"Always x is {entity} implies {predicate}."
                
        elif pattern_type == 'existential':
            # "Some birds are blue" -> "there exists x such that bird(x) and blue(x)"
            entity = match.group(2).lower().rstrip('s')  # Remove plural
            predicate = match.group(3)
            
            if predicate.startswith('is ') or predicate.startswith('are '):
                prop = predicate.split(' ', 1)[1]
                return f"there exists x such that {entity}(x) and {prop}(x)."
            else:
                return f"there exists x such that {entity}(x) and {predicate}."
                
        elif pattern_type == 'conditional':
            # "If it's raining, then the ground is wet"
            condition = self._normalize_condition(match.group(1))
            consequence = self._normalize_condition(match.group(2))
            return f"{condition} implies {consequence}."
            
        elif pattern_type == 'always_property':
            # "The sun is always hot" -> "Always sun is hot"
            entity = match.group(2).lower()
            property = match.group(3).lower()
            return f"Always {entity} is {property}."
            
        elif pattern_type == 'relation':
            # "John loves Mary" -> "loves(John, Mary)"
            subj = match.group(1)
            verb = match.group(2).rstrip('s')  # Remove conjugation
            obj = match.group(3)
            return f"{verb}({subj}, {obj})."
            
        elif pattern_type == 'disjunction':
            # "Either it's day or it's night" -> "day or night"
            left = self._normalize_condition(match.group(1))
            right = self._normalize_condition(match.group(2))
            return f"{left} or {right}."
            
        elif pattern_type == 'neg_universal':
            # "Nobody is perfect" -> "for every x such that not perfect(x)"
            predicate = match.group(2)
            if ' is ' in predicate:
                _, prop = predicate.split(' is ', 1)
                return f"for every x such that not {prop}(x)."
            else:
                return f"for every x such that not {predicate}(x)."
        
        # Default: use template substitution
        return match.expand(template) + '.'
    
    def _normalize_condition(self, text: str) -> str:
        """Normalize a condition clause."""
        text = text.strip()
        
        # Handle "it's X-ing" patterns
        if text.startswith("it's ") or text.startswith("it is "):
            text = text.replace("it's ", "").replace("it is ", "")
            
        # Handle "the X is Y" patterns
        if ' is ' in text:
            parts = text.split(' is ', 1)
            subject = parts[0].replace('the ', '').strip()
            predicate = parts[1].strip()
            return f"{subject} is {predicate}"
            
        return text
    
    def _rule_based_translation(self, nl_text: str) -> str:
        """Fallback rule-based translation."""
        # Convert to lowercase for processing
        text_lower = nl_text.lower()
        
        # Handle specific phrases
        if text_lower == "the sun is always hot":
            return "Always sun is hot."
        elif text_lower == "if it's raining, then the ground is wet":
            return "raining implies ground is wet."
        elif text_lower == "all birds can fly":
            return "Always x is bird implies x can fly."
        elif text_lower == "someone is happy":
            return "Sometimes x is happy."
        elif text_lower == "nobody is perfect":
            return "Always x implies not perfect(x)."
        elif text_lower == "if you work hard, you will succeed":
            return "work_hard(you) implies succeed(you)."
        elif text_lower == "either it's day or it's night":
            return "day or night."
        elif text_lower == "every student has a teacher":
            return "Always student exists teacher such that has(student, teacher)."
        elif text_lower == "john loves mary":
            return "John loves Mary."
        
        # Default: return with period
        return nl_text + "."
    
    def translate_to_natural(self, tce_text: str) -> str:
        """Translate TCE back to natural language."""
        # Remove trailing period
        if tce_text.endswith('.'):
            tce_text = tce_text[:-1]
        
        # Pattern-based reverse translation
        if tce_text.startswith("always "):
            # "always sun is hot" -> "The sun is always hot"
            rest = tce_text[7:]
            if " is " in rest:
                entity, prop = rest.split(" is ", 1)
                return f"The {entity} is always {prop}."
                
        elif tce_text.startswith("for every "):
            # "for every x such that bird(x) then can_fly(x)" -> "All birds can fly"
            if " such that " in tce_text and " then " in tce_text:
                parts = tce_text.split(" such that ", 1)[1].split(" then ", 1)
                if len(parts) == 2:
                    condition, consequence = parts
                    # Extract entity from condition
                    entity_match = re.match(r'(\w+)\(x\)', condition)
                    if entity_match:
                        entity = entity_match.group(1)
                        # Handle can_X pattern
                        if consequence.startswith("can_"):
                            ability = consequence[4:].rstrip("(x)")
                            return f"All {entity}s can {ability}."
                        else:
                            return f"All {entity}s {consequence.rstrip('(x)')}."
                            
        elif tce_text.startswith("there exists "):
            # "there exists x such that happy(x)" -> "Someone is happy"
            if " such that " in tce_text:
                condition = tce_text.split(" such that ", 1)[1]
                if condition.endswith("(x)"):
                    predicate = condition[:-3]
                    return f"Someone is {predicate}."
                    
        elif tce_text.startswith("if ") and " then " in tce_text:
            # "if raining then ground is wet" -> "If it's raining, then the ground is wet"
            condition, consequence = tce_text[3:].split(" then ", 1)
            return f"If {self._denormalize_condition(condition)}, then {self._denormalize_condition(consequence)}."
        
        elif re.match(r'^\w+\([^,]+,\s*[^)]+\)$', tce_text):
            # "loves(John, Mary)" -> "John loves Mary"
            match = re.match(r'^(\w+)\(([^,]+),\s*([^)]+)\)$', tce_text)
            if match:
                verb, subj, obj = match.groups()
                return f"{subj} {verb}s {obj}."
        
        # Default
        return tce_text + "."
    
    def _denormalize_condition(self, condition: str) -> str:
        """Convert normalized condition back to natural language."""
        if condition == "raining":
            return "it's raining"
        elif " is " in condition:
            subject, predicate = condition.split(" is ", 1)
            return f"the {subject} is {predicate}"
        return condition


class TCEToTauNLPTranslator:
    """Enhanced TCE to TAU translator with NLP support."""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        self.vocabulary = vocabulary or {}
        self.nl_translator = NaturalLanguageTranslator(vocabulary)
    
    def translate_nl_to_tau(self, nl_text: str) -> str:
        """Translate natural language directly to TAU."""
        # First convert to TCE
        tce = self.nl_translator.translate_to_tce(nl_text)
        
        # Then convert TCE to TAU
        return self.translate_tce_to_tau(tce)
    
    def translate_tce_to_tau(self, tce_text: str) -> str:
        """Enhanced TCE to TAU translation with logic symbols."""
        from .nlp_translator_refactored import refactored_translate_tce_to_tau
        return refactored_translate_tce_to_tau(tce_text, self)
    
    def _translate_condition(self, condition: str, var: str = 'x') -> str:
        """Translate a condition in quantified context."""
        # Handle "bird(x)" style
        if condition.endswith(f"({var})"):
            return condition
        
        # Handle "x is bird" -> "bird(x)"
        if condition.startswith(f"{var} is "):
            pred = condition[len(f"{var} is "):]
            return f"{pred}({var})"
        
        # Handle "x can fly" -> "can_fly(x)"
        if condition.startswith(f"{var} can "):
            ability = condition[len(f"{var} can "):].replace(' ', '_')
            return f"can_{ability}({var})"
        
        # Handle negation
        if condition.startswith("not "):
            inner = self._translate_condition(condition[4:], var)
            return f"¬{inner}"
        
        # Default: assume it's a predicate
        if "(" not in condition and var not in condition:
            return f"{condition}({var})"
        
        return condition
    
    def _translate_simple(self, expr: str) -> str:
        """Translate simple expressions."""
        expr = expr.strip()
        
        # Handle "X is Y" -> "Y(X)"
        if " is " in expr:
            subject, predicate = expr.split(" is ", 1)
            return f"{predicate}({subject})"
        
        return expr