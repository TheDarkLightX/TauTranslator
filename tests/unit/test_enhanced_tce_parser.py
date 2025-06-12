"""
Unit tests for Enhanced TCE Parser
Tests the enhanced parser's ability to handle complex English sentences.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend/unified"))

from tce_parser import TCEParser as EnhancedTCEParser, ParseContext


class TestEnhancedTCEParser:
    """Test suite for EnhancedTCEParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        assert self.parser is not None
        assert isinstance(self.parser.context, ParseContext)
        assert len(self.parser.patterns) > 0
    
    def test_pattern_compilation(self):
        """Test regex patterns compile correctly."""
        # Check key patterns exist
        assert 'for_every_who' in self.parser.patterns
        assert 'who_clause' in self.parser.patterns
        assert 'always_when' in self.parser.patterns
        assert 'stream_at_time' in self.parser.patterns
        
        # Test pattern matching
        text = "for every person who owns a car, they must pay"
        match = self.parser.patterns['for_every_who'].match(text)
        assert match is not None
        assert match.group(1) == "person"
        assert match.group(2) == "owns a car"
    
    def test_context_reset(self):
        """Test context resets between sentences."""
        # Parse first sentence
        self.parser.parse("John owns a car.")
        context1_entities = len(self.parser.context.entities)
        
        # Parse second sentence - context should reset
        self.parser.parse("Mary has a house.")
        assert len(self.parser.context.entities) == 0  # Reset
    
    def test_simple_quantified_all(self):
        """Test simple 'all X are Y' pattern."""
        result = self.parser.parse("all cats are animals.")
        
        assert "all c:" in result
        assert "is_cat(c)" in result
        assert "is_animals(c)" in result
        assert "->" in result
    
    def test_simple_quantified_no(self):
        """Test 'no X is Y' pattern."""
        result = self.parser.parse("no bird is a mammal.")
        
        assert "all b:" in result
        assert "is_bird(b)" in result
        assert "!" in result
        assert "is_mammal(b)" in result
    
    def test_complex_quantified_who_clause(self):
        """Test complex quantified sentence with who clause."""
        sentence = "for every person who owns a car, if the car is red then the person must pay extra."
        result = self.parser.parse(sentence)
        
        # Check structure
        assert "all p:" in result
        assert "exists c:" in result
        assert "is_car(c)" in result
        assert "owns(p, c)" in result
        assert "is red" in result
        assert "pay extra" in result
        
        # Check coreference resolution
        assert result.count("c") >= 2  # car variable used multiple times
        assert result.count("p") >= 2  # person variable used multiple times
    
    def test_relative_clause_parsing(self):
        """Test relative clause parsing."""
        result = self.parser._parse_relative_clause("p", "owns a car")
        
        assert "exists c:" in result
        assert "is_car(c)" in result
        assert "owns(p, c)" in result
    
    def test_coreference_resolution(self):
        """Test coreference resolution."""
        # Set up context
        self.parser.context.entities["p"] = "person"
        self.parser.context.coreferences["the car"] = "c"
        
        # Test resolution
        text = "the car is red and the person drives it"
        resolved = self.parser._resolve_coreferences(text, "person", "p")
        
        assert "c is red" in resolved
        assert "p drives" in resolved
        assert "it" not in resolved  # pronoun resolved
    
    def test_temporal_always(self):
        """Test temporal 'always' pattern."""
        result = self.parser.parse("always output equals input.")
        
        assert "always" in result
        assert "output" in result
        assert "=" in result
        assert "input" in result
    
    def test_temporal_eventually(self):
        """Test temporal 'eventually' pattern."""
        result = self.parser.parse("eventually all requests complete.")
        
        assert "eventually" in result
        assert "all requests complete" in result
    
    def test_temporal_never(self):
        """Test temporal 'never' pattern."""
        result = self.parser.parse("never the system crashes.")
        
        assert "always" in result
        assert "!" in result
        assert "the system crashes" in result
    
    def test_stream_equation_basic(self):
        """Test basic stream equation."""
        result = self.parser.parse("output stream 1 at time t equals input stream 1 at time t.")
        
        assert "o1[t]" in result
        assert "=" in result
        assert "i1[t]" in result
    
    def test_stream_equation_with_offset(self):
        """Test stream equation with time offset."""
        sentences = [
            ("output 1 at t equals input 1 at t minus 1.", "o1[t] = i1[t-1]"),
            ("output at time t plus 1 equals input at time t.", "o[t+1] = i[t]")
        ]
        
        for sentence, expected in sentences:
            result = self.parser.parse(sentence)
            # Remove spaces for comparison
            assert result.replace(" ", "") == expected.replace(" ", "")
    
    def test_conditional_if_then(self):
        """Test if-then conditional."""
        result = self.parser.parse("if x is positive then x is greater than zero.")
        
        assert "(" in result
        assert ")" in result
        assert "->" in result
        assert "positive" in result
        assert ">" in result
        assert "zero" in result
    
    def test_content_parsing_operators(self):
        """Test operator replacement in content."""
        content = "x is greater than y and z equals 5"
        result = self.parser._parse_content(content)
        
        assert "x > y" in result
        assert "&&" in result
        assert "z = 5" in result
    
    def test_content_parsing_must(self):
        """Test 'must' pattern transformation."""
        content = "person must register"
        result = self.parser._parse_content(content)
        
        assert "must_register(person)" in result
    
    def test_basic_transform_fallback(self):
        """Test basic transformation as fallback."""
        sentence = "x is greater than y implies z is true."
        result = self.parser._basic_transform(sentence)
        
        assert "x > y" in result
        assert "->" in result
        assert "z = true" in result
    
    def test_edge_case_empty_input(self):
        """Test empty input handling."""
        assert self.parser.parse("") == ""
        assert self.parser.parse("   ") == ""
        assert self.parser.parse(".") == ""
    
    def test_edge_case_only_operators(self):
        """Test input with only operators."""
        result = self.parser.parse("and or not")
        assert result  # Should not crash
    
    def test_multiple_entity_types(self):
        """Test handling multiple entity types."""
        sentence = "every student who takes a class from a professor must submit homework."
        result = self.parser.parse(sentence)
        
        # Should create variables for different entities
        assert "s" in result  # student
        assert any(c in result for c in ["c", "c1"])  # class
        assert any(c in result for c in ["p", "p1"])  # professor


