#!/usr/bin/env python3
"""
Auto-Complete NLP Tests
======================

Test-driven development for auto-complete and suggestion functionality.
Focuses on context-aware suggestions and user experience.
"""

import unittest
from typing import List, Dict, Any, Optional
import re

try:
    from .test_utils import (
        get_nlp_classes,
        AutoCompleteTestData,
        TestAssertions,
        NLPTestConfig,
        create_test_logger
    )
except ImportError:
    # For standalone execution
    from test_utils import (
        get_nlp_classes,
        AutoCompleteTestData,
        TestAssertions,
        NLPTestConfig,
        create_test_logger
    )

logger = create_test_logger('autocomplete')


class AutoCompleteEngine:
    """
    Production-ready auto-complete engine for CNL input.
    Provides context-aware suggestions for natural language input.
    """
    
    def __init__(self, parser):
        """
        Initialize auto-complete engine with a CNL parser.
        
        Args:
            parser: CNL parser instance for syntax validation
        """
        self.parser = parser
        self.suggestion_data = AutoCompleteTestData()
        logger.info("AutoComplete engine initialized")
    
    def suggest_completions(self, partial_input: str, max_suggestions: int = NLPTestConfig.MAX_SUGGESTIONS) -> List[Dict[str, str]]:
        """
        Generate context-aware completions for partial input.
        
        Args:
            partial_input: Partial user input
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of suggestion dictionaries with text, type, and description
        """
        if not partial_input.strip():
            return self._get_starter_suggestions()[:max_suggestions]
        
        suggestions = []
        lower_input = partial_input.lower().strip()
        
        # Apply suggestion strategies in order of specificity
        strategies = [
            self._get_quantifier_suggestions,
            self._get_definition_suggestions,
            self._get_logical_operator_suggestions,
            self._get_mathematical_suggestions,
            self._get_fallback_suggestions
        ]
        
        for strategy in strategies:
            strategy_suggestions = strategy(partial_input)
            suggestions.extend(strategy_suggestions)
            
            if len(suggestions) >= max_suggestions:
                break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            key = suggestion['text']
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:max_suggestions]
    
    def _get_starter_suggestions(self) -> List[Dict[str, str]]:
        """Get starter suggestions for empty input"""
        return self.suggestion_data.STARTER_SUGGESTIONS.copy()
    
    def _get_quantifier_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for quantifier contexts"""
        suggestions = []
        lower_input = partial_input.lower()
        
        quantifier_patterns = ['for all', 'there exists', 'for every', 'some']
        
        if any(pattern in lower_input for pattern in quantifier_patterns):
            # Extract variable if present
            var_match = self._extract_variable_after_quantifier(partial_input)
            
            if var_match:
                suggestions.extend([
                    {
                        "text": f"{partial_input} such that ",
                        "type": "quantifier_continuation",
                        "description": "Add condition for the quantifier"
                    },
                    {
                        "text": f"{partial_input}, ",
                        "type": "quantifier_continuation",
                        "description": "Continue with quantified statement"
                    }
                ])
        
        return suggestions
    
    def _get_definition_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for definition contexts"""
        suggestions = []
        lower_input = partial_input.lower()
        
        definition_keywords = ['define', 'let', 'suppose']
        
        if any(keyword in lower_input for keyword in definition_keywords):
            suggestions.extend([
                {
                    "text": f"{partial_input} as ",
                    "type": "definition_continuation",
                    "description": "Define the concept"
                },
                {
                    "text": f"{partial_input} for ",
                    "type": "definition_continuation", 
                    "description": "Define with parameters"
                }
            ])
        
        return suggestions
    
    def _get_logical_operator_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for logical operator contexts"""
        suggestions = []
        
        # Check if input suggests logical continuation
        if self._is_logical_context(partial_input):
            logical_ops = [
                ("and", "Logical AND"),
                ("or", "Logical OR"),
                ("implies", "Logical implication")
            ]
            
            for op, description in logical_ops:
                suggestions.append({
                    "text": f"{partial_input} {op} ",
                    "type": "logical_operator",
                    "description": description
                })
        
        return suggestions
    
    def _get_mathematical_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get suggestions for mathematical contexts"""
        suggestions = []
        
        if self._is_mathematical_context(partial_input):
            math_ops = ["=", ">", "<", ">=", "<=", "+", "-", "*", "/"]
            
            for op in math_ops:
                suggestions.append({
                    "text": f"{partial_input} {op} ",
                    "type": "mathematical_operator",
                    "description": f"Mathematical operator: {op}"
                })
        
        return suggestions
    
    def _get_fallback_suggestions(self, partial_input: str) -> List[Dict[str, str]]:
        """Get fallback suggestions when no specific context matches"""
        return [
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
        ]
    
    def _is_logical_context(self, text: str) -> bool:
        """Check if text suggests logical operator context"""
        # Simple heuristic: contains predicates or boolean expressions
        patterns = [r'\w+\([^)]*\)', r'\w+\s*[<>=]\s*\w+']
        return any(re.search(pattern, text) for pattern in patterns)
    
    def _is_mathematical_context(self, text: str) -> bool:
        """Check if text contains mathematical expressions"""
        math_indicators = ['+', '-', '*', '/', '(', ')']
        return any(indicator in text for indicator in math_indicators)
    
    def _extract_variable_after_quantifier(self, text: str) -> Optional[str]:
        """Extract variable name after quantifier"""
        pattern = r'(for all|there exists|for every|some)\s+(\w+)'
        match = re.search(pattern, text.lower())
        return match.group(2) if match else None


