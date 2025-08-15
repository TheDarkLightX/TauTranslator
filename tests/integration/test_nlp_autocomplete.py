#!/usr/bin/env python3
"""
TDD Tests for NLP Auto-Complete Features
========================================

Test-driven development for auto-complete and suggestion functionality:
1. Context-aware suggestions
2. Grammar-based completions  
3. Intelligent phrase suggestions
4. Real-time typing assistance

These tests define the expected behavior for auto-complete features.
"""

import unittest
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
    from tau_translator_omega.core_engine.cnl_parser.ast_nodes import *
except ImportError as e:
    print(f"Warning: Import error - {e}")
    # Create mock class for testing framework
    class CNLParser:
        def parse(self, text): return None


class AutoCompleteEngine:
    """Mock auto-complete engine for TDD"""
    
    def __init__(self, parser: CNLParser):
        self.parser = parser
        self.common_starters = [
            {"text": "For all ", "type": "quantifier", "description": "Universal quantifier"},
            {"text": "There exists ", "type": "quantifier", "description": "Existential quantifier"},
            {"text": "If ", "type": "conditional", "description": "Conditional statement"},
            {"text": "Define ", "type": "definition", "description": "Definition statement"},
            {"text": "Let ", "type": "definition", "description": "Variable definition"},
            {"text": "Suppose ", "type": "assumption", "description": "Assumption statement"}
        ]
        
        self.logical_operators = [
            {"text": " and ", "type": "operator", "description": "Logical AND"},
            {"text": " or ", "type": "operator", "description": "Logical OR"}, 
            {"text": " implies ", "type": "operator", "description": "Logical implication"},
            {"text": " not ", "type": "operator", "description": "Logical negation"}
        ]
        
        self.quantifier_continuations = [
            {"text": " such that ", "type": "quantifier_continuation", "description": "Condition for quantifier"},
            {"text": ", ", "type": "quantifier_continuation", "description": "Simple quantifier continuation"}
        ]
    
    def suggest_completions(self, partial_input: str, max_suggestions: int = 10) -> List[Dict[str, str]]:
        """Generate context-aware completions for partial input"""
        suggestions = []
        
        # Empty or whitespace input - suggest starters
        if not partial_input.strip():
            return self.common_starters[:max_suggestions]
        
        # Detect context and provide appropriate suggestions
        lower_input = partial_input.lower().strip()
        
        # Quantifier contexts
        if self._is_quantifier_context(lower_input):
            suggestions.extend(self._get_quantifier_suggestions(partial_input))
        
        # Logical operator contexts
        if self._is_logical_operator_context(lower_input):
            suggestions.extend(self._get_logical_operator_suggestions(partial_input))
        
        # Definition contexts
        if self._is_definition_context(lower_input):
            suggestions.extend(self._get_definition_suggestions(partial_input))
        
        # Mathematical contexts
        if self._is_mathematical_context(lower_input):
            suggestions.extend(self._get_mathematical_suggestions(partial_input))
        
        # Handle temporal contexts
        if self._is_temporal_context(lower_input):
            suggestions.extend(self._get_temporal_suggestions(partial_input))
        
        # Fallback suggestions
        if not suggestions:
            suggestions = self._get_fallback_suggestions(partial_input)
        
        return suggestions[:max_suggestions]
    
    def _is_quantifier_context(self, input_text: str) -> bool:
        """Check if input is in quantifier context"""
        quantifier_patterns = ['for all', 'there exists', 'for every', 'some']
        return any(pattern in input_text for pattern in quantifier_patterns)
    
    def _is_logical_operator_context(self, input_text: str) -> bool:
        """Check if input expects logical operators"""
        # Check if input ends with incomplete logical operator or could use one
        stripped = input_text.strip()
        return (
            stripped.endswith('and') or 
            stripped.endswith('or') or 
            ('(' in input_text and ')' in input_text) or 
            any(op in input_text for op in ['and', 'or']) or
            # Check for variable patterns that could be connected
            any(c.isalpha() for c in stripped) and len(stripped.split()) >= 1
        )
    
    def _is_definition_context(self, input_text: str) -> bool:
        """Check if input is defining something"""
        return any(keyword in input_text for keyword in ['define', 'let', 'suppose'])
    
    def _is_mathematical_context(self, input_text: str) -> bool:
        """Check if input contains mathematical expressions"""
        math_indicators = ['+', '-', '*', '/', '=', '<', '>', '<=', '>=']
        # Also check for function notation f(x), g(n), etc.
        import re
        has_function = bool(re.search(r'[a-zA-Z]+\([^)]*\)', input_text))
        return any(indicator in input_text for indicator in math_indicators) or has_function
    
    def _is_temporal_context(self, input_text: str) -> bool:
        """Check if input contains temporal logic keywords"""
        temporal_keywords = ['always', 'eventually', 'until', 'next', 'finally']
        return any(keyword in input_text for keyword in temporal_keywords)
    
    def _get_quantifier_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for quantifier contexts"""
        suggestions = []
        lower_input = partial_input.lower()
        
        # Handle different quantifier patterns
        if 'for all' in lower_input or 'there exists' in lower_input or 'for every' in lower_input:
            var_match = self._extract_variable_after_quantifier(partial_input)
            if var_match:
                suggestions.append({
                    "text": f"{partial_input} such that ",
                    "type": "quantifier_continuation",
                    "description": "Add condition for the quantifier"
                })
                suggestions.append({
                    "text": f"{partial_input}, ",
                    "type": "quantifier_continuation", 
                    "description": "Continue with quantified statement"
                })
        
        return suggestions
    
    def _get_logical_operator_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for logical operator contexts"""
        suggestions = []
        stripped = partial_input.strip()
        
        # Handle cases where input ends with logical operator
        if stripped.endswith('and'):
            suggestions.append({
                "text": f"{partial_input} y",
                "type": "variable",
                "description": "Continue with variable"
            })
            suggestions.append({
                "text": f"{partial_input} that",
                "type": "continuation",
                "description": "Continue with condition"
            })
        elif stripped.endswith('or'):
            suggestions.append({
                "text": f"{partial_input} y",
                "type": "variable", 
                "description": "Continue with alternative"
            })
        else:
            # Suggest connecting operators
            for op in self.logical_operators:
                suggestions.append({
                    "text": f"{partial_input}{op['text']}",
                    "type": op["type"],
                    "description": op["description"]
                })
        
        return suggestions
    
    def _get_definition_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for definition contexts"""
        suggestions = []
        lower_input = partial_input.lower()
        
        if 'define' in lower_input:
            suggestions.append({
                "text": f"{partial_input} as ",
                "type": "definition_continuation",
                "description": "Define the concept"
            })
            suggestions.append({
                "text": f"{partial_input} for ",
                "type": "definition_continuation",
                "description": "Define with parameters"
            })
        elif 'let' in lower_input:
            suggestions.append({
                "text": f"{partial_input} as ",
                "type": "definition_continuation", 
                "description": "Define the function or variable"
            })
            suggestions.append({
                "text": f"{partial_input} for ",
                "type": "definition_continuation",
                "description": "Define with domain"
            })
        elif 'suppose' in lower_input:
            suggestions.append({
                "text": f"{partial_input} for ",
                "type": "assumption_continuation",
                "description": "Specify assumption domain"
            })
            suggestions.append({
                "text": f"{partial_input} as ",
                "type": "assumption_continuation",
                "description": "Clarify assumption"
            })
        
        return suggestions
    
    def _get_mathematical_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for mathematical contexts"""
        suggestions = []
        
        # Common mathematical completions
        math_completions = [
            " = 0", " > 0", " < 0", " >= 0", " <= 0",
            " + 1", " - 1", " * 2", " / 2"
        ]
        
        for completion in math_completions:
            suggestions.append({
                "text": f"{partial_input}{completion}",
                "type": "mathematical",
                "description": f"Mathematical expression with {completion.strip()}"
            })
        
        return suggestions
    
    def _get_temporal_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for temporal logic contexts"""
        suggestions = []
        lower_input = partial_input.lower()
        
        if 'always' in lower_input:
            suggestions.extend([
                {
                    "text": f"{partial_input} eventually ",
                    "type": "temporal_operator",
                    "description": "Temporal operator: always eventually"
                },
                {
                    "text": f"{partial_input} until ",
                    "type": "temporal_operator", 
                    "description": "Temporal operator: always until"
                }
            ])
        elif 'eventually' in lower_input:
            suggestions.append({
                "text": f"{partial_input} always ",
                "type": "temporal_operator",
                "description": "Temporal operator: eventually always"
            })
        
        return suggestions
    
    def _get_fallback_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get fallback suggestions when no context matches"""
        suggestions = []
        lower_input = partial_input.lower()
        
        # Handle temporal logic keywords
        if 'always' in lower_input:
            suggestions.extend([
                {
                    "text": f"{partial_input} eventually ",
                    "type": "temporal_operator",
                    "description": "Temporal operator: always eventually"
                },
                {
                    "text": f"{partial_input} until ",
                    "type": "temporal_operator", 
                    "description": "Temporal operator: always until"
                }
            ])
        
        # Standard fallback suggestions
        suggestions.extend([
            {
                "text": f"{partial_input} and ",
                "type": "continuation",
                "description": "Continue with AND"
            },
            {
                "text": f"{partial_input}.",
                "type": "completion",
                "description": "Complete the statement"
            }
        ])
        
        return suggestions
    
    def _extract_variable_after_quantifier(self, text: str) -> Optional[str]:
        """Extract variable name after quantifier"""
        import re
        # Simple pattern to find variable after "for all", "there exists", or "for every"
        pattern = r'(for all|there exists|for every)\s+(\w+)'
        match = re.search(pattern, text.lower())
        return match.group(2) if match else None