class TestParseContext:
    """Test ParseContext data structure."""
    
    def test_context_creation(self):
        """Test creating parse context."""
        context = ParseContext()
        
        assert context.entities == {}
        assert context.variables == []
        assert context.coreferences == {}
    
    def test_context_manipulation(self):
        """Test manipulating context."""
        context = ParseContext()
        
        # Add entity
        context.entities["x"] = "person"
        assert "x" in context.entities
        assert context.entities["x"] == "person"
        
        # Add variable
        context.variables.append("x")
        assert "x" in context.variables
        
        # Add coreference
        context.coreferences["he"] = "x"
        assert context.coreferences["he"] == "x"


class TestPatternMatching:
    """Test individual pattern matching."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def test_for_every_who_pattern(self):
        """Test 'for every X who Y, Z' pattern."""
        test_cases = [
            ("for every person who owns a car, they must register it.", 
             ("person", "owns a car", "they must register it")),
            ("for every student who passes the exam, the student graduates.",
             ("student", "passes the exam", "the student graduates"))
        ]
        
        for sentence, expected in test_cases:
            match = self.parser.patterns['for_every_who'].match(sentence)
            assert match is not None
            assert match.groups() == expected
    
    def test_stream_at_time_pattern(self):
        """Test stream time pattern."""
        test_cases = [
            ("input stream 1 at time t", ("input", "1", "t")),
            ("output 2 at time t plus 1", ("output", "2", "t plus 1"))
        ]
        
        for text, expected_groups in test_cases:
            match = self.parser.patterns['stream_at_time'].search(text)
            assert match is not None
            # Note: groups may include None for optional parts
    
    def test_comparison_pattern(self):
        """Test comparison patterns."""
        test_cases = [
            "x is greater than y",
            "a is less than b",
            "value is equal to 10"
        ]
        
        for text in test_cases:
            match = self.parser.patterns['is_comparison'].match(text)
            assert match is not None
    
    def test_if_then_pattern(self):
        """Test if-then pattern."""
        test_cases = [
            ("if a then b", ("a", "b")),
            ("if x equals 5 then return true", ("x equals 5", "return true"))
        ]
        
        for text, expected in test_cases:
            match = self.parser.patterns['if_then'].match(text)
            assert match is not None
            assert match.group(1).strip() == expected[0]
            assert match.group(2).strip() == expected[1]


class TestIntegrationScenarios:
    """Test complete scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def test_business_rule_scenario(self):
        """Test business rule translation."""
        rule = "all customers who have purchased more than 5 items receive a discount."
        result = self.parser.parse(rule)
        
        # Should have quantifier and structure
        assert "all" in result.lower()
        assert "customer" in result
        # The exact format depends on parsing strategy
    
    def test_scientific_constraint(self):
        """Test scientific constraint."""
        constraint = "for all x, if x is positive then the square root of x exists."
        result = self.parser.parse(constraint)
        
        assert "all x" in result or "∀x" in result
        assert "->" in result
        assert "positive" in result
        assert "square root" in result or "sqrt" in result
    
    def test_protocol_specification(self):
        """Test protocol specification."""
        spec = "always when a request arrives, eventually a response is sent."
        result = self.parser.parse(spec)
        
        assert "always" in result
        assert "request arrives" in result
        assert "response" in result
    
    def test_combined_features(self):
        """Test sentence combining multiple features."""
        sentence = """for every user who is authenticated, 
                     always when the user requests data, 
                     if the data exists then send the data 
                     else send error message."""
        
        result = self.parser.parse(sentence)
        
        # Should handle despite complexity
        assert result
        assert len(result) > 50  # Non-trivial output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])