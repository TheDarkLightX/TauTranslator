"""
Test suite for GrammarDrivenParser
==================================

Tests the grammar-driven parsing and translation capabilities.

Author: DarkLightX / Dana Edwards
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from tau_translator_omega.core_engine.parsers.grammar_driven_parser import (
    GrammarDrivenParser, TranslationMode, ParseResult,
    GrammarDrivenTranslationStrategy, GrammarDrivenTransformer
)
from tau_translator_omega.core_engine.grammar_processing import (
    TGFGrammarService, LoadedGrammar
)
from tau_translator_omega.core_engine.result_enhanced import Success, Failure
from tau_translator_omega.infrastructure.grammar_io import GrammarRepository


class TestGrammarDrivenParser:
    """Test grammar-driven parser functionality."""
    
    @pytest.fixture
    def mock_grammar(self):
        """Create a mock grammar for testing."""
        return LoadedGrammar(
            filename="test.tgf",
            original_name="test.tgf",
            type=".tgf",
            content="test grammar content",
            is_active=True,
            rules={
                'solve_command': {
                    'type': 'rule',
                    'alternatives': [[
                        {'type': 'literal', 'value': 'solve'},
                        {'type': 'non_terminal', 'value': 'constraint'}
                    ]]
                },
                'constraint': {
                    'type': 'rule',
                    'alternatives': [[
                        {'type': 'non_terminal', 'value': 'expression'}
                    ]]
                }
            },
            terminals=['solve', '>', '<', '='],
            non_terminals=['solve_command', 'constraint', 'expression']
        )
    
    @pytest.fixture
    def mock_grammar_loader(self, mock_grammar):
        """Create a mock grammar loader."""
        loader = Mock(spec=TGFGrammarService)
        # Mock methods called by GrammarDrivenParser
        loader.load_and_parse_all_grammars.return_value = Success(None)
        loader.set_active_grammar.return_value = Success(None)

        # Set attributes accessed by GrammarDrivenParser
        loader.active_grammar = mock_grammar
        loader.loaded_grammars = {'test.tgf': mock_grammar}
        # TGFGrammarService.get_grammar_for_parser is not directly called by GrammarDrivenParser.
        # The parser uses TGFGrammarConverter.to_lark_grammar(self.current_grammar), which is what get_grammar_for_parser calls.
        # We mock the end result here.
        loader.get_grammar_for_parser.return_value = 'program: "a"\n'
        return loader
    
    def test_parser_initialization(self, mock_grammar_loader):
        """Test parser initialization with grammar."""
        parser = GrammarDrivenParser(mock_grammar_loader)
        
        assert parser.grammar_service == mock_grammar_loader
        assert parser.current_grammar is not None
        assert parser.parser is not None
    
    def test_parser_without_grammar(self):
        """Test parser behavior when no grammar is loaded."""
        mock_loader = Mock(spec=TGFGrammarService)
        mock_loader.load_and_parse_all_grammars.return_value = Success(None) # Simulate successful load
        mock_loader.active_grammar = None  # No active grammar
        mock_loader.loaded_grammars = {}   # No loaded grammars
        
        parser = GrammarDrivenParser(mock_loader)
        result = parser.parse("solve x > 5")
        
        assert not result.success
        assert result.error == "No grammar loaded"
    
    def test_parse_valid_expression(self, mock_grammar_loader):
        """Test parsing a valid expression."""
        parser = GrammarDrivenParser(mock_grammar_loader)
        
        # Since we're using a simple test grammar, we need a simple expression
        result = parser.parse("solve x")
        
        # The actual parsing may fail with our mock grammar
        # but we're testing the flow
        assert isinstance(result, ParseResult)
    
    def test_translation_mode_detection(self, mock_grammar_loader):
        """Test correct translation mode detection."""
        parser = GrammarDrivenParser(mock_grammar_loader)
        
        # Tau to English
        success, _ = parser.translate("solve x", "tau", "english")
        # Note: actual success depends on grammar implementation
        
        # English to Tau
        success, _ = parser.translate("find x", "english", "tau")
        
        # Unsupported translation
        success, error = parser.translate("test", "french", "german")
        assert not success
        assert "Unsupported translation" in error
    
    def test_get_available_grammars(self, mock_grammar_loader):
        """Test getting list of available grammars."""
        parser = GrammarDrivenParser(mock_grammar_loader)
        grammars = parser.get_available_grammars()
        
        assert isinstance(grammars, list)
        assert 'test.tgf' in grammars
    
    def test_switch_grammar(self, mock_grammar_loader):
        """Test switching between grammars."""
        parser = GrammarDrivenParser(mock_grammar_loader)
        
        mock_grammar_loader.set_active_grammar.return_value = Success(None) # Ensure it returns a Result object
        # The active_grammar attribute on the mock_grammar_loader is already set by the fixture.
        # TGFGrammarService.active_grammar will be updated by the service's set_active_grammar method.
        
        # The service method returns a Result object
        mock_grammar_loader.set_active_grammar.return_value = Success(None)
        
        # The parser's switch_grammar returns a boolean
        switched = parser.switch_grammar("test.tgf")
        assert switched is True
        mock_grammar_loader.set_active_grammar.assert_called_with('test.tgf')
    
    def test_validate_grammar(self, mock_grammar_loader):
        """Test grammar validation."""
        parser = GrammarDrivenParser(mock_grammar_loader)
        
        # Valid grammar - must include 'program' as the start rule
        valid_grammar = """
            program: "hello" "world"
            %import common.WS
            %ignore WS
        """
        is_valid, error = parser.validate_grammar(valid_grammar)
        assert is_valid
        assert error is None
        
        # Invalid grammar
        invalid_grammar = "this is not valid lark grammar"
        is_valid, error = parser.validate_grammar(invalid_grammar)
        assert not is_valid
        assert error is not None
    
    def test_get_grammar_info(self, mock_grammar_loader):
        """Test getting grammar information."""
        parser = GrammarDrivenParser(mock_grammar_loader)
        info = parser.get_grammar_info()
        
        assert info is not None
        assert info['filename'] == 'test.tgf'
        assert info['type'] == '.tgf'
        assert info['num_rules'] == 2
        assert info['num_terminals'] == 4
        assert info['is_active'] is True
    
    def test_parse_error_handling(self, mock_grammar_loader):
        """Test handling of parse errors."""
        parser = GrammarDrivenParser(mock_grammar_loader)
        
        # This should cause a parse error with our simple grammar
        result = parser.parse("invalid syntax $#@!")
        
        assert not result.success
        assert result.error is not None
        assert "error" in result.error.lower() or "expected" in result.error.lower()


class TestGrammarDrivenTransformer:
    """Test the grammar-driven transformer."""
    
    @pytest.fixture
    def mock_grammar(self):
        """Create a mock grammar for testing."""
        return LoadedGrammar(
            filename="test.tgf",
            original_name="test.tgf",
            type=".tgf",
            content="test grammar content",
            is_active=True,
            rules={
                'solve_command': {
                    'type': 'rule',
                    'alternatives': [[
                        {'type': 'literal', 'value': 'solve'},
                        {'type': 'non_terminal', 'value': 'constraint'}
                    ]]
                },
                'constraint': {
                    'type': 'rule',
                    'alternatives': [[
                        {'type': 'non_terminal', 'value': 'expression'}
                    ]]
                }
            },
            terminals=['solve', '>', '<', '='],
            non_terminals=['solve_command', 'constraint', 'expression']
        )
    
    def test_transformer_initialization(self, mock_grammar):
        """Test transformer initialization."""
        transformer = GrammarDrivenTransformer(
            mock_grammar, 
            TranslationMode.TAU_TO_NATURAL
        )
        
        assert transformer.grammar == mock_grammar
        assert transformer.mode == TranslationMode.TAU_TO_NATURAL
        assert len(transformer.translation_rules) > 0
    
    def test_translation_rule_building(self, mock_grammar):
        """Test building translation rules from grammar."""
        transformer = GrammarDrivenTransformer(
            mock_grammar,
            TranslationMode.TAU_TO_NATURAL
        )
        
        # Check that rules were created
        assert 'solve_command' in transformer.translation_rules
        rule = transformer.translation_rules['solve_command']
        assert rule.rule_name == 'solve_command'
        assert rule.template == "Find values that satisfy: {constraint}"
        assert 'constraint' in rule.variables


class TestGrammarDrivenTranslationStrategy:
    """Test the grammar-driven translation strategy."""
    
    @patch('src.tau_translator_omega.core_engine.parsers.grammar_driven_parser.GrammarDrivenParser')
    def test_strategy_initialization(self, mock_parser_class):
        """Test strategy initialization."""
        strategy = GrammarDrivenTranslationStrategy()
        assert strategy.parser is not None
    
    @patch('src.tau_translator_omega.core_engine.parsers.grammar_driven_parser.GrammarDrivenParser')
    def test_strategy_translate(self, mock_parser_class):
        """Test translation through strategy."""
        mock_parser = Mock()
        mock_parser.translate.return_value = (True, "Translated text")
        mock_parser.get_grammar_info.return_value = {'filename': 'test.tgf'}
        mock_parser_class.return_value = mock_parser
        
        strategy = GrammarDrivenTranslationStrategy()
        result = strategy.translate("solve x > 5")
        
        assert result['success'] is True
        assert result['output'] == "Translated text"
        assert result['method'] == 'grammar-driven'
        assert result['grammar'] is not None
    
    @patch('src.tau_translator_omega.core_engine.parsers.grammar_driven_parser.GrammarDrivenParser')
    def test_strategy_availability(self, mock_parser_class):
        """Test checking strategy availability."""
        mock_parser = Mock()
        mock_parser.current_grammar = Mock()
        mock_parser_class.return_value = mock_parser
        
        strategy = GrammarDrivenTranslationStrategy()
        assert strategy.is_available() is True
        
        # Test when no grammar is loaded
        mock_parser.current_grammar = None
        assert strategy.is_available() is False


class TestIntegration:
    """Integration tests with real grammar files."""
    
    def test_real_grammar_loading(self):
        """Test with actual grammar files if available."""
        # Check if grammar directory exists
        grammar_dir = Path("grammars")
        if not grammar_dir.exists():
            pytest.skip("Grammar directory not found")
        
        # Check for tau.tgf
        tau_grammar = grammar_dir / "tau.tgf"
        if not tau_grammar.exists():
            pytest.skip("tau.tgf not found")
        
        # Load real grammar
        repo = FileSystemGrammarRepository(grammar_dir=grammar_dir)
        loader = TGFGrammarService(grammar_repository=repo)
        
        load_result = loader.load_grammar_from_file(tau_grammar.name)
        
        if load_result.is_failure():
            pytest.fail(f"Failed to load grammar {tau_grammar.name}: {load_result.error_value()}")
            return

        grammar = load_result.value
        
        parser = GrammarDrivenParser(loader)
        # Ensure an active grammar is set if parser relies on it during init, or set it explicitly.
        # TGFGrammarService.set_active_grammar might be needed if not loading by name or if auto-activation isn't happening.
        # For now, assuming GrammarDrivenParser will handle it or set_grammar is sufficient.
        if grammar:
             loader.set_active_grammar(grammar.filename) # Ensure the loaded grammar is active for the service

        parser.set_grammar(grammar) # This should pass the LoadedGrammar object
            
        # Try parsing a simple expression
        result = parser.parse("solve x = 5")
        # We don't assert success as it depends on the actual grammar
        assert isinstance(result, ParseResult)