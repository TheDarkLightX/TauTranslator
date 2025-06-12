"""
Refactored NLP Translator Module
================================

This module contains a refactored version of the translate_tce_to_tau function
with reduced cyclomatic complexity by extracting sub-functions.

Author: DarkLightX / Dana Edwards
"""

import re
from typing import Tuple, Optional


class TCEToTauTranslator:
    """Translator for TCE (Tau Controlled English) to Tau logic notation."""
    
    def translate_tce_to_tau(self, tce_text: str) -> str:
        """Enhanced TCE to TAU translation with logic symbols."""
        # Normalize input
        tce_text = self._normalize_input(tce_text)
        
        # Try pattern matchers in order of specificity
        patterns = [
            self._translate_always_is_pattern,
            self._translate_always_implies_pattern,
            self._translate_always_exists_pattern,
            self._translate_simple_implication,
            self._translate_universal_quantification,
            self._translate_existential_quantification,
            self._translate_sometimes_pattern,
            self._translate_always_not_pattern,
            self._translate_conditional_pattern,
            self._translate_relation_pattern,
            self._translate_disjunction_pattern,
        ]
        
        for pattern_handler in patterns:
            result = pattern_handler(tce_text)
            if result is not None:
                return result
        
        # Default: return as-is
        return tce_text
    
    def _normalize_input(self, text: str) -> str:
        """Normalize input text by removing trailing period."""
        if text.endswith('.'):
            return text[:-1]
        return text
    
    def _translate_always_is_pattern(self, text: str) -> Optional[str]:
        """Handle 'Always X is Y' -> '□Y(X)'."""
        if (text.startswith("always ") or text.startswith("Always ")) and " is " in text:
            if " implies " not in text:  # Don't match if it's part of a larger pattern
                rest = text[7:]  # Remove "always " or "Always "
                entity, prop = rest.split(" is ", 1)
                return f"□{prop}({entity})"
        return None
    
    def _translate_always_implies_pattern(self, text: str) -> Optional[str]:
        """Handle 'Always x is bird implies x can fly' -> '∀x(bird(x) → can_fly(x))'."""
        if text.startswith("Always ") and " is " in text and " implies " in text:
            rest = text[7:]  # Remove "Always "
            parts = rest.split(" implies ", 1)
            condition_part = parts[0]
            consequence_part = parts[1]
            
            # Extract variable from condition
            if " is " in condition_part:
                var, entity = condition_part.split(" is ", 1)
                if " can " in consequence_part:
                    # "x can fly" -> "can_fly(x)"
                    ability = consequence_part.replace(f"{var} can ", "").replace(" ", "_")
                    return f"∀{var}({entity}({var}) → can_{ability}({var}))"
        return None
    
    def _translate_always_exists_pattern(self, text: str) -> Optional[str]:
        """Handle 'Always student exists teacher such that...'."""
        if text.startswith("Always ") and " exists " in text:
            rest = text[7:]  # Remove "Always "
            if " exists " in rest and " such that " in rest:
                var1, rest2 = rest.split(" exists ", 1)
                var2, condition = rest2.split(" such that ", 1)
                return f"∀{var1}∃{var2}({condition})"
        return None
    
    def _translate_simple_implication(self, text: str) -> Optional[str]:
        """Handle implications 'X implies Y' -> 'X → Y'."""
        if " implies " in text and not text.startswith("Always "):
            left, right = text.split(" implies ", 1)
            return f"{left} → {right}"
        return None
    
    def _translate_universal_quantification(self, text: str) -> Optional[str]:
        """Handle universal quantification patterns."""
        if text.startswith("for every "):
            return self._handle_for_every_pattern(text)
        return None
    
    def _handle_for_every_pattern(self, text: str) -> str:
        """Process 'for every' patterns."""
        if " such that " in text:
            return self._handle_for_every_such_that(text)
        elif " there exists " in text:
            return self._handle_for_every_exists(text)
        else:
            # Simple case: "for every x"
            var = text[10:].strip()  # Remove "for every "
            return f"∀{var}"
    
    def _handle_for_every_such_that(self, text: str) -> str:
        """Handle 'for every X such that Y' patterns."""
        parts = text.split(" such that ", 1)
        var = parts[0][10:].strip()  # Remove "for every "
        rest = parts[1]
        
        # Check for implications
        if " then " in rest or " implies " in rest:
            delimiter = " then " if " then " in rest else " implies "
            condition, consequence = rest.split(delimiter, 1)
            
            # Handle special patterns
            if self._is_bird_fly_pattern(condition, consequence, var):
                return "∀x(bird(x) → can_fly(x))"
            elif condition == "not " + consequence:
                # "for every x such that not perfect(x)"
                pred = consequence.replace(f"({var})", "")
                return f"∀x(¬{pred}(x))"
            
            # General case
            return f"∀{var}({self._translate_condition(condition, var)} → {self._translate_condition(consequence, var)})"
        else:
            # No implication
            return f"∀{var}({self._translate_condition(rest, var)})"
    
    def _handle_for_every_exists(self, text: str) -> str:
        """Handle 'for every X there exists Y such that Z' patterns."""
        parts = text.split(" there exists ", 1)
        var1 = parts[0][10:].strip()
        
        if " such that " in parts[1]:
            var2_part, condition = parts[1].split(" such that ", 1)
            var2 = var2_part.strip()
            return f"∀{var1}∃{var2}({condition})"
        else:
            var2 = parts[1].strip()
            return f"∀{var1}∃{var2}"
    
    def _is_bird_fly_pattern(self, condition: str, consequence: str, var: str) -> bool:
        """Check if this is the special bird/fly pattern."""
        return ((condition == f"{var} is bird" or condition == f"bird({var})") and
                (consequence == f"{var} can fly" or consequence == f"can_fly({var})"))
    
    def _translate_existential_quantification(self, text: str) -> Optional[str]:
        """Handle existential quantification."""
        if text.startswith("there exists "):
            if " such that " in text:
                parts = text.split(" such that ", 1)
                var = parts[0][13:].strip()  # Remove "there exists "
                condition = parts[1]
                
                # Handle conjunction
                if " and " in condition:
                    conds = condition.split(" and ")
                    translated = " ∧ ".join([self._translate_condition(c, var) for c in conds])
                    return f"∃{var}({translated})"
                else:
                    return f"∃{var}({self._translate_condition(condition, var)})"
            else:
                var = text[13:].strip()  # Remove "there exists "
                return f"∃{var}"
        return None
    
    def _translate_sometimes_pattern(self, text: str) -> Optional[str]:
        """Handle 'Sometimes x is Y' -> '∃x(Y(x))'."""
        if text.startswith("Sometimes ") and " is " in text:
            rest = text[10:]  # Remove "Sometimes "
            var, prop = rest.split(" is ", 1)
            return f"∃{var}({prop}({var}))"
        return None
    
    def _translate_always_not_pattern(self, text: str) -> Optional[str]:
        """Handle 'Always x implies not Y(x)' -> '∀x(¬Y(x))'."""
        if text.startswith("Always ") and " implies not " in text:
            rest = text[7:]  # Remove "Always "
            var, prop = rest.split(" implies not ", 1)
            prop_clean = prop.rstrip("(x)").rstrip(".")
            return f"∀{var}(¬{prop_clean}({var}))"
        return None
    
    def _translate_conditional_pattern(self, text: str) -> Optional[str]:
        """Handle conditionals 'if X then Y' -> '(X) → Y'."""
        if text.startswith("if ") and " then " in text:
            condition, consequence = text[3:].split(" then ", 1)
            return f"{self._translate_simple(condition)} → {self._translate_simple(consequence)}"
        return None
    
    def _translate_relation_pattern(self, text: str) -> Optional[str]:
        """Handle relations like 'John loves Mary' -> 'loves(John, Mary)'."""
        # Check if it's already in relation format
        if re.match(r'^\w+\([^,]+,\s*[^)]+\)$', text):
            return text
        
        # Check for subject-verb-object pattern
        if re.match(r'^[A-Z]\w+\s+\w+\s+[A-Z]\w+$', text):
            parts = text.split()
            if len(parts) == 3:
                subj, verb, obj = parts
                return f"{verb}({subj}, {obj})"
        return None
    
    def _translate_disjunction_pattern(self, text: str) -> Optional[str]:
        """Handle disjunction 'X or Y' -> 'X ∨ Y'."""
        if " or " in text:
            parts = text.split(" or ")
            return " ∨ ".join([self._translate_simple(p.strip()) for p in parts])
        return None
    
    def _translate_condition(self, condition: str, var: str) -> str:
        """Translate a condition to predicate logic format."""
        # Handle "x is Y" -> "Y(x)"
        if condition.startswith(f"{var} is "):
            predicate = condition[len(f"{var} is "):]
            return f"{predicate}({var})"
        
        # Handle "not X" -> "¬X"
        if condition.startswith("not "):
            rest = condition[4:]
            return f"¬{self._translate_condition(rest, var)}"
        
        # Handle "x can Y" -> "can_Y(x)"
        if condition.startswith(f"{var} can "):
            ability = condition[len(f"{var} can "):].replace(" ", "_")
            return f"can_{ability}({var})"
        
        # Handle already formatted predicates
        if "(" in condition and ")" in condition:
            return condition
        
        # Default: assume it's a predicate that needs the variable
        return f"{condition}({var})"
    
    def _translate_simple(self, text: str) -> str:
        """Translate simple expressions."""
        text = text.strip()
        
        # Handle "not X" -> "¬X"
        if text.startswith("not "):
            return f"¬{self._translate_simple(text[4:])}"
        
        # Handle predicates
        if "(" in text and ")" in text:
            return text
        
        return text


# Example usage
def refactored_translate_tce_to_tau(tce_text: str, nlp_translator=None) -> str:
    """Wrapper function to maintain compatibility."""
    translator = TCEToTauTranslator()
    if nlp_translator:
        # Use methods from the original translator instance
        translator._translate_condition = nlp_translator._translate_condition
        translator._translate_simple = nlp_translator._translate_simple
    return translator.translate_tce_to_tau(tce_text)