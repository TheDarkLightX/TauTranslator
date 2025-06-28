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

from backend.unified.tce_parser_enhanced import EnhancedTCEParser


class TestEnhancedTCEParser:
    """Test complete integration scenarios for the Enhanced TCE Parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()

    def test_business_rule_scenario(self):
        """Test business rule translation."""
        rule = "all customers who have purchased more than 5 items receive a discount."
        result = self.parser.parse(rule)

        # Should have quantifier and structure
        assert "all" in result.parsed_text.lower()
        assert "customer" in result.parsed_text
        # The exact format depends on parsing strategy

    def test_scientific_constraint(self):
        """Test scientific constraint."""
        constraint = "for all x, if x is positive then the square root of x exists."
        result = self.parser.parse(constraint)

        assert "all x" in result.parsed_text or "∀x" in result.parsed_text
        assert "->" in result.parsed_text
        assert "positive" in result.parsed_text
        assert "square root" in result.parsed_text or "sqrt" in result.parsed_text

    def test_protocol_specification(self):
        """Test protocol specification."""
        spec = "always when a request arrives, eventually a response is sent."
        result = self.parser.parse(spec)

        assert "always" in result.parsed_text
        assert "request arrives" in result.parsed_text
        assert "response" in result.parsed_text

    def test_combined_features(self):
        """Test sentence combining multiple features."""
        sentence = """for every user who is authenticated,
                     always when the user requests data,
                     if the data exists then send the data
                     else send error message."""

        result = self.parser.parse(sentence)

        # Should handle despite complexity
        assert result.parsed_text
        assert len(result.parsed_text) > 10  # Check for some non-trivial output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])