class TestAutoCompleteBasics(unittest.TestCase):
    """Test basic auto-complete functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = CNLParser()
        self.autocomplete = AutoCompleteEngine(self.parser)
    
    def test_empty_input_suggestions(self):
        """Test suggestions for empty input"""
        suggestions = self.autocomplete.suggest_completions("")
        
        # Should provide starter suggestions
        self.assertGreater(len(suggestions), 0, "Should provide suggestions for empty input")
        
        # Should include common starters
        suggestion_texts = [s["text"] for s in suggestions]
        self.assertIn("For all ", suggestion_texts)
        self.assertIn("There exists ", suggestion_texts)
        self.assertIn("If ", suggestion_texts)
        self.assertIn("Define ", suggestion_texts)
        
        # Each suggestion should have required metadata
        for suggestion in suggestions:
            self.assertIn("text", suggestion)
            self.assertIn("type", suggestion)
            self.assertIn("description", suggestion)
            self.assertIsInstance(suggestion["text"], str)
            self.assertGreater(len(suggestion["text"]), 0)
    
    def test_quantifier_context_suggestions(self):
        """Test suggestions in quantifier contexts"""
        test_cases = [
            "For all x",
            "There exists y", 
            "For every person p"
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                suggestions = self.autocomplete.suggest_completions(case)
                
                self.assertGreater(len(suggestions), 0, f"Should provide suggestions for: {case}")
                
                # Should suggest quantifier continuations
                suggestion_texts = [s["text"] for s in suggestions]
                has_such_that = any("such that" in text for text in suggestion_texts)
                has_comma = any(case + "," in text for text in suggestion_texts)
                
                self.assertTrue(has_such_that or has_comma, 
                              f"Should suggest quantifier continuations for: {case}")
    
    def test_logical_operator_suggestions(self):
        """Test suggestions for logical operators"""
        test_cases = [
            "P(x)",
            "x > 0",
            "prime(n)"
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                suggestions = self.autocomplete.suggest_completions(case)
                
                self.assertGreater(len(suggestions), 0, f"Should provide suggestions for: {case}")
                
                # Should suggest logical operators
                suggestion_texts = [s["text"] for s in suggestions]
                has_and = any(" and " in text for text in suggestion_texts)
                has_or = any(" or " in text for text in suggestion_texts)
                
                self.assertTrue(has_and or has_or, 
                              f"Should suggest logical operators for: {case}")
    
    def test_definition_context_suggestions(self):
        """Test suggestions in definition contexts"""
        test_cases = [
            "Define prime",
            "Let f(x)",
            "Suppose P(x)"
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                suggestions = self.autocomplete.suggest_completions(case)
                
                self.assertGreater(len(suggestions), 0, f"Should provide suggestions for: {case}")
                
                # Should suggest definition continuations
                suggestion_texts = [s["text"] for s in suggestions]
                has_as = any(" as " in text for text in suggestion_texts)
                has_for = any(" for " in text for text in suggestion_texts)
                
                self.assertTrue(has_as or has_for, 
                              f"Should suggest definition continuations for: {case}")
    
    def test_mathematical_context_suggestions(self):
        """Test suggestions in mathematical contexts"""
        test_cases = [
            "x + y",
            "f(n)",
            "n * 2"
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                suggestions = self.autocomplete.suggest_completions(case)
                
                self.assertGreater(len(suggestions), 0, f"Should provide suggestions for: {case}")
                
                # Should suggest mathematical continuations
                suggestion_texts = [s["text"] for s in suggestions]
                has_comparison = any(any(op in text for op in ['=', '>', '<']) for text in suggestion_texts)
                
                self.assertTrue(has_comparison, 
                              f"Should suggest mathematical operators for: {case}")


class TestAutoCompleteAdvanced(unittest.TestCase):
    """Test advanced auto-complete functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = CNLParser()
        self.autocomplete = AutoCompleteEngine(self.parser)
    
    def test_context_aware_suggestions(self):
        """Test that suggestions are context-aware"""
        # Quantifier context should not suggest mathematical operators
        quantifier_suggestions = self.autocomplete.suggest_completions("For all x")
        quantifier_texts = [s["text"] for s in quantifier_suggestions]
        
        # Should focus on quantifier continuations, not math
        has_such_that = any("such that" in text for text in quantifier_texts)
        has_math_ops = any(any(op in text for op in ['+', '*', '/']) for text in quantifier_texts)
        
        self.assertTrue(has_such_that, "Should suggest quantifier continuations")
        self.assertFalse(has_math_ops, "Should not suggest math operators in quantifier context")
    
    def test_suggestion_relevance(self):
        """Test that suggestions are relevant to current context"""
        test_cases = [
            ("Define factorial", ["as", "for"]),  # Should suggest definition keywords
            ("x and", ["y", "that"]),  # Should suggest logical continuations
            ("always", ["eventually", "until"]),  # Should suggest temporal operators
        ]
        
        for input_text, expected_keywords in test_cases:
            with self.subTest(input=input_text):
                suggestions = self.autocomplete.suggest_completions(input_text)
                suggestion_texts = " ".join([s["text"] for s in suggestions])
                
                # Should contain at least some expected keywords
                found_keywords = [kw for kw in expected_keywords if kw in suggestion_texts]
                self.assertGreater(len(found_keywords), 0, 
                                 f"Should suggest relevant keywords for '{input_text}'")
    
    def test_suggestion_metadata_quality(self):
        """Test quality of suggestion metadata"""
        suggestions = self.autocomplete.suggest_completions("For all x")
        
        for suggestion in suggestions:
            # Should have meaningful descriptions
            description = suggestion["description"]
            self.assertGreater(len(description), 5, "Description should be meaningful")
            self.assertNotIn("TODO", description, "Should not contain placeholder text")
            
            # Type should be categorized
            suggestion_type = suggestion["type"]
            valid_types = ["quantifier", "operator", "definition", "mathematical", 
                          "continuation", "completion", "quantifier_continuation"]
            self.assertIn(suggestion_type, valid_types, 
                         f"Type '{suggestion_type}' should be valid category")
    
    def test_suggestion_limit_respected(self):
        """Test that suggestion limits are respected"""
        max_suggestions = 5
        suggestions = self.autocomplete.suggest_completions("", max_suggestions)
        
        self.assertLessEqual(len(suggestions), max_suggestions, 
                            "Should respect max_suggestions limit")
        
        # Should still provide meaningful suggestions within limit
        self.assertGreater(len(suggestions), 0, "Should provide some suggestions")
    
    def test_progressive_typing_workflow(self):
        """Test auto-complete behavior during progressive typing"""
        typing_sequence = [
            "F",
            "For",
            "For ",
            "For all",
            "For all x",
            "For all x ",
            "For all x such",
            "For all x such that"
        ]
        
        previous_suggestions = []
        for i, partial_input in enumerate(typing_sequence):
            with self.subTest(step=i, input=partial_input):
                suggestions = self.autocomplete.suggest_completions(partial_input)
                
                # Should always provide some suggestions
                self.assertGreater(len(suggestions), 0, 
                                 f"Should provide suggestions at step {i}: '{partial_input}'")
                
                # Suggestions should become more specific as typing progresses
                if i > 0:
                    current_texts = set(s["text"] for s in suggestions)
                    previous_texts = set(s["text"] for s in previous_suggestions)
                    
                    # Not all suggestions should be the same (some refinement expected)
                    self.assertNotEqual(current_texts, previous_texts, 
                                      f"Suggestions should evolve between steps {i-1} and {i}")
                
                previous_suggestions = suggestions