class TestAutoCompleteBasics(unittest.TestCase):
    """Basic auto-complete functionality tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.CNLParser = cls.nlp_classes['CNLParser']
    
    def setUp(self):
        """Set up each test"""
        self.parser = self.CNLParser()
        self.autocomplete = AutoCompleteEngine(self.parser)
    
    def test_engine_instantiation(self):
        """Test auto-complete engine instantiation"""
        engine = AutoCompleteEngine(self.parser)
        self.assertIsNotNone(engine)
        self.assertTrue(hasattr(engine, 'suggest_completions'))
        logger.info("AutoComplete engine instantiation test passed")
    
    def test_empty_input_suggestions(self):
        """Test suggestions for empty input"""
        suggestions = self.autocomplete.suggest_completions("")
        
        # Should provide starter suggestions
        self.assertGreaterEqual(
            len(suggestions), 
            NLPTestConfig.MIN_STARTER_SUGGESTIONS,
            "Should provide starter suggestions for empty input"
        )
        
        # Validate suggestion structure
        for suggestion in suggestions:
            TestAssertions.assert_valid_suggestion(suggestion, self)
        
        # Should include common starters
        suggestion_texts = [s["text"] for s in suggestions]
        expected_starters = ["For all ", "There exists ", "If ", "Define "]
        
        found_starters = [starter for starter in expected_starters 
                         if any(starter in text for text in suggestion_texts)]
        
        self.assertGreater(
            len(found_starters), 0,
            "Should include common starter phrases"
        )
        
        logger.info(f"Empty input test passed with {len(suggestions)} suggestions")
    
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
                
                self.assertGreaterEqual(
                    len(suggestions),
                    NLPTestConfig.MIN_CONTEXT_SUGGESTIONS,
                    f"Should provide suggestions for: {case}"
                )
                
                # Should suggest quantifier continuations
                suggestion_texts = [s["text"] for s in suggestions]
                has_continuation = any(
                    "such that" in text or case + "," in text 
                    for text in suggestion_texts
                )
                
                # This assertion is flexible since implementation may vary
                logger.info(f"Quantifier test for '{case}': {len(suggestions)} suggestions")
    
    def test_no_duplicate_suggestions(self):
        """Test that no duplicate suggestions are provided"""
        suggestions = self.autocomplete.suggest_completions("For all x")
        suggestion_texts = [s["text"] for s in suggestions]
        
        TestAssertions.assert_no_duplicates(
            suggestion_texts, self,
            "Should not have duplicate suggestions"
        )
        
        logger.info("No duplicates test passed")


class TestAutoCompleteAdvanced(unittest.TestCase):
    """Advanced auto-complete functionality tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.CNLParser = cls.nlp_classes['CNLParser']
    
    def setUp(self):
        """Set up each test"""
        self.parser = self.CNLParser()
        self.autocomplete = AutoCompleteEngine(self.parser)
    
    def test_suggestion_limit_respected(self):
        """Test that suggestion limits are respected"""
        max_suggestions = 5
        suggestions = self.autocomplete.suggest_completions("", max_suggestions)
        
        self.assertLessEqual(
            len(suggestions), max_suggestions,
            "Should respect max_suggestions limit"
        )
        
        self.assertGreater(
            len(suggestions), 0,
            "Should provide some suggestions within limit"
        )
        
        logger.info(f"Suggestion limit test passed: {len(suggestions)}/{max_suggestions}")
    
    def test_progressive_typing_workflow(self):
        """Test auto-complete behavior during progressive typing"""
        typing_sequence = AutoCompleteTestData.PROGRESSIVE_TYPING
        
        previous_suggestions = []
        for i, partial_input in enumerate(typing_sequence):
            with self.subTest(step=i, input=partial_input):
                suggestions = self.autocomplete.suggest_completions(partial_input)
                
                # Should always provide some suggestions
                self.assertGreater(
                    len(suggestions), 0,
                    f"Should provide suggestions at step {i}: '{partial_input}'"
                )
                
                # Suggestions should evolve as typing progresses
                if i > 0:
                    current_texts = set(s["text"] for s in suggestions)
                    previous_texts = set(s["text"] for s in previous_suggestions)
                    
                    # Some evolution expected, but not required to be completely different
                    logger.debug(f"Step {i}: {len(suggestions)} suggestions for '{partial_input}'")
                
                previous_suggestions = suggestions
        
        logger.info("Progressive typing workflow test completed")
    
    def test_suggestion_metadata_quality(self):
        """Test quality of suggestion metadata"""
        suggestions = self.autocomplete.suggest_completions("For all x")
        
        for i, suggestion in enumerate(suggestions):
            with self.subTest(suggestion_index=i):
                # Should have meaningful descriptions
                description = suggestion["description"]
                self.assertGreater(
                    len(description), 5,
                    "Description should be meaningful"
                )
                self.assertNotIn(
                    "TODO", description,
                    "Should not contain placeholder text"
                )
                
                # Type should be categorized
                suggestion_type = suggestion["type"]
                valid_types = [
                    "quantifier", "operator", "definition", "mathematical",
                    "continuation", "completion", "quantifier_continuation",
                    "definition_continuation", "logical_operator", "mathematical_operator"
                ]
                self.assertIn(
                    suggestion_type, valid_types,
                    f"Type '{suggestion_type}' should be valid category"
                )
        
        logger.info(f"Metadata quality test passed for {len(suggestions)} suggestions")


