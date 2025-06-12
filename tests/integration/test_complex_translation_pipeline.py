"""
Integration tests for complex sentence translation pipeline
Tests the full English -> TCE -> Tau translation flow with complex sentences.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend/unified"))

from tce_parser import TCEParser as EnhancedTCEParser
from declarative_tce_parser import enhance_existing_tce_parser


class TestComplexTranslationPipeline:
    """Integration tests for complex sentence translation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.simple_parser = EnhancedTCEParser()
        self.declarative_parser = enhance_existing_tce_parser()
    
    def test_quantified_with_relative_clause(self):
        """Test: for every X who Y, Z."""
        sentence = "for every person who owns a car, if the car is red then the person must pay extra."
        
        # Test with simple parser
        result = self.simple_parser.parse(sentence)
        
        # Should contain key elements
        assert "all p:" in result
        assert "owns(p, c)" in result
        assert "red" in result
        assert "pay extra" in result
        
        # Should handle coreference
        assert result.count("c") >= 2  # car variable used multiple times
        assert result.count("p") >= 2  # person variable used multiple times
    
    def test_nested_quantifiers(self):
        """Test: for all X there exists Y such that Z."""
        sentences = [
            "for all epsilon greater than 0 there exists delta greater than 0 such that the function is continuous.",
            "for every company there exists at least one employee who manages all projects.",
            "for all x, if x is positive then there exists y such that y squared equals x."
        ]
        
        for sentence in sentences:
            result = self.simple_parser.parse(sentence)
            
            # Should have nested quantifiers
            assert "all" in result or "∀" in result
            assert "exists" in result or "ex" in result or "∃" in result
    
    def test_temporal_properties(self):
        """Test temporal logic statements."""
        test_cases = [
            ("always output 1 at time t equals input 1 at time t.", 
             ["always", "o1[t]", "i1[t]", "="]),
            ("eventually all processes terminate.",
             ["eventually", "all", "processes", "terminate"]),
            ("never the buffer overflows.",
             ["always", "!", "buffer", "overflow"]),
            ("input stream 1 at time t plus 1 equals output stream 2 at time t.",
             ["i1[t", "o2[t]", "="])
        ]
        
        for sentence, expected_elements in test_cases:
            result = self.simple_parser.parse(sentence)
            
            for element in expected_elements:
                assert element in result, f"Expected '{element}' in result for: {sentence}"
    
    def test_conditional_with_multiple_clauses(self):
        """Test complex conditionals."""
        sentence = "if all tests pass and the build succeeds then deploy to production."
        
        result = self.simple_parser.parse(sentence)
        
        # Should have conditional structure
        assert "->" in result
        assert "&&" in result or "and" in result
        assert "tests pass" in result
        assert "build succeeds" in result
        assert "deploy" in result
    
    def test_property_declarations(self):
        """Test property and constraint declarations."""
        test_cases = [
            "all prime numbers are greater than 1.",
            "no system state is both active and inactive.",
            "every valid transaction has a unique identifier.",
            "some functions are continuous but not differentiable."
        ]
        
        for sentence in test_cases:
            result = self.simple_parser.parse(sentence)
            assert result  # Should produce some output
            assert len(result) > 10  # Non-trivial translation
    
    def test_stream_equations(self):
        """Test stream processing equations."""
        test_cases = [
            {
                "input": "output stream 1 at time t equals input stream 1 at time t minus 1.",
                "expected": "o1[t] = i1[t-1]"
            },
            {
                "input": "input 2 at t plus 1 equals output 1 at t.",
                "expected": "i2[t+1] = o1[t]"
            },
            {
                "input": "output at time t equals input at time t plus input at time t minus 1.",
                "expected_contains": ["o", "[t]", "=", "i", "[t]", "+", "i", "[t-1]"]
            }
        ]
        
        for test in test_cases:
            result = self.simple_parser.parse(test["input"])
            
            if "expected" in test:
                # Remove spaces for comparison
                assert result.replace(" ", "") == test["expected"].replace(" ", "")
            else:
                for element in test["expected_contains"]:
                    assert element in result
    
    def test_business_rules(self):
        """Test business rule translations."""
        rules = [
            "all customers who have made purchases exceeding 1000 dollars receive a 10 percent discount.",
            "every employee who completes training must be certified within 30 days.",
            "if a transaction fails three times then lock the account for 24 hours."
        ]
        
        for rule in rules:
            result = self.simple_parser.parse(rule)
            assert result
            assert len(result) > len(rule) * 0.5  # Should expand into formal notation
    
    def test_mathematical_statements(self):
        """Test mathematical and logical statements."""
        statements = [
            "for all x, x greater than 0 implies x not equals 0.",
            "there exists a prime number p such that p is greater than any given number.",
            "the sum of any two even numbers is even.",
            "if n divides a times b then n divides a or n divides b."
        ]
        
        for statement in statements:
            result = self.simple_parser.parse(statement)
            
            # Should contain logical operators
            assert any(op in result for op in ["->", "implies", "&&", "||", "all", "exists"])