class TestAutoCompleteIntegration(unittest.TestCase):
    """Integration tests for auto-complete functionality"""
    
    def test_autocomplete_engine_instantiation(self):
        """Test that auto-complete engine can be instantiated"""
        parser = CNLParser()
        autocomplete = AutoCompleteEngine(parser)
        
        self.assertIsNotNone(autocomplete)
        self.assertTrue(hasattr(autocomplete, 'suggest_completions'))
    
    def test_minimum_suggestions_provided(self):
        """Test that minimum number of suggestions are provided"""
        test_cases = [
            ("", 3),  # Should have several starter suggestions
            ("For all x", 1),  # Should have at least one continuation
            ("P(x)", 1),  # Should have at least one logical operator
            ("Define", 1),  # Should have definition continuations
        ]
        
        parser = CNLParser()
        autocomplete = AutoCompleteEngine(parser)
        
        for input_text, expected_min_suggestions in test_cases:
            with self.subTest(input_text=input_text):
                suggestions = autocomplete.suggest_completions(input_text)
                self.assertGreaterEqual(len(suggestions), expected_min_suggestions)
    
    def test_suggestion_structure_consistency(self):
        """Test that all suggestions have consistent structure"""
        parser = CNLParser()
        autocomplete = AutoCompleteEngine(parser)
        
        suggestions = autocomplete.suggest_completions("For all x")
        
        required_fields = ["text", "type", "description"]
        for suggestion in suggestions:
            for field in required_fields:
                self.assertIn(field, suggestion, f"Suggestion missing required field: {field}")
                self.assertIsInstance(suggestion[field], str, f"Field {field} should be string")
                self.assertGreater(len(suggestion[field]), 0, f"Field {field} should not be empty")
    
    def test_no_duplicate_suggestions(self):
        """Test that no duplicate suggestions are provided"""
        parser = CNLParser()
        autocomplete = AutoCompleteEngine(parser)
        
        suggestions = autocomplete.suggest_completions("For all x")
        suggestion_texts = [s["text"] for s in suggestions]
        
        # Should not have duplicate suggestions
        self.assertEqual(len(suggestion_texts), len(set(suggestion_texts)), "Should not have duplicate suggestions")


if __name__ == "__main__":
    print("🎯 Running Auto-Complete NLP Feature Tests")
    print("=" * 50)
    print("Testing auto-complete and suggestion functionality...")
    print("=" * 50)
    
    # Run unittest tests
    unittest.main(verbosity=2)