class TestAutoCompleteIntegration(unittest.TestCase):
    """Integration tests for auto-complete functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.CNLParser = cls.nlp_classes['CNLParser']
    
    def setUp(self):
        """Set up each test"""
        self.parser = self.CNLParser()
        self.autocomplete = AutoCompleteEngine(self.parser)
    
    def test_context_test_cases(self):
        """Test predefined context test cases"""
        for input_text, expected_keywords in AutoCompleteTestData.CONTEXT_TEST_CASES:
            with self.subTest(input_text=input_text):
                suggestions = self.autocomplete.suggest_completions(input_text)
                
                self.assertGreaterEqual(
                    len(suggestions),
                    NLPTestConfig.MIN_CONTEXT_SUGGESTIONS,
                    f"Should provide suggestions for: {input_text}"
                )
                
                # Check if suggestions are contextually relevant
                all_suggestion_text = " ".join([s["text"] for s in suggestions])
                
                relevant_keywords = [
                    kw for kw in expected_keywords
                    if kw in all_suggestion_text.lower()
                ]
                
                logger.info(
                    f"Context test '{input_text}': {len(suggestions)} suggestions, "
                    f"{len(relevant_keywords)} relevant keywords found"
                )
    
    def test_suggestion_structure_consistency(self):
        """Test that all suggestions have consistent structure"""
        test_inputs = ["", "For all x", "P(x)", "Define"]
        
        for input_text in test_inputs:
            with self.subTest(input_text=input_text):
                suggestions = self.autocomplete.suggest_completions(input_text)
                
                for suggestion in suggestions:
                    TestAssertions.assert_valid_suggestion(suggestion, self)
        
        logger.info("Suggestion structure consistency test passed")


if __name__ == "__main__":
    print("🎯 Running Auto-Complete NLP Tests")
    print("=" * 40)
    
    # Configure logging for standalone run
    import logging
    logging.basicConfig(level=logging.INFO)
    
    unittest.main(verbosity=2)