class TestDeclarativeTranslation:
    """Test declarative TCE translation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = enhance_existing_tce_parser()
    
    def test_simple_declarations(self):
        """Test simple declarative statements."""
        test_cases = [
            ("all persons are mortal.", "all p: is_person(p) -> is_mortal(p)"),
            ("socrates is a person.", "socrates = person"),
            ("x equals 5.", "x = 5"),
            ("the sky is blue.", "the sky = blue")
        ]
        
        for input_text, expected_pattern in test_cases:
            result = self.parser.parse(input_text)
            # Check for key patterns rather than exact match
            assert any(part in result for part in expected_pattern.split())
    
    def test_property_declarations(self):
        """Test property declarations."""
        sentences = [
            "every car has wheels.",
            "all students must study.",
            "no bird is a mammal.",
            "some numbers are prime."
        ]
        
        for sentence in sentences:
            result = self.parser.parse(sentence)
            assert result
            assert not result.startswith(sentence.lower())  # Should be transformed


class TestErrorHandling:
    """Test error handling in translation pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def test_malformed_input(self):
        """Test handling of malformed input."""
        test_cases = [
            "",  # Empty
            "...",  # Just punctuation
            "for every",  # Incomplete
            "if then",  # Missing parts
        ]
        
        for text in test_cases:
            result = self.parser.parse(text)
            # Should return something, even if just cleaned input
            assert result is not None
    
    def test_unknown_constructs(self):
        """Test handling of unknown language constructs."""
        sentences = [
            "the eigenvalue lambda satisfies the characteristic equation.",
            "perform gradient descent until convergence.",
            "the algorithm terminates in O(n log n) time."
        ]
        
        for sentence in sentences:
            result = self.parser.parse(sentence)
            # Should make best effort
            assert result
            assert len(result) > 0


class TestRealWorldExamples:
    """Test with real-world specification examples."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def test_access_control_rules(self):
        """Test access control specifications."""
        rules = [
            "all users who are authenticated can read public resources.",
            "if a user has admin role then the user can modify all resources.",
            "no user can delete resources owned by other users unless the user is an admin."
        ]
        
        for rule in rules:
            result = self.parser.parse(rule)
            assert "all" in result or "if" in result or "no" in result
            assert len(result) > 20  # Non-trivial translation
    
    def test_protocol_specifications(self):
        """Test protocol/state machine specifications."""
        specs = [
            "always when a request is received, eventually a response is sent.",
            "if the connection is established then data can be transmitted.",
            "the system never sends data before authentication completes."
        ]
        
        for spec in specs:
            result = self.parser.parse(spec)
            assert result
            # Should contain temporal or conditional logic
            assert any(keyword in result for keyword in 
                      ["always", "eventually", "never", "->", "if", "then"])
    
    def test_database_constraints(self):
        """Test database constraint specifications."""
        constraints = [
            "every order must have at least one order item.",
            "the sum of item quantities equals the total quantity.",
            "no two users can have the same email address.",
            "if an order is cancelled then all its items are cancelled."
        ]
        
        for constraint in constraints:
            result = self.parser.parse(constraint)
            assert result
            assert len(result) > len(constraint) * 0.3  # Some expansion expected


class TestPerformanceAndScalability:
    """Test performance with complex inputs."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def test_long_sentences(self):
        """Test handling of very long sentences."""
        # Create a long sentence with multiple clauses
        base = "for every entity that has property A and property B"
        conditions = " and property C" * 10  # Add many conditions
        conclusion = ", the entity must satisfy constraint X and constraint Y and constraint Z"
        
        long_sentence = base + conditions + conclusion
        
        result = self.parser.parse(long_sentence)
        assert result
        assert "all" in result or "for every" in result.lower()
    
    def test_deeply_nested_structures(self):
        """Test deeply nested logical structures."""
        # Build nested conditionals
        nested = "if a then (if b then (if c then (if d then e)))"
        
        result = self.parser.parse(nested)
        assert result
        assert result.count("->") >= 3 or result.count("then") >= 3
    
    def test_multiple_sentences_batch(self):
        """Test batch processing of multiple sentences."""
        sentences = [
            "all x are y.",
            "some y are z.", 
            "no z is x.",
            "if something is x then it is not z.",
            "there exists w such that w is neither x nor y nor z."
        ]
        
        results = []
        for sentence in sentences:
            result = self.parser.parse(sentence)
            results.append(result)
        
        # All should produce results
        assert all(results)
        assert len(set(results)) == len(results)  # All different


if __name__ == "__main__":
    pytest.main([__file__, "-v"])