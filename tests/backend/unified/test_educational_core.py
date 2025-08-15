"""
Test the core autocomplete functionality by directly testing the Trie.

This test verifies that the Trie-based autocomplete service provides correct
suggestions for both Tau and TCE keywords.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from tau_translator_omega.core_engine.trie import Trie

class TestEducationalCoreAutocomplete:
    """Test suite for the core autocomplete feature via the Trie."""

    @pytest.fixture(scope="class")
    def populated_trie(self) -> Trie:
        """Provides a Trie populated with both TCE and Tau keywords."""
        trie = Trie(case_sensitive=False)
        tce_keywords = [
            "for all",
            "there exists",
            "it is always the case that",
            "define the constant",
            "let the function",
        ]
        tau_keywords = [
            "always",
            "sometimes",
            "forall",
            "exists",
            "->",
            "&&",
        ]
        for keyword in tce_keywords + tau_keywords:
            trie.insert(keyword)
        return trie

    def test_tau_educational_autocomplete(self, populated_trie: Trie):
        """Test autocomplete for a common Tau keyword prefix."""
        suggestions = populated_trie.autocomplete("alw", max_results=1)
        assert suggestions == ["always"]

    def test_tce_educational_autocomplete(self, populated_trie: Trie):
        """Test autocomplete for a common TCE keyword prefix."""
        suggestions = populated_trie.autocomplete("for ", max_results=1)
        assert suggestions == ["for all"]

    def test_context_aware_suggestions_for_definition(self, populated_trie: Trie):
        """Test context-aware suggestions for a definition keyword."""
        suggestions = populated_trie.autocomplete("define", max_results=1)
        assert suggestions == ["define the constant"]

    def test_symbolic_operator_autocomplete(self, populated_trie: Trie):
        """Test autocomplete for a symbolic operator."""
        suggestions = populated_trie.autocomplete("-", max_results=1)
        assert suggestions == ["->"]

    def test_no_suggestions_for_unknown_prefix(self, populated_trie: Trie):
        """Test that no suggestions are returned for an unknown prefix."""
        suggestions = populated_trie.autocomplete("xyz", max_results=5)
        assert not suggestions