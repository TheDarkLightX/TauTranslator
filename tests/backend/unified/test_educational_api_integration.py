"""
Test the educational autocomplete functionality using the Trie.

This test verifies that the Trie-based autocomplete service provides
correct suggestions based on the new pure-English grammar.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from tau_translator_omega.core_engine.trie import Trie

class TestEducationalAutocomplete:
    """Test suite for the autocomplete feature."""

    @pytest.fixture(scope="class")
    def populated_trie(self) -> Trie:
        """Fixture to create a Trie populated with TCE keywords."""
        trie = Trie(case_sensitive=False)
        tce_keywords = [
            "it is always the case that",
            "it is not the case that",
            "it will eventually be the case that",
            "let the function",
            "define the constant",
            "the expression",
            "end expression",
            "for all",
            "there exists",
        ]
        tau_keywords = [
            "always",
            "sometimes",
            "->",
            "<->",
            "&&",
            "||",
            "!",
            ":=",
            "all",
            "ex",
        ]
        for keyword in tce_keywords + tau_keywords:
            trie.insert(keyword)
        return trie

    def test_basic_autocomplete(self, populated_trie: Trie):
        """Test a basic autocomplete request with a common prefix."""
        prefix = "it is"
        suggestions = populated_trie.autocomplete(prefix, max_results=3)
        
        assert len(suggestions) == 2
        assert "it is always the case that" in suggestions
        assert "it is not the case that" in suggestions

    def test_function_definition_autocomplete(self, populated_trie: Trie):
        """Test autocomplete for a function definition."""
        prefix = "let the"
        suggestions = populated_trie.autocomplete(prefix, max_results=1)
        
        assert len(suggestions) == 1
        assert "let the function" in suggestions

    def test_quantifier_autocomplete(self, populated_trie: Trie):
        """Test autocomplete for quantifiers."""
        prefix = "for"
        suggestions = populated_trie.autocomplete(prefix, max_results=1)
        
        assert len(suggestions) == 1
        assert "for all" in suggestions

    def test_no_match_autocomplete(self, populated_trie: Trie):
        """Test autocomplete for a prefix with no matches."""
        prefix = "when the"
        suggestions = populated_trie.autocomplete(prefix, max_results=5)
        
        assert len(suggestions) == 0

    def test_case_insensitivity(self, populated_trie: Trie):
        """Test that autocomplete is case-insensitive."""
        prefix = "IT IS ALWAYS"
        suggestions = populated_trie.autocomplete(prefix, max_results=1)
        
        assert len(suggestions) == 1
        assert "it is always the case that" in suggestions

    def test_symbolic_tau_autocomplete(self, populated_trie: Trie):
        """Test autocomplete for symbolic Tau operators."""
        prefix = "-"
        suggestions = populated_trie.autocomplete(prefix, max_results=1)
        assert suggestions == ["->"]

        prefix = "&"
        suggestions = populated_trie.autocomplete(prefix, max_results=1)
        assert suggestions == ["&&"]

    def test_tau_keyword_autocomplete(self, populated_trie: Trie):
        """Test autocomplete for Tau keywords like 'always'."""
        prefix = "alw"
        suggestions = populated_trie.autocomplete(prefix, max_results=1)
        
        assert len(suggestions) == 1
        assert "always" in suggestions