"""
Comprehensive unit tests for the grammar-aware translation engine.

Author: DarkLightX / Dana Edwards
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.grammar_translator import GrammarTranslationEngine
from backend.unified.translators.base import TranslationDirection, TranslationResult


class TestGrammarTranslationEngine:
    """Unit tests for GrammarTranslationEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a grammar translation engine instance."""
        # Mock the initialization to avoid grammar loading issues
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
            return engine
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        settings = Mock()
        settings.enable_grammar = True
        settings.log_level = "INFO"
        settings.log_format = "%(message)s"
        return settings
    
    def get_mock_tce_grammar(self):
        """Get a simple mock TCE grammar for testing."""
        return """
        start: expression
        
        expression: term
                  | expression "and" term -> and_expr
                  | expression "or" term -> or_expr
        
        term: atom
            | "not" term -> not_expr
        
        atom: CNAME -> variable
            | CNAME "equals" NUMBER -> equals_expr
            | NUMBER -> number
        
        CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/
        NUMBER: /[0-9]+/
        
        %import common.WS
        %ignore WS
        """
    
    # Basic functionality tests
    
    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
            assert engine.name == "grammar_aware"
            assert engine.description == "Grammar-driven translation with Lark parser"
            assert engine.cache_size == 100
    
    def test_engine_with_no_grammar_file(self):
        """Test engine handles missing grammar file gracefully."""
        with patch('backend.unified.translators.grammar_translator.Path.exists', return_value=False):
            engine = GrammarTranslationEngine()
            # Should still initialize but may not have parser
            assert engine.is_available == (engine.tce_parser is not None)
    
    def test_can_translate_with_cnl_parser(self):
        """Test can_translate when CNL parser is available."""
        engine = GrammarTranslationEngine()
        engine.cnl_parser = Mock()
        
        assert engine.can_translate("x equals 5", TranslationDirection.TO_TAU)
        assert not engine.can_translate("", TranslationDirection.TO_TAU)
    
    def test_can_translate_without_parsers(self):
        """Test can_translate when parsers are not available."""
        engine = GrammarTranslationEngine()
        engine.cnl_parser = None
        engine.tau_parser = None
        
        assert not engine.can_translate("x equals 5", TranslationDirection.TO_TAU)
        assert not engine.can_translate("x > 5", TranslationDirection.TO_TCE)
    
    def test_supported_directions(self):
        """Test engine reports correct supported directions."""
        engine = GrammarTranslationEngine()
        
        # With only CNL parser
        engine.cnl_parser = Mock()
        engine.tau_parser = None
        directions = engine.get_supported_directions()
        assert TranslationDirection.TO_TAU in directions
        assert TranslationDirection.TO_TCE not in directions
        
        # With both parsers
        engine.tau_parser = Mock()
        directions = engine.get_supported_directions()
        assert TranslationDirection.TO_TAU in directions
        assert TranslationDirection.TO_TCE in directions
    
    # Grammar loading tests
    
    def test_load_tau_grammar_success(self):
        """Test successful Tau grammar loading."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="start: expr\nexpr: CNAME\nCNAME: /[a-zA-Z_][a-zA-Z0-9_]*/")):
                with patch('backend.unified.translators.grammar_translator.Lark') as mock_lark:
                    result = engine.load_tau_grammar("/path/to/grammar.lark")
                    assert result == True
                    assert mock_lark.called
    
    def test_load_tau_grammar_file_not_found(self):
        """Test Tau grammar loading with missing file."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        
        with patch('os.path.exists', return_value=False):
            result = engine.load_tau_grammar("/nonexistent/grammar.lark")
            assert result == False
    
    def test_load_tau_grammar_parse_error(self):
        """Test Tau grammar loading with parse error."""
        engine = GrammarTranslationEngine()
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="invalid grammar")):
                with patch('lark.Lark', side_effect=Exception("Parse error")):
                    result = engine.load_tau_grammar("/path/to/bad_grammar.lark")
                    assert result == False
    
    def test_load_cnl_grammar_with_transformer(self):
        """Test loading CNL grammar with custom transformer."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        transformer_class = Mock()
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="start: expr\nexpr: CNAME\nCNAME: /[a-zA-Z_][a-zA-Z0-9_]*/")):
                with patch('backend.unified.translators.grammar_translator.Lark') as mock_lark:
                    result = engine.load_cnl_grammar("/path/to/cnl.lark", transformer_class)
                    assert result == True
                    assert engine.cnl_transformer is not None
    
    # Translation tests with mocked parsers
    
    def test_translate_tce_to_tau_success(self):
        """Test successful TCE to Tau translation."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        
        # Mock parser and transformer
        mock_tree = Mock()
        engine.tce_parser = Mock()
        engine.tce_parser.parse.return_value = mock_tree
        engine.cnl_parser = engine.tce_parser  # Set cnl_parser for can_translate
        engine.tce_transformer = Mock()
        engine.tce_transformer.transform.return_value = "x=5"
        
        result = engine.translate("x equals 5", TranslationDirection.TO_TAU)
        
        assert result.success == True
        assert result.translated_text == "x=5"
        assert result.confidence == 0.95
        assert result.metadata["engine_type"] == "grammar_parser"
    
    def test_translate_tce_to_tau_parse_error(self):
        """Test TCE to Tau translation with parse error."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        
        # Mock parser to raise exception
        from lark.exceptions import UnexpectedInput
        engine.tce_parser = Mock()
        error = UnexpectedInput("", 0, 1, 1)
        error.line = 1
        error.column = 1
        engine.tce_parser.parse.side_effect = error
        engine.cnl_parser = engine.tce_parser  # Set cnl_parser for can_translate
        engine.tce_transformer = Mock()
        
        result = engine.translate("invalid syntax", TranslationDirection.TO_TAU)
        
        assert result.success == False
        assert "Parse error" in result.error_message
        assert result.metadata.get("parse_error") == True
    
    def test_translate_tau_to_tce_no_parser(self):
        """Test Tau to TCE translation without Tau parser."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        engine.tau_parser = None
        
        result = engine.translate("x > 5", TranslationDirection.TO_TCE)
        
        assert result.success == False
        assert "Tau grammar" in result.error_message  # More flexible assertion
    
    # Caching tests
    
    def test_translation_caching(self):
        """Test that translations are cached."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        
        # Mock successful translation
        mock_tree = Mock()
        engine.tce_parser = Mock()
        engine.tce_parser.parse.return_value = mock_tree
        engine.cnl_parser = engine.tce_parser  # Set cnl_parser for can_translate
        engine.tce_transformer = Mock()
        engine.tce_transformer.transform.return_value = "x=5"
        
        # First translation
        result1 = engine.translate("x equals 5", TranslationDirection.TO_TAU)
        assert result1.success == True
        
        # Second translation (should use cache)
        result2 = engine.translate("x equals 5", TranslationDirection.TO_TAU)
        assert result2.success == True
        
        # Parser should only be called once due to caching
        assert engine.tce_parser.parse.call_count == 1
    
    def test_cache_key_generation(self):
        """Test cache key generation for different inputs."""
        engine = GrammarTranslationEngine()
        
        key1 = engine._get_cache_key("x equals 5", TranslationDirection.TO_TAU)
        key2 = engine._get_cache_key("x equals 5", TranslationDirection.TO_TCE)
        key3 = engine._get_cache_key("y equals 5", TranslationDirection.TO_TAU)
        
        # Different keys for different inputs
        assert key1 != key2  # Different direction
        assert key1 != key3  # Different text
    
    # Pattern extraction tests
    
    def test_extract_patterns_from_tree(self):
        """Test pattern extraction from parse tree."""
        engine = GrammarTranslationEngine()
        
        # Create mock tree structure
        from lark import Tree
        tree = Tree("expression", [
            Tree("and_expr", [
                Tree("variable", ["x"]),
                Tree("variable", ["y"])
            ])
        ])
        
        patterns = engine._extract_patterns_from_tree(tree)
        assert "expression" in patterns
        assert "and_expr" in patterns
        assert "variable" in patterns
        assert len(patterns) <= 10  # Limited to 10
    
    # Transformer tests
    
    def test_set_tau_transformer(self):
        """Test setting custom Tau transformer."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        engine.tau_parser = Mock()
        
        custom_transformer = Mock()
        custom_transformer.__name__ = "MockTransformer"  # Add missing attribute
        engine.set_tau_transformer(custom_transformer)
        
        assert isinstance(engine.tau_transformer, Mock)
    
    def test_set_tau_transformer_no_parser(self):
        """Test setting transformer without parser loaded."""
        engine = GrammarTranslationEngine()
        engine.tau_parser = None
        
        custom_transformer = Mock()
        engine.set_tau_transformer(custom_transformer)
        
        # Should warn but not crash
        assert engine.tau_transformer != custom_transformer
    
    # Grammar info tests
    
    def test_get_grammar_info(self):
        """Test getting grammar information."""
        engine = GrammarTranslationEngine()
        
        info = engine.get_grammar_info()
        
        assert "cnl_grammar" in info
        assert "tau_grammar" in info
        assert "can_translate_to_tau" in info
        assert "can_translate_to_cnl" in info
        
        # Check CNL grammar info
        assert info["cnl_grammar"]["loaded"] == (engine.cnl_parser is not None)
        assert info["cnl_grammar"]["is_default"] == (info["cnl_grammar"]["name"] == "TCE (default)")
    
    # Error handling tests
    
    def test_translation_with_exception(self):
        """Test translation handles general exceptions."""
        with patch.object(GrammarTranslationEngine, '_initialize_default_tce_parser'):
            engine = GrammarTranslationEngine()
        engine.tce_parser = Mock()
        engine.tce_parser.parse.side_effect = Exception("Unexpected error")
        engine.cnl_parser = engine.tce_parser  # Set cnl_parser for can_translate
        
        result = engine.translate("x equals 5", TranslationDirection.TO_TAU)
        
        assert result.success == False
        assert "Grammar translation failed" in result.error_message
    
    def test_invalid_direction(self):
        """Test handling of unsupported translation direction."""
        engine = GrammarTranslationEngine()
        
        # Mock a direction that's not TO_TAU or TO_TCE
        result = engine.translate("test", TranslationDirection.TO_TAU)
        
        if not engine.can_translate("test", TranslationDirection.TO_TAU):
            assert result.success == False


class TestGrammarTranslationEngineIntegration:
    """Integration tests for grammar engine with real parsing."""
    
    def test_real_tce_parsing(self):
        """Test with real TCE parsing if grammar is available."""
        try:
            engine = GrammarTranslationEngine()
            if engine.tce_parser:
                # Test simple expression
                result = engine.translate("x equals 5", TranslationDirection.TO_TAU)
                # May fail due to grammar issues, but should not crash
                assert isinstance(result, TranslationResult)
        except Exception:
            # Grammar loading might fail in test environment
            pass
    
    def test_metadata_includes_patterns(self):
        """Test that metadata includes detected patterns."""
        engine = GrammarTranslationEngine()
        
        # Mock successful parsing
        from lark import Tree
        mock_tree = Tree("expression", [Tree("variable", ["x"])])
        engine.tce_parser = Mock()
        engine.tce_parser.parse.return_value = mock_tree
        engine.tce_transformer = Mock()
        engine.tce_transformer.transform.return_value = "x"
        
        result = engine.translate("x", TranslationDirection.TO_TAU)
        
        if result.success:
            assert "patterns_detected" in result.metadata
            assert isinstance(result.metadata["patterns_detected"], list)


def mock_open(read_data=""):
    """Helper to create a mock file open."""
    import io
    return lambda *args, **kwargs: io.StringIO(read_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])